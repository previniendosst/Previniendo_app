import uuid

from django.db import models
from model_utils.models import TimeStampedModel


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
