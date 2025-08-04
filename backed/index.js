const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

// Carga las variables de entorno
dotenv.config();

const app = express();

// Logger para depuración
// app.use((req, res, next) => {
//     console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
//     next();
// });

// Configuración de CORS
const allowedOrigins = [
  'http://localhost:3000',
  'http://localhost:5173', 
  'http://localhost:5174',  // Add the actual port the frontend is using
  'http://localhost:8004',   // Add the NLP API port
  'https://lynx-shop-production.up.railway.app'  // Railway production URL
]; 

const productionOrigin = process.env.CORS_ORIGIN;

if (productionOrigin && productionOrigin.trim() !== '') {
  allowedOrigins.push(productionOrigin);
}

// Ensure no empty strings if productionOrigin was an empty string and then trimmed.
const uniqueAllowedOrigins = [...new Set(allowedOrigins.filter(origin => origin && origin.trim() !== ''))];

console.log('[CORS] Allowed origins:', uniqueAllowedOrigins);

const corsOptions = {
  origin: function (origin, callback) {
    console.log('[CORS] Request from origin:', origin);
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);
    if (uniqueAllowedOrigins.indexOf(origin) === -1) {
      const msg = `The CORS policy for this site does not allow access from the specified Origin: ${origin}`;
      console.log('[CORS ERROR]', msg);
      return callback(new Error(msg), false);
    }
    return callback(null, true);
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  optionsSuccessStatus: 200 // some legacy browsers (IE11, various SmartTVs) choke on 204
};

app.use(cors(corsOptions));
// console.log('[CORS DEBUG] Allowing all origins'); // Reverted

// Middlewares
app.use(express.json());

// Configuración para servir archivos estáticos desde el directorio uploads
const uploadsPath = path.join(__dirname, '../uploads');
console.log('📂 Uploads path:', uploadsPath);
console.log('📂 Uploads directory exists:', require('fs').existsSync(uploadsPath));
if (require('fs').existsSync(uploadsPath)) {
    const files = require('fs').readdirSync(uploadsPath);
    console.log(`📂 Found ${files.length} files in uploads:`, files.slice(0, 5));
}

app.use('/uploads', express.static(uploadsPath, {
  maxAge: '1d', // Caché por 1 día
  setHeaders: function (res, path, stat) {
    res.set('Cache-Control', 'public, max-age=86400'); // 1 día en segundos
    res.set('Expires', new Date(Date.now() + 86400000).toUTCString()); // 1 día en milisegundos
  }
}));

// Configuración para servir archivos estáticos desde el directorio cliente/public
app.use('/assets', express.static(path.join(__dirname, '../cliente/public/assets'), {
  maxAge: '1d', // Caché por 1 día
  setHeaders: function (res, path, stat) {
    res.set('Cache-Control', 'public, max-age=86400'); // 1 día en segundos
    res.set('Expires', new Date(Date.now() + 86400000).toUTCString()); // 1 día en milisegundos
  }
}));

// Importar rutas
const authRoutes = require('./routes/authRoutes');
const productRoutes = require('./routes/productRoutes');
const pedidosRoutes = require('./routes/pedidosRoutes');
const categoryRoutes = require('./routes/categoryRoutes');
const recommendationRoutes = require('./routes/recommendations');
const uploadRoutes = require('./routes/uploadRoutes');
const passwordResetRoutes = require('./routes/passwordResetRoutes');
const sinonimosRoutes = require('./routes/sinonimosRoutes');
const lclnRoutes = require('./routes/lcln');

// Logger avanzado para depuración
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url} - Body:`, 
        req.method === 'POST' || req.method === 'PUT' ? JSON.stringify(req.body).substring(0, 200) : '');
    next();
});

// Usar rutas
app.use('/api/auth', authRoutes);
app.use('/api/productos', productRoutes);
app.use('/api/pedidos', pedidosRoutes);
app.use('/api/categorias', categoryRoutes);
app.use('/api/recommendations', recommendationRoutes);
app.use('/api/uploads', uploadRoutes);
app.use('/api/password-reset', passwordResetRoutes);
app.use('/api/admin/sinonimos', sinonimosRoutes);
app.use('/api/lcln', lclnRoutes);

// Ruta temporal de pruebas (sin autenticación)
const testSinonimosRoutes = require('./routes/testSinonimosRoutes');
app.use('/api/test/sinonimos', testSinonimosRoutes);

// Servir archivos estáticos del frontend (React build)
app.use(express.static(path.join(__dirname, 'public')));

// Ruta catch-all para servir index.html en rutas de frontend (SPA)
app.get('*', (req, res, next) => {
    // Solo servir index.html para rutas que NO sean de API
    if (req.path.startsWith('/api/')) {
        return next();
    }
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Ruta de prueba para verificar que la API está en funcionamiento
app.get('/api/test', (req, res) => {
    res.json({ message: 'API funcionando correctamente', timestamp: new Date().toISOString() });
});

// Ruta de health check para Docker healthchecks
app.get('/api/health', async (req, res) => {
    try {
        // Verificar conexión a base de datos
        const pool = require('./config/db');
        await pool.query('SELECT 1');
        
        res.json({ 
            status: 'healthy',
            timestamp: new Date().toISOString(),
            database: 'connected',
            service: 'backend' 
        });
    } catch (error) {
        res.status(503).json({ 
            status: 'unhealthy',
            timestamp: new Date().toISOString(),
            database: 'disconnected',
            service: 'backend',
            error: error.message 
        });
    }
});

// Endpoint de debug para verificar imágenes
app.get('/api/debug/uploads', (req, res) => {
    const fs = require('fs');
    const uploadsPath = path.join(__dirname, '../uploads');
    
    try {
        const exists = fs.existsSync(uploadsPath);
        let files = [];
        
        if (exists) {
            files = fs.readdirSync(uploadsPath);
        }
        
        res.json({
            uploadsPath,
            exists,
            fileCount: files.length,
            files: files.slice(0, 10) // Primeros 10 archivos
        });
    } catch (error) {
        res.status(500).json({
            error: error.message,
            uploadsPath
        });
    }
});

// Ruta de depuración específica para pedidos
app.get('/api/debug/rutas', (req, res) => {
    // Recopilar información sobre las rutas registradas
    const routes = [];
    
    // Recopilar información sobre pedidosRoutes
    try {
        const pedidosRouter = express.Router();
        pedidosRoutes.stack.forEach(layer => {
            if (layer.route) {
                routes.push({
                    path: '/api/pedidos' + layer.route.path,
                    methods: Object.keys(layer.route.methods).join(', ').toUpperCase()
                });
            }
        });
    } catch (err) {
        console.error('Error al analizar rutas de pedidos:', err);
    }
    
    res.json({
        message: 'Rutas disponibles en la API',
        timestamp: new Date().toISOString(),
        routes: routes
    });
});

// Manejo de rutas no encontradas
app.use((req, res, next) => {
    if (!res.headersSent) {
        console.log(`Ruta no encontrada: ${req.method} ${req.originalUrl}`);
        res.status(404).json({
            error: 'Ruta no encontrada',
            path: req.originalUrl,
            method: req.method,
            available_api_routes: [
                '/api/auth',
                '/api/productos',
                '/api/pedidos',
                '/api/categorias',
                '/api/recommendations',
                '/api/test',
                '/api/debug/rutas'
            ]
        });
    }
    next();
});

// Manejo de errores mejorado
app.use((err, req, res, next) => {
    console.error('Error en la API:', err);
    console.error('Stack trace:', err.stack);
    
    if (err.code === 'ECONNREFUSED') {
        return res.status(500).json({ 
            error: 'Error de conexión a la base de datos',
            message: 'No se pudo conectar a la base de datos. Verifique que MySQL esté en ejecución.'
        });
    }
    
    res.status(500).json({ 
        error: 'Error interno del servidor',
        message: process.env.NODE_ENV === 'production' ? 
            'Algo salió mal' : 
            err.message || 'Error desconocido',
        stack: process.env.NODE_ENV === 'production' ? null : err.stack
    });
});

// Inicialización del servidor
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
    console.log('Ambiente:', process.env.NODE_ENV || 'development');
});