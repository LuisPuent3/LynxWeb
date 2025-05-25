# Script de migración para Railway (PowerShell)
# Ejecutar después de crear el servicio MySQL en Railway

Write-Host "Iniciando migración de base de datos a Railway..." -ForegroundColor Green

# Verificar que las variables estén configuradas
if (-not $env:MYSQLHOST -or -not $env:MYSQLUSER -or -not $env:MYSQLPASSWORD -or -not $env:MYSQLDATABASE) {
    Write-Host "Error: Variables de Railway no configuradas" -ForegroundColor Red
    Write-Host "Asegúrate de tener un servicio MySQL activo en Railway" -ForegroundColor Red
    Write-Host "Configura las variables con: railway variables" -ForegroundColor Yellow
    exit 1
}

Write-Host "Conectando a: $env:MYSQLHOST:$env:MYSQLPORT" -ForegroundColor Cyan
Write-Host "Base de datos: $env:MYSQLDATABASE" -ForegroundColor Cyan
Write-Host "Usuario: $env:MYSQLUSER" -ForegroundColor Cyan

# Ejecutar el dump SQL
$mysqlCommand = "mysql -h $env:MYSQLHOST -P $env:MYSQLPORT -u $env:MYSQLUSER -p$env:MYSQLPASSWORD $env:MYSQLDATABASE"
$dumpFile = "database\lynxshop.sql"

Write-Host "Ejecutando migración..." -ForegroundColor Yellow

try {
    cmd /c "$mysqlCommand < $dumpFile"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migración completada exitosamente" -ForegroundColor Green
        Write-Host "Base de datos LynxShop migrada a Railway" -ForegroundColor Green
    } else {
        throw "Error en comando MySQL"
    }
} catch {
    Write-Host "❌ Error en la migración: $_" -ForegroundColor Red
    exit 1
}
