import { useState, useEffect, useCallback } from 'react';
import nlpService, { NLPSearchResponse, ProductRecommendation } from '../services/nlpService';
import { Producto } from '../types/types';

interface UseNLPSearchResult {
  // Estados
  isNLPAvailable: boolean;
  isSearching: boolean;
  nlpResults: NLPSearchResponse | null;
  suggestedProducts: Producto[];
  
  // Funciones
  performNLPSearch: (query: string) => Promise<void>;
  clearNLPResults: () => void;
  
  // Información adicional
  hasCorrections: boolean;
  correctedQuery: string | null;
  searchInterpretation: any;
  processingTime: number;
}

/**
 * Hook para manejar búsquedas con NLP
 */
export const useNLPSearch = (): UseNLPSearchResult => {
  const [isNLPAvailable, setIsNLPAvailable] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [nlpResults, setNlpResults] = useState<NLPSearchResponse | null>(null);
  const [suggestedProducts, setSuggestedProducts] = useState<Producto[]>([]);

  // Verificar disponibilidad del servicio NLP al cargar
  useEffect(() => {
    const checkNLPAvailability = async () => {
      const available = await nlpService.checkHealth();
      setIsNLPAvailable(available);
      
      if (available) {
        console.log('🧠 LYNX NLP Service connected');
      } else {
        console.log('⚠️ NLP Service not available - using standard search');
      }
    };

    checkNLPAvailability();
    
    // Re-verificar cada 30 segundos si no está disponible
    const interval = setInterval(() => {
      if (!isNLPAvailable) {
        checkNLPAvailability();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isNLPAvailable]);

  /**
   * Realizar búsqueda usando NLP
   */
  const performNLPSearch = useCallback(async (query: string): Promise<void> => {
    if (!isNLPAvailable || !query.trim()) {
      return;
    }

    setIsSearching(true);
    
    try {
      const result = await nlpService.search(query.trim(), 20);
      
      if (result) {
        setNlpResults(result);
        
        // Convertir productos NLP al formato del frontend
        const convertedProducts = nlpService.mapNLPProductsToFrontend(result.recommendations);
        setSuggestedProducts(convertedProducts as Producto[]);
        
        console.log(`🔍 NLP Search completed: ${result.recommendations.length} products in ${result.processing_time_ms}ms`);
        
        // Mostrar correcciones si las hay
        if (result.corrections?.applied) {
          console.log(`🔧 Query corrected: "${query}" → "${result.corrections.corrected_query}"`);
        }
      } else {
        console.warn('NLP search failed - falling back to standard search');
        setNlpResults(null);
        setSuggestedProducts([]);
      }
    } catch (error) {
      console.error('Error in NLP search:', error);
      setNlpResults(null);
      setSuggestedProducts([]);
    } finally {
      setIsSearching(false);
    }
  }, [isNLPAvailable]);

  /**
   * Limpiar resultados NLP
   */
  const clearNLPResults = useCallback(() => {
    setNlpResults(null);
    setSuggestedProducts([]);
  }, []);

  // Información derivada de los resultados
  const hasCorrections = nlpResults?.corrections?.applied ?? false;
  const correctedQuery = nlpResults?.corrections?.corrected_query ?? null;
  const searchInterpretation = nlpResults?.interpretation ?? null;
  const processingTime = nlpResults?.processing_time_ms ?? 0;

  return {
    isNLPAvailable,
    isSearching,
    nlpResults,
    suggestedProducts,
    performNLPSearch,
    clearNLPResults,
    hasCorrections,
    correctedQuery,
    searchInterpretation,
    processingTime
  };
};

export default useNLPSearch;
