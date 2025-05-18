FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Crear directorio para datos y modelo
RUN mkdir -p /app/data

# Exponer el puerto para FastAPI
EXPOSE 8000

# Ejecución por defecto: iniciar el servicio FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 