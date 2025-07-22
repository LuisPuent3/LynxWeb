const db = require('./config/db');
const fs = require('fs');

// 🧠 ANALIZADOR SEMÁNTICO INTELIGENTE CON EMOJIS
class AnalizadorSemanticoInteligente {
    constructor() {
        // 📚 Diccionario de categorías con emojis y palabras clave
        this.categoriasSemanticas = {
            'frutas': {
                emoji: '🍎',
                palabrasClave: ['fruta', 'frutas', 'fresco', 'fresca', 'frescas', 'natural', 'vitamina', 'jugosa', 'dulce natural'],
                caracteristicas: ['citrico', 'tropical', 'acido', 'dulce', 'jugoso', 'fresco'],
                productos: ['limón', 'mango', 'manzana', 'pera', 'plátano', 'banana', 'guayaba', 'mamey', 'mandarina', 'durazno', 'ciruela'],
                sinonimos: ['apple', 'banana', 'lime', 'pear', 'tropical', 'citrico', 'jugosa']
            },
            'bebidas': {
                emoji: '🥤',
                palabrasClave: ['bebida', 'bebidas', 'liquido', 'refresco', 'agua', 'jugo', 'té', 'te'],
                caracteristicas: ['frio', 'caliente', 'gasificado', 'natural', 'energizante', 'hidratante'],
                productos: ['agua', 'coca', 'sprite', 'jugo', 'limonada', 'naranjada', 'té', 'redbull', 'boing'],
                sinonimos: ['h2o', 'chesco', 'refresco', 'cola', 'energizante', 'hidratante']
            },
            'snacks': {
                emoji: '🍿',
                palabrasClave: ['snack', 'snacks', 'botana', 'botanas', 'papitas', 'chips', 'galletas saladas'],
                caracteristicas: ['crujiente', 'salado', 'picante', 'queso', 'chile'],
                productos: ['doritos', 'cheetos', 'fritos', 'crujitos', 'papitas', 'chips', 'oreo'],
                sinonimos: ['chips', 'papitas', 'dorito', 'cheetos', 'chettos', 'picante', 'fuego', 'chile']
            },
            'golosinas': {
                emoji: '🍭',
                palabrasClave: ['dulce', 'dulces', 'golosina', 'golosinas', 'caramelo', 'chocolate', 'chicle'],
                caracteristicas: ['dulce', 'masticable', 'chocolate', 'azucar', 'confite'],
                productos: ['chocolate', 'caramelo', 'chicle', 'paleta', 'mazapan', 'pelon'],
                sinonimos: ['chocolate', 'caramelo', 'chicle', 'candy', 'chamoy', 'tamarindo']
            },
            'papeleria': {
                emoji: '📝',
                palabrasClave: ['papeleria', 'escolar', 'oficina', 'escribir', 'dibujar'],
                caracteristicas: ['negro', 'rojo', 'azul', 'profesional', 'escolar'],
                productos: ['bolígrafo', 'marcador', 'cuaderno', 'pluma', 'lápiz'],
                sinonimos: ['pluma', 'birome', 'lapicero', 'marker', 'cuaderno', 'libreta']
            }
        };
        
        // 💰 Rangos de precio con emojis
        this.rangosPrecio = {
            'muy_barato': { max: 5, emoji: '💸', palabras: ['muy barato', 'super barato', 'económico', 'centavos'] },
            'barato': { max: 15, emoji: '💰', palabras: ['barato', 'economico', 'accesible', 'low cost'] },
            'medio': { max: 30, emoji: '💵', palabras: ['medio', 'normal', 'regular', 'promedio'] },
            'caro': { max: 50, emoji: '💸', palabras: ['caro', 'costoso', 'premium'] },
            'muy_caro': { max: 999, emoji: '💎', palabras: ['muy caro', 'premium', 'lujo', 'exclusivo'] }
        };
        
        // 🔧 Normalizador de caracteres especiales
        this.caracteresEspeciales = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U',
            'ñ': 'n', 'Ñ': 'N'
        };
    }
    
    // 🔧 Normalizar texto (quitar acentos y caracteres especiales)
    normalizarTexto(texto) {
        let textoNormalizado = texto.toLowerCase();
        for (const [especial, normal] of Object.entries(this.caracteresEspeciales)) {
            textoNormalizado = textoNormalizado.replace(new RegExp(especial, 'g'), normal);
        }
        return textoNormalizado;
    }
    
    // 🎯 Detectar categoría semántica principal
    detectarCategoriaSemantica(consulta) {
        const consultaNormalizada = this.normalizarTexto(consulta);
        const palabras = consultaNormalizada.split(/\\s+/);
        
        let puntuacionesCategorias = {};
        
        // Inicializar puntuaciones
        for (const categoria of Object.keys(this.categoriasSemanticas)) {
            puntuacionesCategorias[categoria] = 0;
        }
        
        // Analizar cada palabra contra las categorías
        for (const palabra of palabras) {
            for (const [categoria, config] of Object.entries(this.categoriasSemanticas)) {
                // Palabras clave principales (peso 10)
                if (config.palabrasClave.some(pc => pc.includes(palabra) || palabra.includes(pc))) {
                    puntuacionesCategorias[categoria] += 10;
                }
                
                // Características (peso 8)
                if (config.caracteristicas.some(c => c.includes(palabra) || palabra.includes(c))) {
                    puntuacionesCategorias[categoria] += 8;
                }
                
                // Productos específicos (peso 6)
                if (config.productos.some(p => p.includes(palabra) || palabra.includes(p))) {
                    puntuacionesCategorias[categoria] += 6;
                }
                
                // Sinónimos (peso 4)
                if (config.sinonimos.some(s => s.includes(palabra) || palabra.includes(s))) {
                    puntuacionesCategorias[categoria] += 4;
                }
            }
        }
        
        // Encontrar la categoría con mayor puntuación
        let mejorCategoria = null;
        let maxPuntuacion = 0;
        
        for (const [categoria, puntuacion] of Object.entries(puntuacionesCategorias)) {
            if (puntuacion > maxPuntuacion) {
                maxPuntuacion = puntuacion;
                mejorCategoria = categoria;
            }
        }
        
        return mejorCategoria ? {
            categoria: mejorCategoria,
            emoji: this.categoriasSemanticas[mejorCategoria].emoji,
            puntuacion: maxPuntuacion,
            confianza: Math.min(maxPuntuacion / 10, 1.0) // Confianza normalizada
        } : null;
    }
    
    // 💰 Detectar filtros de precio semánticos
    detectarFiltroPrecio(consulta) {
        const consultaNormalizada = this.normalizarTexto(consulta);
        
        for (const [rango, config] of Object.entries(this.rangosPrecio)) {
            if (config.palabras.some(palabra => consultaNormalizada.includes(palabra))) {
                return {
                    rango: rango,
                    precioMax: config.max,
                    emoji: config.emoji,
                    palabrasDetectadas: config.palabras.filter(p => consultaNormalizada.includes(p))
                };
            }
        }
        
        // Detectar números específicos
        const numeroMatch = consultaNormalizada.match(/(?:menos de|menor a|hasta|máximo|max)\\s+(\\d+)/);
        if (numeroMatch) {
            const precio = parseInt(numeroMatch[1]);
            return {
                rango: 'custom',
                precioMax: precio,
                emoji: '💰',
                palabrasDetectadas: [numeroMatch[0]]
            };
        }
        
        return null;
    }
    
    // 🚫 Detectar contradicciones semánticas
    detectarContradicciones(consulta, categoriaDetectada, productosEncontrados) {
        const consultaNormalizada = this.normalizarTexto(consulta);
        const contradicciones = [];
        
        // Si busca frutas pero encuentra snacks/golosinas
        if (consultaNormalizada.includes('fruta') && categoriaDetectada !== 'frutas') {
            if (productosEncontrados.some(p => p.categoria.toLowerCase() === 'snacks' || p.categoria.toLowerCase() === 'golosinas')) {
                contradicciones.push({
                    tipo: 'categoria_incorrecta',
                    mensaje: 'Buscas frutas 🍎 pero encontré snacks/dulces',
                    sugerencia: 'filtrar_por_categoria_frutas'
                });
            }
        }
        
        // Si busca snacks picantes pero encuentra té
        if (consultaNormalizada.includes('chetos') || consultaNormalizada.includes('picante')) {
            if (productosEncontrados.some(p => p.categoria.toLowerCase() === 'bebidas' && p.nombre.toLowerCase().includes('té'))) {
                contradicciones.push({
                    tipo: 'producto_incorrecto',
                    mensaje: 'Buscas snacks picantes 🌶️ pero encontré té',
                    sugerencia: 'filtrar_por_snacks_picantes'
                });
            }
        }
        
        return contradicciones;
    }
    
    // 🔧 Generar sinónimos semánticamente correctos
    async generarSinonimosSemanticamente() {
        console.log('🧠 GENERANDO SINÓNIMOS SEMÁNTICAMENTE CORRECTOS');
        console.log('================================================\\n');
        
        try {
            // Obtener productos actuales
            const [productos] = await db.query(`
                SELECT p.id_producto, p.nombre, p.precio, c.nombre as categoria
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                ORDER BY c.nombre, p.nombre
            `);
            
            const sinonimosSematicos = [];
            let totalGenerados = 0;
            
            for (const producto of productos) {
                const nombreNormalizado = this.normalizarTexto(producto.nombre);
                const categoria = producto.categoria?.toLowerCase();
                
                console.log(`${this.categoriasSemanticas[categoria]?.emoji || '📦'} Analizando: ${producto.nombre} (${producto.categoria})`);
                
                // Detectar categoría semántica del producto
                const categoriaSemantica = this.detectarCategoriaSemantica(nombreNormalizado);
                
                if (categoriaSemantica && categoriaSemantica.confianza > 0.5) {
                    const config = this.categoriasSemanticas[categoriaSemantica.categoria];
                    
                    // Generar sinónimos específicos y precisos
                    const sinonimosPrecisos = new Set();
                    
                    // Sinónimos por palabras del nombre
                    const palabrasNombre = nombreNormalizado.split(/[\\s\\-]+/);
                    for (const palabra of palabrasNombre) {
                        if (palabra.length > 2) {
                            // Buscar sinónimos precisos en la configuración
                            for (const sinonimo of config.sinonimos) {
                                if (palabra.includes(sinonimo) || sinonimo.includes(palabra)) {
                                    sinonimosPrecisos.add(sinonimo);
                                    console.log(`  ✅ "${sinonimo}" (preciso para: ${palabra})`);
                                }
                            }
                        }
                    }
                    
                    // Sinónimos por características del producto
                    if (nombreNormalizado.includes('picante') || nombreNormalizado.includes('fuego') || nombreNormalizado.includes('chile')) {
                        sinonimosPrecisos.add('picante');
                        sinonimosPrecisos.add('spicy');
                        sinonimosPrecisos.add('chile');
                        console.log(`  🌶️ Agregado: picante, spicy, chile`);
                    }
                    
                    if (categoria === 'frutas') {
                        sinonimosPrecisos.add('fruta');
                        sinonimosPrecisos.add('fresco');
                        sinonimosPrecisos.add('natural');
                        console.log(`  🍎 Agregado: fruta, fresco, natural`);
                    }
                    
                    // Preparar para inserción
                    Array.from(sinonimosPrecisos).forEach((sinonimo, index) => {
                        sinonimosSematicos.push({
                            producto_id: producto.id_producto,
                            sinonimo: sinonimo,
                            popularidad: Math.max(1, 25 - index * 3),
                            precision_score: categoriaSemantica.confianza,
                            fuente: 'semantic_analysis',
                            categoria_objetivo: categoriaSemantica.categoria
                        });
                        totalGenerados++;
                    });
                }
                
                console.log();
            }
            
            console.log(`🎯 RESUMEN:`);
            console.log(`• Productos analizados: ${productos.length}`);
            console.log(`• Sinónimos semánticos generados: ${totalGenerados}`);
            
            // Generar archivo SQL
            if (totalGenerados > 0) {
                let sqlContent = '-- SINÓNIMOS SEMÁNTICAMENTE CORREGIDOS CON EMOJIS\\n';
                sqlContent += '-- Total sinónimos: ' + totalGenerados + '\\n';
                sqlContent += '-- Fecha: ' + new Date().toISOString() + '\\n\\n';
                
                // PRIMERO: Limpiar sinónimos problemáticos
                sqlContent += '-- Eliminar sinónimos que causan confusión semántica\\n';
                sqlContent += `DELETE FROM producto_sinonimos WHERE sinonimo IN ('te', 'galletas') AND fuente = 'auto_learning';\\n\\n`;
                
                // SEGUNDO: Insertar nuevos sinónimos semánticos
                sqlContent += 'INSERT INTO producto_sinonimos (producto_id, sinonimo, popularidad, activo, precision_score, fuente) VALUES\\n';
                
                const sqlValues = sinonimosSematicos.map(s => 
                    `(${s.producto_id}, '${s.sinonimo}', ${s.popularidad}, 1, ${s.precision_score}, '${s.fuente}')`
                ).join(',\\n');
                
                sqlContent += sqlValues + ';\\n';
                
                // Guardar archivo
                fs.writeFileSync('sinonimos_semanticos_corregidos.sql', sqlContent);
                console.log(`\\n✅ Archivo generado: sinonimos_semanticos_corregidos.sql`);
            }
            
            return sinonimosSematicos;
            
        } catch (error) {
            console.error('❌ Error:', error.message);
            return [];
        }
    }
}

// Función principal
async function main() {
    const analizador = new AnalizadorSemanticoInteligente();
    
    // Probar casos problemáticos
    console.log('🔍 === PRUEBAS DEL ANALIZADOR SEMÁNTICO ===\\n');
    
    const casosProblema = [
        'fruta fresca',
        'cosas baratas', 
        'chetos picantes',
        'agüita'
    ];
    
    for (const consulta of casosProblema) {
        console.log(`🔍 Analizando: "${consulta}"`);
        
        const categoria = analizador.detectarCategoriaSemantica(consulta);
        const precio = analizador.detectarFiltroPrecio(consulta);
        
        if (categoria) {
            console.log(`  ${categoria.emoji} Categoría: ${categoria.categoria} (confianza: ${(categoria.confianza*100).toFixed(1)}%)`);
        }
        
        if (precio) {
            console.log(`  ${precio.emoji} Precio: ≤ $${precio.precioMax} (${precio.palabrasDetectadas.join(', ')})`);
        }
        
        console.log();
    }
    
    // Generar sinónimos semánticamente correctos
    await analizador.generarSinonimosSemanticamente();
    
    process.exit(0);
}

if (require.main === module) {
    main();
}

module.exports = { AnalizadorSemanticoInteligente };
