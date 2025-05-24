// Ruta de diagnóstico para el sistema de recuperación de contraseña
exports.diagnostico = async (req, res) => {
  try {
    // Validar conexión a la base de datos
    const pool = require('../config/db');
    let dbStatus = "Sin probar";
    
    try {
      const [result] = await pool.query('SELECT 1 as test');
      dbStatus = (result && result[0] && result[0].test === 1) ? "Conectada" : "Error en consulta";
    } catch (dbError) {
      dbStatus = `Error: ${dbError.message}`;
    }

    // Validar configuración de correo
    let emailConfig = {
      host: process.env.EMAIL_HOST || '(no configurado)',
      port: process.env.EMAIL_PORT || '(no configurado)',
      secure: process.env.EMAIL_SECURE || '(no configurado)',
      user: process.env.EMAIL_USER ? 'Configurado' : 'No configurado',
      pass: process.env.EMAIL_PASS ? 'Configurado' : 'No configurado',
      testMode: true // El modo de prueba está activado
    };

    // Validar configuración JWT
    let jwtConfig = {
      secret: process.env.JWT_SECRET ? 'Configurado' : 'No configurado (usando valor por defecto)',
      expiresIn: process.env.JWT_EXPIRES_IN || '10m (valor por defecto para recuperación)'
    };

    // Validar ruta del frontend
    let frontendUrl = process.env.FRONTEND_URL || 'http://localhost:5173';

    // Responder con información de diagnóstico
    res.status(200).json({
      status: "Funcionando",
      timestamp: new Date().toISOString(),
      database: {
        status: dbStatus,
        host: process.env.DB_HOST,
        user: process.env.DB_USER,
        database: process.env.DB_NAME
      },
      email: emailConfig,
      jwt: jwtConfig,
      frontend: frontendUrl
    });
  } catch (error) {
    console.error('Error en diagnóstico:', error);
    res.status(500).json({
      status: "Error",
      error: error.message,
      stack: process.env.NODE_ENV === 'production' ? null : error.stack
    });
  }
};
