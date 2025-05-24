@echo off
REM Script para construir y desplegar LynxWeb con Docker en Windows

echo 🚀 Iniciando despliegue de LynxWeb...

REM Verificar que Docker esté instalado y corriendo
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no está instalado. Por favor instale Docker primero.
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no está corriendo. Por favor inicie Docker primero.
    exit /b 1
)

REM Verificar que docker-compose esté disponible
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Docker Compose no está disponible. Por favor instale Docker Compose.
        exit /b 1
    )
    set DOCKER_COMPOSE=docker compose
) else (
    set DOCKER_COMPOSE=docker-compose
)

REM Crear directorios necesarios
echo [INFO] Creando directorios necesarios...
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "logs\nginx" mkdir logs\nginx

REM Copiar archivo de entorno si no existe
if not exist ".env" (
    if exist ".env.production" (
        echo [INFO] Copiando .env.production a .env...
        copy .env.production .env
    ) else (
        echo [WARNING] No se encontró archivo .env ni .env.production. Usando valores por defecto.
    )
)

REM Construir imágenes
echo [INFO] Construyendo imágenes Docker...
%DOCKER_COMPOSE% build --no-cache

if %errorlevel% neq 0 (
    echo [ERROR] Error al construir las imágenes Docker
    exit /b 1
)

echo [SUCCESS] Imágenes construidas exitosamente

REM Detener contenedores existentes
echo [INFO] Deteniendo contenedores existentes...
%DOCKER_COMPOSE% down

REM Iniciar servicios
echo [INFO] Iniciando servicios...
%DOCKER_COMPOSE% up -d

if %errorlevel% neq 0 (
    echo [ERROR] Error al iniciar los servicios
    exit /b 1
)

REM Esperar a que los servicios estén listos
echo [INFO] Esperando que los servicios estén listos...
timeout /t 15 /nobreak >nul

REM Mostrar status final
echo [INFO] Estado final de los servicios:
%DOCKER_COMPOSE% ps

REM Mostrar URLs de acceso
echo.
echo 🎉 Despliegue completado exitosamente!
echo.
echo 📋 URLs de acceso:
echo    Frontend:              http://localhost
echo    Backend API:           http://localhost:5000
echo    Microservicio IA:      http://localhost:8000
echo    Nginx Proxy:           http://localhost:8080
echo    Base de datos MySQL:   localhost:3306
echo.
echo 📊 Para ver logs: %DOCKER_COMPOSE% logs -f [servicio]
echo 🛑 Para detener:  %DOCKER_COMPOSE% down
echo 🔄 Para reiniciar: %DOCKER_COMPOSE% restart [servicio]

pause
