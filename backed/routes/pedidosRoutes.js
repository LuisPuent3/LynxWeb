const express = require('express');
const router = express.Router();
const {
    createOrder,
    getOrdersByUser,
    getAllOrders,
    updateOrderStatus,
    getOrderById
} = require('../controllers/pedidoController');

// Agregar middleware para registro de solicitudes
router.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - Pedidos API: ${req.method} ${req.url}`);
    console.log('Parámetros en middleware de ruta:', req.params);
    next();
});

// Prueba simple para verificar si la ruta está funcionando
router.get('/test', (req, res) => {
    res.json({ message: 'La ruta de pedidos está funcionando correctamente' });
});

// Ruta para obtener un pedido específico por su ID
router.get('/detalle/:id', (req, res, next) => {
    console.log(`[pedidosRoutes.js] Petición a /detalle/:id con ID: ${req.params.id}`);
    getOrderById(req, res, next);
});

// Ruta para obtener pedidos de un usuario específico
router.get('/usuario/:id', (req, res, next) => {
    console.log(`[pedidosRoutes.js] Petición a /usuario/:id con ID: ${req.params.id}`);
    getOrdersByUser(req, res, next); // Pasar next por si getOrdersByUser es un middleware
});

// Mantener la ruta antigua por compatibilidad (opcional, considera si realmente la necesitas)
router.get('/user/:id', (req, res, next) => {
    console.log(`[pedidosRoutes.js] Petición a /user/:id con ID: ${req.params.id}`);
    getOrdersByUser(req, res, next);
});

// Ruta para crear un pedido
router.post('/', createOrder);

// Ruta para obtener todos los pedidos (solo para administradores)
router.get('/admin', getAllOrders);

// Ruta para obtener todos los pedidos (endpoint raíz)
router.get('/', getAllOrders);

// Ruta para actualizar el estado de un pedido
router.put('/:id', updateOrderStatus);

module.exports = router;
