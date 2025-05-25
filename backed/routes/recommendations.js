const express = require('express');
const router = express.Router();
const axios = require('axios');
const { verifyToken } = require('../middlewares/authMiddleware');
const pool = require('../config/db');

// Configuración del servicio de recomendaciones
const RECOMMENDER_SERVICE_URL = 'http://127.0.0.1:8000'; // Force IPv4 loopback

/**
 * @route GET /api/recommendations
 * @desc Obtener recomendaciones para el usuario actual
 * @access Privado
 */
router.get('/', verifyToken, async (req, res) => {
  try {
    const userId = req.userId;

    // Verificar si el usuario existe
    const [user] = await pool.query('SELECT id_usuario FROM usuarios WHERE id_usuario = ?', [userId]);
    
    if (!user || user.length === 0) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    let productos = [];
    
    try {
      // Llamar al microservicio de recomendaciones
      const response = await axios.get(`${RECOMMENDER_SERVICE_URL}/predict/${userId}`, {
        timeout: 5000
      });
      
      if (response.data && response.data.recommendations && response.data.recommendations.length > 0) {
        const recommendedProductIds = response.data.recommendations.map(item => item.id_producto);

        // Obtener información detallada de los productos recomendados
        const [productosRecomendados] = await pool.query(
          `SELECT 
            p.id_producto, 
            p.nombre, 
            p.precio, 
            p.imagen, 
            p.cantidad as stock, 
            c.nombre as categoria 
          FROM productos p
          JOIN categorias c ON p.id_categoria = c.id_categoria
          WHERE p.id_producto IN (?)`,
          [recommendedProductIds]
        );

        // Ordenar productos según el orden de las recomendaciones
        productos = recommendedProductIds.map(id => {
          const producto = productosRecomendados.find(p => p.id_producto === id);
          const recomendacion = response.data.recommendations.find(r => r.id_producto === id);
          
          if (producto && recomendacion) {
            return {
              ...producto,
              score: recomendacion.score
            };
          }
          return null;
        }).filter(Boolean);
      }
    } catch (pythonServiceError) {
      console.log('Python service not available for user recommendations, using fallback:', pythonServiceError.message);
    }

    // Fallback: Si el servicio Python no está disponible, devolver productos populares
    if (productos.length === 0) {
      const [productosFallback] = await pool.query(
        `SELECT 
          p.id_producto, 
          p.nombre, 
          p.precio, 
          p.imagen, 
          p.cantidad as stock, 
          c.nombre as categoria 
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        WHERE p.cantidad > 0
        ORDER BY p.cantidad DESC
        LIMIT 10`
      );
      
      productos = productosFallback.map(producto => ({
        ...producto,
        score: 1.0 // Score por defecto para productos populares
      }));
    }

    res.json({ productos });
  } catch (error) {
    console.error('Error al obtener recomendaciones:', error);
    res.status(500).json({ 
      error: 'Error al procesar recomendaciones',
      mensaje: error.message
    });
  }
});

/**
 * @route GET /api/recommendations/guest
 * @desc Obtener recomendaciones para usuario invitado
 * @access Público
 */
router.get('/guest', async (req, res) => {
  try {
    let productos = [];
    
    try {
      // Intentar obtener recomendaciones del servicio Python
      const response = await axios.get(`${RECOMMENDER_SERVICE_URL}/predict/0`, {
        timeout: 5000
      });
      
      if (response.data && response.data.recommendations && response.data.recommendations.length > 0) {
        const recommendedProductIds = response.data.recommendations.map(item => item.id_producto);

        // Obtener información detallada de los productos recomendados
        const [productosRecomendados] = await pool.query(
          `SELECT 
            p.id_producto, 
            p.nombre, 
            p.precio, 
            p.imagen, 
            p.cantidad as stock, 
            c.nombre as categoria 
          FROM productos p
          JOIN categorias c ON p.id_categoria = c.id_categoria
          WHERE p.id_producto IN (?)`,
          [recommendedProductIds]
        );

        // Ordenar productos según el orden de las recomendaciones
        productos = recommendedProductIds.map(id => {
          const producto = productosRecomendados.find(p => p.id_producto === id);
          const recomendacion = response.data.recommendations.find(r => r.id_producto === id);
          
          if (producto && recomendacion) {
            return {
              ...producto,
              score: recomendacion.score
            };
          }
          return null;
        }).filter(Boolean);
      }
    } catch (pythonServiceError) {
      console.log('Python service not available, using fallback recommendations:', pythonServiceError.message);
    }

    // Fallback: Si el servicio Python no está disponible, devolver productos populares
    if (productos.length === 0) {
      const [productosFallback] = await pool.query(
        `SELECT 
          p.id_producto, 
          p.nombre, 
          p.precio, 
          p.imagen, 
          p.cantidad as stock, 
          c.nombre as categoria 
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        WHERE p.cantidad > 0
        ORDER BY p.cantidad DESC
        LIMIT 10`
      );
      
      productos = productosFallback.map(producto => ({
        ...producto,
        score: 1.0 // Score por defecto para productos populares
      }));
    }

    res.json({ productos });
  } catch (error) {
    console.error('Error al obtener recomendaciones para invitado:', error);
    res.status(500).json({ 
      error: 'Error al procesar recomendaciones para invitado',
      mensaje: error.message
    });
  }
});

/**
 * @route GET /api/recommendations/health
 * @desc Verificar estado del servicio de recomendaciones
 * @access Público
 */
router.get('/health', async (req, res) => {
  try {
    const response = await axios.get(`${RECOMMENDER_SERVICE_URL}/health`, {
      timeout: 5000
    });
    res.json({ 
      ...response.data, 
      python_service: 'available',
      fallback: false 
    });
  } catch (error) {
    res.status(200).json({ 
      status: 'ok',
      python_service: 'unavailable',
      fallback: true,
      message: 'Using fallback recommendations',
      error: error.message
    });
  }
});

module.exports = router;