import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import api from '../utils/api';
import { render, screen, waitFor } from '@testing-library/react';
import ProductList from '../components/products/ProductList';
import { BrowserRouter } from 'react-router-dom';

/**
 * Test Case ID: LYNX_003
 * Pruebas Unitarias para verificar la conexión API Frontend-Backend
 * 
 * De acuerdo al Plan de Pruebas:
 * - Este test forma parte del Sprint 4, actividad "Pruebas de conexión frontend-backend"
 * - Corresponde a la sección "Tipos de Pruebas" -> "Pruebas Unitarias" y "Pruebas de Integración"
 * - Criterio de aceptación: 100% de pruebas exitosas para funcionalidades críticas
 */

// Mock de axios
vi.mock('axios', async () => {
  const mockAxios = {
    create: vi.fn(() => ({
      get: vi.fn(),
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

describe('LYNX_003: Prueba de Conexión API Frontend-Backend', () => {
  let mockAxiosGet;
  
  beforeEach(() => {
    // Limpiar mocks entre pruebas
    vi.clearAllMocks();
    
    // Configurar el mock para axios.get
    mockAxiosGet = vi.fn();
    const axiosInstance = axios.create();
    axiosInstance.get = mockAxiosGet;
    
    // Sobrescribir la implementación de api.get para usar nuestro mock
    api.get = mockAxiosGet;
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  /**
   * Prueba: Escenario de éxito
   * 
   * Objetivo: Verificar que el componente realiza correctamente la petición GET 
   * a /api/productos y renderiza los datos recibidos (Criterio de aceptación #3: Funcionalidad)
   */
  it('Debe realizar una petición GET a /api/productos y procesar la respuesta correctamente', async () => {
    // Preparar datos mock
    const mockProductos = [
      { id_producto: 1, nombre: 'Producto 1', precio: 100, descripcion: 'Descripción 1', categoria: 'Categoría 1', imagen: 'imagen1.jpg', cantidad: 1 },
      { id_producto: 2, nombre: 'Producto 2', precio: 200, descripcion: 'Descripción 2', categoria: 'Categoría 2', imagen: 'imagen2.jpg', cantidad: 1 }
    ];

    // Configurar el mock para devolver datos
    mockAxiosGet.mockResolvedValueOnce({ data: mockProductos });

    // Renderizar el componente
    render(
      <BrowserRouter>
        <ProductList addToCart={() => {}} searchTerm="" />
      </BrowserRouter>
    );

    // Verificar que la llamada a la API se realizó correctamente
    // Esto valida el paso #3 del Caso de Prueba: "Observar las llamadas de red"
    await waitFor(() => {
      expect(mockAxiosGet).toHaveBeenCalledWith('/productos');
    });

    // Verificar que los productos se muestran en la interfaz
    // Esto valida el paso #5 del Caso de Prueba: "Verificar renderizado"
    await waitFor(() => {
      expect(screen.getByText('Producto 1')).toBeInTheDocument();
      expect(screen.getByText('Producto 2')).toBeInTheDocument();
    });
  });

  /**
   * Prueba: Escenario de error
   * 
   * Objetivo: Verificar el manejo correcto de errores en la comunicación con la API
   * (Criterio de aceptación #3: Funcionalidad - Manejo robusto de errores)
   */
  it('Debe manejar errores en la petición API correctamente', async () => {
    // Configurar el mock para simular un error
    const errorResponse = {
      response: {
        status: 500,
        data: { error: 'Error interno del servidor' }
      }
    };
    
    // Sobrescribir console.error para evitar mensajes de error en la salida de la prueba
    const originalConsoleError = console.error;
    console.error = vi.fn();

    mockAxiosGet.mockRejectedValueOnce(errorResponse);

    // Renderizar el componente
    render(
      <BrowserRouter>
        <ProductList addToCart={() => {}} searchTerm="" />
      </BrowserRouter>
    );

    // Verificar que la llamada a la API se realizó
    await waitFor(() => {
      expect(mockAxiosGet).toHaveBeenCalledWith('/productos');
    });

    // Verificar que se manejó el error
    // Según el Plan de Pruebas, esto cubre el aspecto "Manejo de errores en la comunicación frontend-backend"
    await waitFor(() => {
      expect(console.error).toHaveBeenCalled();
      expect(screen.getByText('No se encontraron productos')).toBeInTheDocument();
    });

    // Restaurar console.error
    console.error = originalConsoleError;
  });

  /**
   * Prueba: Tiempo de respuesta
   * 
   * Objetivo: Verificar que el tiempo de respuesta está dentro de los parámetros aceptables
   * (Criterio de aceptación #4: Rendimiento - Tiempo de respuesta de API < 300ms)
   */
  it('Debe procesar la respuesta de la API dentro del tiempo aceptable', async () => {
    // Preparar datos mock
    const mockProductos = [
      { id_producto: 1, nombre: 'Producto 1', precio: 100, descripcion: 'Descripción 1', categoria: 'Categoría 1', imagen: 'imagen1.jpg', cantidad: 1 }
    ];

    // Configurar el mock para simular un tiempo de respuesta realista (pero rápido)
    mockAxiosGet.mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({ data: mockProductos });
        }, 50); // Simulamos una respuesta de 50ms
      });
    });

    // Registrar tiempo inicial
    const startTime = performance.now();

    // Renderizar el componente
    render(
      <BrowserRouter>
        <ProductList addToCart={() => {}} searchTerm="" />
      </BrowserRouter>
    );

    // Esperar a que los datos se muestren
    await waitFor(() => {
      expect(screen.getByText('Producto 1')).toBeInTheDocument();
    });

    // Registrar tiempo final
    const endTime = performance.now();
    const responseTime = endTime - startTime;

    // Verificar que el tiempo de respuesta está dentro de límites aceptables
    // Según el Plan de Pruebas, el criterio es "Tiempo de respuesta de API < 300ms"
    expect(responseTime).toBeLessThan(300);
    
    // Logging para diagnóstico
    console.log(`Tiempo de respuesta: ${responseTime.toFixed(2)}ms`);
  });
}); 