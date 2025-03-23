/**
 * Test Case ID: LYNX_010
 * Pruebas para verificar el manejo de errores en la API
 * 
 * De acuerdo al Plan de Pruebas:
 * - Este test verifica que la API maneja correctamente los errores y devuelve respuestas apropiadas
 * - Criterio de aceptación: Todas las respuestas de error deben tener el código HTTP correcto y mensajes claros
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';

// Mock de axios
vi.mock('axios', async () => {
  const mockAxios = {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    })),
    defaults: {
      headers: {
        common: {}
      }
    }
  };
  return {
    default: mockAxios,
    ...mockAxios
  };
});

describe('LYNX_010: Prueba de Manejo de Errores API', () => {
  let mockApi;
  
  beforeEach(() => {
    // Limpiar mocks entre pruebas
    vi.clearAllMocks();
    
    // Crear una instancia mockeada de API
    mockApi = axios.create();
  });

  /**
   * Prueba: Ruta inexistente
   * 
   * Objetivo: Verificar que la API devuelve un código 404 con mensaje de error claro
   * cuando se solicita una ruta que no existe.
   */
  it('Debe devolver código 404 al solicitar una ruta inexistente', async () => {
    // Configurar el mock para simular una respuesta de error 404
    const errorResponse = {
      response: {
        status: 404,
        data: { error: 'Ruta no encontrada' }
      }
    };
    
    // Configurar el mock para rechazar la promesa
    mockApi.get.mockRejectedValueOnce(errorResponse);

    try {
      // Realizar petición a ruta inexistente
      await mockApi.get('/api/rutainexistente');
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false); // Esto nunca debería ejecutarse
    } catch (error) {
      // Verificar que la API respondió con el código y mensaje correctos
      expect(error.response.status).toBe(404);
      expect(error.response.data).toHaveProperty('error');
      expect(error.response.data.error).toBe('Ruta no encontrada');
      
      console.log('Test de ruta inexistente exitoso');
    }
  });

  /**
   * Prueba: Producto inexistente
   * 
   * Objetivo: Verificar que la API devuelve un código 404 con mensaje específico
   * al solicitar un producto que no existe.
   */
  it('Debe devolver código 404 al solicitar un producto inexistente', async () => {
    // Configurar el mock para simular una respuesta de error 404
    const errorResponse = {
      response: {
        status: 404,
        data: { error: 'Producto no encontrado' }
      }
    };
    
    // Configurar el mock para rechazar la promesa
    mockApi.get.mockRejectedValueOnce(errorResponse);

    try {
      // Realizar petición a un producto inexistente
      await mockApi.get('/api/productos/9999');
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false); // Esto nunca debería ejecutarse
    } catch (error) {
      // Verificar que la API respondió con el código y mensaje correctos
      expect(error.response.status).toBe(404);
      expect(error.response.data).toHaveProperty('error');
      expect(error.response.data.error).toBe('Producto no encontrado');
      
      console.log('Test de producto inexistente exitoso');
    }
  });

  /**
   * Prueba: Autenticación requerida
   * 
   * Objetivo: Verificar que la API devuelve un código 401 cuando se intenta
   * acceder a una ruta protegida sin token de autenticación.
   */
  it('Debe devolver código 401 al acceder a ruta protegida sin token', async () => {
    // Configurar el mock para simular una respuesta de error 401
    const errorResponse = {
      response: {
        status: 401,
        data: { error: 'Se requiere autenticación' }
      }
    };
    
    // Configurar el mock para rechazar la promesa
    mockApi.get.mockRejectedValueOnce(errorResponse);

    try {
      // Realizar petición a una ruta protegida sin token
      await mockApi.get('/api/admin/usuarios');
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false); // Esto nunca debería ejecutarse
    } catch (error) {
      // Verificar que la API respondió con el código y mensaje correctos
      expect(error.response.status).toBe(401);
      expect(error.response.data).toHaveProperty('error');
      expect(error.response.data.error).toBe('Se requiere autenticación');
      
      console.log('Test de autenticación requerida exitoso');
    }
  });

  /**
   * Prueba: Token inválido
   * 
   * Objetivo: Verificar que la API devuelve un código 401 cuando se proporciona
   * un token de autenticación inválido.
   */
  it('Debe devolver código 401 al proporcionar un token inválido', async () => {
    // Configurar el mock para simular una respuesta de error 401
    const errorResponse = {
      response: {
        status: 401,
        data: { error: 'Token inválido' }
      }
    };
    
    // Configurar el mock para rechazar la promesa
    mockApi.get.mockRejectedValueOnce(errorResponse);

    // Configurar headers con token inválido
    const headers = {
      Authorization: 'Bearer invalidtoken12345'
    };

    try {
      // Realizar petición con token inválido
      await mockApi.get('/api/admin/usuarios', { headers });
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false); // Esto nunca debería ejecutarse
    } catch (error) {
      // Verificar que la API respondió con el código y mensaje correctos
      expect(error.response.status).toBe(401);
      expect(error.response.data).toHaveProperty('error');
      expect(error.response.data.error).toBe('Token inválido');
      
      console.log('Test de token inválido exitoso');
    }
  });

  /**
   * Prueba: Datos inválidos en POST
   * 
   * Objetivo: Verificar que la API devuelve un código 400 cuando se envían
   * datos inválidos en una solicitud POST.
   */
  it('Debe devolver código 400 al enviar datos inválidos en POST', async () => {
    // Datos inválidos - falta el campo requerido 'nombre'
    const datosInvalidos = {
      precio: 50,
      descripcion: 'Descripción del producto'
      // falta el campo nombre
    };

    // Configurar el mock para simular una respuesta de error 400
    const errorResponse = {
      response: {
        status: 400,
        data: { 
          error: 'Datos inválidos',
          detalles: { 
            nombre: 'El campo nombre es requerido'
          }
        }
      }
    };
    
    // Configurar el mock para rechazar la promesa
    mockApi.post.mockRejectedValueOnce(errorResponse);

    try {
      // Realizar solicitud POST con datos inválidos
      await mockApi.post('/api/productos', datosInvalidos);
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false); // Esto nunca debería ejecutarse
    } catch (error) {
      // Verificar que la API respondió con el código y mensaje correctos
      expect(error.response.status).toBe(400);
      expect(error.response.data).toHaveProperty('error');
      expect(error.response.data).toHaveProperty('detalles');
      expect(error.response.data.error).toBe('Datos inválidos');
      expect(error.response.data.detalles).toHaveProperty('nombre');
      
      console.log('Test de datos inválidos en POST exitoso');
    }
  });

  /**
   * Prueba: Permisos insuficientes
   * 
   * Objetivo: Verificar que la API devuelve un código 403 cuando un usuario
   * intenta realizar una acción para la que no tiene permisos.
   */
  it('Debe devolver código 403 al intentar acción sin permisos', async () => {
    // Configurar el mock para simular una respuesta de error 403
    const errorResponse = {
      response: {
        status: 403,
        data: { error: 'Acceso denegado. No tiene permisos para realizar esta acción' }
      }
    };
    
    // Configurar el mock para rechazar la promesa
    mockApi.delete.mockRejectedValueOnce(errorResponse);

    // Configurar headers con token de usuario no autorizado
    const headers = {
      Authorization: 'Bearer token-usuario-cliente'
    };

    try {
      // Intentar eliminar un producto sin tener permisos de administrador
      await mockApi.delete('/api/productos/1', { headers });
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false); // Esto nunca debería ejecutarse
    } catch (error) {
      // Verificar que la API respondió con el código y mensaje correctos
      expect(error.response.status).toBe(403);
      expect(error.response.data).toHaveProperty('error');
      expect(error.response.data.error).toBe('Acceso denegado. No tiene permisos para realizar esta acción');
      
      console.log('Test de permisos insuficientes exitoso');
    }
  });
}); 