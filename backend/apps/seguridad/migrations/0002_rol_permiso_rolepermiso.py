# Generated migration for Rol, Permiso, RolPermiso models and M2M for Usuario-Ingreso

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('seguridad', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('codigo', models.CharField(max_length=50, unique=True, verbose_name='código')),
                ('descripcion', models.CharField(max_length=255, verbose_name='descripción')),
            ],
            options={
                'verbose_name': 'rol',
                'verbose_name_plural': 'roles',
                'default_permissions': (),
                'app_label': 'seguridad',
            },
        ),
        migrations.CreateModel(
            name='Permiso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('accion', models.CharField(choices=[('create', 'Crear'), ('read', 'Leer'), ('update', 'Actualizar'), ('delete', 'Eliminar'), ('detail', 'Detalle'), ('finish', 'Finalizar')], max_length=50, verbose_name='acción')),
                ('sujeto', models.CharField(choices=[('Usuarios', 'Usuarios'), ('Ingresos', 'Ingresos'), ('Roles', 'Roles'), ('MiEspacio', 'Mi Espacio'), ('all', 'Todos')], max_length=50, verbose_name='sujeto')),
                ('descripcion', models.CharField(blank=True, max_length=255, verbose_name='descripción')),
            ],
            options={
                'verbose_name': 'permiso',
                'verbose_name_plural': 'permisos',
                'default_permissions': (),
                'app_label': 'seguridad',
                'unique_together': {('accion', 'sujeto')},
            },
        ),
        migrations.CreateModel(
            name='RolPermiso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('permiso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seguridad.permiso', verbose_name='permiso')),
                ('rol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permisos', to='seguridad.rol', verbose_name='rol')),
            ],
            options={
                'verbose_name': 'rol permiso',
                'verbose_name_plural': 'rol permisos',
                'default_permissions': (),
                'app_label': 'seguridad',
                'unique_together': {('rol', 'permiso')},
            },
        ),
        migrations.AddField(
            model_name='usuario',
            name='rol_sistema',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios', to='seguridad.rol', verbose_name='rol del sistema'),
        ),
        migrations.CreateModel(
            name='UsuarioIngreso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('ingreso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ingreso', verbose_name='ingreso')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_ingresos', to='seguridad.usuario', verbose_name='usuario')),
            ],
            options={
                'verbose_name': 'usuario ingreso',
                'verbose_name_plural': 'usuario ingresos',
                'default_permissions': (),
                'app_label': 'seguridad',
                'unique_together': {('usuario', 'ingreso')},
            },
        ),
        migrations.AddField(
            model_name='usuario',
            name='ingresos',
            field=models.ManyToManyField(related_name='usuarios', through='seguridad.UsuarioIngreso', to='core.ingreso', verbose_name='ingresos'),
        ),
    ]
