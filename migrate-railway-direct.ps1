# Script de migración directa para Railway (PowerShell)
# Con variables configuradas directamente

Write-Host "Iniciando migración de base de datos a Railway..." -ForegroundColor Green

# Configurar variables de Railway directamente
$MYSQLHOST = "shortline.proxy.rlwy.net"
$MYSQLPORT = "40498"
$MYSQLUSER = "root"
$MYSQLPASSWORD = "vqWpDisjeFSLHcFhnNLRIdvSqzKFPCei"
$MYSQLDATABASE = "railway"

Write-Host "Conectando a: ${MYSQLHOST}:${MYSQLPORT}" -ForegroundColor Cyan
Write-Host "Base de datos: $MYSQLDATABASE" -ForegroundColor Cyan
Write-Host "Usuario: $MYSQLUSER" -ForegroundColor Cyan

# Verificar que el archivo SQL existe
$dumpFile = "database\lynxshop.sql"
if (-not (Test-Path $dumpFile)) {
    Write-Host "❌ Error: No se encontró el archivo $dumpFile" -ForegroundColor Red
    exit 1
}

# Ejecutar el dump SQL
$mysqlCommand = "mysql -h $MYSQLHOST -P $MYSQLPORT -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE"

Write-Host "Ejecutando migración..." -ForegroundColor Yellow

try {
    cmd /c "$mysqlCommand < $dumpFile"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migración completada exitosamente" -ForegroundColor Green
        Write-Host "Base de datos LynxShop migrada a Railway" -ForegroundColor Green
    } else {
        throw "Error en comando MySQL (código: $LASTEXITCODE)"
    }
} catch {
    Write-Host "❌ Error en la migración: $_" -ForegroundColor Red
    Write-Host "Verifica que MySQL client esté instalado" -ForegroundColor Yellow
    exit 1
}

Write-Host "🎉 Proceso completado" -ForegroundColor Green
