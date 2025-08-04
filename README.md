# 🦁 LynxWeb - E-commerce Inteligente

LynxWeb es una plataforma de e-commerce moderna con búsqueda inteligente basada en procesamiento de lenguaje natural (NLP) y un sistema de recomendaciones avanzado. La aplicación integra múltiples servicios especializados para ofrecer una experiencia de compra superior.

## 🚀 Características Principales

### 🔍 Búsqueda Inteligente (Sistema LCLN)
- **Procesamiento de Lenguaje Natural**: Búsqueda semántica que entiende consultas en español natural
- **Corrección Ortográfica**: Detección y corrección automática de errores de escritura
- **Sinónimos Inteligentes**: Reconocimiento de sinónimos y variaciones de productos
- **Análisis Léxico Formal**: Sistema de compiladores con autómatas finitos determinísticos (AFD)

### 🛒 E-commerce Completo
- **Gestión de Productos**: CRUD completo con categorías y variantes
- **Carrito de Compras**: Funcionalidad completa con persistencia
- **Sistema de Pedidos**: Procesamiento y seguimiento de órdenes
- **Gestión de Usuarios**: Autenticación, roles y perfiles

### 🤖 Sistema de Recomendaciones
- **Recomendaciones Personalizadas**: Basadas en historial de compra y preferencias
- **Análisis de Comportamiento**: Machine Learning para sugerencias inteligentes
- **Filtrado Colaborativo**: Recomendaciones basadas en usuarios similares

### 👨‍💼 Panel de Administración
- **Dashboard Analítico**: Métricas y estadísticas en tiempo real
- **Gestión de Inventario**: Control de stock con alertas
- **Administración de Sinónimos**: Sistema avanzado para mejorar búsquedas
- **Gestión de Categorías**: Organización jerárquica de productos

## 🏗️ Arquitectura del Sistema

### Frontend (Cliente)
- **Framework**: React 18 + TypeScript + Vite
- **UI/UX**: Bootstrap 5 + React Bootstrap
- **Estado**: Context API + Custom Hooks
- **Routing**: React Router DOM v6
- **Validación**: Formik + Yup
- **HTTP Client**: Axios

### Backend (API REST)
- **Framework**: Node.js + Express.js
- **Base de Datos**: MySQL con Pool de Conexiones
- **Autenticación**: JWT + bcrypt
- **Upload de Archivos**: Multer + Sharp (optimización de imágenes)
- **Logging**: Sistema personalizado para debugging
- **CORS**: Configuración avanzada para múltiples orígenes

### Sistema NLP (LCLN)
- **Framework**: Python + FastAPI
- **Análisis Léxico**: Autómatas Finitos Determinísticos (AFD)
- **Corrección Ortográfica**: Algoritmos de distancia de edición
- **Procesamiento Semántico**: Sistema de sinónimos inteligente
- **Análisis Sintáctico**: Gramática formal LCLN

### Sistema de Recomendaciones
- **Framework**: Python + FastAPI
- **Machine Learning**: scikit-learn + pandas
- **Persistencia**: Modelos serializados con pickle
- **Base de Datos**: MySQL con análisis de patrones

## 📁 Estructura del Proyecto

```
LynxWeb/
├── cliente/                          # Frontend React
│   ├── src/
│   │   ├── components/              # Componentes reutilizables
│   │   │   ├── auth/               # Autenticación
│   │   │   ├── admin/              # Panel administrativo
│   │   │   ├── products/           # Gestión de productos
│   │   │   ├── search/             # Búsqueda inteligente
│   │   │   └── layout/             # Layout y navegación
│   │   ├── contexts/               # Context API
│   │   ├── hooks/                  # Custom Hooks
│   │   ├── pages/                  # Páginas principales
│   │   ├── services/               # Servicios API
│   │   ├── types/                  # TypeScript definitions
│   │   └── utils/                  # Utilidades
│   ├── public/                     # Archivos estáticos
│   └── tests/                      # Tests unitarios
│
├── backed/                          # Backend API
│   ├── controllers/                # Controladores MVC
│   ├── routes/                     # Definición de rutas
│   ├── middlewares/                # Middlewares personalizados
│   ├── config/                     # Configuración DB
│   ├── utils/                      # Utilidades backend
│   └── tests/                      # Tests de integración
│
├── AnalizadorNPLLynx/              # Sistema NLP/LCLN
│   └── AnalizadorLynx-main/
│       ├── sistema_lcln_simple.py  # Core del sistema LCLN
│       ├── servidor_lcln_api.py    # API FastAPI
│       ├── analizador_lexico.py    # Análisis léxico
│       ├── corrector_ortografico.py # Corrección de texto
│       ├── afd_*.py                # Autómatas finitos
│       └── docs/                   # Documentación técnica
│
├── services/                       # Microservicios
│   └── recommender/               # Sistema de recomendaciones
│       ├── main.py                # API FastAPI
│       ├── etl.py                 # Extracción y procesamiento
│       └── data/                  # Modelos ML
│
├── database/                      # Scripts de BD
├── uploads/                       # Archivos subidos
├── docs/                         # Documentación
└── tests/                        # Tests E2E
```

## 🛠️ Tecnologías Utilizadas

### Frontend
- **React 18.2** - Framework UI moderno
- **TypeScript 5.3** - Tipado estático
- **Vite 5.1** - Build tool y dev server
- **Bootstrap 5.3** - Framework CSS
- **React Router DOM 6.22** - Routing SPA
- **Axios 1.6** - Cliente HTTP
- **Formik + Yup** - Manejo de formularios
- **JWT Decode** - Manejo de tokens

### Backend
- **Node.js + Express.js 4.18** - Servidor web
- **MySQL2 3.11** - Driver de base de datos
- **JWT + bcrypt** - Autenticación segura
- **Multer + Sharp** - Upload y procesamiento de imágenes
- **Nodemailer** - Envío de emails
- **CORS** - Cross-Origin Resource Sharing
- **dotenv** - Variables de entorno

### NLP/LCLN
- **Python 3.9+** - Lenguaje principal
- **FastAPI** - Framework API moderno
- **Pandas** - Manipulación de datos
- **NumPy** - Computación numérica
- **Asyncio** - Programación asíncrona

### Recomendaciones
- **scikit-learn** - Machine Learning
- **pandas** - Análisis de datos
- **pickle** - Serialización de modelos
- **PyMySQL** - Conector MySQL

### Base de Datos
- **MySQL 8.0** - Sistema de gestión
- **InnoDB** - Motor de almacenamiento
- **Índices optimizados** - Performance
- **Foreign Keys** - Integridad referencial

## 🚀 Instalación y Configuración

### Prerrequisitos
- Node.js 18+ y npm
- Python 3.9+
- MySQL 8.0+
- XAMPP (opcional para desarrollo local)

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd LynxWeb
```

### 2. Configurar Base de Datos
```bash
# Importar esquema de base de datos
mysql -u root -p < database/lynxshop.sql
```

### 3. Instalar Backend
```bash
cd backed
npm install
cp .env.example .env  # Configurar variables de entorno
npm run dev           # Desarrollo
npm start            # Producción
```

### 4. Instalar Frontend
```bash
cd cliente
npm install
npm run dev          # Desarrollo en puerto 5173
npm run build        # Build de producción
```

### 5. Configurar Sistema NLP
```bash
cd AnalizadorNPLLynx/AnalizadorLynx-main
pip install -r requirements.txt
python servidor_lcln_api.py  # Puerto 8004
```

### 6. Sistema de Recomendaciones
```bash
cd services/recommender
pip install -r requirements.txt
python main.py       # Puerto 8003
```

## ⚙️ Variables de Entorno

### Backend (.env)
```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=lynxshop

# JWT
JWT_SECRET=tu_secreto_super_seguro

# Email (Nodemailer)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASS=tu_password_app

# CORS
CORS_ORIGIN=http://localhost:5173

# Railway (Producción)
MYSQLHOST=
MYSQLPORT=
MYSQLUSER=
MYSQLPASSWORD=
MYSQLDATABASE=
```

## 🔧 Servicios y Puertos

| Servicio | Puerto | Descripción |
|----------|---------|-------------|
| Frontend | 5173 | Aplicación React (Vite dev) |
| Backend API | 5000 | API REST principal |
| Sistema NLP | 8004 | Servicio de búsqueda inteligente |
| Recomendaciones | 8003 | Sistema ML de recomendaciones |
| MySQL | 3306 | Base de datos |

## 📊 Esquema de Base de Datos

### Tablas Principales
- **usuarios**: Gestión de usuarios y roles
- **productos**: Catálogo de productos
- **categorias**: Organización por categorías  
- **pedidos**: Órdenes de compra
- **detallepedido**: Items de cada pedido
- **sinonimos**: Sistema de sinónimos para búsqueda
- **password_resets**: Tokens de recuperación

### Relaciones
- Usuario → Pedidos (1:N)
- Pedido → DetallePedido (1:N)
- Producto → DetallePedido (1:N)
- Categoría → Productos (1:N)

## 🔍 Sistema LCLN (Búsqueda Inteligente)

### Características Avanzadas
1. **Análisis Léxico**: Tokenización con AFD especializados
2. **Corrección Ortográfica**: Algoritmo de distancia de Levenshtein
3. **Expansión de Sinónimos**: Base de datos semántica
4. **Filtrado Inteligente**: Por categorías, precios y atributos
5. **Análisis Semántico**: Interpretación de consultas complejas

### Ejemplo de Uso
```javascript
// Frontend
const resultados = await nlpService.search("coca sin azucar");

// Backend LCLN procesa:
// 1. "coca" → ["coca-cola", "refresco de cola"]
// 2. "sin azucar" → ["diet", "zero", "light"]
// 3. Filtra productos que coincidan
```

## 🤖 Sistema de Recomendaciones

### Algoritmos Implementados
1. **Filtrado Colaborativo**: Usuarios similares
2. **Filtrado por Contenido**: Productos relacionados
3. **Híbrido**: Combinación de ambos enfoques
4. **Tendencias**: Productos más populares

### Métricas de Evaluación
- Precisión y Recall
- RMSE (Root Mean Square Error)
- Cobertura del catálogo
- Diversidad de recomendaciones

## 🧪 Testing

### Frontend
```bash
cd cliente
npm run test          # Tests unitarios con Vitest
npm run test:watch    # Modo watch
```

### Backend
```bash
cd backed
npm test              # Tests con Jest
```

### E2E
```bash
# Tests end-to-end con Playwright
npm run test:e2e
```

## 📈 Métricas y Monitoreo

### Logs Disponibles
- **API Requests**: Todas las peticiones HTTP
- **Errores**: Stack traces detallados
- **Performance**: Tiempos de respuesta
- **Búsquedas**: Queries y resultados NLP

### Health Checks
- **GET /api/health**: Estado del backend
- **GET /api/test**: Verificación básica
- Monitoreo de conexión a BD

## 🚢 Despliegue

### Railway (Recomendado)
1. **Conectar repositorio** a Railway
2. **Configurar variables** de entorno
3. **Deploy automático** con cada push
4. **Escalado horizontal** automático

### Docker
```bash
# Build y run con Docker Compose
docker-compose up --build
```

### Manual
1. **Build frontend**: `npm run build`
2. **Configurar nginx** como proxy reverso
3. **PM2** para gestión de procesos Node.js
4. **Supervisord** para servicios Python

## 🔒 Seguridad

### Implementadas
- **JWT Authentication** con refresh tokens
- **Bcrypt** para hash de contraseñas
- **SQL Injection** prevención con queries parametrizadas
- **CORS** configuración restrictiva
- **Rate Limiting** en rutas críticas
- **Validación** estricta de inputs
- **Sanitización** de archivos subidos

### Recomendaciones Adicionales
- HTTPS en producción
- Firewall de aplicación web (WAF)
- Monitoreo de seguridad continuo
- Backup automático de base de datos

## 🤝 Contribución

### Flujo de Desarrollo
1. **Fork** del repositorio
2. **Crear rama** feature/nueva-funcionalidad
3. **Commits** descriptivos y atómicos
4. **Tests** para nueva funcionalidad
5. **Pull Request** con descripción detallada

### Estándares de Código
- **ESLint** para JavaScript/TypeScript
- **Prettier** para formateo
- **Conventional Commits** para mensajes
- **Documentación** JSDoc para funciones

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

Para reportar bugs o solicitar features:
1. **Issues** en GitHub
2. **Documentación** técnica en `/docs`
3. **Logs** detallados para debugging

---

**Desarrollado con ❤️ por el equipo LynxWeb**

*Última actualización: Julio 2025*
#   D e p l o y   t r i g g e r   0 8 / 0 3 / 2 0 2 5   1 9 : 1 3 : 3 1  
 