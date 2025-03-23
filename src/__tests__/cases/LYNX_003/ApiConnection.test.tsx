import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import ProductList from './components/products/ProductList';

// Mock del componente ProductList que usa axios
vi.mock('axios');

describe('LYNX_003: Prueba de Conexión API Frontend-Backend (Componentes)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('Debe cargar y mostrar productos desde la API', async () => {
    // Configurar el mock para que devuelva datos de productos
    (axios.get as any).mockResolvedValueOnce({
      data: [
        { id: 1, nombre: 'Producto 1', precio: 100, descripcion: 'Descripción del producto 1' },
        { id: 2, nombre: 'Producto 2', precio: 200, descripcion: 'Descripción del producto 2' }
      ]
    });
    
    // Renderizamos el componente
    render(<ProductList />);
    
    // Verificamos que se muestran los productos
    await waitFor(() => {
      expect(screen.getByText('Producto 1')).toBeInTheDocument();
      expect(screen.getByText('Producto 2')).toBeInTheDocument();
    });
    
    console.log('Test de carga de productos en componente exitoso');
  });
  
  it('Debe mostrar un mensaje de error cuando la API falla', async () => {
    // Configurar el mock para que devuelva un error
    (axios.get as any).mockRejectedValueOnce(new Error('Error de API'));
    
    // Renderizamos el componente
    render(<ProductList />);
    
    // Verificamos que se muestra un mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/error al cargar los productos/i)).toBeInTheDocument();
    });
    
    console.log('Test de manejo de errores en componente exitoso');
  });
}); 