from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from apps.seguridad.models import Usuario
from django.urls import reverse
from django.core import mail


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailUIIntegrationTests(TestCase):
    def setUp(self):
        # Admin user to perform actions in the UI
        self.admin = Usuario.objects.create_user(email='admin@example.com', password='adminpass', username='admin', is_staff=True, is_superuser=True, rol=Usuario.ROL_ADMINISTRADOR)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_create_user_triggers_email(self):
        """Simular la creación de usuario desde la UI y comprobar que se envía correo"""
        url = reverse('seguridad-usuarios-api')
        payload = {
            'username': 'nuevo',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com'
        }
        # Ensure outbox empty
        mail.outbox.clear()

        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, 201)

        # Un correo debe haberse enviado con datos de acceso
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn('Datos de acceso', sent.subject)
        self.assertIn('nuevo@example.com', sent.to)

    def test_generar_clave_triggers_email(self):
        """Simular pulsar 'Enviar contraseña' en la UI"""
        # Crear usuario objetivo
        usuario = Usuario.objects.create_user(email='target@example.com', password='pass', username='target')
        mail.outbox.clear()

        url = reverse('seguridad-usuarios-generar-clave', kwargs={'uuid': usuario.uuid})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn('Datos de acceso', sent.subject)
        self.assertIn('target@example.com', sent.to)
