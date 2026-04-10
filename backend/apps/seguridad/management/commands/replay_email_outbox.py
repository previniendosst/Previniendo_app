from django.core.management.base import BaseCommand
import os
import json
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reenvía los correos guardados por EMAIL_WRITE_ON_FAIL o escritos por file backend'

    def handle(self, *args, **options):
        path = os.environ.get('EMAIL_FAIL_DIR', os.environ.get('EMAIL_FILE_PATH', '/tmp/email_outbox'))
        if not os.path.isdir(path):
            self.stdout.write(self.style.WARNING(f'Path {path} no existe o no es directorio'))
            return
        files = sorted([f for f in os.listdir(path) if f.endswith('.json')])
        if not files:
            self.stdout.write(self.style.SUCCESS('No hay mensajes pendientes'))
            return

        conn = get_connection(fail_silently=False, timeout=getattr(settings, 'EMAIL_TIMEOUT', 10))
        sent_count = 0
        for fname in files:
            fpath = os.path.join(path, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                subject = data.get('subject', '')
                html = data.get('html', '')
                text = data.get('text', '') or ''
                to = data.get('to', [])

                # Si SendGrid está configurado como primario, usar la API para reenviar
                if os.environ.get('SENDGRID_PRIMARY', 'false').lower() in ('1', 'true', 'yes'):
                    sg_key = os.environ.get('SENDGRID_API_KEY')
                    if sg_key:
                        try:
                            headers = {'Authorization': f'Bearer {sg_key}', 'Content-Type': 'application/json'}
                            payload = {
                                'personalizations': [{'to': [{'email': to[0]}], 'subject': subject}],
                                'from': {'email': getattr(settings, 'DEFAULT_FROM_EMAIL', None)},
                                'content': [
                                    {'type': 'text/plain', 'value': text or ' '},
                                    {'type': 'text/html', 'value': html}
                                ]
                            }
                            import requests
                            resp = requests.post('https://api.sendgrid.com/v3/mail/send', json=payload, headers=headers, timeout=10)
                            if resp.status_code in (200, 202):
                                os.remove(fpath)
                                sent_count += 1
                                self.stdout.write(self.style.SUCCESS(f'SendGrid: Enviado y borrado {fname}'))
                                continue
                            else:
                                self.stdout.write(self.style.ERROR(f'SendGrid envío fallido {fname}: {resp.status_code} {resp.text}'))
                        except Exception as exc_sg:
                            logger.exception('SendGrid reenvío falló %s: %s', fname, exc_sg)
                    else:
                        self.stdout.write(self.style.WARNING('SENDGRID_PRIMARY está activo pero SENDGRID_API_KEY no está definido; usando SMTP para reenvío'))

                # Fallback a SMTP
                msg = EmailMultiAlternatives(subject=subject, body=text or ' ', from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None), to=to, connection=conn)
                if html:
                    msg.attach_alternative(html, 'text/html')
                msg.send()
                os.remove(fpath)
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(f'Enviado y borrado {fname}'))
            except Exception as e:
                logger.exception('Fallo reenvío %s: %s', fname, e)
                self.stdout.write(self.style.ERROR(f'Fallo reenvío {fname}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Enviados {sent_count}/{len(files)} mensajes'))
