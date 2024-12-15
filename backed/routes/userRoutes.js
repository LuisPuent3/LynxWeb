const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

// Obtener todos los usuarios (solo para administradores)
router.get('/', userController.getAllUsers);

// Obtener un usuario específico
router.get('/:id', userController.getUserById);

module.exports = router;
