const express = require('express');
const router = express.Router();
const passwordResetController = require('../controllers/passwordResetController');
const diagnosticoController = require('../controllers/diagnosticoController');

// Ruta de prueba para verificar que el controlador está cargado
router.get('/test', (req, res) => {
  res.status(200).json({
    message: 'El sistema de recuperación de contraseña está funcionando correctamente',
    timestamp: new Date().toISOString()
  });
});

// Ruta de diagnóstico para verificar configuración y conexiones
router.get('/diagnostico', diagnosticoController.diagnostico);

// Ruta para solicitar recuperación de contraseña
router.post('/request', passwordResetController.requestPasswordReset);

// Ruta para restablecer contraseña con token
router.post('/reset', passwordResetController.resetPassword);

module.exports = router;
