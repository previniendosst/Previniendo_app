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
