const express = require('express');
const router = express.Router();
const axios = require('axios');

// Configuración del servicio LCLN
const LCLN_SERVICE_URL = 'http://127.0.0.1:8007'; // Puerto del servicio LCLN AFD limpio

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
      // Llamar al servicio LCLN Python
      const response = await axios.post(`${LCLN_SERVICE_URL}/api/nlp/analyze`, {
        query: query.trim(),
        limit: limit
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data) {
        console.log(`[LCLN] Respuesta exitosa: ${response.data.products_found || 0} productos`);
        
        // Formatear respuesta para el frontend
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
    const response = await axios.get(`${LCLN_SERVICE_URL}/api/health`, {
      timeout: 5000
    });
    
    res.json({
      success: true,
      lcln_service: 'available',
      status: response.data,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      success: false,
      lcln_service: 'unavailable',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
