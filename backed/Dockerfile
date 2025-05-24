# Dockerfile para el backend del proyecto LYNX
FROM node:20-alpine

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para compilar bcrypt y herramientas de health check
RUN apk add --no-cache make gcc g++ python3 wget

# Copiar archivos de configuración del proyecto
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm ci --only=production

# Reconstruir bcrypt para la arquitectura actual
RUN npm rebuild bcrypt --build-from-source

# Copiar el código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/uploads /app/logs

# Puerto en el que se ejecutará la aplicación
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/api/diagnostico || exit 1

# Comando para iniciar el servidor
CMD ["node", "index.js"]