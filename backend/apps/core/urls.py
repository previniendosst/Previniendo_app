from django.urls import path

from .views import (
    IngresoListCreateAPIView,
    IngresoRetrieveUpdateDestroyAPIView,
    TiposIngresoListAPIView,
    DocumentFolderListCreateAPIView,
    DocumentUploadAPIView,
    DocumentListByFolderAPIView,
    AssignUserDocumentAccessAPIView,
    UserDocumentAccessListAPIView,
    DocumentDownloadAPIView,
)

urlpatterns = [
    path('ingresos/', IngresoListCreateAPIView.as_view(), name='core-ingresos-api'),
    path('ingresos/<uuid:uuid>/', IngresoRetrieveUpdateDestroyAPIView.as_view(), name='core-ingresos-detail-api'),
    path('ingresos/tipos/', TiposIngresoListAPIView.as_view(), name='core-ingresos-tipos-api'),
    path('documents/folders/', DocumentFolderListCreateAPIView.as_view(), name='core-documents-folders-api'),
    path('documents/upload/', DocumentUploadAPIView.as_view(), name='core-documents-upload-api'),
    path('documents/', DocumentListByFolderAPIView.as_view(), name='core-documents-list-api'),
    path('documents/user-access/', AssignUserDocumentAccessAPIView.as_view(), name='core-documents-assign-user-access-api'),
    path('documents/user-folders/', UserDocumentAccessListAPIView.as_view(), name='core-documents-user-folders-api'),
    path('documents/<uuid:document_uuid>/download/', DocumentDownloadAPIView.as_view(), name='core-documents-download-api'),
]