from rest_framework.permissions import BasePermission
from .models import Usuario


class EsUsuarioAdministrador(BasePermission):
    """
    Valida si el usuario autenticado tiene rol admin.
    """

    def has_permission(self, request, view):
        return hasattr(request.user, 'rol') and request.user.rol == Usuario.ROL_ADMINISTRADOR
