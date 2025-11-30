"""previniendo backend URL Configuration
"""
from django.conf.urls import include
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/v1/seguridad/', include('apps.seguridad.urls')),
    path('api/v1/core/', include('apps.core.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
