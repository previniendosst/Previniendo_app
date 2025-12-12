import uuid

from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingreso(TimeStampedModel):
    """
    Representa un Ingreso (Conjunto o Empresa) en el sistema
    """
    TIPO_CONJUNTO = 'conjunto'
    TIPO_EMPRESA = 'empresa'
    
    TIPO_INGRESO_CHOICES = (
        (TIPO_CONJUNTO, 'Conjunto'),
        (TIPO_EMPRESA, 'Empresa'),
    )
    
    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    tipo_ingreso = models.CharField(
        choices=TIPO_INGRESO_CHOICES,
        max_length=10,
        verbose_name='tipo ingreso'
    )
    
    nombre = models.CharField(
        max_length=255,
        verbose_name='nombre'
    )
    
    nit = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='NIT'
    )
    
    direccion = models.CharField(
        max_length=500,
        verbose_name='dirección'
    )
    
    nombre_admin = models.CharField(
        max_length=255,
        verbose_name='nombre administrador / representante legal'
    )
    
    correo = models.EmailField(
        verbose_name='correo electrónico'
    )
    
    telefono = models.CharField(
        max_length=20,
        verbose_name='teléfono'
    )
    
    class Meta:
        app_label = 'core'
        verbose_name = 'ingreso'
        verbose_name_plural = 'ingresos'
        default_permissions = ()
    
    def __str__(self):
        """
        Retorna la representación de la instancia del modelo
        """
        return self.nombre


class DocumentFolder(TimeStampedModel):
    """Carpeta de documentos asociada a un Ingreso"""
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    ingreso = models.ForeignKey('Ingreso', related_name='folders', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    creado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'core'
        verbose_name = 'Carpeta de documentos'
        verbose_name_plural = 'Carpetas de documentos'

    def __str__(self):
        return f"{self.nombre} - {self.ingreso}"


class Document(TimeStampedModel):
    """Documento cargado"""
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    carpeta = models.ForeignKey(DocumentFolder, related_name='documents', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documents/%Y/%m/%d/')
    nombre_original = models.CharField(max_length=512, blank=True, null=True)
    creado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'core'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return self.nombre_original or str(self.uuid)


class UserDocumentAccess(TimeStampedModel):
    """Controla qué carpetas y documentos puede ver cada usuario (no Admin)"""
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    usuario = models.ForeignKey(User, related_name='document_access', on_delete=models.CASCADE)
    carpeta = models.ForeignKey(DocumentFolder, related_name='usuario_acceso', on_delete=models.CASCADE)
    puede_descargar = models.BooleanField(default=True, verbose_name='Puede descargar')

    class Meta:
        app_label = 'core'
        verbose_name = 'Acceso a carpeta de usuario'
        verbose_name_plural = 'Accesos a carpetas de usuario'
        unique_together = ('usuario', 'carpeta')

    def __str__(self):
        return f"{self.usuario.username} -> {self.carpeta.nombre}"
