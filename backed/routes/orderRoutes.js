const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');

// Rutas de pedidos
router.post('/', orderController.createOrder);
router.get('/user/:id_usuario', orderController.getOrdersByUser);
router.get('/order', orderController.getOrder); 


module.exports = router;