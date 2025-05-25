# 🚀 Despliegue LynxWeb en Railway - Monolito

## ✅ Preparación Completada

Tu aplicación está lista para desplegar en Railway como monolito. Todo el código ha sido configurado.

## 📋 Pasos para Desplegar

### 1. Instalar Railway CLI
```powershell
npm install -g @railway/cli
```

### 2. Login a Railway
```powershell
railway login
```

### 3. Crear Proyecto
```powershell
# Desde la raíz del proyecto
railway new
# Selecciona "Empty Project"
```

### 4. Agregar MySQL
```powershell
railway add mysql
```

### 5. Configurar Variables de Entorno
```powershell
# Variables que Railway configura automáticamente:
# MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE

# Variables que debes configurar:
railway variables set JWT_SECRET="tu_jwt_secret_super_seguro_aqui_2024"
railway variables set NODE_ENV="production"
```

### 6. Migrar Base de Datos
```powershell
# Obtener las variables de Railway primero
railway run echo $env:MYSQLHOST

# Ejecutar migración
railway run .\migrate-to-railway.ps1
```

### 7. Desplegar Aplicación
```powershell
railway up
```

### 8. Verificar Despliegue
```powershell
railway status
railway logs
```

## 🔧 Configuración Incluida

### ✅ Dockerfile
- Multi-stage build optimizado
- Frontend React compilado
- Backend Node.js
- Health check configurado

### ✅ Backend Actualizado
- Configuración de BD para Railway
- Servir frontend en producción
- Health check endpoint: `/api/health`
- Fallback para React Router

### ✅ Base de Datos
- Compatible con MySQL de Railway
- Migración automática con script
- SSL configurado para producción

## 🌐 URLs Después del Despliegue

- **Frontend**: `https://tu-app.railway.app`
- **API**: `https://tu-app.railway.app/api/`
- **Health Check**: `https://tu-app.railway.app/api/health`
- **Imágenes**: `https://tu-app.railway.app/uploads/`

## 🛠️ Comandos Útiles Railway

```powershell
# Ver variables de entorno
railway variables

# Ver logs en tiempo real
railway logs -f

# Conectar a la BD directamente
railway connect mysql

# Redeploy manual
railway up --detach

# Ver servicios
railway status
```

## ⚠️ Notas Importantes

1. **JWT_SECRET**: Cambia por uno seguro de al menos 32 caracteres
2. **Imágenes**: Las imágenes de productos se incluyen en el build
3. **Base de Datos**: Todas las tablas y datos se migran automáticamente
4. **SSL**: Railway maneja HTTPS automáticamente

## 🎯 Verificación Final

Después del despliegue, verifica:

1. ✅ Health check: `GET /api/health`
2. ✅ Frontend carga correctamente
3. ✅ Login/registro funciona
4. ✅ Productos se muestran con imágenes
5. ✅ Carrito y pedidos funcionan

## 🚨 Troubleshooting

Si hay problemas:

```powershell
# Ver logs detallados
railway logs --tail 100

# Verificar variables
railway variables

# Redeploy
railway up --detach

# Conectar a BD para verificar datos
railway connect mysql
```

## 📞 Soporte

Tu aplicación funciona igual que en local. Todos los endpoints, autenticación, carrito, pedidos y administración están configurados y listos.
