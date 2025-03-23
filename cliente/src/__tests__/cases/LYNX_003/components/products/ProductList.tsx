import React, { useEffect, useState } from 'react';
import axios from 'axios';

// Interfaces para los props y productos
interface Product {
  id_producto: number;
  nombre: string;
  precio: string; // El API devuelve esto como string
  descripcion: string;
  categoria?: string;
  imagen?: string;
  cantidad?: number;
}

interface ProductListProps {
  addToCart?: (product: Product) => void;
  searchTerm?: string;
}

const ProductList: React.FC<ProductListProps> = ({ addToCart, searchTerm = '' }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar productos cuando el componente se monta
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        // Usar axios directamente sin importar api.ts
        const response = await axios.get('/productos');
        setProducts(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error al cargar productos:', err);
        setError('No se encontraron productos');
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Filtrar productos según el término de búsqueda
  const filteredProducts = products.filter(product =>
    product.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.descripcion.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <div data-testid="loading">Cargando productos...</div>;
  if (error) return <div data-testid="error">{error}</div>;
  if (filteredProducts.length === 0) return <div>No se encontraron productos</div>;

  return (
    <div className="product-list">
      {filteredProducts.map(product => (
        <div key={product.id_producto} className="product-card">
          {product.imagen && (
            <img 
              src={product.imagen} 
              alt={product.nombre} 
              className="product-image" 
            />
          )}
          <h3>{product.nombre}</h3>
          <p className="product-price">${product.precio}</p>
          <p className="product-description">{product.descripcion}</p>
          {addToCart && (
            <button 
              onClick={() => addToCart(product)}
              className="add-to-cart-button"
            >
              Añadir al carrito
            </button>
          )}
        </div>
      ))}
    </div>
  );
};

export default ProductList;








