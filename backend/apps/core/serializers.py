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


class UserDocumentAccessSerializer(serializers.ModelSerializer):
    carpeta = serializers.PrimaryKeyRelatedField(queryset=DocumentFolder.objects.all(), write_only=True)
    carpeta_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserDocumentAccess
        fields = ['uuid', 'usuario', 'carpeta', 'carpeta_info', 'puede_descargar']
        read_only_fields = ['uuid', 'usuario', 'carpeta_info']

    def get_carpeta_info(self, obj):
        return {
            'uuid': str(obj.carpeta.uuid),
            'nombre': obj.carpeta.nombre,
            'ingreso': obj.carpeta.ingreso.uuid if obj.carpeta.ingreso else None,
        }


class DocumentFolderWithDocumentsSerializer(serializers.ModelSerializer):
    """Serializer para devolver carpeta con sus documentos"""
    documents = DocumentSerializer(many=True, read_only=True)
    ingreso_nombre = serializers.CharField(source='ingreso.nombre', read_only=True)

    class Meta:
        model = DocumentFolder
        fields = ['uuid', 'nombre', 'ingreso_nombre', 'documents', 'created']
        read_only_fields = ['uuid', 'documents', 'ingreso_nombre', 'created']


