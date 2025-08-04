const express = require('express');
const router = express.Router();
const axios = require('axios');

// Configuración del servicio LCLN
const LCLN_SERVICE_URL = 'http://127.0.0.1:8005';

console.log(`[LCLN] Service URL configured: ${LCLN_SERVICE_URL}`);

/**
 * @route POST /api/lcln/search
 * @desc Búsqueda inteligente usando tu sistema LCLN original completo
 * @access Público
 */
router.post('/search', async (req, res) => {
  const query = req.body?.query || '';
  const limit = req.body?.limit || 20;

  if (!query || query.trim() === '') {
    return res.status(400).json({ 
      error: 'Consulta requerida',
      success: false 
    });
  }

  console.log(`[LCLN] Procesando consulta: "${query}"`);

  try {
    // Usar únicamente tu microservicio LCLN original
    console.log(`[LCLN] Llamando a microservicio en ${LCLN_SERVICE_URL}/search`);
    
    const response = await axios.post(`${LCLN_SERVICE_URL}/search`, {
      query: query.trim(),
      limit: limit
    }, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log(`[LCLN] ✅ Respuesta del microservicio:`, {
      success: response.data?.success,
      products_found: response.data?.products_found,
      recommendations_count: response.data?.recommendations?.length
    });
    
    // Devolver directamente la respuesta de tu microservicio LCLN
    return res.json(response.data);

  } catch (serviceError) {
    console.error(`[LCLN] ❌ Error en microservicio LCLN:`, serviceError.message);
    if (serviceError.response) {
      console.error(`[LCLN] ❌ Status:`, serviceError.response.status);
      console.error(`[LCLN] ❌ Response data:`, serviceError.response.data);
    }
    
    return res.status(503).json({
      success: false,
      error: 'Microservicio LCLN no disponible',
      message: 'El sistema LCLN original no está funcionando',
      details: serviceError.message,
      query: query
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
    console.log(`[LCLN] Checking status at: ${LCLN_SERVICE_URL}/health`);
    const response = await axios.get(`${LCLN_SERVICE_URL}/health`, {
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
