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
    : '';

  return (    <div className="card h-100 shadow-sm">
      <div className="position-relative">
        {!imgError && producto.imagen ? (
          <img
            src={imageUrl}
            className="card-img-top"
            alt={producto.nombre}
            style={{ height: '200px', objectFit: 'cover' }}
            loading="lazy"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="bg-light d-flex align-items-center justify-content-center" style={{ height: '200px' }}>
            <i className="bi bi-image text-secondary" style={{ fontSize: '3rem' }}></i>
          </div>
        )}
        {/* Mostramos badge de últimas unidades */}
        {producto.cantidad > 0 && producto.cantidad <= 5 && (
          <span className="position-absolute top-0 end-0 badge bg-warning m-2">
            ¡Últimas unidades!
          </span>
        )}
        {/* Mostramos badge de sin stock */}
        {producto.cantidad === 0 && (
          <span className="position-absolute top-0 end-0 badge bg-danger m-2">
            Sin stock
          </span>
        )}
      </div>
      <div className="card-body d-flex flex-column">
        <h5 className="card-title">{producto.nombre}</h5>
        <p className="card-text text-muted mb-2">
          {producto.cantidad > 0 
            ? `Disponibles: ${producto.cantidad}` 
            : <span className="text-danger">No disponible</span>}
        </p>
        <div className="mt-auto">
          <p className="h5 mb-3 text-primary">
            ${isNaN(precioNumerico) ? '0.00' : precioNumerico.toFixed(2)}
          </p>
          <button
            className={`btn w-100 d-flex align-items-center justify-content-center gap-2 ${producto.cantidad > 0 ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => addToCart(producto)}
            disabled={producto.cantidad === 0}
            title={producto.cantidad === 0 ? "Producto sin stock disponible" : "Agregar al carrito"}
          >
            <i className={`bi ${producto.cantidad > 0 ? 'bi-cart-plus' : 'bi-x-circle'}`}></i>
            {producto.cantidad > 0 ? 'Agregar al carrito' : 'Sin stock'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;