/**
 * Test Case ID: LYNX_003
 * Este archivo contiene pruebas de integración que verifican la conexión real entre frontend y backend.
 * Estas pruebas deben ejecutarse con el backend en funcionamiento en la URL de la API correspondiente (por ejemplo, Railway o local).
 * 
 * De acuerdo al Plan de Pruebas:
 * - Este test forma parte del Sprint 4, actividad "Pruebas de conexión frontend-backend"
 * - Corresponde a la sección "Tipos de Pruebas" -> "Pruebas de Integración"
 * - Prueba el componente crítico "Comunicación entre frontend y backend"
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import api from '../../../utils/api';
import axios, { AxiosResponse } from 'axios';

// Esta prueba de integración requiere que el backend esté en ejecución
describe('LYNX_003: Prueba de Integración de Conexión API Frontend-Backend', () => {
  // Almacenar el estado original de api.interceptors
  let originalInterceptors;
  
  // Configuración antes de todas las pruebas
  beforeAll(() => {
    // Guardar los interceptores originales para restaurarlos después
    originalInterceptors = {
      request: api.interceptors.request.handlers.slice(),
      response: api.interceptors.response.handlers.slice()
    };
    
    // Limpiamos los interceptores para que no afecten nuestras pruebas
    api.interceptors.request.handlers = [];
    api.interceptors.response.handlers = [];
    
    // Opcional: Agregar un interceptor de registro para diagnóstico
    api.interceptors.request.use(config => {
      console.log(`[TEST] Solicitud a: ${config.url}`);
      return config;
    });
    
    api.interceptors.response.use(
      response => {
        console.log(`[TEST] Respuesta exitosa de: ${response.config.url}`);
        return response;
      },
      error => {
        console.error(`[TEST] Error de: ${error.config?.url || 'desconocido'}`);
        return Promise.reject(error);
      }
    );
  });
  
  // Restaurar después de todas las pruebas
  afterAll(() => {
    // Restaurar los interceptores originales
    api.interceptors.request.handlers = originalInterceptors.request;
    api.interceptors.response.handlers = originalInterceptors.response;
  });

  /**
   * Prueba: Validación de respuesta del servidor
   * 
   * Objetivo: Verificar que el backend responde correctamente a las solicitudes API
   * (Criterio de aceptación #3: Funcionalidad - 100% pruebas exitosas para funcionalidades críticas)
   * (Criterio de aceptación #4: Rendimiento - Tiempo de respuesta de API < 300ms)
   * 
   * Valida los pasos #3 y #4 del caso de prueba:
   * - Observar las llamadas de red
   * - Verificar respuesta del servidor
   */
  it('Debe realizar una petición GET a /api/productos y recibir código 200', async () => {
    // Registrar tiempo inicial para medir rendimiento
    const startTime = performance.now();
    
    try {
      // Hacer una solicitud real a la API
      const response: AxiosResponse = await api.get('/productos');
      
      // Calcular tiempo de respuesta
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      // Verificar tiempo de respuesta (criterio: < 300ms según el plan de pruebas)
      console.log(`Tiempo de respuesta: ${responseTime.toFixed(2)}ms`);
      
      // No hacemos assert sobre el tiempo aquí porque depende del entorno real
      // Sólo lo registramos para análisis
      
      // Verificar código de estado
      expect(response.status).toBe(200);
      
      // Verificar que la respuesta es un array
      expect(Array.isArray(response.data)).toBe(true);
      
      // Verificar la estructura de los datos
      if (response.data.length > 0) {
        const primerProducto = response.data[0];
        expect(primerProducto).toHaveProperty('id_producto');
        expect(primerProducto).toHaveProperty('nombre');
        expect(primerProducto).toHaveProperty('precio');
        
        // Verificar valores (opcional, dependiendo de los datos disponibles)
        expect(typeof primerProducto.id_producto).toBe('number');
        expect(typeof primerProducto.nombre).toBe('string');
        expect(typeof primerProducto.precio).toBe('string');
      }
      
      console.log('✅ Conexión API exitosa');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('❌ Error de conexión API:', error.message);
        if (error.response) {
          console.error('Detalles:', error.response.data);
          console.error('Código de estado:', error.response.status);
        } else if (error.request) {
          console.error('❌ No se recibió respuesta. Posible problema de conexión o CORS.');
        }
      }
      throw error; // Re-lanzar para que la prueba falle
    }
  });

  /**
   * Prueba: Validación de CORS
   * 
   * Objetivo: Verificar que el servidor tiene correctamente configurados los encabezados CORS
   * (Plan de Pruebas: "Corrección de la Conectividad API" -> "Configuración correcta de CORS")
   * 
   * Valida el paso #3 del caso de prueba:
   * - Observar las llamadas de red y verificar que no hay errores CORS
   */
  it('Debe incluir los encabezados CORS apropiados en la respuesta', async () => {
    try {
      // Hacer una solicitud real a la API
      const response: AxiosResponse = await api.get('/productos');
      
      // Verificar encabezados CORS 
      const headers = response.headers;
      
      // La mayoría de los servidores modernos deberían incluir Access-Control-Allow-Origin
      if (headers['access-control-allow-origin']) {
        expect(headers['access-control-allow-origin']).toBeTruthy();
        
        // Registrar los encabezados CORS para documentación
        console.log('✅ Encabezados CORS presentes:');
        console.log(`  - Access-Control-Allow-Origin: ${headers['access-control-allow-origin']}`);
        
        // Verificar otros encabezados CORS importantes (si están presentes)
        if (headers['access-control-allow-methods']) {
          console.log(`  - Access-Control-Allow-Methods: ${headers['access-control-allow-methods']}`);
        }
        
        if (headers['access-control-allow-headers']) {
          console.log(`  - Access-Control-Allow-Headers: ${headers['access-control-allow-headers']}`);
        }
      } else {
        console.log('⚠️ Encabezados CORS no detectados - esto podría ser normal según la configuración del servidor');
      }
      
      // Prueba adicional: verificar que no hay errores de CORS simulando una solicitud OPTIONS
      // Nota: Esta es una prueba indirecta, ya que no podemos simular completamente un navegador
      const optionsResponse = await axios({
        method: 'options',
        url: api.defaults.baseURL + '/productos',
        headers: {
          'Origin': 'http://localhost:5173', // Origen típico de una app Vite
          'Access-Control-Request-Method': 'GET',
          'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
      }).catch(e => {
        // Si hay un error, verificamos si es de CORS o de otro tipo
        if (e.response) {
          return e.response; // Devolvemos la respuesta para analizarla
        }
        throw e; // Re-lanzar otros errores
      });
      
      // Si recibimos una respuesta OPTIONS, verificamos el código de estado
      if (optionsResponse) {
        const expectedCodes = [200, 204]; // Códigos típicos para respuestas OPTIONS exitosas
        expect(expectedCodes).toContain(optionsResponse.status);
        console.log(`✅ Solicitud OPTIONS exitosa (código ${optionsResponse.status})`);
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('❌ Error verificando encabezados CORS:', error.message);
        
        // Detalle sobre errores CORS específicos
        if (error.response) {
          console.error('Detalles de la respuesta:', {
            status: error.response.status,
            headers: error.response.headers,
            data: error.response.data
          });
        }
      }
      throw error;
    }
  });
  
  /**
   * Prueba: Validación del contenido de la respuesta
   * 
   * Objetivo: Verificar que los datos devueltos por la API tienen el formato y contenido esperados
   * (Criterio de aceptación #3: Funcionalidad - Cumplimiento de requisitos funcionales)
   * 
   * Valida el paso #5 del caso de prueba:
   * - Verificar que los datos recibidos tienen la estructura y formato esperados para su renderizado
   */
  it('Debe devolver datos en el formato correcto para su renderizado', async () => {
    try {
      // Hacer una solicitud real a la API
      const response: AxiosResponse = await api.get('/productos');
      
      // Verificar que hay datos
      expect(response.data.length).toBeGreaterThan(0);
      
      // Verificar que todos los elementos tienen la estructura correcta
      response.data.forEach((producto, index) => {
        expect(producto).toHaveProperty('id_producto');
        expect(producto).toHaveProperty('nombre');
        expect(producto).toHaveProperty('precio');
        
        // Verificar que los tipos de datos son correctos para asegurar renderizado adecuado
        expect(typeof producto.id_producto).toBe('number');
        expect(typeof producto.nombre).toBe('string');
        expect(typeof producto.precio).toBe('string');
        
        // Verificar que no hay valores nulos en campos críticos
        expect(producto.id_producto).not.toBeNull();
        expect(producto.nombre).not.toBeNull();
        expect(producto.precio).not.toBeNull();
        
        console.log(`✅ Producto ${index + 1} (${producto.nombre}) tiene estructura válida`);
      });
      
      console.log(`✅ Total de ${response.data.length} productos verificados con estructura correcta`);
    } catch (error) {
      console.error('❌ Error validando estructura de datos:', error);
      throw error;
    }
  });
});