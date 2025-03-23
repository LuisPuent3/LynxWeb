import React, { useEffect, useState } from 'react';
import api from '../utils/api';

interface Product {
  id: number;
  nombre: string;
  precio: number;
  descripcion?: string;
}

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await api.get('/productos');
        setProducts(response.data);
        setError(null);
      } catch (err) {
        setError('Error al cargar los productos. Por favor, intenta nuevamente.');
        console.error('Error al cargar productos:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return <div className="loading">Cargando productos...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="product-list">
      <h2>Lista de Productos</h2>
      {products.length === 0 ? (
        <p>No hay productos disponibles.</p>
      ) : (
        <ul>
          {products.map((product) => (
            <li key={product.id} className="product-item">
              <h3>{product.nombre}</h3>
              <p className="price">Precio: ${product.precio}</p>
              {product.descripcion && <p>{product.descripcion}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ProductList; 