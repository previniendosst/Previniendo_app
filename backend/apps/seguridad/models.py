import uuid as uuid_module

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os
import requests
import base64
import mimetypes
from django.template.loader import render_to_string
from django.core.mail import send_mail

from model_utils.models import TimeStampedModel
from .managers import UsuarioManager
from .utils import generar_cadena_aleatoria


class Rol(TimeStampedModel):
    """
    Representa un Rol en el sistema con sus permisos asociados
    """
    uuid = models.UUIDField(
        db_index=True,
        default=uuid_module.uuid4,
        editable=False,
        unique=True
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='código'
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name='descripción'
    )
    
    class Meta:
        app_label = 'seguridad'
        verbose_name = 'rol'
        verbose_name_plural = 'roles'
        default_permissions = ()
    
    def __str__(self):
        return self.descripcion


class Permiso(TimeStampedModel):
    """
    Representa un Permiso en el sistema
    """
    ACCIONES = (
        ('create', 'Crear'),
        ('read', 'Leer'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('detail', 'Detalle'),
        ('finish', 'Finalizar'),
    )
    
    SUJETOS = (
        ('Usuarios', 'Usuarios'),
        ('Ingresos', 'Ingresos'),
        ('Roles', 'Roles'),
        ('MiEspacio', 'Mi Espacio'),
        ('all', 'Todos'),
    )
    
    uuid = models.UUIDField(
        db_index=True,
        default=uuid_module.uuid4,
        editable=False,
        unique=True
    )
    accion = models.CharField(
        choices=ACCIONES,
        max_length=50,
        verbose_name='acción'
    )
    sujeto = models.CharField(
        choices=SUJETOS,
        max_length=50,
        verbose_name='sujeto'
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name='descripción',
        blank=True
    )
    
    class Meta:
        app_label = 'seguridad'
        verbose_name = 'permiso'
        verbose_name_plural = 'permisos'
        default_permissions = ()
        unique_together = ('accion', 'sujeto')
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.get_sujeto_display()}"


class RolPermiso(TimeStampedModel):
    """
    Relaciona Roles con Permisos (Muchos a Muchos explícita)
    """
    uuid = models.UUIDField(
        db_index=True,
        default=uuid_module.uuid4,
        editable=False,
        unique=True
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        verbose_name='rol',
        related_name='permisos'
    )
    permiso = models.ForeignKey(
        Permiso,
        on_delete=models.CASCADE,
        verbose_name='permiso'
    )
    
    class Meta:
        app_label = 'seguridad'
        verbose_name = 'rol permiso'
        verbose_name_plural = 'rol permisos'
        default_permissions = ()
        unique_together = ('rol', 'permiso')
    
    def __str__(self):
        return f"{self.rol.descripcion} - {self.permiso}"


class Usuario(AbstractUser, TimeStampedModel):
    """
    Representa un Usuario en el sistema
    """
    ROL_ADMINISTRADOR = 'AD'
    ROLES = (
        (ROL_ADMINISTRADOR, 'Administrador'),
    )
    uuid = models.UUIDField(
        db_index=True,
        default=uuid_module.uuid4,
        editable=False,
        unique=True
    )
    rol = models.CharField(
        choices=ROLES,
        max_length=2,
        verbose_name='rol',
        null=True,
        blank=True
    )
    
    rol_sistema = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='rol del sistema',
        related_name='usuarios'
    )
    
    ingresos = models.ManyToManyField(
        'core.Ingreso',
        through='UsuarioIngreso',
        verbose_name='ingresos',
        related_name='usuarios'
    )

    email = models.EmailField(unique=True)

    objects = UsuarioManager()

    class Meta:
        app_label = 'seguridad'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        default_permissions = ()

    def __str__(self):
        """
        Retorna la representación de la instancia del modelo
        """
        return self.email

    def save(self, *args, **kwargs):
        creando = not self.pk
        # Si el atributo _skip_email_on_create está definido, no enviar correo inicial
        skip_initial = getattr(self, '_skip_email_on_create', False)
        super(Usuario, self).save(*args, **kwargs)

        # Ya no se genera ni envía una contraseña inicial automáticamente al crear usuarios.
        # La contraseña se debe proporcionar manualmente en el formulario de creación.
        if creando and not skip_initial:
            pass

    def generar_nueva_clave(self):
        password = generar_cadena_aleatoria(6)
        self.set_password(password)
        self.save()
        self.enviar_datos_acceso(password)

    def enviar_datos_acceso(self, password):
        asunto = 'Previniendo SST - Datos de acceso'
        datos = {
            'nombre_completo': self.get_full_name(),
            'username': self.username,
            'contraseña': password,
            'site_url': settings.SITE_URL
        }

        mensaje = render_to_string('emails/generar_contrasena.html', {'datos': datos})
        self.enviar_mail(asunto, mensaje)

    def enviar_mail(self, asunto, mensaje):
        """Enviar correo. En producción, si `EMAIL_FAIL_RAISE` está activado, se enviará de forma
        síncrona y se propagará cualquier excepción para hacer visible fallos de envío.
        En caso contrario, el envío se realiza en background (Thread) y errores se registran.
        """
        from threading import Thread
        from django.core.mail import get_connection, EmailMultiAlternatives
        import logging

        logger = logging.getLogger(__name__)

        def _do_send(host_override=None, raise_on_error=False):
            connection = None
            try:
                timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
                if host_override:
                    connection = get_connection(host=host_override, port=settings.EMAIL_PORT, username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD, use_tls=getattr(settings, 'EMAIL_USE_TLS', False), fail_silently=False, timeout=timeout)
                else:
                    connection = get_connection(fail_silently=False, timeout=timeout)

                subject = asunto
                text_content = ''
                if mensaje:
                    # Strip tags for plain text fallback (simple heuristic)
                    try:
                        import re
                        text_content = re.sub('<[^<]+?>', '', mensaje)
                    except Exception:
                        text_content = ''

                logger.info('SMTP send attempt: host=%s port=%s user=%s to=%s', settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER, self.email)

                # Si se configuró SendGrid como primario, intentar API primero
                if os.environ.get('SENDGRID_PRIMARY', 'false').lower() in ('1', 'true', 'yes'):
                    sg_key = os.environ.get('SENDGRID_API_KEY')
                    if sg_key:
                        try:
                            headers = {'Authorization': f'Bearer {sg_key}', 'Content-Type': 'application/json'}
                            payload = {
                                'personalizations': [{'to': [{'email': self.email}], 'subject': subject}],
                                'from': {'email': settings.DEFAULT_FROM_EMAIL},
                                'content': [
                                    {'type': 'text/plain', 'value': text_content or ' '},
                                    {'type': 'text/html', 'value': mensaje}
                                ],
                                'reply_to': {'email': settings.DEFAULT_FROM_EMAIL},
                                'headers': {
                                    'List-Unsubscribe': f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe>'
                                }
                            }
                            # Adjuntar logo inline si está disponible (para evitar que clientes bloqueen imágenes remotas)
                            try:
                                img_path = os.path.join(settings.BASE_DIR, 'config', 'templates', 'emails', 'escudo_itagui.png')
                                if os.path.exists(img_path):
                                    with open(img_path, 'rb') as _img:
                                        b = _img.read()
                                    content = base64.b64encode(b).decode()
                                    mime = mimetypes.guess_type(img_path)[0] or 'image/png'
                                    payload['attachments'] = [{
                                        'content': content,
                                        'type': mime,
                                        'filename': 'escudo_itagui.png',
                                        'disposition': 'inline',
                                        'content_id': '<escudo_itagui>'
                                    }]
                            except Exception:
                                logger.exception('No se pudo adjuntar imagen inline para SendGrid')

                            resp = requests.post('https://api.sendgrid.com/v3/mail/send', json=payload, headers=headers, timeout=10)
                            if resp.status_code in (200, 202):
                                logger.info('Correo enviado vía SendGrid (primario) a %s', self.email)
                                return 1
                            else:
                                logger.warning('SendGrid primario envío fallido: %s %s', resp.status_code, resp.text)
                        except Exception as exc_sg_primary:
                            logger.exception('SendGrid primario falló: %s', exc_sg_primary)
                    else:
                        logger.warning('SENDGRID_PRIMARY está activo pero no se encontró SENDGRID_API_KEY en el entorno')

                msg = EmailMultiAlternatives(subject=subject, body=text_content or ' ', from_email=settings.DEFAULT_FROM_EMAIL, to=[self.email], connection=connection)
                # Headers útiles para entregabilidad
                msg.extra_headers = {
                    'Reply-To': settings.DEFAULT_FROM_EMAIL,
                    'List-Unsubscribe': f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe>'
                }
                msg.attach_alternative(mensaje, "text/html")
                # Adjuntar imagen inline para clientes que respeten Content-ID
                try:
                    from email.mime.image import MIMEImage
                    img_path = os.path.join(settings.BASE_DIR, 'config', 'templates', 'emails', 'escudo_itagui.png')
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as _img:
                            img = MIMEImage(_img.read(), _subtype=(mimetypes.guess_type(img_path)[0] or 'image/png').split('/')[1])
                        img.add_header('Content-ID', '<escudo_itagui>')
                        img.add_header('Content-Disposition', 'inline', filename='escudo_itagui.png')
                        msg.attach(img)
                except Exception:
                    logger.exception('No se pudo adjuntar imagen inline para SMTP')
                sent = msg.send()
                return sent
            except OSError as exc:
                logger.exception('Error socket enviando mail (intentando IPv4 fallback) al usuario %s: %s', self.email, exc)
                # Intentar resolver a IPv4 explícitamente y reintentar
                try:
                    import socket
                    hosts = socket.getaddrinfo(settings.EMAIL_HOST, settings.EMAIL_PORT, socket.AF_INET, socket.SOCK_STREAM)
                    if hosts:
                        ipv4 = hosts[0][4][0]
                        logger.info('Usando IPv4 %s para conectar SMTP', ipv4)
                        timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
                        # Intento STARTTLS IPv4 primero
                        try:
                            connection = get_connection(host=ipv4, port=settings.EMAIL_PORT, username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD, use_tls=getattr(settings, 'EMAIL_USE_TLS', False), fail_silently=False, timeout=timeout)
                            subject = asunto
                            text_content = ''
                            if mensaje:
                                import re
                                try:
                                    text_content = re.sub('<[^<]+?>', '', mensaje)
                                except Exception:
                                    text_content = ''
                            msg = EmailMultiAlternatives(subject=subject, body=text_content or ' ', from_email=settings.DEFAULT_FROM_EMAIL, to=[self.email], connection=connection)
                            msg.attach_alternative(mensaje, "text/html")
                            sent = msg.send()
                            return sent
                        except Exception as exc1:
                            logger.warning('STARTTLS IPv4 reintento fallido: %s', exc1)
                            # Intentar SSL en 465
                            try:
                                ssl_port = int(os.environ.get('EMAIL_SSL_PORT', 465))
                                connection = get_connection(host=ipv4, port=ssl_port, username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD, use_ssl=True, use_tls=False, fail_silently=False, timeout=timeout)
                                subject = asunto
                                text_content = ''
                                if mensaje:
                                    import re
                                    try:
                                        text_content = re.sub('<[^<]+?>', '', mensaje)
                                    except Exception:
                                        text_content = ''
                                msg = EmailMultiAlternatives(subject=subject, body=text_content or ' ', from_email=settings.DEFAULT_FROM_EMAIL, to=[self.email], connection=connection)
                                msg.attach_alternative(mensaje, "text/html")
                                sent = msg.send()
                                return sent
                            except Exception as exc2:
                                logger.exception('SSL IPv4 reintento fallido al enviar mail al usuario %s: %s', self.email, exc2)
                                # Fallback: usar SendGrid HTTP API si está configurado
                                try:
                                    sg_key = os.environ.get('SENDGRID_API_KEY')
                                    if sg_key:
                                        headers = {'Authorization': f'Bearer {sg_key}', 'Content-Type': 'application/json'}
                                        payload = {
                                            'personalizations': [{'to': [{'email': self.email}], 'subject': asunto}],
                                            'from': {'email': settings.DEFAULT_FROM_EMAIL},
                                            'content': [
                                                {'type': 'text/plain', 'value': text_content or ' '},
                                                {'type': 'text/html', 'value': mensaje}
                                            ],
                                            'reply_to': {'email': settings.DEFAULT_FROM_EMAIL},
                                            'headers': {
                                                'List-Unsubscribe': f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe>'
                                            }
                                        }
                                        # Intentar adjuntar inline el logo si está disponible
                                        try:
                                            img_path = os.path.join(settings.BASE_DIR, 'config', 'templates', 'emails', 'escudo_itagui.png')
                                            if os.path.exists(img_path):
                                                with open(img_path, 'rb') as _img:
                                                    b = _img.read()
                                                content = base64.b64encode(b).decode()
                                                mime = mimetypes.guess_type(img_path)[0] or 'image/png'
                                                payload['attachments'] = [{
                                                    'content': content,
                                                    'type': mime,
                                                    'filename': 'escudo_itagui.png',
                                                    'disposition': 'inline',
                                                    'content_id': '<escudo_itagui>'
                                                }]
                                        except Exception:
                                            logger.exception('No se pudo adjuntar imagen inline para SendGrid (fallback)')

                                        resp = requests.post('https://api.sendgrid.com/v3/mail/send', json=payload, headers=headers, timeout=10)
                                        if resp.status_code in (200, 202):
                                            logger.info('Correo enviado vía SendGrid a %s', self.email)
                                            return 1
                                        else:
                                            logger.error('SendGrid envío fallido: %s %s', resp.status_code, resp.text)
                                            if raise_on_error:
                                                resp.raise_for_status()
                                except Exception as exc_sg:
                                    logger.exception('SendGrid fallback falló al enviar mail al usuario %s: %s', self.email, exc_sg)
                                    if raise_on_error:
                                        raise
                                if raise_on_error:
                                    raise
                    else:
                        logger.error('No se encontraron direcciones IPv4 para %s', settings.EMAIL_HOST)
                except Exception as exc2:
                    logger.exception('Reintento IPv4 fallido al enviar mail al usuario %s: %s', self.email, exc2)
                    if raise_on_error:
                        raise
            except Exception as exc:
                logger.exception('Error enviando mail de acceso al usuario %s: %s', self.email, exc)
                if raise_on_error:
                    raise
            finally:
                try:
                    if connection:
                        connection.close()
                except Exception:
                    pass
            # Si está configurado, escribir el correo fallido en disco para reintento posterior
            try:
                if os.environ.get('EMAIL_WRITE_ON_FAIL', 'false').lower() in ('1', 'true', 'yes'):
                    import json
                    import datetime
                    path = os.environ.get('EMAIL_FAIL_DIR', os.environ.get('EMAIL_FILE_PATH', '/tmp/email_outbox'))
                    os.makedirs(path, exist_ok=True)
                    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
                    fname = f'email_{self.email}_{timestamp}.json'
                    payload = {'to': [self.email], 'subject': asunto, 'html': mensaje, 'text': text_content or ''}
                    try:
                        with open(os.path.join(path, fname), 'w', encoding='utf-8') as f:
                            json.dump(payload, f, ensure_ascii=False)
                        logger.info('Correo fallido guardado en %s', os.path.join(path, fname))
                    except Exception:
                        logger.exception('Fallo al escribir mail fallido a disco')
            except Exception:
                logger.exception('Fallo comprobando EMAIL_WRITE_ON_FAIL')
            return 0

        # Si la configuración obliga a fallar en caso de error, normalmente enviamos de forma
        # síncrona y propagamos; sin embargo, si está activado el guardado de mails fallidos
        # (EMAIL_WRITE_ON_FAIL) no debemos abortar operaciones críticas (p.ej. creación de usuarios),
        # por lo que preferimos no propagar la excepción y dejar que el correo se guarde para reintento.
        if getattr(settings, 'EMAIL_FAIL_RAISE', False) and os.environ.get('EMAIL_WRITE_ON_FAIL', 'false').lower() not in ('1', 'true', 'yes'):
            return _do_send(raise_on_error=True)

        # Si está activado el guardado de mails fallidos, intentar envío síncrono
        # sin propagar errores y escribir a disco inmediatamente en caso de fallo.
        if os.environ.get('EMAIL_WRITE_ON_FAIL', 'false').lower() in ('1', 'true', 'yes'):
            return _do_send(raise_on_error=False)

        # Modo asíncrono por defecto: ejecutar en background y registrar errores
        def _send():
            try:
                _do_send()
            except Exception:
                # Ya registrado dentro de _do_send
                pass

        Thread(target=_send, daemon=True).start()


class UsuarioIngreso(TimeStampedModel):
    """
    Relaciona Usuarios con Ingresos (Muchos a Muchos explícita)
    Permite que un usuario tenga múltiples ingresos asignados
    """
    uuid = models.UUIDField(
        db_index=True,
        default=uuid_module.uuid4,
        editable=False,
        unique=True
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name='usuario',
        related_name='usuario_ingresos'
    )
    ingreso = models.ForeignKey(
        'core.Ingreso',
        on_delete=models.CASCADE,
        verbose_name='ingreso'
    )
    
    class Meta:
        app_label = 'seguridad'
        verbose_name = 'usuario ingreso'
        verbose_name_plural = 'usuario ingresos'
        default_permissions = ()
        unique_together = ('usuario', 'ingreso')
    
    def __str__(self):
        return f"{self.usuario.email} - {self.ingreso.nombre}"
