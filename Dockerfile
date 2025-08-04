# Dockerfile para monolito LynxWeb en Railway
# Single-stage build con Ubuntu para mayor estabilidad

FROM ubuntu:22.04

WORKDIR /app

# Instalar Node.js, Python y dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY . .

# Asegurar que las imágenes estén en la ubicación correcta
RUN mkdir -p /app/uploads
# Si las imágenes están en la raíz del proyecto, copiarlas explícitamente
RUN if [ -d "uploads" ]; then cp -r uploads/* /app/uploads/ 2>/dev/null || echo "No files to copy"; fi
RUN ls -la /app/uploads/ && echo "Total files: $(ls /app/uploads/ 2>/dev/null | wc -l)"

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
RUN pip3 install --no-cache-dir fastapi uvicorn python-dotenv pymysql pandas numpy scikit-learn pydantic requests nltk unidecode mysql-connector-python python-multipart graphviz

# Mover el build del frontend
RUN mkdir -p backed/public && cp -r cliente/dist/* backed/public/

# Script de inicio
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting LynxWeb monolith..."\n\
\n\
# Inicializar base de datos (opcional)\n\
echo "📋 Initializing database..."\n\
python3 /app/init-db.py || echo "⚠️  BD initialization failed, continuing..."\n\
\n\
# Iniciar microservicio de recomendaciones\n\
echo "📊 Starting recommender service..."\n\
cd /app/services/recommender\n\
uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Iniciar microservicio NLP LCLN\n\
echo "🧠 Starting NLP LCLN service..."\n\
cd /app/AnalizadorNPLLynx/AnalizadorLynx-main/api\n\
uvicorn main_lcln_simple:app --host 0.0.0.0 --port 8005 &\n\
\n\
# Dar tiempo a los microservicios\n\
sleep 3\n\
\n\
# Iniciar backend principal\n\
echo "🌐 Starting main backend..."\n\
cd /app/backed\n\
exec node index.js' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 5000

ENV NODE_ENV=production
ENV RECOMMENDER_SERVICE_URL=http://localhost:8000
ENV NLP_SERVICE_URL=http://localhost:8005

CMD ["/app/start.sh"]
