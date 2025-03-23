import axios from 'axios';
import { vi } from 'vitest';

// Mock del servicio api basado en axios
const api = axios.create({
  baseURL: 'http://localhost:3000/api',
  timeout: 5000,
});

// Mock de GET para simular obtención de productos
api.get = vi.fn().mockImplementation((url) => {
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
  } else if (url === '/productos/1') {
    return Promise.resolve({
      status: 200,
      data: { id: 1, nombre: 'Producto 1', precio: 100, descripcion: 'Descripción del producto 1' },
      headers: {
        'access-control-allow-origin': '*'
      }
    });
  } else if (url === '/productos/999') {
    // Simular 404 para un producto que no existe
    return Promise.reject({
      response: {
        status: 404,
        data: { mensaje: 'Producto no encontrado' }
      }
    });
  } else if (url.startsWith('/admin') && !url.includes('token=admin')) {
    // Simular 401 para rutas protegidas sin token
    return Promise.reject({
      response: {
        status: 401,
        data: { mensaje: 'No autorizado' }
      }
    });
  } else {
    // Simular 404 para rutas no existentes
    return Promise.reject({
      response: {
        status: 404,
        data: { mensaje: 'Ruta no encontrada' }
      }
    });
  }
});

// Mock de POST para simular login y creación
api.post = vi.fn().mockImplementation((url, data) => {
  if (url === '/login') {
    if (data.username === 'usuario' && data.password === 'password') {
      return Promise.resolve({
        status: 200,
        data: { token: 'user_token_123', user: { id: 1, username: 'usuario', role: 'user' } },
        headers: {
          'access-control-allow-origin': '*'
        }
      });
    } else if (data.username === 'admin' && data.password === 'admin') {
      return Promise.resolve({
        status: 200,
        data: { token: 'admin_token_456', user: { id: 2, username: 'admin', role: 'admin' } },
        headers: {
          'access-control-allow-origin': '*'
        }
      });
    } else {
      // Credenciales inválidas
      return Promise.reject({
        response: {
          status: 401,
          data: { mensaje: 'Credenciales inválidas' }
        }
      });
    }
  } else if (url === '/productos' && data.nombre && data.precio) {
    // Creación de producto exitosa
    return Promise.resolve({
      status: 201,
      data: { id: 3, ...data },
      headers: {
        'access-control-allow-origin': '*'
      }
    });
  } else {
    // Datos inválidos para cualquier otra ruta
    return Promise.reject({
      response: {
        status: 400,
        data: { mensaje: 'Datos inválidos' }
      }
    });
  }
});

// Mock de DELETE para simular eliminación
api.delete = vi.fn().mockImplementation((url) => {
  if (url.startsWith('/usuarios/') && url.includes('token=admin')) {
    // Eliminación exitosa si es admin
    return Promise.resolve({
      status: 200,
      data: { mensaje: 'Usuario eliminado correctamente' },
      headers: {
        'access-control-allow-origin': '*'
      }
    });
  } else {
    // No autorizado si no es admin
    return Promise.reject({
      response: {
        status: 403,
        data: { mensaje: 'No tienes permisos para esta acción' }
      }
    });
  }
});

export default api; 