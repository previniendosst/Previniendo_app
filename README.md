# App para Previniendo

## Ambiente de desarrollo
* Backend: Django + Postgresql
* Frontend: Vue 3 + Quasar v2

## Para inciar el ambiente de desarrollo
En la terminal escribir el siguiente comando:

```bash
docker-compose -f docker-compose-desarrollo.yml up
```

Si desea recompilar la imagen del docker corra

```bash
docker-compose -f docker-compose-desarrollo.yml up --build
```

Ahora la aplicación deberá estar funcionando al visitar las urls: 
* Backend: http://127.0.0.1:8000/api/
* Frontend: http://127.0.0.1:9000/

Los datos de conexión a la base de datos son los siguientes:
* Usuario: previniendo
* Base de datos: previniendo
* Password: previniendo
* host: 127.0.0.1
* puerto: 5435

## Para ejecutar comandos django en el ambiente de desarrollo
Se debe ejecutar el comando de la siguiente forma:
```bash
docker exec -it dev-previniendo-backend  python manage.py <comando>
```
Ejemplos
```bash
docker exec -it dev-previniendo-backend  python manage.py makemigrations
docker exec -it dev-previniendo-backend  python manage.py migrate
docker exec -it dev-previniendo-backend  python manage.py createsuperuser
```

## Envío de correos cuando el servidor bloquea salidas (puerto 2525) ⚠️

- *Capturar correos mientras el servidor está bloqueado* (sin tocar el código): en el entorno (o `docker-compose`) configure el backend por archivos:

```bash
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/email_outbox
```

- *Alternativa (no cambia backend):* active el guardado automático de correos fallidos en disco mientras esté bloqueado:

```bash
EMAIL_WRITE_ON_FAIL=1
EMAIL_FAIL_DIR=/tmp/email_outbox
```

- *Cuando desbloqueen el puerto 2525:* ajuste la configuración SMTP y vuelva al backend SMTP:

```bash
EMAIL_PORT=2525
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_WRITE_ON_FAIL=0
```

- *Reenviar los correos acumulados:* una vez el SMTP esté disponible, ejecute:

```bash
docker exec -it dev-previniendo-backend python manage.py replay_email_outbox
```

- Nota: el proyecto ya tiene reintentos IPv4, SSL y fallback vía SendGrid (`SENDGRID_API_KEY`) en `apps/seguridad/models.py`.

## SendGrid — usar API como método primario (recomendado)

Para evitar bloqueos salientes en el host (puertos SMTP), puede activar SendGrid como método primario (la aplicación intentará la API primero y si falla caerá a SMTP / guardar en disco).

**Inyección segura de la clave (recomendado)**

- No ponga la clave en git. Use un gestor de secretos de su proveedor o un archivo de entorno local no versionado (ej. `.env.production`). Hemos añadido un **`.env.sample`** en la raíz del repo para facilitar el proceso.

Ejemplo (.env.production, **NO** subir al repo):

```bash
SENDGRID_PRIMARY=1
SENDGRID_API_KEY=SG.xxxxxxx
```

**Verificación E2E (lista de pasos)**

1. Copie `.env.sample` → `.env.production` y reemplace los valores reales (o inyecte la variable en su gestor de secrets).
2. Reinicie el backend con la variable disponible en el entorno del contenedor:

```bash
# Si usa export en su host antes de docker-compose
export SENDGRID_API_KEY="<su_clave>"
docker compose -f docker-compose-produccion.yml up --build -d previniendo-backend
```

3. Compruebe la conectividad/API desde el contenedor:

```bash
docker exec -it previniendo-backend python3 manage.py check_smtp
# Ver verá 'SendGrid test OK' cuando la API esté correcta
```

4. Cree un usuario desde la UI de producción (o desde el admin) y pulse "Enviar contraseña"; verifique llegada en la cuenta destino y en el dashboard de SendGrid.
5. Si todo OK, compruebe que `/tmp/email_outbox` está vacío (o ejecute `docker exec -it previniendo-backend python3 manage.py replay_email_outbox` para forzar reenvíos pendientes).

**Servicio opcional: `email-replayer` (reintentos automáticos)**

- Se añadió un servicio opcional `email-replayer` en `docker-compose-produccion.yml` que, cuando se activa con `ENABLE_EMAIL_REPLAYER=1`, ejecuta periódicamente `python3 manage.py replay_email_outbox`:

Variables útiles:

- `ENABLE_EMAIL_REPLAYER=0` (deshabilitado por defecto)
- `EMAIL_REPLAYER_INTERVAL=300` (segundos; 5 minutos por defecto)

Ejemplo para habilitarlo en producción (exporte antes de `docker compose up` o use su gestor de secrets):

```bash
export ENABLE_EMAIL_REPLAYER=1
export EMAIL_REPLAYER_INTERVAL=300
export SENDGRID_API_KEY="<su_clave>"
docker compose -f docker-compose-produccion.yml up --build -d
```

**Checks después de la verificación**

- `docker exec -it previniendo-backend python3 manage.py check_smtp` → revisa SMTP y SendGrid API.
- `docker exec -it previniendo-backend python3 manage.py replay_email_outbox` → reenvía pendientes (intenta SendGrid primero si está activo).


## Producción — usar puerto 2525 para SMTP 📤

Si en producción su proveedor o firewall bloquea los puertos SMTP estándar (25, 465, 587), puede usar el puerto **2525** sin cambiar código:

1) Establezca la variable de entorno en su servidor/compose:

```bash
EMAIL_PORT=2525
```

En `docker-compose-produccion.yml` se añadió por defecto `EMAIL_PORT=2525` como ejemplo; asegúrese de que `EMAIL_HOST`, `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` estén definidos en su entorno (secrets) y visibles para el contenedor.

2) Verifique conectividad SMTP desde el contenedor:

```bash
docker exec -it previniendo-backend python manage.py check_smtp
```

3) Reenvío de mensajes acumulados (si usó `EMAIL_WRITE_ON_FAIL=1` o backend file durante el bloqueo):

```bash
docker exec -it previniendo-backend python manage.py replay_email_outbox
```

Notas:
- En `config/settings/produccion.py` se puso **por defecto** `EMAIL_PORT=2525` para evitar cambios de código al desplegar cuando 25/465/587 estén bloqueados.
- En desarrollo se mantiene `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, por lo que los correos se siguen mostrando (HTML incluido) en la salida del contenedor del backend.

## Pruebas automáticas para envíos de correo 🧪

Se añadieron pruebas que verifican los dos flujos que la UI dispara:
- Creación de usuario (POST `/api/seguridad/usuarios/`) → correo con datos de acceso.
- Enviar contraseña (GET `/api/seguridad/usuarios/generar_clave/<uuid>/`) → correo con nueva clave.

Para ejecutar las pruebas desde el contenedor de desarrollo (recomendado):

```bash
docker exec -it dev-previniendo-backend python manage.py test apps.seguridad.tests.test_email_ui -q
```

Salida esperada (ejemplo):

```
..
----------------------------------------------------------------------
Ran 2 tests in X.XXXs

OK
```

Si no puedes ejecutar tests dentro del contenedor, puedes ejecutar el mismo comando en tu entorno virtual local (asegúrate de tener dependencias y Django instalados).

---
