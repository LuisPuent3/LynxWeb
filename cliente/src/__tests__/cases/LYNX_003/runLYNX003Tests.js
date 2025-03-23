/**
 * Script para ejecutar las pruebas del caso LYNX_003 y documentar los resultados
 * Parte del Plan de Pruebas del Proyecto LYNX
 * 
 * Uso: 
 * - Asegúrate de tener el backend en ejecución en http://localhost:5000
 * - Ejecuta: node runLYNX003Tests.js > test_results.txt
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuración
const TEST_CASE_ID = 'LYNX_003';
const TEST_FILES = [
  'ApiConnection.test.tsx',
  'ApiConnectionIntegration.test.tsx'
];
const RESULT_TEMPLATE = 'LYNX_003_TestManualResults.md';
const RESULT_OUTPUT = 'LYNX_003_TestResults.md';

// Función para ejecutar pruebas y capturar salida
function runTest(testFile) {
  console.log(`\n[RUNNING] ${testFile}`);
  console.log('='.repeat(80));
  
  try {
    // Ejecutar la prueba y capturar la salida
    const output = execSync(`npm run test -- ${testFile}`, { 
      encoding: 'utf8',
      stdio: 'pipe' 
    });
    
    console.log(output);
    return { success: true, output };
  } catch (error) {
    console.error(`Error ejecutando ${testFile}:`);
    console.error(error.message);
    
    if (error.stdout) {
      console.log('\nOutput de la prueba:');
      console.log(error.stdout);
    }
    
    return { success: false, output: error.stdout || error.message };
  }
}

// Función para verificar si el backend está en ejecución
function checkBackendConnection() {
  console.log('\n[CHECKING] Conexión con el backend');
  console.log('='.repeat(80));
  
  try {
    // Intentar hacer una solicitud simple al backend
    const axios = require('axios');
    const response = axios.get('http://localhost:5000/api/productos', { timeout: 5000 });
    console.log('✅ Backend conectado correctamente');
    return true;
  } catch (error) {
    console.error('❌ No se pudo conectar con el backend');
    console.error('Por favor, asegúrate de que el servidor backend está en ejecución en http://localhost:5000');
    console.error('Error:', error.message);
    return false;
  }
}

// Función para actualizar el archivo de resultados
function updateResultsFile(testResults) {
  console.log('\n[UPDATING] Archivo de resultados');
  console.log('='.repeat(80));
  
  try {
    // Leer la plantilla
    const templatePath = path.join(__dirname, RESULT_TEMPLATE);
    const outputPath = path.join(__dirname, RESULT_OUTPUT);
    
    if (!fs.existsSync(templatePath)) {
      console.error(`❌ No se encontró la plantilla en ${templatePath}`);
      return false;
    }
    
    let template = fs.readFileSync(templatePath, 'utf8');
    
    // Actualizar fecha de ejecución
    const currentDate = new Date().toISOString().split('T')[0];
    template = template.replace('**Fecha Ejecución Automatizada**: [PENDIENTE]', 
                              `**Fecha Ejecución Automatizada**: ${currentDate}`);
    
    // Actualizar resultados de pruebas unitarias
    if (testResults.ApiConnection) {
      // Simplificar: consideramos éxito si no hay error en la ejecución
      const unitResult = testResults.ApiConnection.success ? 'PASÓ' : 'FALLÓ';
      template = template.replace(/\| 1 \| Petición GET correcta \| \[PENDIENTE\] \|/g, 
                               `| 1 | Petición GET correcta | ${unitResult} |`);
      template = template.replace(/\| 2 \| Manejo de errores \| \[PENDIENTE\] \|/g, 
                               `| 2 | Manejo de errores | ${unitResult} |`);
      template = template.replace(/\| 3 \| Tiempo de respuesta \| \[PENDIENTE\] \|/g, 
                               `| 3 | Tiempo de respuesta | ${unitResult} |`);
    }
    
    // Actualizar resultados de pruebas de integración
    if (testResults.ApiConnectionIntegration) {
      const integResult = testResults.ApiConnectionIntegration.success ? 'PASÓ' : 'FALLÓ';
      template = template.replace(/\| 1 \| Respuesta del servidor \(código 200\) \| \[PENDIENTE\] \|/g, 
                               `| 1 | Respuesta del servidor (código 200) | ${integResult} |`);
      template = template.replace(/\| 2 \| Validación de CORS \| \[PENDIENTE\] \|/g, 
                               `| 2 | Validación de CORS | ${integResult} |`);
      template = template.replace(/\| 3 \| Formato de datos \| \[PENDIENTE\] \|/g, 
                               `| 3 | Formato de datos | ${integResult} |`);
    }
    
    // Actualizar salida de pruebas
    if (testResults.ApiConnection) {
      template = template.replace('[PEGAR AQUÍ EL OUTPUT DE LAS PRUEBAS UNITARIAS]', 
                             testResults.ApiConnection.output.trim());
    }
    
    if (testResults.ApiConnectionIntegration) {
      template = template.replace('[PEGAR AQUÍ EL OUTPUT DE LAS PRUEBAS DE INTEGRACIÓN]', 
                             testResults.ApiConnectionIntegration.output.trim());
    }
    
    // Escribe el archivo actualizado
    fs.writeFileSync(outputPath, template);
    console.log(`✅ Resultados actualizados en ${outputPath}`);
    return true;
  } catch (error) {
    console.error('❌ Error actualizando el archivo de resultados');
    console.error(error);
    return false;
  }
}

// Función principal
async function main() {
  console.log('='.repeat(80));
  console.log(`EJECUTANDO PRUEBAS PARA CASO ${TEST_CASE_ID}`);
  console.log(`Fecha: ${new Date().toISOString()}`);
  console.log(`Sistema: ${os.type()} ${os.release()}`);
  console.log('='.repeat(80));
  
  // Verificar backend
  const backendConnected = checkBackendConnection();
  
  // Resultados de pruebas
  const testResults = {};
  
  // Ejecutar pruebas
  for (const testFile of TEST_FILES) {
    // Si es la prueba de integración y no hay backend, saltarla
    if (testFile.includes('Integration') && !backendConnected) {
      console.log(`\n[SKIPPING] ${testFile} - No hay conexión con el backend`);
      continue;
    }
    
    // Ejecutar la prueba
    const result = runTest(testFile);
    
    // Guardar resultado
    const testName = testFile.replace('.test.tsx', '');
    testResults[testName] = result;
  }
  
  // Actualizar archivo de resultados
  updateResultsFile(testResults);
  
  // Resumen
  console.log('\n[SUMMARY] Resumen de ejecución');
  console.log('='.repeat(80));
  for (const [test, result] of Object.entries(testResults)) {
    console.log(`${test}: ${result.success ? '✅ PASSED' : '❌ FAILED'}`);
  }
}

// Ejecutar
main().catch(error => {
  console.error('Error no controlado:');
  console.error(error);
  process.exit(1);
}); 