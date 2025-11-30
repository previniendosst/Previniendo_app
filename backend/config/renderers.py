from rest_framework.renderers import BaseRenderer
from uuid import UUID
import json


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return f'{obj}'
        return json.JSONEncoder.default(self, obj)


class ErrorApiRenderer(BaseRenderer):
    media_type = 'aplication/json'
    format = 'json'

    def render(self, data, accepted_media_type=None, renderer_context=None):

        response_dict = {
            'detalle': data
        }

        if data.get('non_field_errors'):
            response_dict = {
                'detalle': data.get('non_field_errors')[0]
            }

        if data.get('detail'):
            response_dict = {
                'detalle': data.get('detail')
            }

        return json.dumps(response_dict, cls=CustomEncoder)
