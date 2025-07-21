# 🚀 GUÍA PASO A PASO: CÓMO EJECUTAR LOS MICROSERVICIOS LYNX

## 📋 ORDEN DE EJECUCIÓN (IMPORTANTE):

**Ejecuta en este orden específico:**
1. **Microservicio NLP** (Puerto 8004)
2. **Backend Node.js** (Puerto 5000)  
3. **Frontend React** (Puerto 5173)

---

## 🔧 PASO 1: MICROSERVICIO NLP (Puerto 8004)

### Abrir Terminal 1:
```powershell
# Navegar al directorio del microservicio NLP
cd "C:\xampp\htdocs\LynxWeb\AnalizadorNPLLynx\AnalizadorLynx-main\api"

# Ejecutar el microservicio dinámico
python main_lcln_dynamic.py
```

**✅ Cuando funcione correctamente verás:**
```
🚀 INICIANDO API LYNX DINÁMICA v6.0.0
📊 50 productos cargados dinámicamente
🔄 Cache programado cada 5 minutos
INFO: Uvicorn running on http://0.0.0.0:8004
```

**🌐 Verificar:** http://localhost:8004/api/health

---

## 🔧 PASO 2: BACKEND NODE.JS (Puerto 5000)

### Abrir Terminal 2:
```powershell
# Navegar al directorio del backend
cd "C:\xampp\htdocs\LynxWeb\backed"

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar el servidor backend
npm start
```

**✅ Cuando funcione correctamente verás:**
```
🚀 Servidor iniciado en puerto 5000
✅ Conexión a la base de datos exitosa
📡 CORS configurado para frontend
```

**🌐 Verificar:** http://localhost:5000/api/health

---

## 🔧 PASO 3: FRONTEND REACT (Puerto 5173)

### Abrir Terminal 3:
```powershell
# Navegar al directorio del frontend
cd "C:\xampp\htdocs\LynxWeb\cliente"

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar el servidor de desarrollo
npm run dev
```

**✅ Cuando funcione correctamente verás:**
```
VITE v5.4.19 ready in 283 ms
➜ Local: http://localhost:5173/
➜ Network: use --host to expose
```

**🌐 Verificar:** http://localhost:5173

---

## 🎯 VERIFICACIÓN COMPLETA DEL SISTEMA:

### 🧪 **Test de Integración Rápido:**

```powershell
# Probar el microservicio NLP directamente
Invoke-RestMethod -Uri "http://localhost:8004/api/health" -Method GET

# Probar búsqueda NLP
$body = @{
    query = "bebidas sin azucar"
    options = @{
        max_recommendations = 5
        enable_correction = $true
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8004/api/nlp/analyze" -Method POST -Body $body -ContentType "application/json"
```

---

## 🔍 SOLUCIÓN DE PROBLEMAS COMUNES:

### ❌ **Error: "Port already in use"**
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8004
netstat -ano | findstr :5000
netstat -ano | findstr :5173

# Matar proceso por PID (reemplaza XXXX con el PID)
taskkill /PID XXXX /F
```

### ❌ **Error: Python no encontrado**
```powershell
# Verificar instalación de Python
python --version
# O intentar con:
py --version
```

### ❌ **Error: npm no encontrado**
```powershell
# Verificar instalación de Node.js
node --version
npm --version
```

### ❌ **Error: Módulos no encontrados**
```powershell
# En cada directorio, reinstalar dependencias:
npm clean-install
# O:
rm -rf node_modules
npm install
```

---

## 📱 USANDO EL SISTEMA:

### **1. Frontend con NLP:**
- Ve a: http://localhost:5173
- Usa la barra de búsqueda con el ícono de cerebro 🧠
- Prueba consultas como:
  - "bebidas sin azúcar"
  - "snacks picantes baratos" 
  - "productos menos de 20 pesos"

### **2. API Directa:**
- Health: http://localhost:8004/api/health
- Docs: http://localhost:8004/docs
- Stats: http://localhost:8004/api/stats

### **3. Backend API:**
- Health: http://localhost:5000/api/health
- Productos: http://localhost:5000/api/productos

---

## 🚀 COMANDOS PARA EJECUTAR TODO DE UNA VEZ:

### **Script PowerShell para ejecutar todo:**

```powershell
# Crear script de inicio automático
@"
# Terminal 1 - NLP API
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\xampp\htdocs\LynxWeb\AnalizadorNPLLynx\AnalizadorLynx-main\api'; python main_lcln_dynamic.py"

# Esperar 5 segundos
Start-Sleep -Seconds 5

# Terminal 2 - Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\xampp\htdocs\LynxWeb\backed'; npm start"

# Esperar 3 segundos  
Start-Sleep -Seconds 3

# Terminal 3 - Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\xampp\htdocs\LynxWeb\cliente'; npm run dev"

Write-Host "🚀 Todos los microservicios iniciados!"
Write-Host "🌐 Frontend: http://localhost:5173"
Write-Host "🧠 NLP API: http://localhost:8004"
Write-Host "⚙️  Backend: http://localhost:5000"
"@ | Out-File -FilePath "C:\xampp\htdocs\LynxWeb\iniciar_todo.ps1" -Encoding UTF8

# Ejecutar el script
& "C:\xampp\htdocs\LynxWeb\iniciar_todo.ps1"
```

---

## 🎉 RESULTADO FINAL:

Cuando todo esté funcionando correctamente tendrás:

- ✅ **NLP API**: http://localhost:8004 (Análisis de lenguaje natural)
- ✅ **Backend**: http://localhost:5000 (API de productos y pedidos)  
- ✅ **Frontend**: http://localhost:5173 (Interfaz de usuario)

### **🧠 El NLP funcionará cuando veas:**
- Ícono de cerebro 🧠 en la barra de búsqueda
- Texto "(con IA)" en el placeholder
- Badge verde "LYNX IA conectado"

---

*¡El sistema LYNX estará completamente operativo!* 🎯
