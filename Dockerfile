# Dockerfile para monolito LynxWeb en Railway
# Multi-stage build para optimizar tamaño

# Stage 1: Build del frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app
COPY cliente/ ./cliente/
COPY tsconfig*.json vite.config.mts ./

WORKDIR /app/cliente
RUN rm -rf node_modules package-lock.json
RUN npm install
ENV NODE_OPTIONS=--max-old-space-size=4096
RUN npm run build
ENV NODE_OPTIONS=

# Stage 2: Imagen principal - Backend + Frontend estático + Microservicios Python
FROM node:18-alpine

WORKDIR /app

# Instalar Python y dependencias del sistema
RUN apk add --no-cache python3 py3-pip python3-dev gcc g++ musl-dev

# Instalar dependencias del backend Node.js
COPY backed/package*.json ./
RUN npm ci --production

# Copiar código del backend
COPY backed/ ./

# Copiar microservicios
COPY services/recommender/ ./recommender/
COPY AnalizadorNPLLynx/AnalizadorLynx-main/ ./nlp/

# Instalar dependencias Python
RUN pip3 install --no-cache-dir --break-system-packages fastapi uvicorn python-dotenv pymysql pandas numpy scikit-learn pydantic requests nltk unidecode mysql-connector-python python-multipart

# Copiar el build del frontend
COPY --from=frontend-builder /app/cliente/dist ./public

# Copiar uploads
COPY uploads/ ./uploads/

# Crear directorio para logs
RUN mkdir -p logs

# Script de inicio
COPY <<EOF /app/start.sh
#!/bin/sh
set -e

echo "🚀 Starting LynxWeb monolith..."

# Iniciar microservicio de recomendaciones
cd /app/recommender
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Iniciar microservicio NLP LCLN
cd /app/nlp/api
uvicorn main_lcln_dynamic:app --host 0.0.0.0 --port 8005 &

sleep 5

# Iniciar backend principal
cd /app
exec node index.js
EOF

RUN chmod +x /app/start.sh

EXPOSE 5000

ENV NODE_ENV=production
ENV RECOMMENDER_SERVICE_URL=http://localhost:8000
ENV NLP_SERVICE_URL=http://localhost:8005

CMD ["/app/start.sh"]
