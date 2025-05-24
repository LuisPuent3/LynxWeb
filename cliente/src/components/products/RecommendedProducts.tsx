import React, { useState } from 'react';
import { useRecommendations } from '../../hooks/useRecommendations';
import ProductCard from './ProductCard';
import { useAuth } from '../../contexts/AuthContext';
import { Producto } from '../../types/types';
import '../../styles/RecommendedProducts.css';

interface RecommendedProductsProps {
  limit?: number;
  onAddToCart?: (producto: Producto) => void;
}

const RecommendedProducts: React.FC<RecommendedProductsProps> = ({ limit = 4, onAddToCart }) => {
  const { recommendations, loading, error } = useRecommendations({ limit });
  const { isAuthenticated } = useAuth();
  const [addedToCart, setAddedToCart] = useState<Record<number, boolean>>({});

  if (loading) {
    return (
      <div className="recommended-products">
        <h2>{isAuthenticated ? 'Recomendaciones para ti' : 'Productos populares'}</h2>
        <div className="loading">Cargando recomendaciones...</div>
      </div>
    );
  }

  if (error) {
    return null; // Don't show any error to avoid disturbing the UI
  }

  if (recommendations.length === 0) {
    return null; // Don't render anything if no recommendations
  }

  return (
    <div className="recommended-products">
      <h2>{isAuthenticated ? 'Recomendaciones para ti' : 'Productos populares'}</h2>      <div className="product-grid">
        {recommendations.map((producto) => (
          <ProductCard 
            key={producto.id_producto} 
            producto={producto} 
            addToCart={() => {
              if (onAddToCart) {
                onAddToCart(producto);
                setAddedToCart(prev => ({...prev, [producto.id_producto]: true}));
                setTimeout(() => {
                  setAddedToCart(prev => ({...prev, [producto.id_producto]: false}));
                }, 2000);
              }
            }} 
          />
        ))}
      </div>
    </div>
  );
};

export default RecommendedProducts;
