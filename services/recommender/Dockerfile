FROM python:3.11-slim

WORKDIR /app

# Instalar wget para health checks
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Crear directorio para datos y modelo
RUN mkdir -p /app/data

# Exponer el puerto para FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Ejecución por defecto: iniciar el servicio FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]