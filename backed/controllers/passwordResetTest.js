// Test route for password reset controller
exports.testRoute = (req, res) => {
  res.status(200).json({
    success: true,
    message: 'El controlador de recuperación de contraseña está funcionando correctamente'
  });
};
