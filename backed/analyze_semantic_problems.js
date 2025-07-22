const db = require('./config/db');

async function testProblemasSemanticos() {
    console.log('🔍 === ANÁLISIS DE PROBLEMAS SEMÁNTICOS ===\n');
    
    try {
        // Casos problemáticos mencionados por el usuario
        const casosProblematicos = [
            {
                consulta: 'fruta fresca',
                problema: 'Devuelve galletas en lugar de frutas',
                esperado: 'Frutas frescas'
            },
            {
                consulta: 'cosas baratas',
                problema: 'Devuelve bebidas cuando debería filtrar por precio',
                esperado: 'Productos más económicos de todas las categorías'
            },
            {
                consulta: 'chetos picantes',
                problema: 'Devuelve té en lugar de snacks picantes',
                esperado: 'Cheetos/snacks picantes'
            },
            {
                consulta: 'agüita',
                problema: 'Caracteres especiales pueden causar problemas',
                esperado: 'Agua'
            }
        ];
        
        console.log('🚨 CASOS PROBLEMÁTICOS IDENTIFICADOS:\n');
        
        casosProblematicos.forEach((caso, i) => {
            console.log(`${i+1}. 🔍 "${caso.consulta}"`);
            console.log(`   ❌ Problema: ${caso.problema}`);
            console.log(`   ✅ Esperado: ${caso.esperado}`);
            console.log();
        });
        
        // Verificar sinónimos actuales que pueden causar confusión
        const [sinonimosSospechosos] = await db.query(`
            SELECT ps.sinonimo, ps.popularidad, p.nombre as producto, c.nombre as categoria
            FROM producto_sinonimos ps
            JOIN productos p ON ps.producto_id = p.id_producto
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE ps.activo = 1
            AND (
                ps.sinonimo IN ('te', 'galletas', 'dulce', 'picante', 'fresca', 'barato') OR
                ps.sinonimo LIKE '%citrico%' OR
                ps.sinonimo LIKE '%tropical%'
            )
            ORDER BY ps.sinonimo, ps.popularidad DESC
        `);
        
        console.log('🔍 SINÓNIMOS QUE PUEDEN CAUSAR CONFUSIÓN:\n');
        
        const gruposSinonimos = {};
        sinonimosSospechosos.forEach(s => {
            if (!gruposSinonimos[s.sinonimo]) {
                gruposSinonimos[s.sinonimo] = [];
            }
            gruposSinonimos[s.sinonimo].push({
                producto: s.producto,
                categoria: s.categoria,
                popularidad: s.popularidad
            });
        });
        
        for (const [sinonimo, productos] of Object.entries(gruposSinonimos)) {
            console.log(`🎯 "${sinonimo}":`);
            productos.forEach(p => {
                const emoji = p.categoria === 'Bebidas' ? '🥤' : 
                             p.categoria === 'Frutas' ? '🍎' :
                             p.categoria === 'Snacks' ? '🍿' :
                             p.categoria === 'Golosinas' ? '🍭' :
                             p.categoria === 'Papeleria' ? '📝' : '📦';
                console.log(`   ${emoji} ${p.producto} (${p.categoria}) - Pop: ${p.popularidad}`);
            });
            console.log();
        }
        
        // Analizar distribución de categorías en sinónimos
        const [distribucion] = await db.query(`
            SELECT c.nombre as categoria, COUNT(ps.id) as total_sinonimos
            FROM producto_sinonimos ps
            JOIN productos p ON ps.producto_id = p.id_producto
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE ps.activo = 1
            GROUP BY c.nombre
            ORDER BY total_sinonimos DESC
        `);
        
        console.log('📊 DISTRIBUCIÓN DE SINÓNIMOS POR CATEGORÍA:\n');
        distribucion.forEach(d => {
            const emoji = d.categoria === 'Bebidas' ? '🥤' : 
                         d.categoria === 'Frutas' ? '🍎' :
                         d.categoria === 'Snacks' ? '🍿' :
                         d.categoria === 'Golosinas' ? '🍭' :
                         d.categoria === 'Papeleria' ? '📝' : '📦';
            console.log(`${emoji} ${d.categoria}: ${d.total_sinonimos} sinónimos`);
        });
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
    
    process.exit(0);
}

testProblemasSemanticos();
