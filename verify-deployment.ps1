# Script de verificación para despliegue Railway
Write-Host "🔍 Verificando configuración para Railway..." -ForegroundColor Cyan

$errores = @()
$warnings = @()

# Verificar archivos necesarios
$archivosRequeridos = @(
    "Dockerfile",
    "railway.toml",
    "backed/index.js",
    "backed/config/db.js",
    "backed/package.json",
    "cliente/package.json",
    "database/lynxshop.sql"
)

Write-Host "`n📁 Verificando archivos..." -ForegroundColor Yellow

foreach ($archivo in $archivosRequeridos) {
    if (Test-Path $archivo) {
        Write-Host "✅ $archivo" -ForegroundColor Green
    } else {
        $errores += "❌ Falta: $archivo"
        Write-Host "❌ $archivo" -ForegroundColor Red
    }
}

# Verificar package.json del backend
Write-Host "`n📦 Verificando dependencias del backend..." -ForegroundColor Yellow

if (Test-Path "backed/package.json") {
    $backendPkg = Get-Content "backed/package.json" | ConvertFrom-Json
    $depRequeridas = @("express", "cors", "mysql2", "dotenv", "bcryptjs", "jsonwebtoken", "multer")
    
    foreach ($dep in $depRequeridas) {
        if ($backendPkg.dependencies.$dep) {
            Write-Host "✅ $dep" -ForegroundColor Green
        } else {
            $errores += "❌ Dependencia faltante en backend: $dep"
            Write-Host "❌ $dep" -ForegroundColor Red
        }
    }
} else {
    $errores += "❌ No se encuentra backed/package.json"
}

# Verificar package.json del frontend
Write-Host "`n🎨 Verificando frontend..." -ForegroundColor Yellow

if (Test-Path "cliente/package.json") {
    $frontendPkg = Get-Content "cliente/package.json" | ConvertFrom-Json
    
    if ($frontendPkg.scripts.build) {
        Write-Host "✅ Script de build configurado" -ForegroundColor Green
    } else {
        $warnings += "⚠️ Script de build no encontrado en frontend"
        Write-Host "⚠️ Script de build no encontrado" -ForegroundColor Yellow
    }
} else {
    $errores += "❌ No se encuentra cliente/package.json"
}

# Verificar uploads
Write-Host "`n🖼️ Verificando imágenes..." -ForegroundColor Yellow

if (Test-Path "uploads") {
    $imagenes = Get-ChildItem "uploads" -Filter "*.jpg" | Measure-Object
    Write-Host "✅ Directorio uploads: $($imagenes.Count) imágenes" -ForegroundColor Green
} else {
    $warnings += "⚠️ Directorio uploads no encontrado"
    Write-Host "⚠️ Directorio uploads no encontrado" -ForegroundColor Yellow
}

# Verificar base de datos
Write-Host "`n🗄️ Verificando base de datos..." -ForegroundColor Yellow

if (Test-Path "database/lynxshop.sql") {
    $sqlContent = Get-Content "database/lynxshop.sql" -Raw
    
    $tablasRequeridas = @("usuarios", "productos", "pedidos", "categorias", "detallepedido")
    foreach ($tabla in $tablasRequeridas) {
        if ($sqlContent -match "CREATE TABLE.*$tabla") {
            Write-Host "✅ Tabla $tabla" -ForegroundColor Green
        } else {
            $errores += "❌ Tabla faltante: $tabla"
            Write-Host "❌ Tabla $tabla" -ForegroundColor Red
        }
    }
} else {
    $errores += "❌ No se encuentra database/lynxshop.sql"
}

# Verificar Railway CLI
Write-Host "`n🚄 Verificando Railway CLI..." -ForegroundColor Yellow

try {
    $railwayVersion = railway --version 2>&1
    if ($railwayVersion -match "railway") {
        Write-Host "✅ Railway CLI instalado: $railwayVersion" -ForegroundColor Green
    } else {
        $warnings += "⚠️ Railway CLI no detectado"
        Write-Host "⚠️ Railway CLI no detectado" -ForegroundColor Yellow
    }
} catch {
    $warnings += "⚠️ Railway CLI no instalado"
    Write-Host "⚠️ Railway CLI no instalado - Ejecuta: npm install -g @railway/cli" -ForegroundColor Yellow
}

# Resumen
Write-Host "`n📊 RESUMEN DE VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

if ($errores.Count -eq 0) {
    Write-Host "🎉 ¡TODO LISTO PARA DESPLEGAR!" -ForegroundColor Green
    Write-Host "Tu aplicación está configurada correctamente para Railway" -ForegroundColor Green
    
    if ($warnings.Count -gt 0) {
        Write-Host "`n⚠️ Advertencias:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host $warning -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n🚀 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. railway login" -ForegroundColor White
    Write-Host "2. railway new" -ForegroundColor White
    Write-Host "3. railway add mysql" -ForegroundColor White
    Write-Host "4. railway variables set JWT_SECRET='tu_secret_aqui'" -ForegroundColor White
    Write-Host "5. railway run .\migrate-to-railway.ps1" -ForegroundColor White
    Write-Host "6. railway up" -ForegroundColor White
    
} else {
    Write-Host "❌ ERRORES ENCONTRADOS:" -ForegroundColor Red
    foreach ($error in $errores) {
        Write-Host $error -ForegroundColor Red
    }
    Write-Host "`nCorrege estos errores antes de desplegar" -ForegroundColor Red
}

Write-Host "`n📖 Consulta DEPLOY_RAILWAY.md para instrucciones completas" -ForegroundColor Cyan
