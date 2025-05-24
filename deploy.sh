#!/bin/bash
# Script para construir y desplegar LynxWeb con Docker

set -e

echo "🚀 Iniciando despliegue de LynxWeb..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logs
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar que Docker esté instalado y corriendo
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Por favor instale Docker primero."
    exit 1
fi

if ! docker info &> /dev/null; then
    error "Docker no está corriendo. Por favor inicie Docker primero."
    exit 1
fi

# Verificar que docker-compose esté disponible
if ! command -v docker-compose &> /dev/null; then
    if ! docker compose version &> /dev/null; then
        error "Docker Compose no está disponible. Por favor instale Docker Compose."
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Crear directorios necesarios
log "Creando directorios necesarios..."
mkdir -p nginx/ssl
mkdir -p logs/nginx

# Copiar archivo de entorno si no existe
if [ ! -f .env ]; then
    if [ -f .env.production ]; then
        log "Copiando .env.production a .env..."
        cp .env.production .env
    else
        warning "No se encontró archivo .env ni .env.production. Usando valores por defecto."
    fi
fi

# Construir imágenes
log "Construyendo imágenes Docker..."
$DOCKER_COMPOSE build --no-cache

if [ $? -ne 0 ]; then
    error "Error al construir las imágenes Docker"
    exit 1
fi

success "Imágenes construidas exitosamente"

# Detener contenedores existentes
log "Deteniendo contenedores existentes..."
$DOCKER_COMPOSE down

# Iniciar servicios
log "Iniciando servicios..."
$DOCKER_COMPOSE up -d

if [ $? -ne 0 ]; then
    error "Error al iniciar los servicios"
    exit 1
fi

# Verificar que los servicios estén corriendo
log "Verificando servicios..."
sleep 10

# Función para verificar health de un servicio
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    log "Verificando salud del servicio: $service"
    
    while [ $attempt -le $max_attempts ]; do
        if $DOCKER_COMPOSE ps $service | grep -q "healthy\|Up"; then
            success "Servicio $service está funcionando correctamente"
            return 0
        fi
        
        log "Intento $attempt/$max_attempts - Esperando que $service esté listo..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "El servicio $service no está respondiendo después de $max_attempts intentos"
    return 1
}

# Verificar cada servicio
check_health "database"
check_health "backend"
check_health "frontend"
check_health "recommender"

# Mostrar status final
log "Estado final de los servicios:"
$DOCKER_COMPOSE ps

# Mostrar URLs de acceso
success "🎉 Despliegue completado exitosamente!"
echo
echo "📋 URLs de acceso:"
echo "   Frontend:              http://localhost"
echo "   Backend API:           http://localhost:5000"
echo "   Microservicio IA:      http://localhost:8000"
echo "   Nginx Proxy:           http://localhost:8080"
echo "   Base de datos MySQL:   localhost:3306"
echo
echo "📊 Para ver logs: $DOCKER_COMPOSE logs -f [servicio]"
echo "🛑 Para detener:  $DOCKER_COMPOSE down"
echo "🔄 Para reiniciar: $DOCKER_COMPOSE restart [servicio]"
