import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Product {
  id: number;
  nombre: string;
  precio: number;
  descripcion?: string;
}

interface ProductListProps {
  addToCart?: (product: Product) => void;
  searchTerm?: string;
  onSearch?: (term: string) => void;
}

const ProductList: React.FC<ProductListProps> = ({ addToCart, searchTerm, onSearch }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [localSearchTerm, setLocalSearchTerm] = useState<string>(searchTerm || '');

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    if (searchTerm !== undefined) {
      setLocalSearchTerm(searchTerm);
    }
  }, [searchTerm]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/productos');
      setProducts(response.data);
      setError(null);
    } catch (err) {
      console.error('Error al cargar productos:', err);
      setError('Error al cargar los productos. Por favor, intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product: Product) => {
    if (addToCart) {
      addToCart(product);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalSearchTerm(e.target.value);
    if (onSearch) {
      onSearch(e.target.value);
    }
  };

  if (loading) {
    return <div className="loading">Cargando productos...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="product-list">
      <h2>Lista de Productos</h2>
      
      {onSearch && (
        <div className="search-container">
          <input 
            type="text"
            placeholder="Buscar productos..."
            value={localSearchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>
      )}
      
      {products.length === 0 ? (
        <p>No se encontraron productos</p>
      ) : (
        <ul>
          {products.map((product) => (
            <li key={product.id} className="product-item">
              <h3>{product.nombre}</h3>
              <p className="price">Precio: ${product.precio}</p>
              {product.descripcion && <p className="description">{product.descripcion}</p>}
              
              {addToCart && (
                <button 
                  className="add-to-cart"
                  onClick={() => handleAddToCart(product)}
                >
                  Añadir al carrito
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ProductList; 