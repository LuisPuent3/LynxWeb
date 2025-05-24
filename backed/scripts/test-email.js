// Script para probar el envío de correos electrónicos
require('dotenv').config();
const nodemailer = require('nodemailer');

// Configuración del transportador
const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST || 'smtp.hostinger.com',
  port: process.env.EMAIL_PORT || 465,
  secure: process.env.EMAIL_SECURE !== 'false',
  auth: {
    user: process.env.EMAIL_USER || 'soporte@lynxshop.com',
    pass: process.env.EMAIL_PASS || 'claveSegura2024'
  }
});

// Dirección de correo para pruebas (reemplazar con un correo real para pruebas)
const testEmail = 'destinatario@example.com';

// Función para enviar un correo de prueba
async function sendTestEmail() {
  try {
    console.log('Intentando enviar correo de prueba...');
    console.log('Configuración:', {
      host: process.env.EMAIL_HOST,
      port: process.env.EMAIL_PORT,
      secure: process.env.EMAIL_SECURE !== 'false',
      user: process.env.EMAIL_USER
    });
    
    const info = await transporter.sendMail({
      from: process.env.EMAIL_USER || 'soporte@lynxshop.com',
      to: testEmail,
      subject: 'Prueba de recuperación de contraseña - LynxShop',
      html: `
        <h1>Prueba de envío de correo</h1>
        <p>Este es un correo de prueba para verificar la configuración del sistema de recuperación de contraseñas.</p>
        <p>Si estás recibiendo este correo, la configuración SMTP es correcta.</p>
        <p><a href="#" style="padding: 10px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Este sería el botón de recuperación</a></p>
        <p>Saludos,<br/>Equipo de LynxShop</p>
      `
    });
    
    console.log('Correo enviado correctamente!');
    console.log('ID del mensaje:', info.messageId);
  } catch (error) {
    console.error('Error al enviar el correo:', error);
    
    // Mostrar información más detallada sobre el error
    if (error.code === 'EAUTH') {
      console.error('Error de autenticación. Verifica tu usuario y contraseña.');
    } else if (error.code === 'ESOCKET') {
      console.error('Error de conexión. Verifica el host y puerto del servidor SMTP.');
    }
  }
}

// Ejecutar la función
sendTestEmail();
