from rest_framework import serializers

from .models import Ingreso


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
