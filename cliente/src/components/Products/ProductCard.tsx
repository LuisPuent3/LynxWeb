// src/components/ProductCard.tsx
import React from "react";
import { Producto } from "../../types/types.js";

interface ProductCardProps {
  producto: Producto;
  addToCart: (producto: Producto) => void;
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