import os
import json
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.conf import settings
from unittest import mock

class ReplaySendGridTests(TestCase):
    def setUp(self):
        self.path = '/tmp/email_outbox_test'
        os.makedirs(self.path, exist_ok=True)
        self.filepath = os.path.join(self.path, 'm1.json')
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump({'to': ['x@example.com'], 'subject': 'Hola', 'html': '<p>Hi</p>', 'text': 'Hi'}, f)

    def tearDown(self):
        try:
            for f in os.listdir(self.path):
                os.remove(os.path.join(self.path, f))
            os.rmdir(self.path)
        except Exception:
            pass

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_replay_uses_sendgrid_primary(self):
        os.environ['SENDGRID_PRIMARY'] = '1'
        os.environ['SENDGRID_API_KEY'] = 'fake'
        try:
            called = {}
            class Resp:
                status_code = 202
                text = 'ok'
            def fake_post(url, json, headers, timeout):
                called['ok'] = True
                return Resp()

            with mock.patch('apps.seguridad.management.commands.replay_email_outbox.requests.post', side_effect=fake_post):
                call_command('replay_email_outbox')
                # Verify file removed
                self.assertFalse(os.path.exists(self.filepath))
                self.assertTrue(called.get('ok'))
        finally:
            del os.environ['SENDGRID_PRIMARY']
            del os.environ['SENDGRID_API_KEY']
