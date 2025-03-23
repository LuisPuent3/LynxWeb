/**
 * Mocks para pruebas de API - Proyecto LYNX
 * Este archivo contiene mocks compartidos que pueden ser utilizados por diferentes pruebas.
 */

// Mock de respuesta para productos
export const mockProductsResponse = {
  status: 200,
  data: [
    {
      id: 1,
      nombre: 'Producto 1',
      precio: 19.99,
      descripcion: 'Descripción del producto 1',
      imagen: 'producto1.jpg',
      categoria: 'Categoría 1'
    },
    {
      id: 2,
      nombre: 'Producto 2',
      precio: 29.99,
      descripcion: 'Descripción del producto 2',
      imagen: 'producto2.jpg',
      categoria: 'Categoría 2'
    }
  ],
  headers: {
    'content-type': 'application/json',
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET, POST, PUT, DELETE',
    'access-control-allow-headers': 'Content-Type, Authorization'
  }
};

// Mock para errores de API
export const mockApiErrors = {
  notFound: {
    status: 404,
    data: {
      error: 'No encontrado',
      mensaje: 'El recurso solicitado no existe'
    }
  },
  unauthorized: {
    status: 401,
    data: {
      error: 'No autorizado',
      mensaje: 'Se requiere autenticación para acceder a este recurso'
    }
  },
  badRequest: {
    status: 400,
    data: {
      error: 'Solicitud incorrecta',
      mensaje: 'Los datos proporcionados son inválidos o incompletos'
    }
  },
  forbidden: {
    status: 403,
    data: {
      error: 'Acceso denegado',
      mensaje: 'No tiene permisos para realizar esta acción'
    }
  }
};

// Mock para simulación de retardo en la API
export const mockApiDelay = (ms: number = 100) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Mock de función para simular Axios
export const mockAxios = {
  get: jest.fn().mockResolvedValue(mockProductsResponse),
  post: jest.fn().mockResolvedValue({ status: 201, data: { id: 3, mensaje: 'Creado con éxito' } }),
  put: jest.fn().mockResolvedValue({ status: 200, data: { id: 1, mensaje: 'Actualizado con éxito' } }),
  delete: jest.fn().mockResolvedValue({ status: 204 }),
  create: jest.fn().mockImplementation(() => mockAxios)
}; 