# Multi-stage build para Frontend React
FROM node:18-alpine as build

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias (incluyendo devDependencies para el build)
RUN npm ci

# Copiar código fuente
COPY . .

# Construir aplicación para producción (ignorando errores de TypeScript)
RUN npm run build:ignore-errors

# Stage 2: Nginx para servir la aplicación
FROM nginx:alpine

# Instalar wget para health checks
RUN apk add --no-cache wget

# Copiar build de React a nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
