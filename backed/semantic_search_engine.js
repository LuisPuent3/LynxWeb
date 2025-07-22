const { AnalizadorSemanticoInteligente } = require('./semantic_analyzer_with_emojis');
const db = require('./config/db');

class BusquedaSemanticaLCLN {
    constructor() {
        this.analizador = new AnalizadorSemanticoInteligente();
        
        // 📊 Cache de productos
        this.cacheProductos = null;
        this.cacheExpiry = null;
    }
    
    // 🔧 Normalizar texto (igual que Python)
    normalizarTexto(texto) {
        if (!texto) return "";
        
        const caracteresEspeciales = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U', 'Ñ': 'N'
        };
        
        let textoNormalizado = texto.toLowerCase().trim();
        
        // Reemplazar caracteres especiales
        for (const [especial, normal] of Object.entries(caracteresEspeciales)) {
            textoNormalizado = textoNormalizado.replace(new RegExp(especial, 'g'), normal);
        }
        
        // Remover caracteres no alfanuméricos excepto espacios
        textoNormalizado = textoNormalizado.replace(/[^a-zA-Z0-9\\s]/g, ' ');
        
        // Normalizar espacios
        textoNormalizado = textoNormalizado.replace(/\\s+/g, ' ').trim();
        
        return textoNormalizado;
    }
    
    // 📊 Obtener productos con cache
    async obtenerProductosCache() {
        const now = new Date();
        
        // Verificar cache (5 minutos)
        if (this.cacheProductos && this.cacheExpiry && 
            (now - this.cacheExpiry) < 300000) {
            return this.cacheProductos;
        }
        
        try {
            const [productos] = await db.query(`
                SELECT 
                    p.id_producto,
                    p.nombre,
                    p.precio,
                    p.cantidad,
                    p.imagen,
                    c.nombre as categoria,
                    c.id_categoria,
                    GROUP_CONCAT(DISTINCT ps.sinonimo SEPARATOR ', ') as sinonimos,
                    AVG(ps.popularidad) as popularidad_promedio
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria  
                LEFT JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id AND ps.activo = 1
                GROUP BY p.id_producto, p.nombre, p.precio, p.cantidad, p.imagen, c.nombre, c.id_categoria
                ORDER BY p.nombre
            `);
            
            // Procesar productos
            const productosProcessados = productos.map(producto => {
                if (producto.sinonimos) {
                    producto.lista_sinonimos = producto.sinonimos.split(', ').map(s => s.trim());
                } else {
                    producto.lista_sinonimos = [];
                }
                
                // Detectar categoría semántica
                const categoriaSemantica = this.analizador.detectarCategoriaSemantica(producto.nombre);
                if (categoriaSemantica) {
                    producto.categoria_semantica = categoriaSemantica;
                    producto.emoji = categoriaSemantica.emoji;
                } else {
                    producto.emoji = '📦';
                }
                
                return producto;
            });
            
            this.cacheProductos = productosProcessados;
            this.cacheExpiry = now;
            
            return productosProcessados;
            
        } catch (error) {
            console.error('❌ Error al obtener productos:', error.message);
            return [];
        }
    }
    
    // 🔍 Búsqueda semántica principal
    async buscarProductosSemantico(consulta) {
        const inicio = Date.now();
        
        console.log(`🔍 === BÚSQUEDA SEMÁNTICA MEJORADA ===`);
        console.log(`📝 Consulta original: "${consulta}"`);
        
        // PASO 0: Normalización y análisis semántico
        const consultaNormalizada = this.normalizarTexto(consulta);
        console.log(`🔧 Consulta normalizada: "${consultaNormalizada}"`);
        
        // PASO 0.5: Detección de contexto semántico
        const categoriaSemantica = this.analizador.detectarCategoriaSemantica(consulta);
        if (categoriaSemantica) {
            console.log(`${categoriaSemantica.emoji} Categoría detectada: ${categoriaSemantica.categoria} (confianza: ${(categoriaSemantica.confianza*100).toFixed(1)}%)`);
        }
        
        const filtroPrecio = this.analizador.detectarFiltroPrecio(consulta);
        if (filtroPrecio) {
            console.log(`${filtroPrecio.emoji} Filtro precio: ≤ $${filtroPrecio.precioMax} (${filtroPrecio.palabrasDetectadas.join(', ')})`);
        }
        
        // PASO 1: Obtener productos
        const productos = await this.obtenerProductosCache();
        if (!productos.length) {
            return { productos: [], tiempo_ms: 0, analisis: {} };
        }
        
        console.log(`📦 Productos en base de datos: ${productos.length}`);
        
        // PASO 1.5: Búsqueda multi-criterio
        const resultadosPonderados = [];
        const palabrasBusqueda = consultaNormalizada.split(' ');
        
        for (const producto of productos) {
            let puntuacionTotal = 0;
            const coincidencias = [];
            
            // Datos del producto normalizados
            const nombreNorm = this.normalizarTexto(producto.nombre);
            const categoriaNorm = this.normalizarTexto(producto.categoria || '');
            
            // 🎯 CRITERIO 1: Coincidencia exacta de nombre (peso 50)
            if (consultaNormalizada === nombreNorm) {
                puntuacionTotal += 50;
                coincidencias.push("nombre_exacto");
            }
            
            // 🎯 CRITERIO 2: Palabras en nombre (peso 30)
            for (const palabra of palabrasBusqueda) {
                if (nombreNorm.includes(palabra)) {
                    puntuacionTotal += 30;
                    coincidencias.push(`nombre_contiene_${palabra}`);
                }
            }
            
            // 🎯 CRITERIO 3: Sinónimos (peso 25)
            if (producto.lista_sinonimos.length > 0) {
                for (const sinonimo of producto.lista_sinonimos) {
                    const sinonimoNorm = this.normalizarTexto(sinonimo);
                    for (const palabra of palabrasBusqueda) {
                        if (palabra === sinonimoNorm || sinonimoNorm.includes(palabra)) {
                            puntuacionTotal += 25;
                            coincidencias.push(`sinonimo_${sinonimo}`);
                        }
                    }
                }
            }
            
            // 🎯 CRITERIO 4: Contexto semántico (peso 20)
            if (categoriaSemantica && categoriaSemantica.categoria === categoriaNorm) {
                puntuacionTotal += 20 * categoriaSemantica.confianza;
                coincidencias.push(`categoria_semantica_${categoriaSemantica.categoria}`);
            }
            
            // 🎯 CRITERIO 5: (Eliminado por no tener descripción)
            // for (const palabra of palabrasBusqueda) {
            //     if (descNorm.includes(palabra)) {
            //         puntuacionTotal += 10;
            //         coincidencias.push(`descripcion_${palabra}`);
            //     }
            // }
            
            // 🎯 CRITERIO 6: Filtros de precio
            let cumplePrecio = true;
            if (filtroPrecio) {
                if (producto.precio > filtroPrecio.precioMax) {
                    cumplePrecio = false;
                    puntuacionTotal *= 0.3; // Penalizar pero no eliminar
                } else {
                    puntuacionTotal += 15; // Bonus por cumplir precio
                    coincidencias.push(`precio_ok_${filtroPrecio.rango}`);
                }
            }
            
            // Solo incluir si hay puntuación
            if (puntuacionTotal > 0) {
                const productoResultado = {
                    ...producto,
                    puntuacion: puntuacionTotal,
                    coincidencias: coincidencias,
                    cumple_precio: cumplePrecio
                };
                resultadosPonderados.push(productoResultado);
            }
        }
        
        // PASO 2: Ordenar por puntuación
        resultadosPonderados.sort((a, b) => b.puntuacion - a.puntuacion);
        
        // PASO 2.5: Análisis de contradicciones
        const contradicciones = this.detectarContradicciones(
            consulta, 
            categoriaSemantica?.categoria, 
            resultadosPonderados
        );
        
        // PASO 3: Preparar respuesta
        const tiempoMs = Date.now() - inicio;
        
        console.log(`🎯 Resultados encontrados: ${resultadosPonderados.length}`);
        console.log(`⏱️ Tiempo de búsqueda: ${tiempoMs}ms`);
        
        if (contradicciones.length > 0) {
            console.log("🚫 Contradicciones detectadas:");
            for (const cont of contradicciones) {
                console.log(`  ${cont.icono} ${cont.mensaje}`);
            }
        }
        
        const analisisCompleto = {
            consulta_original: consulta,
            consulta_normalizada: consultaNormalizada,
            categoria_semantica: categoriaSemantica,
            filtro_precio: filtroPrecio,
            contradicciones: contradicciones,
            total_productos_analizados: productos.length,
            productos_encontrados: resultadosPonderados.length,
            tiempo_ms: tiempoMs
        };
        
        return {
            productos: resultadosPonderados.slice(0, 10), // Top 10 resultados
            analisis: analisisCompleto,
            tiempo_ms: tiempoMs
        };
    }
    
    // 🚫 Detectar contradicciones semánticas
    detectarContradicciones(consulta, categoriaDetectada, resultados) {
        const contradicciones = [];
        const consultaNorm = this.normalizarTexto(consulta);
        
        // Si busca frutas pero encuentra snacks/dulces
        if (consultaNorm.includes('fruta') && categoriaDetectada !== 'frutas') {
            const categoriasEncontradas = [...new Set(resultados.map(r => r.categoria?.toLowerCase()))];
            if (categoriasEncontradas.some(cat => ['snacks', 'golosinas'].includes(cat))) {
                contradicciones.push({
                    tipo: 'categoria_incorrecta',
                    mensaje: '⚠️ Buscas frutas 🍎 pero encontré snacks/dulces',
                    sugerencia: 'Intenta: "frutas frescas" o especifica la fruta',
                    icono: '⚠️'
                });
            }
        }
        
        // Si busca snacks picantes pero encuentra té
        if (['chetos', 'picante', 'cheetos'].some(palabra => consultaNorm.includes(palabra))) {
            const productosTe = resultados.filter(r => r.nombre?.toLowerCase().includes('té'));
            if (productosTe.length > 0) {
                contradicciones.push({
                    tipo: 'producto_incorrecto',
                    mensaje: '🌶️ Buscas snacks picantes pero encontré té',
                    sugerencia: 'Intenta: "cheetos fuego" o "snacks picantes"',
                    icono: '🌶️'
                });
            }
        }
        
        return contradicciones;
    }
}

// 🧪 Función de prueba
async function probarCasosProblematicos() {
    const buscador = new BusquedaSemanticaLCLN();
    
    const casosPrueba = [
        'fruta fresca',
        'cosas baratas', 
        'chetos picantes',
        'agüita',
        'té negro',
        'snacks dulces',
        'bebidas sin azucar'
    ];
    
    console.log("🧪 === PRUEBAS DE CASOS PROBLEMÁTICOS ===\\n");
    
    for (const caso of casosPrueba) {
        console.log(`\\n${'='.repeat(60)}`);
        const resultado = await buscador.buscarProductosSemantico(caso);
        
        if (resultado.productos.length > 0) {
            console.log("🎯 RESULTADOS:");
            for (let i = 0; i < Math.min(3, resultado.productos.length); i++) {
                const producto = resultado.productos[i];
                const emoji = producto.emoji || '📦';
                console.log(`  ${i+1}. ${emoji} ${producto.nombre} - $${producto.precio} (${producto.categoria})`);
                console.log(`     Puntuación: ${producto.puntuacion.toFixed(1)} | Coincidencias: ${producto.coincidencias.slice(0, 3).join(', ')}`);
            }
        }
        
        // Mostrar contradicciones
        if (resultado.analisis?.contradicciones?.length > 0) {
            console.log("\\n⚠️ ADVERTENCIAS:");
            for (const cont of resultado.analisis.contradicciones) {
                console.log(`  ${cont.mensaje}`);
                console.log(`  💡 Sugerencia: ${cont.sugerencia}`);
            }
        }
    }
    
    process.exit(0);
}

// Exportar para usar como módulo
module.exports = { BusquedaSemanticaLCLN };

// Ejecutar si es el archivo principal
if (require.main === module) {
    probarCasosProblematicos();
}
