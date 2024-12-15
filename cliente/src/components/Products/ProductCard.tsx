// src/components/ProductCard.tsx
import React from "react";

// Definir la interfaz para el producto
interface Producto {
  id_producto: number;
  nombre: string;
  precio: number;
  cantidad: number;
  imagen: string;
}

interface ProductCardProps {
  producto: Producto; // Tipo del objeto producto
  addToCart: (producto: Producto) => void; // Función que recibe un producto
}

const ProductCard: React.FC<ProductCardProps> = ({ producto, addToCart }) => {
  return (
    <div className="card">
      <img
        src={`http://localhost:5000/uploads/${producto.imagen}`}
        className="card-img-top"
        alt={producto.nombre}
      />
      <div className="card-body">
        <h5 className="card-title">{producto.nombre}</h5>
        <p className="card-text">Precio: ${producto.precio}</p>
        <p className="card-text">Cantidad disponible: {producto.cantidad}</p>
        <button
          className="btn btn-primary"
          onClick={() => addToCart(producto)}
        >
          Agregar al carrito
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
