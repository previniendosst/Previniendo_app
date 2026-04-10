import os
from django.test import TestCase, override_settings
from django.core import mail
from apps.seguridad.models import Usuario
from unittest import mock


class SendGridPrimaryTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='sgtest@example.com', password='x', username='sgtest')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_sendgrid_primary_used_when_configured(self):
        os.environ['SENDGRID_PRIMARY'] = '1'
        os.environ['SENDGRID_API_KEY'] = 'fakekey'

        called = {}

        def fake_post(url, json, headers, timeout):
            called['called'] = True
            class Resp:
                status_code = 202
                text = 'ok'
            return Resp()

        with mock.patch('apps.seguridad.models.requests.post', side_effect=fake_post):
            # Should return 1 (sent) from sendgrid path and not generate SMTP email
            res = self.user.enviar_mail('Asunto SG', '<p>Hola</p>')
            # enviar_mail returns None or int depending on path; we rely on side effects to assert
            self.assertTrue(called.get('called'))

        del os.environ['SENDGRID_PRIMARY']
        del os.environ['SENDGRID_API_KEY']

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_fallback_to_smtp_on_sendgrid_failure(self):
        os.environ['SENDGRID_PRIMARY'] = '1'
        os.environ['SENDGRID_API_KEY'] = 'fakekey2'

        def fake_post_fail(url, json, headers, timeout):
            class Resp:
                status_code = 500
                text = 'error'
            return Resp()

        with mock.patch('apps.seguridad.models.requests.post', side_effect=fake_post_fail):
            # Ensure no leftover messages from setup
            mail.outbox.clear()
            # This should fallback to SMTP-backed sending which with locmem stores the message
            self.user.enviar_mail('Asunto fallback', '<p>Hola fallback</p>')
            # Wait a bit if thread backgrounded
            from time import sleep
            sleep(0.2)
            # Assert at least one SMTP message was produced as fallback (could be 1 or more due to retries)
            self.assertTrue(len(mail.outbox) >= 1)

        del os.environ['SENDGRID_PRIMARY']
        del os.environ['SENDGRID_API_KEY']
