# develop stage
FROM node:18-alpine as develop-stage
WORKDIR /app
RUN apk add --no-cache python3 make g++
# Copiar todos los archivos del proyecto
COPY . .
# Instalar las dependencias del proyecto
RUN npm install
# Instalar Quasar CLI globalmente
RUN npm install -g @quasar/cli

# build stage
FROM develop-stage as build-stage
# Construir la aplicación para producción
RUN quasar build

# production stage
FROM nginx:1.21-alpine as production-stage
# Crear el directorio de la aplicación en el contenedor
RUN mkdir /app
# Copiar los archivos construidos desde la etapa de construcción
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html
# Exponer el puerto 80 para el servidor web
EXPOSE 80
# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]