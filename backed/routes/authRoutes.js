const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const { verifyToken } = require('../middlewares/authMiddleware');

// Registro de usuario
router.post('/register', authController.registerUser);

// Login de usuario
router.post('/login', authController.loginUser);

// Verificar token y obtener información del usuario
router.get('/verify', verifyToken, authController.verifyToken);

module.exports = router;