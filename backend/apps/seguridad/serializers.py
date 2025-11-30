from rest_framework import serializers

from .models import Usuario, Rol, Permiso, RolPermiso, UsuarioIngreso
from apps.core.models import Ingreso


class PermisoSerializer(serializers.ModelSerializer):
    accion = serializers.SerializerMethodField()
    sujeto = serializers.SerializerMethodField()

    class Meta:
        model = Permiso
        fields = ['uuid', 'accion', 'sujeto', 'descripcion']

    def get_accion(self, obj):
        return {
            'codigo': obj.accion,
            'descripcion': obj.get_accion_display()
        }

    def get_sujeto(self, obj):
        return {
            'codigo': obj.sujeto,
            'descripcion': obj.get_sujeto_display()
        }


class RolPermisoSerializer(serializers.ModelSerializer):
    permiso = PermisoSerializer(read_only=True)
    permiso_uuid = serializers.PrimaryKeyRelatedField(
        queryset=Permiso.objects.all(),
        source='permiso',
        write_only=True
    )

    class Meta:
        model = RolPermiso
        fields = ['uuid', 'permiso', 'permiso_uuid']


class RolListRetrieveSerializer(serializers.ModelSerializer):
    permisos = RolPermisoSerializer(many=True, read_only=True)

    class Meta:
        model = Rol
        fields = ['uuid', 'codigo', 'descripcion', 'permisos']


class RolCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['uuid', 'codigo', 'descripcion']


class UsuarioIngresoSerializer(serializers.ModelSerializer):
    ingreso = serializers.SerializerMethodField()
    ingreso_uuid = serializers.PrimaryKeyRelatedField(
        queryset=Ingreso.objects.all(),
        source='ingreso',
        write_only=True
    )

    class Meta:
        model = UsuarioIngreso
        fields = ['uuid', 'ingreso', 'ingreso_uuid']

    def get_ingreso(self, obj):
        from apps.core.serializers import IngresoListRetrieveSerializer
        return IngresoListRetrieveSerializer(obj.ingreso).data


class UsuarioListRetrieveSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()
    ingresos = UsuarioIngresoSerializer(source='usuario_ingresos', many=True, read_only=True)

    class Meta:
        model = Usuario
        fields = ['uuid', 'username', 'first_name', 'last_name', 'email', 'rol', 'ingresos']

    def get_rol(self, obj):
        if obj.rol_sistema:
            return {
                'codigo': obj.rol_sistema.codigo,
                'descripcion': obj.rol_sistema.descripcion,
                'uuid': str(obj.rol_sistema.uuid)
            }
        elif obj.rol:
            return {
                'codigo': obj.rol,
                'descripcion': obj.get_rol_display()
            }
        return None


class UsuarioCreateUpdateSerializer(serializers.ModelSerializer):
    # Accept UUID strings for ingresos and rol_sistema from the frontend.
    # The models expose `uuid` to the API, while the DB primary keys are
    # numeric ids. Using SlugRelatedField with slug_field='uuid' allows the
    # client to send the resource uuid (string) and DRF will resolve the
    # related model instance for create/update.
    ingresos = serializers.SlugRelatedField(
        queryset=Ingreso.objects.all(),
        many=True,
        slug_field='uuid',
        write_only=True,
        required=False
    )
    rol_sistema = serializers.SlugRelatedField(
        queryset=Rol.objects.all(),
        slug_field='uuid',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Usuario
        fields = ['uuid', 'username', 'first_name', 'last_name', 'email', 'rol_sistema', 'ingresos']

    def create(self, validated_data):
        ingresos = validated_data.pop('ingresos', [])
        # Ensure legacy 'rol' DB column is populated to avoid integrity errors
        # if the field is not present / migrations expect NOT NULL. Use an
        # empty string as safe default when no explicit legacy role is set.
        if 'rol' not in validated_data or validated_data.get('rol') is None:
            validated_data['rol'] = ''

        usuario = super().create(validated_data)
        
        for ingreso in ingresos:
            UsuarioIngreso.objects.create(usuario=usuario, ingreso=ingreso)
        
        return usuario

    def update(self, instance, validated_data):
        ingresos = validated_data.pop('ingresos', None)
        # Defensive: ensure legacy 'rol' is not set to None if DB schema
        # requires a non-null value.
        if 'rol' in validated_data and validated_data.get('rol') is None:
            validated_data['rol'] = ''

        usuario = super().update(instance, validated_data)
        
        if ingresos is not None:
            UsuarioIngreso.objects.filter(usuario=usuario).delete()
            for ingreso in ingresos:
                UsuarioIngreso.objects.create(usuario=usuario, ingreso=ingreso)
        
        return usuario


class PerfilSerializer(serializers.ModelSerializer):
    ingresos = UsuarioIngresoSerializer(source='usuario_ingresos', many=True, read_only=True)

    class Meta:
        model = Usuario
        fields = ['uuid', 'first_name', 'last_name', 'email', 'ingresos']
