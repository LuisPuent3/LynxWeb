/**
 * Script para ejecutar automáticamente las pruebas del caso LYNX_010
 * y actualizar el archivo de documentación con los resultados.
 */
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Configuración para obtener el __dirname en ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuración
const TEST_FILE = 'ApiErrorHandling.test.ts';
const DOC_FILE = 'LYNX_010_ApiErrorHandling.md';
const TEST_CASE_ID = 'LYNX_010';

console.log(`=== Iniciando pruebas automatizadas para ${TEST_CASE_ID} ===`);

// Función para obtener la fecha actual en formato DD/MM/YYYY
function getCurrentDate() {
  const now = new Date();
  const day = String(now.getDate()).padStart(2, '0');
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const year = now.getFullYear();
  return `${day}/${month}/${year}`;
}

// Comprobar si los archivos existen
const testFilePath = path.join(__dirname, TEST_FILE);
const docFilePath = path.join(__dirname, DOC_FILE);

if (!fs.existsSync(testFilePath)) {
  console.error(`Error: El archivo de prueba ${TEST_FILE} no existe.`);
  process.exit(1);
}

if (!fs.existsSync(docFilePath)) {
  console.error(`Error: El archivo de documentación ${DOC_FILE} no existe.`);
  process.exit(1);
}

// Ejecutar las pruebas
let testResults = '';
let testPassed = false;

try {
  console.log(`Ejecutando pruebas de ${TEST_FILE}...`);
  // Ejecutar el comando de prueba y capturar la salida
  testResults = execSync(`npm run test -- ${TEST_FILE}`, { encoding: 'utf8' });
  console.log('Pruebas completadas con éxito.');
  testPassed = !testResults.includes('FAIL');
} catch (error) {
  console.error('Error al ejecutar las pruebas:', error.message);
  testResults = error.stdout || 'Error al ejecutar las pruebas.';
  testPassed = false;
}

// Leer el archivo de documentación
let docContent = fs.readFileSync(docFilePath, 'utf8');

// Actualizar la fecha de prueba
docContent = docContent.replace('[FECHA_ACTUAL]', getCurrentDate());

// Actualizar el estado de la prueba
const testStatus = testPassed ? 'Exitoso' : 'Fallido';
docContent = docContent.replace('[ESTADO_ACTUAL]', testStatus);

// Actualizar los resultados de las pruebas
docContent = docContent.replace(/```\n\[SE COMPLETARÁ AUTOMÁTICAMENTE CON RESULTADOS DE EJECUCIÓN\]\n```/, '```\n' + testResults + '```');

// Procesar los resultados para actualizar la tabla de pasos y resultados
const testSteps = [
  { name: 'ruta inexistente', statusCode: 404, expectedMessage: 'Ruta no encontrada', step: 1 },
  { name: 'producto inexistente', statusCode: 404, expectedMessage: 'Producto no encontrado', step: 2 },
  { name: 'autenticación requerida', statusCode: 401, expectedMessage: 'Se requiere autenticación', step: 3 },
  { name: 'token inválido', statusCode: 401, expectedMessage: 'Token inválido', step: 4 },
  { name: 'datos inválidos en POST', statusCode: 400, expectedMessage: 'Datos inválidos', step: 5 },
  { name: 'permisos insuficientes', statusCode: 403, expectedMessage: 'Acceso denegado', step: 6 }
];

// Verificar cada prueba en los resultados
testSteps.forEach(step => {
  const testName = `código ${step.statusCode} al`;
  const passed = testResults.includes(`Test de ${step.name} exitoso`);
  const result = passed 
    ? `Código ${step.statusCode} con mensaje "${step.expectedMessage}"` 
    : `Prueba fallida o no completada`;
  const status = passed ? 'Pasado' : 'Fallido';
  
  // Actualizar la tabla de resultados
  const stepRegex = new RegExp(`\\| ${step.step} \\| .+ \\| .+ \\| \\[COMPLETAR\\] \\| \\[COMPLETAR\\] \\|`);
  docContent = docContent.replace(stepRegex, `| ${step.step} | Enviar petición para probar ${step.name} | Código ${step.statusCode} con mensaje de error claro | ${result} | ${status} |`);
});

// Actualizar conclusiones y recomendaciones
if (testPassed) {
  docContent = docContent.replace('[COMPLETAR DESPUÉS DE LA EJECUCIÓN]', 'Todas las pruebas han sido exitosas. La API maneja correctamente los errores y devuelve los códigos HTTP apropiados con mensajes claros.');
  
  // Recomendaciones
  const recommendations = 'Mantener el sistema de manejo de errores actual y considerar implementar pruebas de integración reales para verificar el comportamiento con el backend.';
  docContent = docContent.replace('[COMPLETAR DESPUÉS DE LA EJECUCIÓN]', recommendations);
} else {
  docContent = docContent.replace('[COMPLETAR DESPUÉS DE LA EJECUCIÓN]', 'Algunas pruebas han fallado. Es necesario revisar el manejo de errores en la API para asegurar que todos los casos de error devuelvan los códigos HTTP apropiados con mensajes claros.');
  
  // Recomendaciones
  const recommendations = 'Revisar la implementación del manejo de errores en la API y asegurar que todos los endpoints manejen correctamente los casos de error. Ejecutar nuevamente las pruebas después de las correcciones.';
  docContent = docContent.replace('[COMPLETAR DESPUÉS DE LA EJECUCIÓN]', recommendations);
}

// Guardar los cambios en el archivo de documentación
fs.writeFileSync(docFilePath, docContent);

console.log(`El archivo de documentación ${DOC_FILE} ha sido actualizado con los resultados de las pruebas.`);
console.log(`=== Pruebas ${testPassed ? 'exitosas' : 'fallidas'} para ${TEST_CASE_ID} ===`); 