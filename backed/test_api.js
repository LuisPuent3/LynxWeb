// Script para probar la API de pedidos directamente

const http = require('http');

// Configuración de la solicitud
const options = {
  hostname: 'localhost',
  port: 5000,
  path: '/api/pedidos/usuario/19',
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  }
};

console.log(`Probando conexión a: http://${options.hostname}:${options.port}${options.path}`);

// Realizar la solicitud
const req = http.request(options, (res) => {
  console.log(`Código de estado: ${res.statusCode}`);
  console.log('Encabezados:', res.headers);
  
  let data = '';
  
  // Un fragmento de datos se ha recibido
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  // La respuesta completa se ha recibido
  res.on('end', () => {
    console.log('Respuesta del servidor:');
    try {
      const parsedData = JSON.parse(data);
      console.log(JSON.stringify(parsedData, null, 2));
    } catch (e) {
      console.log('Datos sin formato:', data);
    }
  });
});

// Manejar errores de red
req.on('error', (e) => {
  console.error(`Problema con la solicitud: ${e.message}`);
  
  // Intentar probar la ruta de prueba
  const testOptions = { ...options, path: '/api/test' };
  console.log(`\nProbando ruta alternativa: http://${testOptions.hostname}:${testOptions.port}${testOptions.path}`);
  
  const testReq = http.request(testOptions, (testRes) => {
    console.log(`Código de estado: ${testRes.statusCode}`);
    let testData = '';
    testRes.on('data', (chunk) => { testData += chunk; });
    testRes.on('end', () => {
      console.log('Respuesta del servidor:');
      try {
        console.log(JSON.parse(testData));
      } catch (e) {
        console.log(testData);
      }
    });
  });
  
  testReq.on('error', (testErr) => {
    console.error(`Prueba alternativa fallida: ${testErr.message}`);
    console.log('El servidor backend parece no estar en ejecución. Inicie el servidor con "npm start" en la carpeta "backed".');
  });
  
  testReq.end();
});

// Enviar la solicitud
req.end();

console.log('Solicitud enviada, esperando respuesta...');