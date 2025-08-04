# Dockerfile para monolito LynxWeb en Railway
# Usando Node.js con Debian Bullseye para estabilidad

FROM node:18-bullseye

WORKDIR /app

# Instalar Python y dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY . .

# Asegurar que las imágenes estén en la ubicación correcta
RUN mkdir -p /app/uploads
# Copiar todas las imágenes del directorio uploads
COPY . /tmp/build/
RUN if [ -d "/tmp/build/uploads" ]; then \
        cp -r /tmp/build/uploads/* /app/uploads/ || echo "No files to copy"; \
        echo "Verificando copia de imágenes:" && ls -la /app/uploads/ && echo "Total files: $(ls /app/uploads/ 2>/dev/null | wc -l)"; \
    else \
        echo "No uploads directory found in build context"; \
    fi

# Build del frontend con fix para Rollup
WORKDIR /app/cliente
RUN rm -rf node_modules package-lock.json
RUN npm install
# Instalar explícitamente la dependencia nativa de Rollup para x64
RUN npm install @rollup/rollup-linux-x64-gnu
ENV NODE_OPTIONS=--max-old-space-size=4096
RUN npm run build
ENV NODE_OPTIONS=

# Instalar dependencias del backend
WORKDIR /app
RUN npm ci --production --prefix backed

# Instalar dependencias Python
RUN pip3 install --no-cache-dir fastapi uvicorn python-dotenv pymysql pandas numpy scikit-learn pydantic requests nltk unidecode mysql-connector-python python-multipart graphviz structlog python-Levenshtein

# Mover el build del frontend
RUN mkdir -p backed/public && cp -r cliente/dist/* backed/public/

# Script de inicio
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting LynxWeb monolith..."\n\
\n\
# Verificar estructura\n\
echo "📁 Checking structure..."\n\
echo "Uploads source dir files:"\n\
ls -la uploads/ || echo "No uploads/ source dir"\n\
echo "Uploads dest dir files:"\n\
ls -la /app/uploads/ || echo "No /app/uploads/ dest dir"\n\
echo "Uploads dir count: $(ls -la /app/uploads/ | wc -l) files"\n\
\n\
# Inicializar base de datos\n\
echo "📋 Initializing database..."\n\
python3 /app/init-db.py || echo "⚠️  BD initialization failed, continuing..."\n\
\n\
# Extraer esquema completo de la base de datos\n\
echo "💾 Extracting complete database schema..."\n\
python3 /app/extract_railway_db.py || echo "⚠️  Schema extraction failed, continuing..."\n\
\n\
# Iniciar microservicio de recomendaciones\n\
echo "📊 Starting recommender service..."\n\
cd /app/services/recommender\n\
uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Iniciar microservicio NLP LCLN con servicio original\n\
echo "🧠 Starting original LCLN service..."\n\
cd /app/AnalizadorNPLLynx/AnalizadorLynx-main\n\
echo "Current dir: $(pwd)"\n\
echo "LCLN files: $(ls -la servidor_lcln_api.py sistema_lcln_simple.py || echo NO_FILES)"\n\
python3 -c "import fastapi; print(f\"FastAPI available: {fastapi.__version__}\")" || echo "FastAPI not available"\n\
python3 -c "import uvicorn; print(f\"Uvicorn available: {uvicorn.__version__}\")" || echo "Uvicorn not available"\n\
echo "Starting original LCLN service with uvicorn..."\n\
export MYSQL_HOST="${MYSQLHOST:-${MYSQL_HOST:-mysql.railway.internal}}"\n\
export MYSQL_DATABASE="${MYSQLDATABASE:-${MYSQL_DATABASE:-railway}}"\n\
export MYSQL_USER="${MYSQLUSER:-${MYSQL_USER:-root}}"\n\
export MYSQL_PASSWORD="${MYSQLPASSWORD:-${MYSQL_PASSWORD}}"\n\
export MYSQL_PORT="${MYSQLPORT:-${MYSQL_PORT:-3306}}"\n\
echo "Lanzando LCLN con uvicorn en puerto 8005..."\n\
uvicorn servidor_lcln_api:app --host 0.0.0.0 --port 8005 > /tmp/lcln.log 2>&1 &\n\
echo "LCLN PID: $!"\n\
\n\
# Dar tiempo a los microservicios\n\
sleep 5\n\
\n\
# Verificar que los servicios estén corriendo\n\
echo "🔧 Checking service status..."\n\
echo "Recommender status: $(curl -s http://localhost:8000/health || echo FAILED)"\n\
echo "LCLN status: $(curl -s http://localhost:8005/api/health || echo FAILED)"\n\
echo "LCLN logs: $(cat /tmp/lcln.log || echo NO_LOGS)"\n\
\n\
# Iniciar backend principal\n\
echo "🌐 Starting main backend..."\n\
cd /app/backed\n\
exec node index.js' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 5000

ENV NODE_ENV=production
ENV RECOMMENDER_SERVICE_URL=http://127.0.0.1:8000
ENV NLP_SERVICE_URL=http://127.0.0.1:8005

CMD ["/app/start.sh"]
