from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from config.pagination import Paginacion
from config.mixins import ProtectedForeignKeyDeleteMixin
from .models import Ingreso
from apps.seguridad.models import UsuarioIngreso
from .serializers import (
    IngresoListRetrieveSerializer,
    IngresoCreateUpdateSerializer,
    DocumentFolderSerializer,
    DocumentUploadSerializer,
    DocumentSerializer,
    UserDocumentAccessSerializer,
    DocumentFolderWithDocumentsSerializer,
)
from .models import DocumentFolder, Document, UserDocumentAccess
from rest_framework.parsers import MultiPartParser, FormParser


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


class DocumentFolderListCreateAPIView(ListCreateAPIView):
    """Listar o crear carpetas de documentos relacionadas a un ingreso"""
    queryset = DocumentFolder.objects.all()
    serializer_class = DocumentFolderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        ingreso_uuid = self.request.query_params.get('ingreso_uuid')
        qs = DocumentFolder.objects.all()
        if ingreso_uuid:
            qs = qs.filter(ingreso__uuid=ingreso_uuid)
        return qs

    def perform_create(self, serializer):
        # Crear la carpeta con el usuario como creador
        # No auto-asignar: el acceso se controla via UsuarioIngreso
        serializer.save(creado_por=self.request.user)


class DocumentUploadAPIView(APIView):
    """Endpoint para subir archivos a una carpeta"""
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            carpeta_uuid = serializer.validated_data.get('carpeta').uuid if serializer.validated_data.get('carpeta') else None
            carpeta = None
            if carpeta_uuid:
                try:
                    carpeta = DocumentFolder.objects.get(uuid=carpeta_uuid)
                except DocumentFolder.DoesNotExist:
                    return Response({'detail': 'Carpeta no encontrada'}, status=status.HTTP_400_BAD_REQUEST)

            document = Document.objects.create(
                carpeta=serializer.validated_data.get('carpeta'),
                archivo=serializer.validated_data.get('archivo'),
                nombre_original=serializer.validated_data.get('nombre_original') or getattr(serializer.validated_data.get('archivo'), 'name', ''),
                creado_por=request.user if request.user.is_authenticated else None
            )

            out_serializer = DocumentSerializer(document)
            return Response(out_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentListByFolderAPIView(ListCreateAPIView):
    """Listar documentos de una carpeta y crear (alternativa al upload separado)"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        carpeta_uuid = self.request.query_params.get('carpeta_uuid')
        qs = Document.objects.all()
        if carpeta_uuid:
            qs = qs.filter(carpeta__uuid=carpeta_uuid)
        return qs

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class AssignUserDocumentAccessAPIView(ListCreateAPIView):
    """Crear acceso de usuario a carpeta de documentos / Listar asignaciones"""
    queryset = Document.objects.none()
    serializer_class = UserDocumentAccessSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        usuario_uuid = self.request.query_params.get('usuario')
        user = self.request.user
        
        # Si se proporciona usuario_uuid y el usuario actual es admin
        if usuario_uuid and user.rol == 'AD':
            User = get_user_model()
            try:
                target_user = User.objects.get(uuid=usuario_uuid)
                return UserDocumentAccess.objects.filter(usuario=target_user)
            except User.DoesNotExist:
                return UserDocumentAccess.objects.none()
        
        # Si es admin, retornar todas
        if user.rol == 'AD':
            return UserDocumentAccess.objects.all()
        
        # Si no es admin, solo sus propias asignaciones
        return UserDocumentAccess.objects.filter(usuario=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            usuario = get_user_model().objects.get(uuid=data['usuario'])
            carpeta = DocumentFolder.objects.get(uuid=data['carpeta'])
        except (get_user_model().DoesNotExist, DocumentFolder.DoesNotExist):
            return Response({'detail': 'Usuario o carpeta no existe'}, status=status.HTTP_404_NOT_FOUND)

        puede_descargar = data.get('puede_descargar', True)
        
        # Crear o actualizar
        access, created = UserDocumentAccess.objects.update_or_create(
            usuario=usuario,
            carpeta=carpeta,
            defaults={'puede_descargar': puede_descargar}
        )
        
        serializer = self.get_serializer(access)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDocumentAccessListAPIView(ListAPIView):
    """Listar carpetas de documentos basadas en ingresos asignados al usuario"""
    serializer_class = DocumentFolderWithDocumentsSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """
        Retornar solo las carpetas cuyos ingresos están asignados al usuario
        - Admins ven todas las carpetas
        - Usuarios regulares ven solo carpetas de sus ingresos asignados
        """
        user = self.request.user
        
        # Admin ve todas
        if user.rol == 'AD':
            return DocumentFolder.objects.all()
        
        # Usuario regular: obtener sus ingresos asignados
        user_ingresos = user.ingresos.all()  # Via UsuarioIngreso M2M
        
        if not user_ingresos.exists():
            # Si no tiene ingresos asignados, no ve nada
            return DocumentFolder.objects.none()
        
        # Retornar solo carpetas de sus ingresos
        return DocumentFolder.objects.filter(ingreso__in=user_ingresos)


class DocumentDownloadAPIView(APIView):
    """Descargar documento (con verificación de permisos basada en ingresos)"""
    permission_classes = (IsAuthenticated,)

    def get(self, request, document_uuid):
        try:
            document = Document.objects.get(uuid=document_uuid)
        except Document.DoesNotExist:
            return Response({'detail': 'Documento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        
        # Verificar si el usuario tiene acceso
        if user.rol == 'AD':
            # Admin siempre puede descargar
            pass
        else:
            # Usuario normal: verificar que tiene acceso al ingreso de la carpeta
            ingreso = document.carpeta.ingreso
            has_access = user.ingresos.filter(uuid=ingreso.uuid).exists()
            
            if not has_access:
                return Response({'detail': 'No tienes permiso para descargar este documento'}, status=status.HTTP_403_FORBIDDEN)

        # Descargar el archivo
        if not document.archivo:
            return Response({'detail': 'Archivo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        from django.http import FileResponse
        import os
        
        file_path = document.archivo.path
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{document.nombre_original or os.path.basename(file_path)}"'
            return response
        
        return Response({'detail': 'Archivo no encontrado en servidor'}, status=status.HTTP_404_NOT_FOUND)
