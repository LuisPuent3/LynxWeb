const express = require('express');
const cartController = require('../controllers/cartController');

const router = express.Router();

router.get('/:id_usuario', cartController.getCart); // Obtener carrito de usuario
router.post('/', cartController.addToCart); // Agregar al carrito
router.delete('/:id', cartController.removeFromCart); // Eliminar producto del carrito

module.exports = router;
