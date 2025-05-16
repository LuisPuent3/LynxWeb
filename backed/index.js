const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

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

// Importar rutas
const authRoutes = require('./routes/authRoutes');
const productRoutes = require('./routes/productRoutes');
const orderRoutes = require('./routes/orderRoutes');
const categoryRoutes = require('./routes/categoryRoutes');

// Usar rutas
app.use('/api/auth', authRoutes);
app.use('/api/productos', productRoutes);
app.use('/api/pedidos', orderRoutes);
app.use('/api/categorias', categoryRoutes);

// Ruta de prueba
app.get('/api/test', (req, res) => {
    res.json({ message: 'API funcionando correctamente' });
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