from rest_framework import serializers

from .models import Ingreso
from .models import DocumentFolder, Document, UserDocumentAccess
from rest_framework import serializers as rf_serializers


class IngresoListRetrieveSerializer(serializers.ModelSerializer):
    tipo_ingreso = serializers.SerializerMethodField()

    class Meta:
        model = Ingreso
        fields = ['uuid', 'tipo_ingreso', 'nombre', 'nit', 'direccion', 'nombre_admin', 'correo', 'telefono']

    def get_tipo_ingreso(self, obj):
        return {
            'codigo': obj.tipo_ingreso,
            'descripcion': obj.get_tipo_ingreso_display()
        }


class IngresoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingreso
        fields = ['uuid', 'tipo_ingreso', 'nombre', 'nit', 'direccion', 'nombre_admin', 'correo', 'telefono']



class DocumentFolderSerializer(serializers.ModelSerializer):
    ingreso = rf_serializers.SlugRelatedField(slug_field='uuid', queryset=Ingreso.objects.all())

    class Meta:
        model = DocumentFolder
        fields = ['uuid', 'ingreso', 'nombre', 'creado_por', 'created']
        read_only_fields = ['uuid', 'creado_por', 'created']


class DocumentSerializer(serializers.ModelSerializer):
    carpeta = rf_serializers.SlugRelatedField(slug_field='uuid', queryset=DocumentFolder.objects.all())

    class Meta:
        model = Document
        fields = ['uuid', 'carpeta', 'archivo', 'nombre_original', 'creado_por', 'created']
        read_only_fields = ['uuid', 'creado_por', 'created']


class DocumentUploadSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField()
    carpeta = rf_serializers.SlugRelatedField(slug_field='uuid', queryset=DocumentFolder.objects.all())

    class Meta:
        model = Document
        fields = ['uuid', 'carpeta', 'archivo', 'nombre_original']
        read_only_fields = ['uuid']

    def validate_archivo(self, value):
        """Validar tamaño máximo basado en settings.DOCUMENT_MAX_UPLOAD_SIZE"""
        from django.conf import settings
        max_size = getattr(settings, 'DOCUMENT_MAX_UPLOAD_SIZE', 26214400)
        if getattr(value, 'size', None) and value.size > max_size:
            # Mensaje claro para el frontend
            raise serializers.ValidationError(f'El archivo es demasiado grande. Tamaño máximo permitido: {max_size // (1024*1024)} MB.')
        return value


class UserDocumentAccessSerializer(serializers.ModelSerializer):
    carpeta = serializers.PrimaryKeyRelatedField(queryset=DocumentFolder.objects.all(), write_only=True)
    carpeta_info = serializers.SerializerMethodField(read_only=True)
    carpeta_documents = DocumentSerializer(source='carpeta.documents', many=True, read_only=True)
    usuario_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserDocumentAccess
        fields = ['uuid', 'usuario', 'usuario_info', 'carpeta', 'carpeta_info', 'carpeta_documents', 'puede_descargar']
        read_only_fields = ['uuid', 'usuario', 'usuario_info', 'carpeta_info', 'carpeta_documents']

    def get_carpeta_info(self, obj):
        return {
            'uuid': str(obj.carpeta.uuid),
            'nombre': obj.carpeta.nombre,
            'ingreso': obj.carpeta.ingreso.uuid if obj.carpeta.ingreso else None,
            'ingreso_nombre': obj.carpeta.ingreso.nombre if obj.carpeta.ingreso else None,
        }

    def get_usuario_info(self, obj):
        nombre = f"{obj.usuario.first_name or ''} {obj.usuario.last_name or ''}".strip()
        return {
            'uuid': str(obj.usuario.uuid),
            'username': getattr(obj.usuario, 'username', None),
            'email': getattr(obj.usuario, 'email', None),
            'nombre': nombre or getattr(obj.usuario, 'username', None) or '',
        }


class DocumentFolderWithDocumentsSerializer(serializers.ModelSerializer):
    """Serializer para devolver carpeta con sus documentos"""
    documents = DocumentSerializer(many=True, read_only=True)
    ingreso_nombre = serializers.CharField(source='ingreso.nombre', read_only=True)

    class Meta:
        model = DocumentFolder
        fields = ['uuid', 'nombre', 'ingreso_nombre', 'documents', 'created']
        read_only_fields = ['uuid', 'documents', 'ingreso_nombre', 'created']


class UserAssignedFoldersSerializer(serializers.Serializer):
    usuario = serializers.DictField()
    folders = DocumentFolderWithDocumentsSerializer(many=True)


