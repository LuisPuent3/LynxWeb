const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const nodemailer = require('nodemailer');
const pool = require('../config/db');

// Configuración del transportador de correo
let transporter;

// Modo de prueba (omite el envío real de correos)
const TEST_MODE = true;

if (TEST_MODE) {
  console.log("⚠️ Sistema de correo en MODO PRUEBA - No se enviarán correos reales");
    // Configuración para modo de prueba (no envía correos reales)
  transporter = {
    sendMail: async (mailOptions) => {
      console.log("✉️ SIMULANDO ENVÍO DE CORREO:");
      console.log("→ Para:", mailOptions.to);
      console.log("→ Asunto:", mailOptions.subject);
      
      // Extraer enlace de forma segura
      let enlace = "No se pudo extraer el enlace";
      try {
        const match = mailOptions.html.match(/href="([^"]+)"/);
        if (match && match.length > 1) {
          enlace = match[1];
        }
      } catch (err) {
        console.error("Error al extraer enlace del correo:", err);
      }
      console.log("→ Enlace:", enlace);
      
      return { messageId: 'test-message-id' };
    }
  };
} else {
  // Configuración normal para envío real de correos
  transporter = nodemailer.createTransport({
    host: process.env.EMAIL_HOST || 'smtp.hostinger.com',
    port: process.env.EMAIL_PORT || 465,
    secure: process.env.EMAIL_SECURE !== 'false', // true por defecto para el puerto 465
    auth: {
      user: process.env.EMAIL_USER || 'soporte@lynxshop.com',
      pass: process.env.EMAIL_PASS || 'claveSegura2024'
    }
  });
}

// Función para solicitar restablecimiento de contraseña
exports.requestPasswordReset = async (req, res) => {
  try {
    const { correo } = req.body;
      // Verificar que el correo exista en la base de datos    console.log("Buscando usuario con correo:", correo);
    
    let user;    try {
      console.log("Ejecutando consulta SQL para verificar si existe el correo:", correo);
      
      // Primero verificamos si la tabla Usuarios existe y tiene la estructura esperada
      const [tables] = await pool.query(`
        SHOW TABLES LIKE 'Usuarios'
      `);
      
      if (tables.length === 0) {
        console.error("La tabla Usuarios no existe en la base de datos");
        throw new Error("Estructura de base de datos incorrecta: tabla Usuarios no encontrada");
      }
      
      console.log("Tabla Usuarios encontrada, verificando columnas...");
      
      // Comprobamos la estructura de las tablas
      const [columns] = await pool.query(`
        SHOW COLUMNS FROM Usuarios
      `);
      
      console.log("Columnas en tabla Usuarios:", columns.map(c => c.Field));
      
      // Realizamos la consulta
      console.log("Buscando usuario con correo:", correo);
        // Primero intentamos la versión con join
      try {
        [user] = await pool.query(`
          SELECT u.id_usuario, u.correo, n.nombre
          FROM Usuarios u
          LEFT JOIN Nombres n ON u.id_nombre = n.id_nombre
          WHERE u.correo = ?
        `, [correo]);
      } catch (joinError) {
        console.error("Error en consulta con JOIN, intentando versión simple:", joinError);
        
        // Si hay problemas con el JOIN, hacemos una consulta más simple
        [user] = await pool.query(`
          SELECT id_usuario, correo, id_nombre
          FROM Usuarios
          WHERE correo = ?
        `, [correo]);
          // Si encontramos el usuario pero no tenemos su nombre, lo dejamos como null
        if (user) {
          if (user.length > 0) {
            user[0].nombre = null;
          }
        }
      }
        console.log("Resultado de la consulta:", user);
      
      if (!user) {
        console.log("No se obtuvo resultado en la consulta para el correo:", correo);
        return res.status(200).json({ 
          success: true, 
          message: 'Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña.' 
        });
      }
      
      if (user.length === 0) {
        // Por seguridad, no revelar si el correo existe o no
        console.log("Usuario no encontrado con el correo:", correo);
        return res.status(200).json({ 
          success: true, 
          message: 'Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña.' 
        });
      }
    } catch (queryError) {
      console.error("Error en la consulta SQL:", queryError);
      throw queryError; // Relanzar para que lo capture el try/catch principal
    }
    
    const usuario = user[0];
    
    // Generar token JWT con expiración corta (10 minutos)
    const token = jwt.sign(
      { id: usuario.id_usuario, tipo: 'recuperacion' }, // incluimos el tipo para diferenciar
      process.env.JWT_SECRET || 'secreto_temporal',
      { expiresIn: '10m' } // Token válido por 10 minutos
    );
      // URL del frontend para restablecer contraseña
    const resetUrl = `${process.env.FRONTEND_URL || 'http://localhost:5173'}/reset-password/${token}`;
    
    console.log("URL de restablecimiento generada:", resetUrl);
    
    // Preparar correo
    const mailOptions = {
      from: process.env.EMAIL_USER || 'soporte@lynxshop.com',
      to: correo,
      subject: 'Recuperación de contraseña - LynxShop',
      html: `
        <h1>Recuperación de Contraseña</h1>
        <p>Hola ${usuario.nombre || 'Usuario'}:</p>
        <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
        <p><a href="${resetUrl}" style="padding: 10px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a></p>
        <p>Este enlace es válido por 10 minutos.</p>
        <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.</p>
        <p>Saludos,<br/>Equipo de LynxShop</p>
      `
    };
    
    // Enviar correo
    await transporter.sendMail(mailOptions);
    
    // Responder al cliente
    res.status(200).json({
      success: true,
      message: 'Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña.'
    });
      } catch (error) {
    console.error('Error al solicitar recuperación de contraseña:', error);
    console.error('Stack trace:', error.stack);
    
    // Proporcionar información detallada sobre el error (solo en desarrollo)
    let errorDetail = {};
    let statusCode = 500;
    let errorMessage = 'Hubo un problema al procesar tu solicitud. Intenta nuevamente más tarde.';
    
    // Errores específicos de SQL
    if (error.code === 'ER_NO_SUCH_TABLE') {
      errorMessage = 'Error de base de datos: La tabla consultada no existe.';
      console.error('Error de tabla no existente:', error.sqlMessage);
    } else if (error.code === 'ER_BAD_FIELD_ERROR') {
      errorMessage = 'Error de base de datos: Campo no encontrado en la tabla.';
      console.error('Error de campo no encontrado:', error.sqlMessage);
    }
    
    if (process.env.NODE_ENV !== 'production') {
      errorDetail = {
        message: error.message,
        name: error.name,
        code: error.code,
        sqlMessage: error.sqlMessage,
        stack: error.stack
      };
    }
    
    res.status(statusCode).json({ 
      error: 'Error al procesar la solicitud',
      mensaje: errorMessage,
      detail: errorDetail
    });
  }
};

// Función para verificar token y restablecer contraseña
exports.resetPassword = async (req, res) => {
  try {
    const { token, nuevaContraseña } = req.body;
    
    // Verificar que el token sea válido
    let decodedToken;
    try {
      decodedToken = jwt.verify(token, process.env.JWT_SECRET || 'secreto_temporal');
    } catch (error) {
      if (error.name === 'TokenExpiredError') {
        return res.status(401).json({ error: 'El enlace ha expirado. Solicita un nuevo restablecimiento.' });
      }
      return res.status(401).json({ error: 'Token inválido. Solicita un nuevo restablecimiento.' });
    }
    
    // Verificar que el token sea del tipo correcto
    if (decodedToken.tipo !== 'recuperacion') {
      return res.status(401).json({ error: 'Token inválido para esta operación.' });
    }
    
    // Obtener el ID de usuario del token
    const userId = decodedToken.id;
    
    // Hash de la nueva contraseña
    const hashedPassword = await bcrypt.hash(nuevaContraseña, 10);
    
    // Actualizar contraseña en la base de datos
    await pool.query('UPDATE Usuarios SET contraseña = ? WHERE id_usuario = ?', [hashedPassword, userId]);
    
    // Responder al cliente
    res.status(200).json({
      success: true,
      message: 'Contraseña actualizada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
    });
    
  } catch (error) {
    console.error('Error al restablecer contraseña:', error);
    res.status(500).json({ 
      error: 'Error al restablecer contraseña',
      mensaje: 'Hubo un problema al actualizar tu contraseña. Intenta nuevamente más tarde.'
    });
  }
};
