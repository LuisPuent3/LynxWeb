import React, { useState } from "react";
import { Producto } from "../../types/types";

interface ProductCardProps {
  producto: Producto;
  addToCart: (producto: Producto) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ producto, addToCart }) => {
  // Convertimos el precio a número antes de usar toFixed
  const precioNumerico = typeof producto.precio === 'string' 
    ? parseFloat(producto.precio) 
    : producto.precio;
  
  // Estado para controlar errores de carga de imagen
  const [imgError, setImgError] = useState(false);

  // Construir URL una sola vez
  const imageUrl = producto.imagen 
    ? `http://localhost:5000/uploads/${producto.imagen}?v=${producto.id_producto}` 
    : 'https://via.placeholder.com/200?text=Producto+sin+imagen';

  return (
    <div className="card h-100 shadow-sm">
      <div className="position-relative">
        <img
          src={imgError ? 'https://via.placeholder.com/200?text=Imagen+no+disponible' : imageUrl}
          className="card-img-top"
          alt={producto.nombre}
          style={{ height: '200px', objectFit: 'cover' }}
          loading="lazy"
          onError={() => setImgError(true)}
        />
        {producto.cantidad <= 5 && (
          <span className="position-absolute top-0 end-0 badge bg-warning m-2">
            ¡Últimas unidades!
          </span>
        )}
      </div>
      <div className="card-body d-flex flex-column">
        <h5 className="card-title">{producto.nombre}</h5>
        <p className="card-text text-muted mb-2">Disponibles: {producto.cantidad}</p>
        <div className="mt-auto">
          <p className="h5 mb-3 text-primary">
            ${isNaN(precioNumerico) ? '0.00' : precioNumerico.toFixed(2)}
          </p>
          <button
            className="btn btn-primary w-100 d-flex align-items-center justify-content-center gap-2"
            onClick={() => addToCart(producto)}
            disabled={producto.cantidad === 0}
          >
            <i className="bi bi-cart-plus"></i>
            Agregar al carrito
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;