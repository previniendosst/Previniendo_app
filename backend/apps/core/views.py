from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

from config.pagination import Paginacion
from config.mixins import ProtectedForeignKeyDeleteMixin
from .models import Ingreso
from .serializers import (
    IngresoListRetrieveSerializer,
    IngresoCreateUpdateSerializer,
)


class IngresoListCreateAPIView(ListCreateAPIView):
    """
    Se encarga de listar y crear los ingresos, soporta los métodos:
    GET y POST
    """
    queryset = Ingreso.objects.all()
    serializer_class = IngresoListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('nombre', 'nit', 'correo', 'nombre_admin')
    ordering = ('nombre',)
    pagination_class = Paginacion

    def get_serializer_class(self):
        if self.request and self.request.method == 'POST':
            return IngresoCreateUpdateSerializer
        return IngresoListRetrieveSerializer

    def get_queryset(self):
        return Ingreso.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class IngresoRetrieveUpdateDestroyAPIView(ProtectedForeignKeyDeleteMixin, RetrieveUpdateDestroyAPIView):
    """
    Se encarga de visualizar, editar y borrar los ingresos, soporta los métodos:
    GET, PUT y DELETE
    """
    queryset = Ingreso.objects.all()
    serializer_class = IngresoListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request and self.request.method == 'PUT':
            return IngresoCreateUpdateSerializer
        return IngresoListRetrieveSerializer

    def get_queryset(self):
        return Ingreso.objects.all()


class TiposIngresoListAPIView(APIView):
    """
    Se encarga de listar los tipos de ingresos
    """

    def get(self, request):
        lista_elementos = []

        for elemento in Ingreso.TIPO_INGRESO_CHOICES:
            lista_elementos.append({
                'codigo': elemento[0],
                'descripcion': elemento[1],
            })
        return Response(lista_elementos, status=status.HTTP_200_OK)
