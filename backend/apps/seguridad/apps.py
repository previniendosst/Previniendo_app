import logging
import os
import socket

from django.apps import AppConfig
from django.core.mail import get_connection
from django.conf import settings


class SeguridadConfig(AppConfig):
    name = 'apps.seguridad'

    def ready(self):
        # Comprueba la conectividad SMTP al inicio en entornos de producción
        logger = logging.getLogger(__name__)
        try:
            if settings.EMAIL_BACKEND.endswith('smtp.EmailBackend') and not settings.DEBUG:
                # Resolver IPv4 para evitar problemas con IPv6
                try:
                    hosts = socket.getaddrinfo(settings.EMAIL_HOST, settings.EMAIL_PORT, socket.AF_INET, socket.SOCK_STREAM)
                    if hosts:
                        ipv4 = hosts[0][4][0]
                    else:
                        ipv4 = settings.EMAIL_HOST
                except Exception:
                    ipv4 = settings.EMAIL_HOST

                timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
                # Intento STARTTLS
                try:
                    conn = get_connection(host=ipv4, port=settings.EMAIL_PORT, username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD, use_tls=getattr(settings, 'EMAIL_USE_TLS', False), timeout=timeout, fail_silently=False)
                    conn.open()
                    conn.close()
                    logger.info('SMTP connectivity check OK: %s (%s:%s)', settings.EMAIL_HOST, ipv4, settings.EMAIL_PORT)
                    return
                except Exception as exc1:
                    logger.warning('STARTTLS check failed: %s', exc1)
                    # Intentar SSL en puerto 465
                    try:
                        ssl_port = int(os.environ.get('EMAIL_SSL_PORT', 465))
                        conn = get_connection(host=ipv4, port=ssl_port, username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD, use_ssl=True, use_tls=False, timeout=timeout, fail_silently=False)
                        conn.open()
                        conn.close()
                        logger.info('SMTP connectivity OK (SSL): %s (%s:%s)', settings.EMAIL_HOST, ipv4, ssl_port)
                        return
                    except Exception as exc2:
                        logger.critical('Both STARTTLS and SSL checks failed: %s; %s', exc1, exc2, exc_info=True)
                        if os.environ.get('SMTP_FAIL_STOP', 'false').lower() in ('1', 'true', 'yes'):
                            raise SystemExit('SMTP connectivity check failed; aborting startup as SMTP_FAIL_STOP is set')
        except Exception as exc:
            logger.critical('SMTP connectivity check failed: %s', exc, exc_info=True)
            # Si se configura la variable de entorno SMTP_FAIL_STOP, detener el arranque para forzar corrección
            if os.environ.get('SMTP_FAIL_STOP', 'false').lower() in ('1', 'true', 'yes'):
                raise SystemExit('SMTP connectivity check failed; aborting startup as SMTP_FAIL_STOP is set')
