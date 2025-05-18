const express = require('express');
const router = express.Router();
const axios = require('axios');
const verifyToken = require('../middleware/verify-token');
const pool = require('../config/database');

// Configuración del servicio de recomendaciones
const RECOMMENDER_SERVICE_URL = process.env.RECOMMENDER_SERVICE_URL || 'http://localhost:8000';

/**
 * @route GET /api/recommendations
 * @desc Obtener recomendaciones para el usuario actual
 * @access Privado
 */
router.get('/', verifyToken, async (req, res) => {
  try {
    const userId = req.userId;

    // Verificar si el usuario existe
    const [user] = await pool.query('SELECT id_usuario FROM Usuarios WHERE id_usuario = ?', [userId]);
    
    if (!user || user.length === 0) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    // Llamar al microservicio de recomendaciones
    const response = await axios.get(`${RECOMMENDER_SERVICE_URL}/predict/${userId}`);
    
    if (!response.data || !response.data.recommendations) {
      return res.status(500).json({ error: 'Error al obtener recomendaciones' });
    }

    const recommendedProductIds = response.data.recommendations.map(item => item.id_producto);

    // Si no hay recomendaciones, devolver array vacío
    if (recommendedProductIds.length === 0) {
      return res.json({ productos: [] });
    }

    // Obtener información detallada de los productos recomendados
    const [productos] = await pool.query(
      `SELECT 
        p.id_producto, 
        p.nombre, 
        p.precio, 
        p.imagen, 
        p.cantidad as stock, 
        c.nombre as categoria 
      FROM Productos p
      JOIN Categorias c ON p.id_categoria = c.id_categoria
      WHERE p.id_producto IN (?)`,
      [recommendedProductIds]
    );

    // Ordenar productos según el orden de las recomendaciones (mantener scores originales)
    const recomendacionesConDetalles = recommendedProductIds.map(id => {
      const producto = productos.find(p => p.id_producto === id);
      const recomendacion = response.data.recommendations.find(r => r.id_producto === id);
      
      if (producto && recomendacion) {
        return {
          ...producto,
          score: recomendacion.score
        };
      }
      return null;
    }).filter(Boolean);

    res.json({ productos: recomendacionesConDetalles });
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
    // Para usuarios invitados, simplemente obtenemos productos populares
    // El ID 0 está reservado para indicar al servicio que devuelva productos populares
    const response = await axios.get(`${RECOMMENDER_SERVICE_URL}/predict/0`);
    
    if (!response.data || !response.data.recommendations) {
      return res.status(500).json({ error: 'Error al obtener recomendaciones' });
    }

    const recommendedProductIds = response.data.recommendations.map(item => item.id_producto);

    // Si no hay recomendaciones, devolver array vacío
    if (recommendedProductIds.length === 0) {
      return res.json({ productos: [] });
    }

    // Obtener información detallada de los productos recomendados
    const [productos] = await pool.query(
      `SELECT 
        p.id_producto, 
        p.nombre, 
        p.precio, 
        p.imagen, 
        p.cantidad as stock, 
        c.nombre as categoria 
      FROM Productos p
      JOIN Categorias c ON p.id_categoria = c.id_categoria
      WHERE p.id_producto IN (?)`,
      [recommendedProductIds]
    );

    // Ordenar productos según el orden de las recomendaciones
    const recomendacionesConDetalles = recommendedProductIds.map(id => {
      const producto = productos.find(p => p.id_producto === id);
      const recomendacion = response.data.recommendations.find(r => r.id_producto === id);
      
      if (producto && recomendacion) {
        return {
          ...producto,
          score: recomendacion.score
        };
      }
      return null;
    }).filter(Boolean);

    res.json({ productos: recomendacionesConDetalles });
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
    const response = await axios.get(`${RECOMMENDER_SERVICE_URL}/health`);
    res.json(response.data);
  } catch (error) {
    res.status(503).json({ 
      status: 'error',
      message: 'Servicio de recomendaciones no disponible',
      error: error.message
    });
  }
});

module.exports = router; 