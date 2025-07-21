/**
 * RUTAS PARA GESTIÓN DE SINÓNIMOS - SISTEMA LCLN v2.0
 * 
 * Endpoints para administración de sinónimos de productos:
 * - CRUD completo de sinónimos
 * - Sugerencias automáticas basadas en métricas
 * - Gestión de atributos de producto
 * - Estadísticas de popularidad
 * 
 * Autor: Sistema LCLN v2.0
 * Fecha: Julio 2025
 */

const express = require('express');
const router = express.Router();
const { verifyToken } = require('../middlewares/authMiddleware');
const db = require('../config/db');

// ================================================
// ENDPOINTS PRINCIPALES - SINÓNIMOS
// ================================================

/**
 * GET /api/admin/sinonimos/producto/:id
 * Obtener todos los sinónimos de un producto específico
 */
router.get('/producto/:id', verifyToken, async (req, res) => {
  try {
    const { id: productoId } = req.params;
    console.log('🔍 Buscando sinónimos para producto ID:', productoId);
    
    const query = `
      SELECT 
        s.id,
        s.producto_id,
        s.sinonimo,
        s.popularidad,
        s.precision_score,
        s.fuente,
        s.activo,
        s.fecha_creacion,
        s.fecha_ultima_actualizacion,
        p.nombre as producto_nombre
      FROM producto_sinonimos s
      INNER JOIN productos p ON s.producto_id = p.id_producto
      WHERE s.producto_id = ? AND s.activo = 1
      ORDER BY s.popularidad DESC, s.precision_score DESC
    `;
    
    const sinonimos = await db.query(query, [productoId]);
    console.log('📝 Sinónimos encontrados:', sinonimos.length, sinonimos);
    
    // El resultado de db.query devuelve [resultados, metadata], necesitamos solo los resultados
    const sinonimosList = Array.isArray(sinonimos[0]) ? sinonimos[0] : sinonimos;
    console.log('📋 Lista procesada de sinónimos:', sinonimosList.length, sinonimosList);
    
    res.json(sinonimosList);
  } catch (error) {
    console.error('Error al obtener sinónimos:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error interno del servidor',
      detail: error.message 
    });
  }
});

/**
 * POST /api/admin/sinonimos
 * Crear un nuevo sinónimo para un producto
 */
router.post('/', verifyToken, async (req, res) => {
  try {
    console.log('🔥 POST /sinonimos recibido:', req.body);
    const { producto_id, sinonimo, fuente = 'admin' } = req.body;
    
    // Validaciones básicas
    if (!producto_id || !sinonimo) {
      return res.status(400).json({
        success: false,
        message: 'Producto ID y sinónimo son requeridos',
        detail: 'Faltan campos obligatorios'
      });
    }
    
    if (sinonimo.length < 2 || sinonimo.length > 255) {
      return res.status(400).json({
        success: false,
        message: 'El sinónimo debe tener entre 2 y 255 caracteres',
        detail: 'Longitud de sinónimo inválida'
      });
    }
    
    if (!/^[a-záéíóúñ\s]+$/i.test(sinonimo)) {
      return res.status(400).json({
        success: false,
        message: 'El sinónimo solo puede contener letras y espacios',
        detail: 'Caracteres no válidos en sinónimo'
      });
    }
    
    // Verificar que el producto existe
    const productoExists = await db.query(
      'SELECT id_producto, nombre FROM productos WHERE id_producto = ?', 
      [producto_id]
    );
    
    if (productoExists.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Producto no encontrado',
        detail: `No existe producto con ID ${producto_id}`
      });
    }
    
    // Verificar duplicados - solo entre sinónimos ACTIVOS
    const duplicateCheck = await db.query(
      'SELECT id FROM producto_sinonimos WHERE producto_id = ? AND LOWER(sinonimo) = LOWER(?) AND activo = 1',
      [producto_id, sinonimo.trim()]
    );
    
    console.log('🔍 Verificando duplicados para:', sinonimo.trim());
    console.log('🔍 Resultado de duplicateCheck:', duplicateCheck);
    console.log('🔍 duplicateCheck[0]:', duplicateCheck[0]);
    console.log('🔍 duplicateCheck[0].length:', duplicateCheck[0].length);
    
    if (duplicateCheck[0].length > 0) {
      return res.status(409).json({
        success: false,
        message: 'Este sinónimo ya existe para este producto',
        detail: 'Sinónimo duplicado'
      });
    }
    
    // Crear el sinónimo
    const insertQuery = `
      INSERT INTO producto_sinonimos (
        producto_id, 
        sinonimo, 
        popularidad, 
        precision_score, 
        fuente, 
        activo,
        fecha_creacion
      ) VALUES (?, ?, 0, 1.0, ?, 1, NOW())
    `;
    
    const result = await db.query(insertQuery, [
      producto_id, 
      sinonimo.trim().toLowerCase(), 
      fuente
    ]);

    console.log('✅ Sinónimo insertado exitosamente:', result.insertId);

    res.status(201).json({
      success: true,
      message: 'Sinónimo creado exitosamente',
      data: {
        id: result.insertId,
        producto_id,
        sinonimo: sinonimo.trim().toLowerCase(),
        fuente
      }
    });
    
  } catch (error) {
    console.error('Error al crear sinónimo:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error interno del servidor',
      detail: error.message 
    });
  }
});

/**
 * DELETE /api/admin/sinonimos/:id
 * Eliminar un sinónimo específico (soft delete)
 */
router.delete('/:id', verifyToken, async (req, res) => {
  try {
    const { id } = req.params;
    
    // Verificar que el sinónimo existe
    const sinonimoExists = await db.query(
      'SELECT id, sinonimo FROM producto_sinonimos WHERE id = ? AND activo = 1',
      [id]
    );
    
    if (sinonimoExists.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Sinónimo no encontrado',
        detail: `No existe sinónimo con ID ${id}`
      });
    }
    
    // Soft delete - marcar como inactivo
    await db.query(
      'UPDATE producto_sinonimos SET activo = 0, fecha_ultima_actualizacion = NOW() WHERE id = ?',
      [id]
    );
    
    res.json({
      success: true,
      message: 'Sinónimo eliminado exitosamente',
      data: {
        id: parseInt(id),
        sinonimo: sinonimoExists[0].sinonimo
      }
    });
    
  } catch (error) {
    console.error('Error al eliminar sinónimo:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error interno del servidor',
      detail: error.message 
    });
  }
});

// ================================================
// ENDPOINTS DE SUGERENCIAS AUTOMÁTICAS
// ================================================

/**
 * GET /api/admin/sinonimos/sugerencias/producto/:id
 * Obtener sugerencias de sinónimos basadas en métricas de búsqueda
 */
router.get('/sugerencias/producto/:id', verifyToken, async (req, res) => {
  try {
    const { id: productoId } = req.params;
    const { limit = 10 } = req.query;
    console.log('💡 Buscando sugerencias para producto ID:', productoId);
    
    const query = `
      SELECT DISTINCT
        bm.termino_busqueda,
        COUNT(*) as frecuencia,
        AVG(bm.clicks) as promedio_clicks,
        MAX(bm.fecha_busqueda) as ultima_busqueda,
        'user_search' as tipo
      FROM busqueda_metricas bm
      WHERE bm.producto_id = ?
        AND bm.termino_busqueda IS NOT NULL
        AND bm.termino_busqueda != ''
        AND bm.clicks > 0
        AND bm.termino_busqueda NOT IN (
          SELECT LOWER(sinonimo) 
          FROM producto_sinonimos 
          WHERE producto_id = ? AND activo = 1
        )
        AND bm.termino_busqueda NOT IN (
          SELECT LOWER(nombre) 
          FROM productos 
          WHERE id_producto = ?
        )
      GROUP BY bm.termino_busqueda
      HAVING frecuencia >= 2 AND promedio_clicks >= 1.0
      ORDER BY frecuencia DESC, promedio_clicks DESC
      LIMIT ?
    `;
    
    const sugerencias = await db.query(query, [productoId, productoId, productoId, parseInt(limit)]);
    console.log('💡 Sugerencias encontradas:', sugerencias.length, sugerencias);
    
    // El resultado de db.query devuelve [resultados, metadata], necesitamos solo los resultados
    const sugerenciasList = Array.isArray(sugerencias[0]) ? sugerencias[0] : sugerencias;
    console.log('💡 Lista procesada de sugerencias:', sugerenciasList.length, sugerenciasList);
    
    res.json({
      success: true,
      sugerencias: sugerenciasList || [],
      producto_id: productoId,
      total_sugerencias: sugerencias?.length || 0
    });
    
  } catch (error) {
    console.error('Error al obtener sugerencias:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error interno del servidor',
      detail: error.message,
      sugerencias: []
    });
  }
});

// ================================================
// ENDPOINTS DE ATRIBUTOS
// ================================================

/**
 * GET /api/admin/sinonimos/producto/:id/atributos
 * Obtener atributos configurados para un producto
 */
router.get('/producto/:id/atributos', verifyToken, async (req, res) => {
  try {
    const { id: productoId } = req.params;
    
    const query = `
      SELECT 
        id,
        producto_id,
        atributo,
        valor,
        intensidad
      FROM producto_atributos
      WHERE producto_id = ?
      ORDER BY atributo ASC
    `;
    
    const atributos = await db.query(query, [productoId]);
    
    res.json(atributos || []);
    
  } catch (error) {
    console.error('Error al obtener atributos:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error interno del servidor',
      detail: error.message,
      data: []
    });
  }
});

/**
 * POST /api/admin/sinonimos/producto/:id/atributos
 * Crear o actualizar atributos de un producto
 */
router.post('/producto/:id/atributos', verifyToken, async (req, res) => {
  try {
    const { id: productoId } = req.params;
    const { atributo, valor, intensidad = 1 } = req.body;
    
    if (!atributo || typeof valor !== 'boolean') {
      return res.status(400).json({
        success: false,
        message: 'Atributo y valor son requeridos',
        detail: 'Faltan campos obligatorios'
      });
    }
    
    // Verificar que el producto existe
    const productoExists = await db.query(
      'SELECT id_producto FROM productos WHERE id_producto = ?', 
      [productoId]
    );
    
    if (productoExists.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Producto no encontrado'
      });
    }
    
    // Insertar o actualizar atributo
    const upsertQuery = `
      INSERT INTO producto_atributos (producto_id, atributo, valor, intensidad)
      VALUES (?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE 
        valor = VALUES(valor),
        intensidad = VALUES(intensidad)
    `;
    
    await db.query(upsertQuery, [productoId, atributo, valor, intensidad]);
    
    res.json({
      success: true,
      message: 'Atributo actualizado exitosamente',
      data: { producto_id: productoId, atributo, valor, intensidad }
    });
    
  } catch (error) {
    console.error('Error al crear/actualizar atributo:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error interno del servidor',
      detail: error.message 
    });
  }
});

// ================================================
// ENDPOINTS DE ESTADÍSTICAS
// ================================================

/**
 * GET /api/admin/sinonimos/estadisticas/:id
 * Obtener estadísticas detalladas de sinónimos de un producto
 */
router.get('/estadisticas/:id', verifyToken, async (req, res) => {
  try {
    const { id: productoId } = req.params;
    
    // Estadísticas generales
    const statsQuery = `
      SELECT 
        COUNT(*) as total_sinonimos,
        SUM(popularidad) as total_busquedas,
        AVG(precision_score) as precision_promedio,
        COUNT(CASE WHEN fuente = 'admin' THEN 1 END) as admin_count,
        COUNT(CASE WHEN fuente = 'auto_learning' THEN 1 END) as auto_count,
        COUNT(CASE WHEN fuente = 'user_feedback' THEN 1 END) as user_count
      FROM producto_sinonimos
      WHERE producto_id = ? AND activo = 1
    `;
    
    const stats = await db.query(statsQuery, [productoId]);
    
    // Top 5 sinónimos más populares
    const topQuery = `
      SELECT sinonimo, popularidad, precision_score, fuente
      FROM producto_sinonimos
      WHERE producto_id = ? AND activo = 1
      ORDER BY popularidad DESC, precision_score DESC
      LIMIT 5
    `;
    
    const top_sinonimos = await db.query(topQuery, [productoId]);
    
    res.json({
      success: true,
      estadisticas: stats[0] || {},
      top_sinonimos: top_sinonimos || [],
      producto_id: productoId
    });
    
  } catch (error) {
    console.error('Error al obtener estadísticas:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error interno del servidor',
      detail: error.message 
    });
  }
});

module.exports = router;
