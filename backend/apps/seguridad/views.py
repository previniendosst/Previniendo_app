from rest_framework import status
from rest_framework_jwt.settings import api_settings
from rest_framework.views import (
    APIView,
    Response
)
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

from config.pagination import Paginacion
from .models import (
    Usuario,
    Rol,
    Permiso,
    RolPermiso,
    UsuarioIngreso,
)
from .serializers import (
    UsuarioListRetrieveSerializer,
    UsuarioCreateUpdateSerializer,
    PerfilSerializer,
    RolListRetrieveSerializer,
    RolCreateUpdateSerializer,
    PermisoSerializer,
    RolPermisoSerializer,
    UsuarioIngresoSerializer,
)
from config.mixins import ProtectedForeignKeyDeleteMixin
from apps.seguridad.permissions import EsUsuarioAdministrador
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate


class LoginAPIView(APIView):
    """
    Endpoint de login personalizado que retorna usuario con sus permisos.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        usuario = authenticate(username=username, password=password)

        if usuario is None:
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener permisos: primero del rol_sistema (modelo Rol), sino del rol legacy
        permisos = []
        if usuario.rol_sistema:
            # Obtener permisos del rol_sistema (tabla seguridad_rolpermiso)
            rol_permisos = RolPermiso.objects.filter(rol=usuario.rol_sistema)
            for rp in rol_permisos:
                permisos.append({
                    'uuid': str(rp.permiso.uuid),
                    'codigo': f"CAN_{rp.permiso.accion.upper()}_{rp.permiso.sujeto.upper()}",
                    'accion': {
                        'codigo': rp.permiso.accion,
                        'descripcion': rp.permiso.get_accion_display()
                    },
                    'sujeto': {
                        'codigo': rp.permiso.sujeto,
                        'descripcion': rp.permiso.get_sujeto_display()
                    },
                    'descripcion': rp.permiso.descripcion
                })
        elif usuario.rol == 'AD':
            # Admin: otorgar permisos a todos los sujetos
            permisos = self._get_all_permissions()

        # Generar token JWT
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(usuario)
        token = jwt_encode_handler(payload)

        # Retornar token y usuario con permisos
        serializer = UsuarioListRetrieveSerializer(usuario)
        usuario_data = serializer.data
        usuario_data['permisos'] = permisos

        return Response({
            'token': token,
            'usuario': usuario_data
        }, status=status.HTTP_200_OK)

    def _get_all_permissions(self):
        """Retorna todos los permisos del sistema para admins."""
        permisos = []
        for perm in Permiso.objects.all():
            permisos.append({
                'uuid': str(perm.uuid),
                'codigo': f"CAN_{perm.accion.upper()}_{perm.sujeto.upper()}",
                'accion': {
                    'codigo': perm.accion,
                    'descripcion': perm.get_accion_display()
                },
                'sujeto': {
                    'codigo': perm.sujeto,
                    'descripcion': perm.get_sujeto_display()
                },
                'descripcion': perm.descripcion
            })
        return permisos

class UsuarioListCreateAPIView(ListCreateAPIView):
    """
    Se encarga de listar y crear los usuarios, soporta los métodos:
    GET y POST
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username')
    pagination_class = Paginacion

    def get_serializer_class(self):
        if self.request and self.request.method == 'POST':
            return UsuarioCreateUpdateSerializer
        return UsuarioListRetrieveSerializer

    def get_queryset(self):
        return Usuario.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class UsuarioRetrieveUpdateDestroyAPIView(ProtectedForeignKeyDeleteMixin, RetrieveUpdateDestroyAPIView):
    """
    Se encarga de visualizar, editar y borrar los usuarios, soporta los métodos:
    GET, PUT y DELETE
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request and self.request.method == 'PUT':
            return UsuarioCreateUpdateSerializer
        return UsuarioListRetrieveSerializer

    def get_queryset(self):
        return Usuario.objects.all()


class RolesUsuarioListAPIView(APIView):
    """
    Se encarga de listar los roles de usuario del nuevo modelo Rol
    """

    def get(self, request):
        roles = Rol.objects.all()
        serializer = RolListRetrieveSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PerfilView(APIView):
    """
    Se encarga de actualizar el perfil de usuario, soporta los métodos:
    GET y PUT
    """

    def get(self, request):
        serializer = PerfilSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = PerfilSerializer(request.user, data=request.data)
        nuevo_password = request.data.get('nuevo_password', None)
        actual_password = request.data.get('actual_password', None)

        if serializer.is_valid():
            serializer.save()
        else:
            return Response({'detail': 'Petición no válida.', 'errores': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        if nuevo_password:
            if request.user.check_password(actual_password):
                try:
                    request.user.set_password(nuevo_password)
                    request.user.save()
                except Exception:
                    return Response({"detail": "Error al actualizar el password."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"detail": "Las contraseñas no coinciden."},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Perfil actualizado correctamente.."},
                        status=status.HTTP_200_OK)


class UsuarioGenerarClaveAPIView(APIView):
    """
    Se encarga de generar una nueva clave al usuario y enviarla por email
    soporta el método GET
    """
    permission_classes = (IsAuthenticated, EsUsuarioAdministrador)

    def get(self, request, uuid):
        try:
            usuario = Usuario.objects.get(uuid=uuid)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'El usuario no existe.'},
                status=status.HTTP_404_NOT_FOUND
            )

        usuario.generar_nueva_clave()

        return Response({'detail': 'Clave de usuario generada correctamente.'})
    
class VerificarCorreoAPIView(APIView):
    """
    Verifica si el email existe en la base de datos.
    """
    permission_classes = ()
    
    def post(self, request):
        
        email = request.data.get('email')
        
        try:
            # Buscamos el email de usuario para verificar si existe
            usuario = Usuario.objects.get(email=email)
            
            # Si el usuario existe, generamos una nueva clave
            usuario.generar_nueva_clave()
            
            # Responder con un mensaje de éxito
            return Response({
                'detail': 'Se ha enviado una nueva clave al correo proporcionado.'
            }, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            return Response({'detail': 'El correo no está registrado.'}, status=status.HTTP_404_NOT_FOUND)


class RolListCreateAPIView(ListCreateAPIView):
    """
    Se encarga de listar y crear los roles, soporta los métodos:
    GET y POST
    """
    queryset = Rol.objects.all()
    serializer_class = RolListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)
    pagination_class = Paginacion

    def get_serializer_class(self):
        if self.request and self.request.method == 'POST':
            return RolCreateUpdateSerializer
        return RolListRetrieveSerializer

    def get_queryset(self):
        return Rol.objects.prefetch_related('permisos')


class RolRetrieveUpdateDestroyAPIView(ProtectedForeignKeyDeleteMixin, RetrieveUpdateDestroyAPIView):
    """
    Se encarga de visualizar, editar y borrar los roles, soporta los métodos:
    GET, PUT y DELETE
    """
    queryset = Rol.objects.prefetch_related('permisos')
    serializer_class = RolListRetrieveSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request and self.request.method == 'PUT':
            return RolCreateUpdateSerializer
        return RolListRetrieveSerializer


class PermisoListAPIView(APIView):
    """
    Se encarga de listar los permisos disponibles.
    Retorna todas las combinaciones de acciones x sujetos, creándolas si no existen.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # Obtener todas las combinaciones posibles de ACCIONES x SUJETOS
        acciones = dict(Permiso.ACCIONES)
        sujetos = dict(Permiso.SUJETOS)

        permisos = []
        for accion_code, accion_desc in acciones.items():
            for sujeto_code, sujeto_desc in sujetos.items():
                # Intentar obtener o crear el permiso
                permiso, created = Permiso.objects.get_or_create(
                    accion=accion_code,
                    sujeto=sujeto_code,
                    defaults={
                        'descripcion': f"{accion_desc} {sujeto_desc}"
                    }
                )
                permisos.append(permiso)

        serializer = PermisoSerializer(permisos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RolPermisoCreateDestroyAPIView(APIView):
    """
    Se encarga de agregar y remover permisos de un rol
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, uuid):
        try:
            rol = Rol.objects.get(uuid=uuid)
            permiso_uuid = request.data.get('permiso_uuid')
            
            try:
                permiso = Permiso.objects.get(uuid=permiso_uuid)
                rol_permiso, created = RolPermiso.objects.get_or_create(
                    rol=rol,
                    permiso=permiso
                )
                
                if created:
                    return Response(
                        {'detail': 'Permiso agregado al rol correctamente.'},
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {'detail': 'El permiso ya está asignado al rol.'},
                        status=status.HTTP_200_OK
                    )
            except Permiso.DoesNotExist:
                return Response(
                    {'detail': 'El permiso no existe.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Rol.DoesNotExist:
            return Response(
                {'detail': 'El rol no existe.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, uuid, permiso_uuid):
        try:
            rol = Rol.objects.get(uuid=uuid)
            rol_permiso = RolPermiso.objects.get(rol=rol, permiso__uuid=permiso_uuid)
            rol_permiso.delete()
            
            return Response(
                {'detail': 'Permiso removido del rol correctamente.'},
                status=status.HTTP_204_NO_CONTENT
            )
        except (Rol.DoesNotExist, RolPermiso.DoesNotExist):
            return Response(
                {'detail': 'No encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )


class UsuarioIngresoListCreateAPIView(APIView):
    """
    Se encarga de listar y crear las asignaciones de ingresos a usuarios
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, usuario_uuid):
        try:
            usuario = Usuario.objects.get(uuid=usuario_uuid)
            usuario_ingresos = UsuarioIngreso.objects.filter(usuario=usuario)
            serializer = UsuarioIngresoSerializer(usuario_ingresos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'El usuario no existe.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, usuario_uuid):
        try:
            usuario = Usuario.objects.get(uuid=usuario_uuid)
            ingreso_uuid = request.data.get('ingreso_uuid')
            
            from apps.core.models import Ingreso
            try:
                ingreso = Ingreso.objects.get(uuid=ingreso_uuid)
                usuario_ingreso, created = UsuarioIngreso.objects.get_or_create(
                    usuario=usuario,
                    ingreso=ingreso
                )
                
                if created:
                    serializer = UsuarioIngresoSerializer(usuario_ingreso)
                    return Response(
                        serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {'detail': 'El ingreso ya está asignado al usuario.'},
                        status=status.HTTP_200_OK
                    )
            except Ingreso.DoesNotExist:
                return Response(
                    {'detail': 'El ingreso no existe.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'El usuario no existe.'},
                status=status.HTTP_404_NOT_FOUND
            )


class UsuarioIngresoDestroyAPIView(APIView):
    """
    Se encarga de remover ingresos de usuarios
    """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, usuario_uuid, ingreso_uuid):
        try:
            usuario = Usuario.objects.get(uuid=usuario_uuid)
            from apps.core.models import Ingreso
            ingreso = Ingreso.objects.get(uuid=ingreso_uuid)
            
            usuario_ingreso = UsuarioIngreso.objects.get(usuario=usuario, ingreso=ingreso)
            usuario_ingreso.delete()
            
            return Response(
                {'detail': 'Ingreso removido del usuario correctamente.'},
                status=status.HTTP_204_NO_CONTENT
            )
        except (Usuario.DoesNotExist, Ingreso.DoesNotExist, UsuarioIngreso.DoesNotExist):
            return Response(
                {'detail': 'No encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )


