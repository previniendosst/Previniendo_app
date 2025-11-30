from .serializers import UsuarioListRetrieveSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'usuario': UsuarioListRetrieveSerializer(user, context={'request': request}).data
    }
