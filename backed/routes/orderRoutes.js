const express = require('express');
const orderController = require('../controllers/orderController');

const router = express.Router();

router.post('/', orderController.createOrder); // Crear un nuevo pedido
router.get('/:id_usuario', orderController.getOrdersByUser); // Obtener pedidos de un usuario
router.get('/:id', orderController.getOrderDetails); // Obtener detalles de un pedido específico

module.exports = router;
