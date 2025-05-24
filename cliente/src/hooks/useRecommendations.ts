import { useState, useEffect } from 'react';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

interface UseRecommendationsProps {
  limit?: number;
}

interface RecommendationItem {
  id_producto: number;
  score: number;
}

export const useRecommendations = ({ limit = 30 }: UseRecommendationsProps = {}) => {
  const [recommendationIds, setRecommendationIds] = useState<number[]>([]);
  const [recommendationScores, setRecommendationScores] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Use the appropriate endpoint based on user authentication status
        const endpoint = isAuthenticated ? '/recommendations' : '/recommendations/guest';
        
        const response = await api.get(endpoint);
        
        if (response.data && response.data.productos) {
          const productos = response.data.productos.slice(0, limit);
          const ids = productos.map((p: any) => p.id_producto);
          
          // Create a map of product ID to recommendation score
          const scores: Record<number, number> = {};
          productos.forEach((p: any) => {
            scores[p.id_producto] = p.score || 0;
          });
          
          setRecommendationIds(ids);
          setRecommendationScores(scores);
        } else {
          setRecommendationIds([]);
          setRecommendationScores({});
        }
      } catch (err: any) {
        console.error('Error fetching recommendations:', err);
        setError(err.message || 'Error al cargar recomendaciones');
        setRecommendationIds([]);
        setRecommendationScores({});
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [isAuthenticated, limit]);

  // Sort function to order products based on recommendations
  const sortProductsByRecommendation = <T extends {id_producto: number}>(products: T[]) => {
    if (recommendationIds.length === 0) return products;
    
    return [...products].sort((a, b) => {
      const aIndex = recommendationIds.indexOf(a.id_producto);
      const bIndex = recommendationIds.indexOf(b.id_producto);
      
      // If both products are in recommendations, sort by their position
      if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
      
      // If only one product is in recommendations, it comes first
      if (aIndex !== -1) return -1;
      if (bIndex !== -1) return 1;
      
      // If neither product is in recommendations, maintain original order
      return 0;
    });
  };

  return { recommendationIds, recommendationScores, sortProductsByRecommendation, loading, error };
};
