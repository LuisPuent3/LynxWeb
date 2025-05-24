/**
 * Script para probar el sistema de recuperación de contraseña
 * 
 * Este script realiza pruebas básicas de las rutas de recuperación de contraseña
 * para asegurarse de que todo funcione correctamente.
 */
import axios from 'axios';

// API URL
const API_URL = 'http://localhost:5000/api';

// Colores para la consola
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

// Función para imprimir con colores
const print = {
  info: (msg) => console.log(`${colors.blue}[INFO]${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}[ÉXITO]${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}[ERROR]${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}[AVISO]${colors.reset} ${msg}`),
  title: (msg) => console.log(`\n${colors.cyan}=== ${msg} ===${colors.reset}\n`)
};

// Función para probar el endpoint de diagnóstico
async function testDiagnostico() {
  print.title('Prueba de Diagnóstico');
  try {
    print.info('Solicitando diagnóstico del sistema de recuperación...');
    const response = await axios.get(`${API_URL}/password-reset/diagnostico`);
    
    print.success('Diagnóstico completado');
    console.log(JSON.stringify(response.data, null, 2));
    
    // Verificar el estado de la base de datos
    if (response.data.database.status === 'Conectada') {
      print.success('Conexión a la base de datos: OK');
    } else {
      print.error(`Conexión a la base de datos: FALLO - ${response.data.database.status}`);
    }
    
    // Verificar configuración de correo
    if (response.data.email.user === 'Configurado' && response.data.email.pass === 'Configurado') {
      print.success('Configuración de correo: OK');
    } else {
      print.warning('Configuración de correo incompleta. El correo no se enviará correctamente.');
      print.warning(`Host: ${response.data.email.host}, Puerto: ${response.data.email.port}`);
      print.warning(`Usuario: ${response.data.email.user}, Contraseña: ${response.data.email.pass}`);
    }
    
    // Verificar configuración JWT
    if (response.data.jwt.secret === 'Configurado') {
      print.success('Configuración JWT: OK');
    } else {
      print.warning('Secreto JWT no configurado. Se está usando un valor por defecto.');
    }
    
    return true;
  } catch (error) {
    print.error(`Error en la prueba de diagnóstico: ${error.message}`);
    if (error.response) {
      print.error(`Estado: ${error.response.status}`);
      print.error(`Datos: ${JSON.stringify(error.response.data)}`);
    }
    return false;
  }
}

// Función para probar el endpoint de solicitud de recuperación
async function testRequest() {
  print.title('Prueba de Solicitud de Recuperación');
  try {
    const testEmail = 'test@example.com';
    print.info(`Solicitando recuperación para correo: ${testEmail}`);
    
    const response = await axios.post(`${API_URL}/password-reset/request`, {
      correo: testEmail
    });
    
    print.success('Solicitud enviada correctamente');
    console.log(JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    print.error(`Error en la prueba de solicitud: ${error.message}`);
    if (error.response) {
      print.error(`Estado: ${error.response.status}`);
      print.error(`Datos: ${JSON.stringify(error.response.data)}`);
    }
    return false;
  }
}

// Función principal para ejecutar todas las pruebas
async function runTests() {
  print.title('PRUEBAS DEL SISTEMA DE RECUPERACIÓN DE CONTRASEÑA');
  
  // Prueba 1: Diagnóstico
  const diagResult = await testDiagnostico();
  
  // Prueba 2: Solicitud de recuperación (solo si el diagnóstico es exitoso)
  if (diagResult) {
    await testRequest();
  }
  
  print.title('FIN DE LAS PRUEBAS');
}

// Ejecutar las pruebas
runTests();
