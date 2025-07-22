const express = require('express');
const router = express.Router();
const { BusquedaSemanticaLCLN } = require('../semantic_search_engine');

// 🧠 Instancia del motor de búsqueda semántica
const buscadorSemantico = new BusquedaSemanticaLCLN();

/**
 * 🔍 API de Búsqueda Semántica LCLN Mejorada
 * POST /api/search/semantic
 * 
 * Body: {
 *   "query": "fruta fresca",
 *   "limit": 10,
 *   "include_analysis": true
 * }
 * 
 * Response: {
 *   "success": true,
 *   "productos": [...],
 *   "analisis": {...},
 *   "metadata": {...}
 * }
 */
router.post('/semantic', async (req, res) => {
    try {
        const { query, limit = 10, include_analysis = true } = req.body;
        
        console.log(`🔍 API: Búsqueda semántica para: "${query}"`);
        
        // Validar entrada
        if (!query || typeof query !== 'string' || query.trim().length === 0) {
            return res.status(400).json({
                success: false,
                error: 'Query es requerido y debe ser una cadena no vacía',
                code: 'INVALID_QUERY',
                emoji: '❌'
            });
        }
        
        // Ejecutar búsqueda semántica
        const resultado = await buscadorSemantico.buscarProductosSemantico(query.trim());
        
        // Limitar resultados si se especifica
        const productos = resultado.productos.slice(0, parseInt(limit));
        
        // Preparar respuesta
        const respuesta = {
            success: true,
            productos: productos.map(producto => ({
                id: producto.id_producto,
                nombre: producto.nombre,
                precio: producto.precio,
                categoria: producto.categoria,
                emoji: producto.emoji,
                imagen: producto.imagen,
                cantidad: producto.cantidad,
                puntuacion: Math.round(producto.puntuacion * 10) / 10,
                coincidencias: producto.coincidencias,
                cumple_precio: producto.cumple_precio
            })),
            metadata: {
                total_encontrados: resultado.productos.length,
                limite_aplicado: limit,
                tiempo_ms: resultado.tiempo_ms,
                timestamp: new Date().toISOString()
            }
        };
        
        // Incluir análisis detallado si se solicita
        if (include_analysis && resultado.analisis) {
            respuesta.analisis = {
                consulta_original: resultado.analisis.consulta_original,
                consulta_normalizada: resultado.analisis.consulta_normalizada,
                categoria_semantica: resultado.analisis.categoria_semantica,
                filtro_precio: resultado.analisis.filtro_precio,
                contradicciones: resultado.analisis.contradicciones,
                estadisticas: {
                    productos_analizados: resultado.analisis.total_productos_analizados,
                    productos_encontrados: resultado.analisis.productos_encontrados,
                    tiempo_procesamiento_ms: resultado.analisis.tiempo_ms
                }
            };
        }
        
        console.log(`✅ API: ${productos.length} productos encontrados en ${resultado.tiempo_ms}ms`);
        
        res.json(respuesta);
        
    } catch (error) {
        console.error('❌ Error en búsqueda semántica:', error);
        
        res.status(500).json({
            success: false,
            error: 'Error interno del servidor en búsqueda semántica',
            code: 'SEMANTIC_SEARCH_ERROR',
            emoji: '💥',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

/**
 * 🎯 API de Análisis Semántico Sin Búsqueda
 * POST /api/search/analyze
 * 
 * Solo analiza la consulta sin ejecutar búsqueda completa
 * Útil para autocompletado y sugerencias
 */
router.post('/analyze', async (req, res) => {
    try {
        const { query } = req.body;
        
        if (!query || typeof query !== 'string') {
            return res.status(400).json({
                success: false,
                error: 'Query es requerido',
                code: 'INVALID_QUERY'
            });
        }
        
        // Solo análisis semántico
        const categoriaSemantica = buscadorSemantico.analizador.detectarCategoriaSemantica(query);
        const filtroPrecio = buscadorSemantico.analizador.detectarFiltroPrecio(query);
        const consultaNormalizada = buscadorSemantico.normalizarTexto(query);
        
        res.json({
            success: true,
            consulta_original: query,
            consulta_normalizada: consultaNormalizada,
            categoria_semantica: categoriaSemantica,
            filtro_precio: filtroPrecio,
            sugerencias: generarSugerencias(query, categoriaSemantica, filtroPrecio),
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('❌ Error en análisis semántico:', error);
        
        res.status(500).json({
            success: false,
            error: 'Error en análisis semántico',
            code: 'ANALYSIS_ERROR'
        });
    }
});

/**
 * 💡 Generar sugerencias basadas en análisis semántico
 */
function generarSugerencias(query, categoriaSemantica, filtroPrecio) {
    const sugerencias = [];
    const queryNorm = query.toLowerCase().trim();
    
    // Sugerencias por categoría
    if (categoriaSemantica) {
        const categoria = categoriaSemantica.categoria;
        const emoji = categoriaSemantica.emoji;
        
        switch (categoria) {
            case 'frutas':
                sugerencias.push(`${emoji} frutas frescas`);
                sugerencias.push(`${emoji} ${queryNorm} natural`);
                break;
            case 'bebidas':
                sugerencias.push(`${emoji} ${queryNorm} fría`);
                sugerencias.push(`${emoji} ${queryNorm} sin azúcar`);
                break;
            case 'snacks':
                sugerencias.push(`${emoji} ${queryNorm} picante`);
                sugerencias.push(`${emoji} ${queryNorm} familiar`);
                break;
            case 'golosinas':
                sugerencias.push(`${emoji} ${queryNorm} dulce`);
                sugerencias.push(`${emoji} chocolate ${queryNorm}`);
                break;
            case 'papeleria':
                sugerencias.push(`${emoji} ${queryNorm} escolar`);
                sugerencias.push(`${emoji} ${queryNorm} profesional`);
                break;
        }
    }
    
    // Sugerencias por precio
    if (!filtroPrecio) {
        sugerencias.push(`💰 ${queryNorm} barato`);
        sugerencias.push(`💸 ${queryNorm} económico`);
    }
    
    // Sugerencias específicas por término
    if (queryNorm.includes('agua') || queryNorm.includes('aguita')) {
        sugerencias.push('💧 agua natural');
        sugerencias.push('💧 agua mineral');
    }
    
    if (queryNorm.includes('chetos') || queryNorm.includes('cheetos')) {
        sugerencias.push('🌶️ cheetos fuego');
        sugerencias.push('🧀 cheetos queso');
    }
    
    return sugerencias.slice(0, 5); // Máximo 5 sugerencias
}

/**
 * 📊 API de Estadísticas del Sistema Semántico
 * GET /api/search/stats
 */
router.get('/stats', async (req, res) => {
    try {
        // Obtener estadísticas del cache
        const productos = await buscadorSemantico.obtenerProductosCache();
        
        const estadisticas = {
            total_productos: productos.length,
            productos_por_categoria: {},
            productos_con_emojis: productos.filter(p => p.emoji !== '📦').length,
            productos_con_sinonimos: productos.filter(p => p.lista_sinonimos.length > 0).length,
            promedio_sinonimos_por_producto: 0,
            cache_info: {
                activo: !!buscadorSemantico.cacheProductos,
                ultima_actualizacion: buscadorSemantico.cacheExpiry,
                productos_en_cache: buscadorSemantico.cacheProductos?.length || 0
            }
        };
        
        // Contar productos por categoría
        for (const producto of productos) {
            const categoria = producto.categoria || 'Sin categoría';
            estadisticas.productos_por_categoria[categoria] = 
                (estadisticas.productos_por_categoria[categoria] || 0) + 1;
        }
        
        // Promedio de sinónimos
        const totalSinonimos = productos.reduce((sum, p) => sum + p.lista_sinonimos.length, 0);
        estadisticas.promedio_sinonimos_por_producto = 
            Math.round((totalSinonimos / productos.length) * 100) / 100;
        
        res.json({
            success: true,
            estadisticas,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('❌ Error obteniendo estadísticas:', error);
        
        res.status(500).json({
            success: false,
            error: 'Error obteniendo estadísticas del sistema',
            code: 'STATS_ERROR'
        });
    }
});

module.exports = router;
