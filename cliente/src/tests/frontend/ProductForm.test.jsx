import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
// Intentando una ruta más común, asumiendo que ProductForm está en cliente/src/components/
import ProductForm from '../../components/ProductForm'; // Corregida la ruta

// Mock de la función onSubmit para espiar su llamada
const mockOnSubmit = vi.fn();

// Mock de react-router-dom si el componente usa useNavigate o Link
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    // Si usas <Link>, también puedes mockearlo o envolver el componente en <MemoryRouter>
  };
});


describe('ProductForm', () => {
  // Prueba de renderizado básico
  it('debería renderizar el formulario de producto correctamente', () => {
    // Arrange
    render(<ProductForm onSubmit={mockOnSubmit} />);

    // Act & Assert
    expect(screen.getByLabelText(/nombre del producto/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/precio/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/descripción/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/categoría/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/stock/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /guardar producto/i })).toBeInTheDocument();
    // TODO: Verificar la existencia de otros campos si los hay (ej. imagen)
  });

  // Prueba de validación de campos requeridos
  it('debería mostrar mensajes de error si los campos requeridos están vacíos al hacer submit', async () => {
    // Arrange
    render(<ProductForm onSubmit={mockOnSubmit} />);
    const submitButton = screen.getByRole('button', { name: /guardar producto/i });

    // Act
    fireEvent.click(submitButton);

    // Assert
    // Esperar a que aparezcan los mensajes de error. La implementación exacta depende de cómo muestres los errores.
    // Esto es un ejemplo, ajusta los selectores y el texto según tu implementación.
    await waitFor(() => {
      expect(screen.getByText(/el nombre es requerido/i)).toBeInTheDocument();
      expect(screen.getByText(/el precio es requerido/i)).toBeInTheDocument();
      // TODO: Añadir aserciones para otros campos requeridos (categoría, etc.)
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  // Prueba de envío exitoso con datos válidos
  it('debería llamar a la función onSubmit con los datos del formulario cuando es válido y se hace submit', async () => {
    // Arrange
    const productData = {
      name: 'Laptop Gamer',
      price: '1500.99',
      description: 'Potente laptop para juegos.',
      categoryId: '1', // Asumiendo que el ID de categoría se maneja como string en el form
      stock: '10',
      // TODO: Añadir campo de imagen si existe
    };
    render(<ProductForm onSubmit={mockOnSubmit} />); // Podrías pasar un producto inicial si el form es para editar

    // Act
    fireEvent.change(screen.getByLabelText(/nombre del producto/i), { target: { value: productData.name } });
    fireEvent.change(screen.getByLabelText(/precio/i), { target: { value: productData.price } });
    fireEvent.change(screen.getByLabelText(/descripción/i), { target: { value: productData.description } });
    fireEvent.change(screen.getByLabelText(/categoría/i), { target: { value: productData.categoryId } });
    fireEvent.change(screen.getByLabelText(/stock/i), { target: { value: productData.stock } });

    const submitButton = screen.getByRole('button', { name: /guardar producto/i });
    fireEvent.click(submitButton);

    // Assert
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: productData.name,
          price: parseFloat(productData.price),
          description: productData.description,
          categoryId: parseInt(productData.categoryId, 10),
          stock: parseInt(productData.stock, 10),
        }),
        expect.anything() // Para el segundo argumento si es un event o formik helpers
      );
    });
  });

  // TODO: Añadir prueba para el caso de edición (si el formulario se usa para crear y editar)
  //       - Debería poblar los campos con los datos del producto existente.
  //       - Debería llamar a onSubmit con el ID del producto y los datos actualizados.

  // TODO: Añadir pruebas para validaciones específicas de campos (ej. precio numérico, stock entero positivo)
  //       Ejemplo: fireEvent.change(screen.getByLabelText(/precio/i), { target: { value: 'texto' } });
  //                // Verificar mensaje de error para precio inválido

  // TODO: Si hay subida de imágenes, mockear la API de File y probar esa funcionalidad.
});
