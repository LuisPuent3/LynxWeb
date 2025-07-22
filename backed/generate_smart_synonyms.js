const db = require('./config/db');

// Base de datos inteligente de sinónimos por categorías
const SINONIMOS_INTELIGENTES = {
    // BEBIDAS - Términos comunes y variaciones
    bebidas: {
        // Bebidas generales
        'agua': ['h2o', 'hydro', 'liquido'],
        'agua mineral': ['agua con gas', 'agua gasificada', 'mineral'],
        'agua natural': ['agua simple', 'agua pura', 'natural'],
        'refresco': ['chesco', 'soda', 'bebida', 'refrescante'],
        'gaseosa': ['chesco', 'soda', 'refrescante'],
        
        // Bebidas específicas
        'coca-cola sin azúcar': ['coca zero', 'coca light', 'coca diet', 'coke zero'],
        'sprite': ['seven up', '7up', 'lima limon', 'citrico'],
        'boing': ['jugo', 'néctar', 'frutal'],
        'boing mango': ['mango', 'jugo mango', 'nectar mango'],
        'powerade': ['bebida deportiva', 'hidratante', 'isotonica'],
        'red bull': ['energizante', 'energia', 'taurina'],
        'limonada': ['agua de limon', 'limonada natural', 'citrico'],
        'naranjada': ['agua de naranja', 'jugo naranja', 'citrico'],
        'té negro': ['te', 'infusion', 'chai']
    },
    
    // SNACKS - Marcas, tipos, características
    snacks: {
        // Marcas populares
        'doritos': ['tortrix', 'chips', 'tostitos', 'nachos'],
        'cheetos': ['chettos', 'colacion', 'queso', 'cheese'],
        'fritos': ['papitas', 'chips', 'sal limon'],
        'oreo': ['galletas', 'cookies', 'chocolate', 'galletitas'],
        'emperador': ['senzo', 'dulce', 'oblea', 'wafer'],
        'crujitos': ['picante', 'fuego', 'chile', 'spicy'],
        
        // Tipos de snacks
        'galletas': ['cookies', 'galletitas', 'crackers'],
        'papitas': ['chips', 'fritos', 'tostadas'],
        'picante': ['chile', 'fuego', 'hot', 'spicy', 'picoso'],
        'dulce': ['sweet', 'azucar', 'endulzado'],
        'salado': ['sal', 'salty', 'salting'],
        
        // Características
        'crujiente': ['crunchy', 'tostado', 'crispeta']
    },
    
    // GOLOSINAS - Dulces, caramelos, chocolates
    golosinas: {
        // Tipos de dulces
        'chocolate': ['cocoa', 'cacao', 'choco', 'nutella'],
        'caramelo': ['dulce', 'confite', 'candy'],
        'goma': ['chicle', 'gummy', 'masticable'],
        'paleta': ['chupeta', 'lollipop', 'chupetín'],
        'mazapan': ['cacahuate', 'mani', 'peanut'],
        'panditas': ['ositos', 'gomas', 'frutal'],
        
        // Marcas y productos específicos
        'pelon': ['chamoy', 'tamarindo', 'picante'],
        'rockaleta': ['chile', 'picante', 'paleta'],
        'trident': ['chicle', 'goma', 'menta']
    },
    
    // FRUTAS - Nombres alternativos, características
    frutas: {
        // Frutas específicas
        'limón': ['lime', 'citrico', 'acido', 'verde'],
        'mango': ['manila', 'tropical', 'dulce'],
        'plátano': ['banana', 'cambur', 'guineo'],
        'manzana': ['apple', 'poma', 'reineta'],
        'naranja': ['orange', 'citrico', 'jugosa'],
        'mandarina': ['tangerina', 'citrico', 'pequeña'],
        'guayaba': ['tropical', 'rosada', 'dulce'],
        'mamey': ['tropical', 'cremoso', 'dulce'],
        'durazno': ['melocoton', 'peach', 'jugoso'],
        'pera': ['pear', 'jugosa', 'dulce'],
        'ciruela': ['plum', 'morada', 'pequeña'],
        
        // Características generales
        'fruta': ['frutal', 'natural', 'fresco', 'vitamina'],
        'citrico': ['acido', 'vitamina c', 'refrescante'],
        'tropical': ['exotico', 'dulce', 'jugoso']
    },
    
    // PAPELERÍA - Útiles escolares y oficina
    papeleria: {
        // Instrumentos de escritura
        'bolígrafo': ['pluma', 'birome', 'lapicero', 'pen'],
        'marcador': ['plumón', 'marker', 'rotulador'],
        'cuaderno': ['libreta', 'notebook', 'block'],
        'lápiz': ['pencil', 'grafito', 'escribir'],
        
        // Marcas
        'bic': ['birome', 'boligrafo', 'economico'],
        'sharpie': ['permanente', 'indeleble', 'professional'],
        
        // Características
        'negro': ['black', 'oscuro', 'tinta'],
        'rojo': ['red', 'colorido', 'tinta'],
        'rayado': ['lineas', 'hojas', 'escolar'],
        'argollado': ['espiral', 'anillas', 'profesional']
    }
};

// Sinónimos basados en popularidad y errores comunes
const SINONIMOS_POPULARES = {
    // Errores de tipeo comunes
    'coca': ['coka', 'koca', 'cocacola'],
    'doritos': ['dorito', 'dorrito', 'dorritos'],
    'cheetos': ['chettos', 'chetos', 'cheato'],
    'chocolate': ['chocollate', 'chocholate', 'choko'],
    
    // Abreviaciones
    'redbull': ['red', 'bull', 'energetico'],
    'cocacola': ['coke', 'cola'],
    
    // Términos coloquiales mexicanos
    'chesco': ['refresco', 'gaseosa', 'soda'],
    'dulces': ['golosinas', 'confites', 'candy'],
    'botana': ['snack', 'colacion', 'picadera'],
    'agua': ['agüita', 'liquido']
};

async function generarSinonimosInteligentes() {
    console.log('🧠 GENERANDO SINÓNIMOS INTELIGENTES');
    console.log('=====================================\n');
    
    try {
        // Obtener todos los productos con sus categorías
        const [productos] = await db.query(`
            SELECT p.id_producto, p.nombre, p.precio, c.nombre as categoria
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            ORDER BY c.nombre, p.nombre
        `);
        
        const sinónimosAGenerar = [];
        let totalSinonimos = 0;
        
        console.log('📝 GENERANDO SINÓNIMOS POR CATEGORÍA:\n');
        
        productos.forEach(producto => {
            const nombreProducto = producto.nombre.toLowerCase();
            const categoria = producto.categoria?.toLowerCase() || 'general';
            const sinonimosProducto = [];
            
            console.log(`🔍 ${producto.nombre} (${producto.categoria || 'Sin categoría'}):`);
            
            // Buscar sinónimos específicos por categoría
            const sinonimosCategoria = SINONIMOS_INTELIGENTES[categoria] || {};
            
            // Buscar coincidencias exactas de nombre de producto
            Object.keys(sinonimosCategoria).forEach(termino => {
                if (nombreProducto.includes(termino)) {
                    sinonimosCategoria[termino].forEach(sinonimo => {
                        if (!sinonimosProducto.includes(sinonimo)) {
                            sinonimosProducto.push(sinonimo);
                            console.log(`  → "${sinonimo}" (categoría: ${termino})`);
                        }
                    });
                }
            });
            
            // Buscar sinónimos populares
            Object.keys(SINONIMOS_POPULARES).forEach(termino => {
                if (nombreProducto.includes(termino)) {
                    SINONIMOS_POPULARES[termino].forEach(sinonimo => {
                        if (!sinonimosProducto.includes(sinonimo)) {
                            sinonimosProducto.push(sinonimo);
                            console.log(`  → "${sinonimo}" (popular: ${termino})`);
                        }
                    });
                }
            });
            
            // Generar sinónimos de palabras clave del nombre
            const palabrasNombre = nombreProducto.split(/[\s\-]+/);
            palabrasNombre.forEach(palabra => {
                if (palabra.length > 3) { // Solo palabras significativas
                    // Buscar en todas las categorías
                    Object.values(SINONIMOS_INTELIGENTES).forEach(catSinonimos => {
                        Object.keys(catSinonimos).forEach(termino => {
                            if (palabra.includes(termino) || termino.includes(palabra)) {
                                catSinonimos[termino].forEach(sinonimo => {
                                    if (!sinonimosProducto.includes(sinonimo) && sinonimo !== palabra) {
                                        sinonimosProducto.push(sinonimo);
                                        console.log(`  → "${sinonimo}" (palabra clave: ${palabra})`);
                                    }
                                });
                            }
                        });
                    });
                }
            });
            
            // Sinónimos por marca (extraer marca del nombre)
            if (nombreProducto.includes('coca-cola')) {
                ['coca', 'coke', 'cola'].forEach(s => {
                    if (!sinonimosProducto.includes(s)) {
                        sinonimosProducto.push(s);
                        console.log(`  → "${s}" (marca)`);
                    }
                });
            }
            
            // Agregar abreviaciones automáticas
            const palabrasSignificativas = palabrasNombre.filter(p => p.length > 3);
            if (palabrasSignificativas.length > 1) {
                const abreviacion = palabrasSignificativas.map(p => p[0]).join('');
                if (abreviacion.length >= 2 && !sinonimosProducto.includes(abreviacion)) {
                    sinonimosProducto.push(abreviacion);
                    console.log(`  → "${abreviacion}" (abreviación)`);
                }
            }
            
            console.log(`  Total sinónimos: ${sinonimosProducto.length}\n`);
            
            // Preparar para inserción
            sinonimosProducto.forEach((sinonimo, index) => {
                sinónimosAGenerar.push({
                    producto_id: producto.id_producto,
                    sinonimo: sinonimo,
                    popularidad: Math.max(1, 20 - index * 2), // Popularidad decreciente
                    fuente: 'auto_learning',
                    precision_score: 0.85 - (index * 0.05) // Score decreciente
                });
                totalSinonimos++;
            });
        });
        
        console.log(`🎯 RESUMEN:`);
        console.log(`• Total productos analizados: ${productos.length}`);
        console.log(`• Total sinónimos generados: ${totalSinonimos}`);
        console.log(`• Promedio sinónimos por producto: ${(totalSinonimos / productos.length).toFixed(1)}`);
        
        // Preguntar si insertar
        console.log(`\n❓ ¿Deseas insertar estos ${totalSinonimos} sinónimos? (se creará archivo SQL)`);
        
        // Generar archivo SQL
        let sqlContent = '-- SINÓNIMOS INTELIGENTES GENERADOS AUTOMÁTICAMENTE\n';
        sqlContent += '-- Total sinónimos: ' + totalSinonimos + '\n';
        sqlContent += '-- Fecha: ' + new Date().toISOString() + '\n\n';
        
        sqlContent += 'INSERT INTO producto_sinonimos (producto_id, sinonimo, popularidad, activo, precision_score, fuente) VALUES\n';
        
        const sqlValues = sinónimosAGenerar.map(s => 
            `(${s.producto_id}, '${s.sinonimo}', ${s.popularidad}, 1, ${s.precision_score}, '${s.fuente}')`
        ).join(',\n');
        
        sqlContent += sqlValues + ';\n';
        
        // Guardar archivo
        const fs = require('fs');
        fs.writeFileSync('sinonimos_inteligentes_generados.sql', sqlContent);
        console.log(`\\n✅ Archivo generado: sinonimos_inteligentes_generados.sql`);
        console.log(`Para aplicar: mysql -u root -p lynxshop < sinonimos_inteligentes_generados.sql`);
        
        return sinónimosAGenerar;
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

if (require.main === module) {
    generarSinonimosInteligentes().then(() => process.exit(0));
}

module.exports = { generarSinonimosInteligentes, SINONIMOS_INTELIGENTES };
