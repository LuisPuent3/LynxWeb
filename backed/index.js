const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

// Carga las variables de entorno
dotenv.config();

const app = express();

// Logger para depuración
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    next();
});

// Middlewares
app.use(cors({
    origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
    credentials: true
}));
app.use(express.json());

// Configuración para servir archivos estáticos desde el directorio uploads
app.use('/uploads', express.static(path.join(__dirname, '../uploads'), {
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

// Ruta de prueba para verificar que la API está en funcionamiento
app.get('/api/test', (req, res) => {
    res.json({ message: 'API funcionando correctamente', timestamp: new Date().toISOString() });
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