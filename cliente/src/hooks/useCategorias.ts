import { useState, useEffect } from 'react';
import api from '../utils/api';

interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion?: string;
}

export const useCategorias = () => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategorias = async () => {
      try {
        setLoading(true);
        const response = await api.get('/categorias');
        setCategorias(response.data);
        setError(null);
      } catch (err) {
        console.error('Error al cargar categorías:', err);
        setError('Error al cargar las categorías');
      } finally {
        setLoading(false);
      }
    };

    fetchCategorias();
  }, []);

  return { categorias, loading, error };
}; 