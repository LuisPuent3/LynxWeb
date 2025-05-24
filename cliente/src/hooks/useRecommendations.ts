import { useState, useEffect } from 'react';
import api from '../utils/api';
import { Producto } from '../types/types';
import { useAuth } from '../contexts/AuthContext';

interface UseRecommendationsProps {
  limit?: number;
}

export const useRecommendations = ({ limit = 10 }: UseRecommendationsProps = {}) => {
  const [recommendations, setRecommendations] = useState<Producto[]>([]);
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
          setRecommendations(response.data.productos.slice(0, limit));
        } else {
          setRecommendations([]);
        }
      } catch (err: any) {
        console.error('Error fetching recommendations:', err);
        setError(err.message || 'Error al cargar recomendaciones');
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [isAuthenticated, limit]);

  return { recommendations, loading, error };
};
