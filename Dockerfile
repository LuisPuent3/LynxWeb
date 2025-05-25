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

# Instalar dependencias de Python (intentar reducir OOM instalando pesados primero)
RUN pip3 install --no-cache-dir --break-system-packages pandas
RUN pip3 install --no-cache-dir --break-system-packages numpy
RUN pip3 install --no-cache-dir --break-system-packages scikit-learn
# Instalar el resto de las dependencias de Python
RUN pip3 install --no-cache-dir --break-system-packages -r ./recommender/requirements.txt

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

# Iniciar el servicio Python en segundo plano
echo "🐍 Starting Python recommender service on port 8000..."
cd /app/recommender

# Verificar que main.py existe
if [ -f "main.py" ]; then
    echo "✓ Found main.py"
else
    echo "❌ main.py not found!"
    ls -la
fi

# Iniciar Python con logs dirigidos a stdout
uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/python.log 2>&1 &
PYTHON_PID=$!
echo "Python service started with PID: $PYTHON_PID"

# Esperar un momento para que Python se inicie
sleep 5

# Verificar si Python sigue corriendo
if kill -0 $PYTHON_PID 2>/dev/null; then
    echo "✅ Python service is running on PID $PYTHON_PID"
    # Verificar el puerto
    if netstat -tuln | grep :8000; then
        echo "✅ Python service listening on port 8000"
    else
        echo "⚠️ Python service running but port 8000 not detected"
        echo "Python logs:"
        tail -n 20 /tmp/python.log || echo "No logs found"
    fi
else
    echo "❌ Python service failed to start"
    echo "Python logs:"
    cat /tmp/python.log || echo "No logs found"
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

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 5000) + '/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Comando de inicio
CMD ["/app/start.sh"]
