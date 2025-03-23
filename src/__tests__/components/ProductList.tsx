import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Product {
  id: number;
  nombre: string;
  precio: number;
  descripcion?: string;
}

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/productos');
      setProducts(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error al cargar productos:', err);
      setError('Error al cargar los productos. Por favor, intenta nuevamente.');
      setLoading(false);
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
      <ul>
        {products.map((product) => (
          <li key={product.id} className="product-item">
            <h3>{product.nombre}</h3>
            <p className="price">Precio: ${product.precio}</p>
            {product.descripcion && <p className="description">{product.descripcion}</p>}
            <button className="add-to-cart">Añadir al carrito</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProductList; 