from rest_framework.views import Response
from rest_framework.pagination import PageNumberPagination


class Paginacion(PageNumberPagination):
    """"""

    page_query_param = 'pagina'
    page_size_query_param = 'tamano_pagina'

    def get_paginated_response(self, data):
        return Response({
            'cantidad': self.page.paginator.count,
            'resultado': data
        })
