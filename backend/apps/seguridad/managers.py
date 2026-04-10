from django.contrib.auth.models import BaseUserManager
from django.apps import apps


class UsuarioManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password.
        Supports a non-persistent flag `_skip_email` in `extra_fields` to avoid
        triggering email sending on creation (useful during bootstrap / superuser creation).
        """
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        # extract skip flag so it doesn't become a model field
        skip_email = extra_fields.pop('_skip_email', False)
        user = self.model(email=email, **extra_fields)
        # set attribute checked by Usuario.save
        user._skip_email_on_create = bool(skip_email)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password.
        By default, do not send initial credentials email to avoid failing startup
        if SMTP is misconfigured; use `_skip_email=False` to override.
        """
        usuario = apps.get_model('seguridad', 'Usuario')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', usuario.ROL_ADMINISTRADOR)
        # By default, skip sending email during superuser creation
        extra_fields.setdefault('_skip_email', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
