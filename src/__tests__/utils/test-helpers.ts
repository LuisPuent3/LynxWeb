/**
 * Utilidades para pruebas - Proyecto LYNX
 * Este archivo contiene funciones de ayuda que pueden ser compartidas entre diferentes pruebas.
 */

/**
 * Espera a que una condición se cumpla durante un tiempo determinado
 * @param condition Función que devuelve un booleano
 * @param timeout Tiempo máximo de espera en ms
 * @param interval Intervalo de tiempo entre comprobaciones
 * @returns Promise que se resuelve cuando la condición es true o se rechaza si se agota el tiempo
 */
export const waitForCondition = (
  condition: () => boolean, 
  timeout: number = 5000, 
  interval: number = 100
): Promise<void> => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const checkCondition = () => {
      if (condition()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error(`Timeout al esperar la condición después de ${timeout}ms`));
      } else {
        setTimeout(checkCondition, interval);
      }
    };
    
    checkCondition();
  });
};

/**
 * Formatea los resultados de las pruebas para la documentación
 * @param testName Nombre de la prueba
 * @param passed Indica si la prueba ha pasado
 * @param error Error en caso de fallar
 * @returns Texto formateado para la documentación
 */
export const formatTestResult = (
  testName: string, 
  passed: boolean, 
  error?: string
): string => {
  const timestamp = new Date().toISOString();
  const status = passed ? '✅ Pasado' : '❌ Fallido';
  
  let result = `### ${testName}\n\n`;
  result += `**Estado:** ${status}\n`;
  result += `**Fecha:** ${timestamp}\n`;
  
  if (!passed && error) {
    result += `**Error:** ${error}\n`;
  }
  
  return result;
};

/**
 * Mide el tiempo de ejecución de una función
 * @param fn Función a medir
 * @returns Resultado de la función y tiempo de ejecución en ms
 */
export const measureExecutionTime = async <T>(fn: () => Promise<T>): Promise<{result: T, time: number}> => {
  const start = performance.now();
  const result = await fn();
  const end = performance.now();
  
  return {
    result,
    time: parseFloat((end - start).toFixed(2))
  };
};

/**
 * Verifica si una respuesta contiene los encabezados CORS adecuados
 * @param headers Objeto de encabezados
 * @returns true si los encabezados CORS están configurados correctamente
 */
export const validateCorsHeaders = (headers: Record<string, any>): boolean => {
  const requiredHeaders = [
    'access-control-allow-origin',
    'access-control-allow-methods',
    'access-control-allow-headers'
  ];
  
  return requiredHeaders.every(header => 
    headers[header] !== undefined && headers[header] !== null && headers[header] !== '');
}; 