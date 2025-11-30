from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.views import Response


class ProtectedForeignKeyDeleteMixin:
    """
    Si una llave foranea tiene configurada la opción 'protected' en el modo de borrado,
    DRF no puede procesar la petición.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
            return_status = status.HTTP_204_NO_CONTENT
            msg = None
        except ProtectedError:
            return_status = status.HTTP_403_FORBIDDEN
            msg = dict()
            msg['detalle'] = "No se puede eliminar un elemento que se encuentra relacionado con otros."
        return Response(status=return_status, data=msg)
