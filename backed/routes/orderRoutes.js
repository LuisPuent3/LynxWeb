const express = require('express');
const { createOrder, getOrdersByUser, getOrderDetails } = require('../controllers/orderController');

const router = express.Router();

router.post('/', createOrder); // Crear un nuevo pedido
router.get('/:id_usuario', getOrdersByUser); // Obtener pedidos de un usuario
router.get('/:id', getOrderDetails); // Obtener detalles de un pedido específico

module.exports = router;