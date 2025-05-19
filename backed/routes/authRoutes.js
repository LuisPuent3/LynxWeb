const express = require('express');
const router = express.Router();
const { registerUser, loginUser, verifyToken, getAllUsers, getUserPhone } = require('../controllers/authController');
const { verifyToken: authMiddleware, verifyRole } = require('../middlewares/authMiddleware');

// Registro de usuario
router.post('/register', registerUser);

// Login de usuario
router.post('/login', loginUser);

// Verificar token y obtener información del usuario
router.get('/verify', authMiddleware, verifyToken);

// Rutas solo para administradores
router.get('/users', authMiddleware, verifyRole(['Administrador']), getAllUsers);

// Obtener teléfono de un usuario específico (accesible públicamente)
router.get('/telefono/:id', getUserPhone);

module.exports = router;