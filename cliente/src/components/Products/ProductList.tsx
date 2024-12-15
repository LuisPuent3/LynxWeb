import { useState, useEffect } from 'react';

interface Product {
  id_producto: number;
  nombre: string;
  precio: number;
  cantidad: number;
  imagen: string;
}

export const ProductList = () => {
  const [productos, setProductos] = useState<Product[]>([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/productos')
      .then(response => response.json())
      .then(data => setProductos(data))
      .catch(error => console.error('Error:', error));
  }, []);

  return (
    <div>
      {productos.map(producto => (
        <div key={producto.id_producto}>
          <h3>{producto.nombre}</h3>
          <p>Precio: ${producto.precio}</p>
        </div>
      ))}
    </div>
  );
};