# Dockerfile para monolito LynxWeb en Railway
# Multi-stage build para optimizar tamaño

# Stage 1: Build del frontend
FROM node:18-alpine AS frontend-builder

# Copiar todo el contexto primero para resolver dependencias de tsconfig
WORKDIR /app
COPY . ./

# Moverse al directorio del cliente y hacer el build
WORKDIR /app/cliente
RUN rm -rf package-lock.json node_modules 2>/dev/null || true
RUN npm install
RUN npm run build

# Stage 2: Imagen principal - Backend + Frontend estático + Microservicio Python
FROM node:18-alpine

WORKDIR /app

# Instalar Python y pip en Alpine
RUN apk add --no-cache python3 py3-pip python3-dev gcc musl-dev

# Instalar dependencias del backend Node.js
COPY backed/package*.json ./
RUN npm ci --production

# Copiar código del backend
COPY backed/ ./

# Copiar el microservicio de recomendaciones
COPY services/recommender/ ./recommender/

# Instalar dependencias de Python
RUN pip3 install --no-cache-dir -r ./recommender/requirements.txt

# Copiar el build del frontend al directorio público del backend
COPY --from=frontend-builder /app/cliente/dist ./public

# Copiar uploads (imágenes de productos)
COPY uploads/ ./uploads/

# Crear directorio para logs
RUN mkdir -p logs

# Crear script de inicio que ejecute ambos servicios
RUN echo '#!/bin/sh' > start.sh && \
    echo 'echo "🚀 Iniciando microservicio de recomendaciones..."' >> start.sh && \
    echo 'cd /app/recommender && python3 main.py &' >> start.sh && \
    echo 'echo "🚀 Iniciando backend Node.js..."' >> start.sh && \
    echo 'cd /app && node index.js' >> start.sh && \
    chmod +x start.sh

# Exponer puertos (5000 para Node.js, 8000 para Python)
EXPOSE 5000 8000

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV PORT=5000
ENV RECOMMENDER_SERVICE_URL=http://localhost:8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Comando de inicio
CMD ["./start.sh"]
