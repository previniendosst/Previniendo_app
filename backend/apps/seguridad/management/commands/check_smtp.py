from django.core.management.base import BaseCommand
from django.core.mail import get_connection
from django.conf import settings
import socket
import os

class Command(BaseCommand):
    help = 'Comprueba la conectividad SMTP usando la configuración de settings'

    def handle(self, *args, **options):
        try:
            # Forzar IPv4 para evitar problemas con IPv6
            hosts = socket.getaddrinfo(settings.EMAIL_HOST, settings.EMAIL_PORT, socket.AF_INET, socket.SOCK_STREAM)
            if hosts:
                ipv4 = hosts[0][4][0]
            else:
                ipv4 = settings.EMAIL_HOST

            timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
            # Intento normal (STARTTLS en 587)
            try:
                conn = get_connection(host=ipv4, port=settings.EMAIL_PORT, username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD, use_tls=getattr(settings, 'EMAIL_USE_TLS', False), timeout=timeout, fail_silently=False)
                conn.open()
                conn.close()
                self.stdout.write(self.style.SUCCESS(f'SMTP connectivity OK: {settings.EMAIL_HOST} ({ipv4}:{settings.EMAIL_PORT})'))
                return
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'Fallback: conexión STARTTLS fallida: {exc}'))
                # Intentar SSL en 465
                try:
                    ssl_port = int(os.environ.get('EMAIL_SSL_PORT', 465))
                    conn = get_connection(host=ipv4, port=ssl_port, username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD, use_ssl=True, use_tls=False, timeout=timeout, fail_silently=False)
                    conn.open()
                    conn.close()
                    self.stdout.write(self.style.SUCCESS(f'SMTP connectivity OK (SSL): {settings.EMAIL_HOST} ({ipv4}:{ssl_port})'))
                    return
                except Exception as exc2:
                    self.stdout.write(self.style.ERROR(f'SSL fallback failed: {exc2}'))
                # Si SMTP falla pero hay SENDGRID_API_KEY, intentar envío de prueba por SendGrid
                sg_key = os.environ.get('SENDGRID_API_KEY')
                if sg_key:
                    try:
                        import requests
                        headers = {'Authorization': f'Bearer {sg_key}', 'Content-Type': 'application/json'}
                        payload = {
                            'personalizations': [{'to': [{'email': settings.EMAIL_HOST_USER}], 'subject': 'Prueba envío API'}],
                            'from': {'email': settings.DEFAULT_FROM_EMAIL},
                            'content': [{'type': 'text/plain', 'value': 'Prueba desde check_smtp'}, {'type': 'text/html', 'value': '<p>Prueba desde check_smtp</p>'}]
                        }
                        resp = requests.post('https://api.sendgrid.com/v3/mail/send', json=payload, headers=headers, timeout=10)
                        if resp.status_code in (200, 202):
                            self.stdout.write(self.style.SUCCESS('SendGrid test OK'))
                            return
                        else:
                            self.stdout.write(self.style.ERROR(f'SendGrid test failed: {resp.status_code} {resp.text}'))
                            raise SystemExit(1)
                    except Exception as exc_sg:
                        self.stdout.write(self.style.ERROR(f'SendGrid test exception: {exc_sg}'))
                        raise SystemExit(1)
                raise SystemExit(1)
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'SMTP connectivity FAILED: {exc}'))
            raise SystemExit(1)
