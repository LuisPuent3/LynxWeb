# Dockerfile para monolito LynxWeb en Railway
# Multi-stage build para optimizar tamaño

# Stage 1: Build del frontend
FROM node:18-alpine AS frontend-builder

# Copiar todo el contexto primero para resolver dependencias de tsconfig
WORKDIR /app
COPY . ./

# Moverse al directorio del cliente y hacer el build
WORKDIR /app/cliente
RUN rm -rf node_modules package-lock.json # Limpiar para resolver problema de rollup
RUN npm install # Usar npm install en lugar de npm ci
ENV NODE_OPTIONS=--max-old-space-size=4096
RUN npm run build
ENV NODE_OPTIONS=

# Stage 2: Imagen principal - Backend + Frontend estático + Microservicio Python
FROM node:18-alpine

WORKDIR /app

# Instalar Python y pip en Alpine con herramientas de debug
RUN apk add --no-cache python3 py3-pip python3-dev gcc g++ musl-dev # Añadido g++

# Instalar dependencias del backend Node.js
COPY backed/package*.json ./
RUN npm ci --production

# Copiar código del backend
COPY backed/ ./

# Copiar el microservicio de recomendaciones y sus requisitos
COPY services/recommender/ ./recommender/

# Copiar el microservicio NLP LCLN
COPY AnalizadorNPLLynx/AnalizadorLynx-main/ ./nlp/

# Instalar dependencias de Python (intentar reducir OOM instalando pesados primero)
RUN pip3 install --no-cache-dir --break-system-packages pandas
RUN pip3 install --no-cache-dir --break-system-packages numpy
RUN pip3 install --no-cache-dir --break-system-packages scikit-learn
# Instalar el resto de las dependencias de Python
RUN pip3 install --no-cache-dir --break-system-packages -r ./recommender/requirements.txt

# Instalar dependencias del microservicio NLP
RUN pip3 install --no-cache-dir --break-system-packages -r ./nlp/requirements.txt

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

# Exponer solo el puerto principal (Railway usa PORT)
EXPOSE $PORT

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV RECOMMENDER_SERVICE_URL=http://localhost:8000
ENV NLP_SERVICE_URL=http://localhost:8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 5000) + '/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Comando de inicio
CMD ["/app/start.sh"]
