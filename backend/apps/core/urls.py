from django.urls import path

from .views import (
    IngresoListCreateAPIView,
    IngresoRetrieveUpdateDestroyAPIView,
    TiposIngresoListAPIView,
)

urlpatterns = [
    path('ingresos/', IngresoListCreateAPIView.as_view(), name='core-ingresos-api'),
    path('ingresos/<uuid:uuid>/', IngresoRetrieveUpdateDestroyAPIView.as_view(), name='core-ingresos-detail-api'),
    path('ingresos/tipos/', TiposIngresoListAPIView.as_view(), name='core-ingresos-tipos-api'),
]