import uuid as uuid_module

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
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
        super(Usuario, self).save(*args, **kwargs)

        if creando:
            self.generar_nueva_clave()

    def generar_nueva_clave(self):
        password = generar_cadena_aleatoria(6)
        self.set_password(password)
        self.save()
        self.enviar_datos_acceso(password)

    def enviar_datos_acceso(self, password):
        asunto = 'Presupuesto participativo - Datos de acceso'
        datos = {
            'nombre_completo': self.get_full_name(),
            'username': self.username,
            'contraseña': password,
            'site_url': settings.SITE_URL
        }

        mensaje = render_to_string('emails/generar_contrasena.html', {'datos': datos})
        self.enviar_mail(asunto, mensaje)

    def enviar_mail(self, asunto, mensaje):
        # Enviar el correo en segundo plano usando EmailMultiAlternatives
        # para garantizar un body en texto plano y HTML y usar un timeout
        from threading import Thread
        from django.core.mail import get_connection, EmailMultiAlternatives
        import logging

        logger = logging.getLogger(__name__)

        def _send():
            connection = None
            try:
                timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
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

                msg = EmailMultiAlternatives(subject=subject, body=text_content or ' ', from_email=settings.DEFAULT_FROM_EMAIL, to=[self.email], connection=connection)
                # Attach HTML message
                msg.attach_alternative(mensaje, "text/html")
                msg.send()
            except Exception as exc:
                # Loguear el error pero no interrumpir el flujo de creación de usuario
                logger.exception('Error enviando mail de acceso al usuario %s: %s', self.email, exc)
            finally:
                try:
                    if connection:
                        connection.close()
                except Exception:
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
