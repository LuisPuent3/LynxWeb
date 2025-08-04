# Dockerfile para monolito LynxWeb en Railway
# Multi-stage build para optimizar tamaño

# Stage 1: Build del frontend
FROM node:20-alpine AS frontend-builder

# Configurar timeouts y reintentos para mayor estabilidad
RUN apk add --no-cache curl

# Copiar solo archivos necesarios para el frontend primero
WORKDIR /app
COPY cliente/package*.json ./cliente/
COPY tsconfig*.json vite.config.mts ./
COPY cliente/src ./cliente/src/
COPY cliente/public ./cliente/public/
COPY cliente/index.html ./cliente/
COPY cliente/vite.config.ts ./cliente/

# Moverse al directorio del cliente y hacer el build
WORKDIR /app/cliente
RUN rm -rf node_modules package-lock.json
RUN npm install --no-audit --no-fund --timeout=300000
ENV NODE_OPTIONS=--max-old-space-size=2048
RUN npm run build
ENV NODE_OPTIONS=

# Stage 2: Imagen principal - Backend + Frontend estático + Microservicio Python
FROM node:20-alpine

WORKDIR /app

# Instalar dependencias del sistema con timeouts más largos
RUN apk add --no-cache python3 py3-pip python3-dev gcc g++ musl-dev curl

# Instalar dependencias del backend Node.js
COPY backed/package*.json ./
RUN npm ci --production

# Copiar código del backend
COPY backed/ ./

# Copiar el microservicio de recomendaciones y sus requisitos
COPY services/recommender/ ./recommender/

# Copiar el microservicio NLP LCLN
COPY AnalizadorNPLLynx/AnalizadorLynx-main/ ./nlp/

# Instalar dependencias de Python de forma más eficiente
# Primero instalar las dependencias básicas de ciencia de datos
RUN pip3 install --no-cache-dir --break-system-packages wheel setuptools
RUN pip3 install --no-cache-dir --break-system-packages numpy==1.24.3
RUN pip3 install --no-cache-dir --break-system-packages pandas==2.0.3
RUN pip3 install --no-cache-dir --break-system-packages scikit-learn==1.3.0

# Verificar que los archivos requirements.txt existen antes de instalar
RUN if [ -f "./recommender/requirements.txt" ]; then \
        echo "Installing recommender requirements..."; \
        pip3 install --no-cache-dir --break-system-packages -r ./recommender/requirements.txt; \
    else \
        echo "⚠️ Warning: ./recommender/requirements.txt not found"; \
    fi

RUN if [ -f "./nlp/requirements.txt" ]; then \
        echo "Installing NLP requirements..."; \
        pip3 install --no-cache-dir --break-system-packages -r ./nlp/requirements.txt; \
    else \
        echo "⚠️ Warning: ./nlp/requirements.txt not found"; \
    fi

# Copiar el build del frontend al directorio público del backend
COPY --from=frontend-builder /app/cliente/dist ./public

# Copiar uploads (imágenes de productos)
COPY uploads/ ./uploads/

# Crear directorio para logs
RUN mkdir -p logs

# Crear script de inicio que ejecute ambos servicios
COPY <<EOF /app/start.sh
#!/bin/sh
set -e

echo "🚀 Starting LynxWeb monolith..."

# Iniciar el servicio Python de recomendaciones en segundo plano
echo "🐍 Starting Python recommender service on port 8000..."
cd /app/recommender

# Verificar que main.py existe
if [ -f "main.py" ]; then
    echo "✓ Found recommender main.py"
else
    echo "❌ Recommender main.py not found!"
    ls -la
fi

# Iniciar Python con logs dirigidos a stdout
uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/recommender.log 2>&1 &
RECOMMENDER_PID=$!
echo "Recommender service started with PID: $RECOMMENDER_PID"

# Iniciar el servicio NLP en segundo plano
echo "🧠 Starting NLP LCLN service on port 8005..."
cd /app/nlp/api

# Verificar que main_lcln_dynamic.py existe
if [ -f "main_lcln_dynamic.py" ]; then
    echo "✓ Found NLP main_lcln_dynamic.py"
else
    echo "❌ NLP main_lcln_dynamic.py not found!"
    ls -la
fi

# Iniciar NLP con uvicorn dirigido a stdout  
uvicorn main_lcln_dynamic:app --host 0.0.0.0 --port 8005 > /tmp/nlp.log 2>&1 &
NLP_PID=$!
echo "NLP service started with PID: $NLP_PID"

# Esperar un momento para que ambos servicios se inicien
sleep 8

# Verificar si ambos servicios siguen corriendo
echo "🔍 Checking services status..."

if kill -0 $RECOMMENDER_PID 2>/dev/null; then
    echo "✅ Recommender service is running on PID $RECOMMENDER_PID"
else
    echo "❌ Recommender service failed to start"
    echo "Recommender logs:"
    cat /tmp/recommender.log || echo "No logs found"
fi

if kill -0 $NLP_PID 2>/dev/null; then
    echo "✅ NLP service is running on PID $NLP_PID"
else
    echo "❌ NLP service failed to start"  
    echo "NLP logs:"
    cat /tmp/nlp.log || echo "No logs found"
fi

# Iniciar Node.js
echo "🟢 Starting Node.js backend on port \$PORT..."
cd /app
exec node index.js
EOF

RUN sed -i 's/\r$//' /app/start.sh # Asegurar finales de línea LF
RUN chmod +x /app/start.sh

# Exponer puerto por defecto (Railway asignará automáticamente)
EXPOSE 5000

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV RECOMMENDER_SERVICE_URL=http://localhost:8000
ENV NLP_SERVICE_URL=http://localhost:8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 5000) + '/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Comando de inicio
CMD ["/app/start.sh"]
