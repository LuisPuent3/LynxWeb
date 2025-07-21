const express = require('express');
const router = express.Router();
const db = require('../config/db');

// ================================================
// ENDPOINTS PARA GESTIÓN DE SINÓNIMOS (SIN AUTH - SOLO PRUEBAS)
// ================================================

// GET - Obtener sinónimos de un producto
router.get('/producto/:id', async (req, res) => {
    try {
        const { id } = req.params;
        
        console.log(`[TEST] Obteniendo sinónimos para producto ${id}`);
        
        const query = `
            SELECT id, producto_id, sinonimo, popularidad, precision_score, fuente, activo, 
                   DATE_FORMAT(fecha_creacion, '%Y-%m-%d %H:%i:%s') as fecha_creacion,
                   DATE_FORMAT(fecha_ultima_actualizacion, '%Y-%m-%d %H:%i:%s') as fecha_ultima_actualizacion
            FROM producto_sinonimos 
            WHERE producto_id = ? AND activo = true
            ORDER BY popularidad DESC, precision_score DESC
        `;
        
        const [results] = await db.execute(query, [id]);
        
        console.log(`[TEST] Encontrados ${results.length} sinónimos`);
        res.json(results);
        
    } catch (error) {
        console.error('[TEST] Error obteniendo sinónimos:', error);
        res.status(500).json({ 
            error: 'Error interno del servidor',
            detail: error.message 
        });
    }
});

// POST - Agregar nuevo sinónimo
router.post('/', async (req, res) => {
    try {
        const { producto_id, sinonimo, fuente = 'admin' } = req.body;
        
        console.log(`[TEST] Agregando sinónimo "${sinonimo}" para producto ${producto_id}`);
        
        // Validaciones
        if (!producto_id || !sinonimo) {
            return res.status(400).json({ 
                error: 'Datos requeridos faltantes',
                detail: 'producto_id y sinonimo son requeridos'
            });
        }

        // Verificar duplicados
        const checkQuery = 'SELECT id FROM producto_sinonimos WHERE producto_id = ? AND sinonimo = ? AND activo = true';
        const [existing] = await db.execute(checkQuery, [producto_id, sinonimo.toLowerCase()]);
        
        if (existing.length > 0) {
            return res.status(409).json({
                error: 'Sinónimo duplicado',
                detail: 'Este sinónimo ya existe para este producto'
            });
        }

        // Insertar sinónimo
        const insertQuery = `
            INSERT INTO producto_sinonimos 
            (producto_id, sinonimo, popularidad, precision_score, fuente, activo, fecha_creacion, fecha_ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, NOW(), NOW())
        `;
        
        const [result] = await db.execute(insertQuery, [
            producto_id,
            sinonimo.toLowerCase(),
            0, // popularidad inicial
            0.8, // precision_score inicial
            fuente,
            true
        ]);

        console.log(`[TEST] Sinónimo agregado con ID ${result.insertId}`);
        
        res.status(201).json({ 
            success: true,
            id: result.insertId,
            message: 'Sinónimo agregado correctamente'
        });

    } catch (error) {
        console.error('[TEST] Error agregando sinónimo:', error);
        res.status(500).json({ 
            error: 'Error interno del servidor',
            detail: error.message 
        });
    }
});

// GET - Obtener sugerencias para un producto
router.get('/sugerencias/producto/:id', async (req, res) => {
    try {
        const { id } = req.params;
        
        console.log(`[TEST] Obteniendo sugerencias para producto ${id}`);
        
        const query = `
            SELECT 
                termino_busqueda,
                COUNT(*) as frecuencia,
                AVG(clicks) as promedio_clicks,
                MAX(fecha_busqueda) as ultima_busqueda
            FROM busqueda_metricas 
            WHERE producto_id = ? 
              AND termino_busqueda NOT IN (
                  SELECT sinonimo FROM producto_sinonimos 
                  WHERE producto_id = ? AND activo = true
              )
            GROUP BY termino_busqueda 
            HAVING frecuencia >= 2 OR promedio_clicks >= 3
            ORDER BY frecuencia DESC, promedio_clicks DESC 
            LIMIT 10
        `;
        
        const [results] = await db.execute(query, [id, id]);
        
        console.log(`[TEST] Encontradas ${results.length} sugerencias`);
        
        res.json({
            producto_id: id,
            sugerencias: results
        });
        
    } catch (error) {
        console.error('[TEST] Error obteniendo sugerencias:', error);
        res.status(500).json({ 
            error: 'Error interno del servidor',
            detail: error.message 
        });
    }
});

module.exports = router;
