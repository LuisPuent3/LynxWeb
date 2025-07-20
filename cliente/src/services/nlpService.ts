/**
 * Servicio NLP para integrar con el sistema LYNX
 * Conecta con el microservicio FastAPI en puerto 8000
 */

interface ProductRecommendation {
  id: number;
  name: string;
  price: number;
  category: string;
  match_score: number;
  match_reasons: string[];
  available: boolean;
}

interface NLPCorrection {
  from: string;
  to: string;
  confidence: number;
}

interface NLPInterpretation {
  producto?: string;
  categoria?: string;
  atributos?: string[];
  filtros?: {
    precio?: {
      max?: number;
      min?: number;
      tendency?: string;
    };
    atributos?: Array<{
      modificador: string;
      atributo: string;
    }>;
  };
}

interface NLPSearchResponse {
  success: boolean;
  message: string;
  query: string;
  processing_time_ms: number;
  interpretation: NLPInterpretation;
  recommendations: ProductRecommendation[];
  corrections?: {
    applied: boolean;
    corrected_query?: string;
    changes?: NLPCorrection[];
  };
  sql_query?: string;
  user_message?: string;
}

interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  components: {
    [key: string]: string;
  };
}

class NLPService {
  private baseUrl: string;
  private isHealthy: boolean = false;

  constructor() {
    this.baseUrl = 'http://localhost:8000';
    this.checkHealth();
  }
  /**
   * Verificar si el servicio NLP está funcionando
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.warn('NLP Service not available');
        this.isHealthy = false;
        return false;
      }

      const health: HealthResponse = await response.json();
      this.isHealthy = health.status === 'healthy';
      
      if (this.isHealthy) {
        const products = health.components.products || '0';
        const synonyms = health.components.synonyms || '0';
        console.log(`🧠 LYNX NLP Service ready: ${products}, ${synonyms}`);
      }

      return this.isHealthy;
    } catch (error) {
      console.warn('NLP Service connection failed:', error);
      this.isHealthy = false;
      return false;
    }
  }

  /**
   * Realizar búsqueda usando procesamiento de lenguaje natural
   */
  async search(query: string, limit: number = 10): Promise<NLPSearchResponse | null> {
    // Verificar que el servicio esté disponible
    if (!this.isHealthy) {
      await this.checkHealth();
      if (!this.isHealthy) {
        return null;
      }
    }    try {
      const response = await fetch(`${this.baseUrl}/api/nlp/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          options: {
            max_recommendations: limit,
            enable_correction: true,
            enable_recommendations: true,
            enable_sql_generation: true
          }
        }),
      });

      if (!response.ok) {
        console.error('NLP Search failed:', response.status, response.statusText);
        return null;
      }

      const result: NLPSearchResponse = await response.json();
      
      // Log de debug para desarrollo
      if (process.env.NODE_ENV === 'development') {
        console.log('🔍 NLP Search Result:', {
          query: result.query,
          time: `${result.processing_time_ms}ms`,
          products: result.recommendations.length,
          corrected: result.corrections?.applied || false
        });
      }

      return result;
    } catch (error) {
      console.error('NLP Service error:', error);
      return null;
    }
  }

  /**
   * Obtener sugerencias rápidas basadas en el input del usuario
   */
  async getSuggestions(partialQuery: string): Promise<string[]> {
    if (!this.isHealthy || partialQuery.length < 2) {
      return [];
    }

    // Implementación simple - en producción se podría hacer más sofisticado
    const commonSuggestions = [
      'bebidas sin azúcar',
      'snacks picantes baratos',
      'productos menos de 20 pesos',
      'coca cola',
      'papitas sabritas',
      'leche deslactosada',
      'dulces para niños',
      'botanas saladas'
    ];

    const filtered = commonSuggestions.filter(suggestion => 
      suggestion.toLowerCase().includes(partialQuery.toLowerCase())
    );

    return filtered.slice(0, 5);
  }

  /**
   * Convertir respuesta NLP a formato compatible con el frontend
   */
  mapNLPProductsToFrontend(nlpProducts: ProductRecommendation[]): any[] {
    return nlpProducts.map(product => ({
      id_producto: product.id,
      nombre: product.name,
      precio: product.price,
      categoria: product.category,
      cantidad: product.available ? 10 : 0, // Asumir stock si está disponible
      match_score: product.match_score,
      match_reasons: product.match_reasons,
      // Agregar propiedades por defecto que espera el frontend
      descripcion: '',
      id_categoria: 1, // Mapear según categoría
      imagen: 'default.jpg'
    }));
  }

  /**
   * Verificar si el servicio está disponible
   */
  isServiceHealthy(): boolean {
    return this.isHealthy;
  }

  /**
   * Obtener estadísticas del sistema
   */
  async getStats(): Promise<HealthResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      return null;
    }
  }
}

// Singleton instance
const nlpService = new NLPService();
export default nlpService;
export type { NLPSearchResponse, ProductRecommendation, NLPInterpretation };
