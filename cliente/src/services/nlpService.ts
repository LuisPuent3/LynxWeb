/**
 * Servicio NLP para integrar con el sistema LYNX LCLN Dinámico
 * Conecta con el backend Node.js que proxy al microservicio FastAPI LCLN
 */

interface ProductRecommendation {
  // Formato español (original)
  id: number;
  id_producto: number;
  nombre: string;
  precio: number;
  categoria: string;
  categoria_nombre?: string;
  id_categoria?: number;
  cantidad: number;
  imagen: string;
  available: boolean;
  match_score: number;
  match_reasons: string[];
  source: string;
  descripcion?: string;
  
  // Formato inglés (nuevo formato de API)
  name?: string;
  price?: number;
  category?: string;
  stock?: number;
  image?: string;
  relevance?: number;
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
  message?: string;
  query?: string; // Mantener compatibilidad
  original_query?: string; // Nuevo formato
  processing_time_ms: number;
  products_found?: number;
  user_message?: string;
  interpretation: NLPInterpretation;
  recommendations: ProductRecommendation[];
  products?: ProductRecommendation[]; // Campo adicional del backend
  corrections?: {
    applied: boolean;
    original_query?: string;
    corrected_query?: string;
    corrections_details?: NLPCorrection[];
    changes?: NLPCorrection[];
  };
  metadata?: {
    database?: string;
    cache_timestamp?: string;
    imagenes_incluidas?: boolean;
    filtro_precio_aplicado?: boolean;
    producto_original_rechazado?: boolean;
  };
  sql_query?: string;
}

interface HealthResponse {
  success: boolean;
  lcln_service: string;
  status?: {
    status?: string;
    system?: string;
    version?: string;
    database?: string;
    cache_products?: number;
    cache_synonyms?: number;
    timestamp?: string;
  };
  error?: string;
  timestamp?: string;
  // Formato legacy (mantener compatibilidad)
  components?: {
    [key: string]: string;
  };
  productos?: number;
  sinonimos?: number;
}

class NLPService {
  private baseUrl: string;
  private isHealthy: boolean = false;  constructor() {
    this.baseUrl = import.meta.env.PROD ? '' : 'http://localhost:5000'; // En producción usa la URL actual, en desarrollo localhost
    this.checkHealth();
  }
  /**
   * Verificar si el servicio NLP está funcionando
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/lcln/status`, {
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
      this.isHealthy = health.success && health.lcln_service === 'available';
      
      if (this.isHealthy) {
        const products = health.status?.cache_products || '0';
        const synonyms = health.status?.cache_synonyms || '0';
        console.log(`🧠 LYNX NLP Service ready: ${products} productos, ${synonyms} sinónimos`);
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
      const response = await fetch(`${this.baseUrl}/api/lcln/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          limit: limit
        }),
      });

      if (!response.ok) {
        console.error('NLP Search failed:', response.status, response.statusText);
        return null;
      }

      const result: NLPSearchResponse = await response.json();
      
      // Debug completo para ver la estructura
      console.log('🐛 DEBUG - Respuesta completa del backend:', result);
      
      // Mapear la respuesta del backend al formato esperado del frontend
      const mappedResult: NLPSearchResponse = {
        success: result.success,
        processing_time_ms: result.processing_time_ms,
        query: result.query,
        original_query: result.query, 
        products_found: result.products_found,
        user_message: result.message,
        recommendations: result.products || [], // Mapear 'products' a 'recommendations'
        interpretation: result.interpretation || {},
        corrections: result.corrections || { applied: false },
        metadata: result.metadata
      };
      
      // Log de debug para desarrollo
      if (process.env.NODE_ENV === 'development') {
        console.log('🔍 NLP Search Result:', {
          query: mappedResult.query || mappedResult.original_query,
          time: `${mappedResult.processing_time_ms}ms`,
          products: mappedResult.recommendations?.length || 0,
          corrected: mappedResult.corrections?.applied || false
        });
      }

      return mappedResult;
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
  }  /**
   * Convertir respuesta NLP a formato compatible con el frontend
   */
  mapNLPProductsToFrontend(nlpProducts: ProductRecommendation[]): any[] {
    return nlpProducts.map(product => ({
      // Mapeo flexible - soporta tanto formato español como inglés
      id_producto: product.id_producto || product.id,
      nombre: product.nombre || product.name,
      precio: product.precio || product.price,
      cantidad: product.cantidad || product.stock || (product.available ? 10 : 0),
      id_categoria: product.id_categoria || 1,
      imagen: product.imagen || product.image || 'default.jpg',
      categoria: product.categoria || product.category,
      categoria_nombre: product.categoria_nombre || product.category,
      // Propiedades adicionales del NLP
      match_score: product.match_score || product.relevance || 0.8,
      match_reasons: product.match_reasons || [],
      // Propiedades por defecto que espera el frontend
      descripcion: product.descripcion || '',
      // Asegurar disponibilidad
      available: (product.cantidad || product.stock || 0) > 0
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

  /**
   * Obtener URL completa de imagen del producto
   */
  getImageUrl(imageName: string): string {
    if (!imageName || imageName === 'default.jpg') {
      return '/uploads/default.jpg';
    }
    return `/uploads/${imageName}`;
  }
  /**
   * Obtener estadísticas del sistema LCLN
   */
  async getLCLNStats(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/stats`);
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      return null;
    }
  }

  /**
   * Forzar actualización del cache (útil después de agregar productos)
   */
  async refreshCache(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/force-cache-refresh`);
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
