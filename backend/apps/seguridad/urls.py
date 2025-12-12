from rest_framework_jwt.views import obtain_jwt_token

from django.urls import path

from .views import (
    LoginAPIView,
    UsuarioListCreateAPIView,
    UsuarioRetrieveUpdateDestroyAPIView,
    RolesUsuarioListAPIView,
    PerfilView,
    UsuarioGenerarClaveAPIView,
    VerificarCorreoAPIView,
    RolListCreateAPIView,
    RolRetrieveUpdateDestroyAPIView,
    PermisoListAPIView,
    RolPermisoCreateDestroyAPIView,
    UsuarioIngresoListCreateAPIView,
    UsuarioIngresoDestroyAPIView,
)

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='seguridad-login-api'),
    path('usuarios/', UsuarioListCreateAPIView.as_view(), name='seguridad-usuarios-api'),
    path('usuarios/<uuid:uuid>/', UsuarioRetrieveUpdateDestroyAPIView.as_view(), name='seguridad-usuarios-api'),
    path('usuarios/roles/', RolesUsuarioListAPIView.as_view(), name='seguridad-usuarios-roles-api'),
    path('usuarios/generar_clave/<uuid:uuid>/', UsuarioGenerarClaveAPIView.as_view(),
         name='seguridad-usuarios-generar-clave'),
    path('usuarios/<uuid:usuario_uuid>/ingresos/', UsuarioIngresoListCreateAPIView.as_view(), 
         name='seguridad-usuario-ingresos-api'),
    path('usuarios/<uuid:usuario_uuid>/ingresos/<uuid:ingreso_uuid>/', UsuarioIngresoDestroyAPIView.as_view(),
         name='seguridad-usuario-ingreso-destroy-api'),
    path('perfil/', PerfilView.as_view(), name='seguridad-perfil'),
    path('verificar_correo/', VerificarCorreoAPIView.as_view(), name='verificar-correo'),
    path('roles/', RolListCreateAPIView.as_view(), name='seguridad-roles-api'),
    path('roles/<uuid:uuid>/', RolRetrieveUpdateDestroyAPIView.as_view(), name='seguridad-roles-detail-api'),
    path('roles/<uuid:uuid>/permisos/', RolPermisoCreateDestroyAPIView.as_view(), name='seguridad-rol-permisos-api'),
    path('roles/<uuid:uuid>/permisos/<uuid:permiso_uuid>/', RolPermisoCreateDestroyAPIView.as_view(),
         name='seguridad-rol-permiso-destroy-api'),
    path('permisos/', PermisoListAPIView.as_view(), name='seguridad-permisos-api'),
]
