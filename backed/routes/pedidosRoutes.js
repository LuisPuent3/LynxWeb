const express = require('express');
const router = express.Router();
const {
    createOrder,
    getOrdersByUser,
    getAllOrders,
    updateOrderStatus
} = require('../controllers/pedidoController');

// Ruta para crear un pedido
router.post('/', createOrder);

// Ruta para obtener pedidos de un usuario específico
router.get('/user/:id', getOrdersByUser);

// Ruta para obtener todos los pedidos (solo para administradores)
router.get('/admin', getAllOrders);

// Ruta para actualizar el estado de un pedido
router.put('/:id', updateOrderStatus);

module.exports = router;
