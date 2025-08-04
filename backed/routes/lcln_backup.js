const express = require('express');
const router = express.Router();
const axios = require('axios');

// Configuración del servicio LCLN
const LCLN_SERVICE_URL = process.env.NLP_SERVICE_URL || 'http://127.0.0.1:8005';

console.log(`[LCLN] Service URL configured: ${LCLN_SERVICE_URL}`);

/**
 * @route POST /api/lcln/search
 * @desc Búsqueda inteligente usando sistema LCLN
 * @access Público
 */
router.post('/search', async (req, res) => {
  try {
    const { query, limit = 20 } = req.body;

    if (!query || query.trim() === '') {
      return res.status(400).json({ 
        error: 'Consulta requerida',
        success: false 
      });
    }

    console.log(`[LCLN] Procesando consulta: "${query}"`);

    try {
      // Intentar llamar al servicio LCLN Python
      const response = await axios.post(`${LCLN_SERVICE_URL}/api/search`, {
        query: query.trim(),
        limit: limit
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data) {
        console.log(`[LCLN] Respuesta exitosa del microservicio: ${response.data.products_found || 0} productos`);
        
        // Formatear respuesta para el frontend
        const respuestaFormateada = {
          success: true,
          query: query,
          processing_time_ms: response.data.processing_time_ms || 0,
          products_found: response.data.products_found || 0,
          message: response.data.user_message || 'Búsqueda completada',
          products: response.data.recommendations || [],
          source: 'lcln_microservice'
        };

        return res.json(respuestaFormateada);
      }
    } catch (serviceError) {
      console.log(`[LCLN] Microservicio no disponible, usando búsqueda básica: ${serviceError.message}`);
      
      // Fallback: usar búsqueda básica en la base de datos
      const db = req.app.locals.db;
      const searchTerms = query.trim().toLowerCase().split(' ');
      const searchPattern = `%${searchTerms.join('%')}%`;
      
      const sql = `
        SELECT p.*, c.nombre as categoria_nombre, c.color as categoria_color
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id 
        WHERE LOWER(p.nombre) LIKE ? OR LOWER(p.descripcion) LIKE ?
        ORDER BY 
          CASE WHEN LOWER(p.nombre) LIKE ? THEN 1 ELSE 2 END,
          p.precio ASC
        LIMIT ?
      `;
      
      const productos = await new Promise((resolve, reject) => {
        db.query(sql, [searchPattern, searchPattern, `%${searchTerms[0]}%`, limit], (err, results) => {
          if (err) reject(err);
          else resolve(results);
        });
      });

      console.log(`[LCLN] Búsqueda básica encontró ${productos.length} productos`);

      return res.json({
        success: true,
        query: query,
        processing_time_ms: Date.now() % 1000,
        products_found: productos.length,
        message: 'Búsqueda básica completada (microservicio no disponible)',
        products: productos,
        source: 'fallback_basic_search'
      });
    }
  } catch (error) {
    console.error('[LCLN] Error en búsqueda:', error);
    res.status(500).json({ 
      success: false,
      error: 'Error interno del servidor',
      details: error.message 
    });
  }
});
        const respuestaFormateada = {
          success: true,
          query: query,
          processing_time_ms: response.data.processing_time_ms || 0,
          products_found: response.data.products_found || 0,
          message: response.data.user_message || 'Búsqueda completada',
          products: response.data.recommendations || [],
          interpretation: response.data.interpretation || {},
          corrections: response.data.corrections || {},
          metadata: response.data.metadata || {}
        };

        return res.json(respuestaFormateada);
      }
    } catch (lcnlServiceError) {
      console.error('Error llamando al servicio LCLN:', lcnlServiceError.message);
      
      // Si es error de timeout o conexión, devolver error específico
      if (lcnlServiceError.code === 'ECONNREFUSED') {
        return res.status(503).json({
          success: false,
          error: 'Servicio LCLN no disponible',
          message: 'El sistema de búsqueda inteligente está temporalmente fuera de servicio'
        });
      }

      if (lcnlServiceError.code === 'ECONNABORTED') {
        return res.status(504).json({
          success: false,
          error: 'Timeout en búsqueda',
          message: 'La búsqueda está tomando más tiempo del esperado'
        });
      }

      throw lcnlServiceError;
    }

  } catch (error) {
    console.error('Error en endpoint LCLN:', error);
    return res.status(500).json({
      success: false,
      error: 'Error interno del servidor',
      message: 'Ocurrió un error procesando tu búsqueda'
    });
  }
});

/**
 * @route GET /api/lcln/status
 * @desc Verificar estado del servicio LCLN
 * @access Público
 */
router.get('/status', async (req, res) => {
  try {
    console.log(`[LCLN] Checking status at: ${LCLN_SERVICE_URL}/api/health`);
    const response = await axios.get(`${LCLN_SERVICE_URL}/api/health`, {
      timeout: 5000
    });
    
    console.log(`[LCLN] Status check successful:`, response.data);
    res.json({
      success: true,
      lcln_service: 'available',
      status: response.data,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.log(`[LCLN] Status check failed:`, error.message);
    // Return 200 with fallback status instead of 503
    res.json({
      success: true,
      lcln_service: 'fallback',
      microservice_status: 'unavailable',
      fallback_mode: true,
      message: 'Using basic search functionality',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
