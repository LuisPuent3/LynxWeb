import React, { useState } from "react";
import { Producto } from "../../types/types";
import { useRecommendations } from "../../hooks/useRecommendations";

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
  
  // Obtener información de recomendaciones
  const { recommendationIds } = useRecommendations();
  const recommendationIndex = recommendationIds.indexOf(producto.id_producto);
  const isTopRecommendation = recommendationIndex >= 0 && recommendationIndex < 6; // Top 6
  const isSecondaryRecommendation = recommendationIndex >= 6 && recommendationIndex < 12; // Recomendaciones secundarias
  // Construir URL una sola vez
  const imageUrl = producto.imagen 
    ? `http://localhost:5000/uploads/${producto.imagen}?v=${producto.id_producto}` 
    : '';
    
  // Definimos los estilos de la tarjeta según las recomendaciones
  const cardStyle = isTopRecommendation 
    ? { transform: 'translateY(-3px)', transition: 'all 0.3s' } 
    : isSecondaryRecommendation 
      ? { transition: 'all 0.3s' } 
      : undefined;
      
  const cardClass = isTopRecommendation 
    ? 'card h-100 shadow' 
    : isSecondaryRecommendation 
      ? 'card h-100 shadow-sm border border-primary border-opacity-25' 
      : 'card h-100 shadow-sm';

  return (    
    <div className={cardClass} style={cardStyle}>
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
        
        {/* Mostramos badge de recomendación */}
        {isTopRecommendation && (
          <span className="position-absolute top-0 start-0 badge bg-primary m-2">
            <i className="bi bi-star-fill me-1"></i> Recomendado
          </span>
        )}

        {/* Mostramos badge de últimas unidades */}
        {producto.cantidad > 0 && producto.cantidad <= 5 && (
          <span className="position-absolute top-0 end-0 badge bg-warning m-2">
            ¡Pocas!
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