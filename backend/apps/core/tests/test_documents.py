from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from apps.core.serializers import DocumentUploadSerializer
from apps.core.models import DocumentFolder, Document
from django.contrib.auth import get_user_model

class DocumentUploadTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', email='t@example.com', password='secret')
        self.folder = DocumentFolder.objects.create(ingreso=None, nombre='test', creado_por=self.user)

    def test_serializer_rejects_files_larger_than_limit(self):
        max_size = getattr(settings, 'DOCUMENT_MAX_UPLOAD_SIZE', 26214400)
        large = SimpleUploadedFile('big.bin', b'a' * (max_size + 1), content_type='application/octet-stream')
        data = {'carpeta': str(self.folder.uuid), 'archivo': large}
        serializer = DocumentUploadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('archivo', serializer.errors)

    def test_download_endpoint_inline(self):
        # Crear documento pequeño
        f = SimpleUploadedFile('small.txt', b'hello world', content_type='text/plain')
        doc = Document.objects.create(carpeta=self.folder, archivo=f, nombre_original='small.txt', creado_por=self.user)
        self.client.login(username='test', password='secret')
        url = reverse('core-documents-download-api', kwargs={'document_uuid': doc.uuid}) + '?inline=1'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        cd = resp.get('Content-Disposition', '')
        self.assertTrue(cd.startswith('inline'))
