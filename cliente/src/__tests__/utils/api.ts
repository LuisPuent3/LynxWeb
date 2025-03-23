// src/utils/api.ts
import axios from 'axios';
import { vi } from 'vitest';

// Crear un mock de axios para las pruebas
const mockAxios = axios.create({
  baseURL: 'http://localhost:3000/api', // URL base para las solicitudes API
  timeout: 5000, // Tiempo máximo de espera para las solicitudes
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Mock para get
mockAxios.get = vi.fn().mockImplementation((url, config) => {
  if (url === '/productos') {
    return Promise.resolve({
      status: 200,
      data: [
        { id: 1, nombre: 'Producto 1', precio: 100, descripcion: 'Descripción del producto 1' },
        { id: 2, nombre: 'Producto 2', precio: 200, descripcion: 'Descripción del producto 2' }
      ],
      headers: {
        'access-control-allow-origin': '*'
      }
    });
  }
  
  // Errores específicos para las pruebas de error
  if (url === '/ruta-que-no-existe' || url === '/productos/99999') {
    return Promise.reject({
      response: {
        status: 404,
        data: { mensaje: 'No encontrado' }
      }
    });
  }
  
  if (url === '/admin/usuarios') {
    // Verificar si tiene token válido
    const authHeader = config?.headers?.Authorization;
    if (!authHeader) {
      return Promise.reject({
        response: {
          status: 401,
          data: { mensaje: 'No autorizado' }
        }
      });
    }
    
    if (authHeader === 'Bearer token-invalido') {
      return Promise.reject({
        response: {
          status: 401,
          data: { mensaje: 'Token inválido' }
        }
      });
    }
    
    // Si el token es "user" (simulando un usuario normal)
    if (authHeader === 'Bearer user') {
      return Promise.reject({
        response: {
          status: 403,
          data: { mensaje: 'Permisos insuficientes' }
        }
      });
    }
    
    // Solo con token admin llegaría aquí
    return Promise.resolve({
      status: 200,
      data: { mensaje: 'Acceso correcto' }
    });
  }
  
  // Para cualquier otra ruta, devolvemos un error
  return Promise.reject(new Error('Network Error'));
});

// Mock para post
mockAxios.post = vi.fn().mockImplementation((url, data) => {
  if (url === '/productos' && (!data || Object.keys(data).length === 0)) {
    return Promise.reject({
      response: {
        status: 400,
        data: { mensaje: 'Datos inválidos' }
      }
    });
  }
  
  if (url === '/auth/login') {
    if (data.usuario === 'usuario_normal') {
      return Promise.resolve({
        status: 200,
        data: { token: 'user' }
      });
    }
    if (data.usuario === 'admin') {
      return Promise.resolve({
        status: 200,
        data: { token: 'admin' }
      });
    }
  }
  
  return Promise.resolve({
    status: 200,
    data: { mensaje: 'Operación exitosa' }
  });
});

// Mock para delete
mockAxios.delete = vi.fn().mockImplementation((url, config) => {
  if (url.includes('/admin/usuarios/')) {
    const authHeader = config?.headers?.Authorization;
    
    if (!authHeader) {
      return Promise.reject({
        response: {
          status: 401,
          data: { mensaje: 'No autorizado' }
        }
      });
    }
    
    if (authHeader === 'Bearer user') {
      return Promise.reject({
        response: {
          status: 403,
          data: { mensaje: 'Permisos insuficientes' }
        }
      });
    }
  }
  
  return Promise.resolve({
    status: 200,
    data: { mensaje: 'Eliminado correctamente' }
  });
});

export default mockAxios;