import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.desarrollo')
django.setup()

from apps.seguridad.models import Rol, Permiso, RolPermiso

# Crear permisos por defecto
permisos_data = [
    ('read', 'Usuarios'),
    ('create', 'Usuarios'),
    ('update', 'Usuarios'),
    ('delete', 'Usuarios'),
    ('read', 'Ingresos'),
    ('create', 'Ingresos'),
    ('update', 'Ingresos'),
    ('delete', 'Ingresos'),
    ('read', 'Roles'),
    ('create', 'Roles'),
    ('update', 'Roles'),
    ('delete', 'Roles'),
    ('read', 'MiEspacio'),
]

permisos_creados = []
for accion, sujeto in permisos_data:
    permiso, created = Permiso.objects.get_or_create(
        accion=accion,
        sujeto=sujeto,
        defaults={'descripcion': f'{accion.capitalize()} {sujeto}'}
    )
    permisos_creados.append(permiso)
    if created:
        print(f"Permiso creado: {permiso}")

# Crear rol administrador
rol_admin, created = Rol.objects.get_or_create(
    codigo='admin',
    defaults={'descripcion': 'Administrador del Sistema'}
)

if created:
    print(f"Rol creado: {rol_admin}")
    # Asignar todos los permisos al rol administrador
    for permiso in permisos_creados:
        RolPermiso.objects.get_or_create(rol=rol_admin, permiso=permiso)
    print(f"Se asignaron {len(permisos_creados)} permisos al rol administrador")
else:
    print(f"Rol admin ya existe")

# Crear rol usuario
rol_usuario, created = Rol.objects.get_or_create(
    codigo='user',
    defaults={'descripcion': 'Usuario Regular'}
)

if created:
    print(f"Rol creado: {rol_usuario}")
    # Asignar solo permisos de lectura al rol usuario
    permisos_usuario = [p for p in permisos_creados if p.accion == 'read']
    for permiso in permisos_usuario:
        RolPermiso.objects.get_or_create(rol=rol_usuario, permiso=permiso)
    print(f"Se asignaron {len(permisos_usuario)} permisos al rol usuario")

print("Datos de prueba creados exitosamente")
print(f"Total permisos: {Permiso.objects.count()}")
print(f"Total roles: {Rol.objects.count()}")
