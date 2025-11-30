# Generated migration file for Ingreso model

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingreso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('tipo_ingreso', models.CharField(choices=[('conjunto', 'Conjunto'), ('empresa', 'Empresa')], max_length=10, verbose_name='tipo ingreso')),
                ('nombre', models.CharField(max_length=255, verbose_name='nombre')),
                ('nit', models.CharField(max_length=20, unique=True, verbose_name='NIT')),
                ('direccion', models.CharField(max_length=500, verbose_name='dirección')),
                ('nombre_admin', models.CharField(max_length=255, verbose_name='nombre administrador / representante legal')),
                ('correo', models.EmailField(max_length=254, verbose_name='correo electrónico')),
                ('telefono', models.CharField(max_length=20, verbose_name='teléfono')),
            ],
            options={
                'verbose_name': 'ingreso',
                'verbose_name_plural': 'ingresos',
                'default_permissions': (),
                'app_label': 'core',
            },
        ),
    ]
