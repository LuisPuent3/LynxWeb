const db = require('./config/db');

async function analyzeSynonyms() {
    console.log('🔍 ANÁLISIS COMPLETO DE SINÓNIMOS');
    console.log('=====================================\n');
    
    try {
        // 1. Verificar productos actuales
        const [productos] = await db.query(`
            SELECT p.id_producto, p.nombre, p.id_categoria, p.precio, c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            ORDER BY p.id_categoria, p.nombre
        `);
        
        console.log('📦 PRODUCTOS DISPONIBLES:');
        console.log(`Total: ${productos.length} productos\n`);
        
        const categorias = {};
        productos.forEach(p => {
            const catKey = p.categoria_nombre || `Categoria_${p.id_categoria}`;
            if (!categorias[catKey]) categorias[catKey] = [];
            categorias[catKey].push(p);
        });
        
        for (const [catName, prods] of Object.entries(categorias)) {
            console.log(`${catName}:`);
            prods.forEach(p => console.log(`  - ${p.nombre} ($${p.precio}) [ID: ${p.id_producto}]`));
            console.log();
        }
        
        // 2. Verificar sinónimos actuales
        const [sinonimos] = await db.query(`
            SELECT ps.sinonimo, ps.producto_id, ps.fuente, ps.popularidad, ps.activo,
                   p.nombre as producto_nombre, p.precio
            FROM producto_sinonimos ps
            JOIN productos p ON ps.producto_id = p.id_producto
            WHERE ps.activo = 1
            ORDER BY ps.popularidad DESC, p.nombre
        `);
        
        console.log('📝 SINÓNIMOS ACTUALES:');
        console.log(`Total: ${sinonimos.length} sinónimos activos\n`);
        
        const sinonimosPorProducto = {};
        sinonimos.forEach(s => {
            if (!sinonimosPorProducto[s.producto_id]) {
                sinonimosPorProducto[s.producto_id] = {
                    nombre: s.producto_nombre,
                    precio: s.precio,
                    sinonimos: []
                };
            }
            sinonimosPorProducto[s.producto_id].sinonimos.push({
                sinonimo: s.sinonimo,
                fuente: s.fuente,
                popularidad: s.popularidad
            });
        });
        
        for (const [prodId, data] of Object.entries(sinonimosPorProducto)) {
            console.log(`${data.nombre} ($${data.precio}):`);
            data.sinonimos.forEach(s => 
                console.log(`  → "${s.sinonimo}" (${s.fuente}, pop: ${s.popularidad})`)
            );
            console.log();
        }
        
        // 3. Identificar productos SIN sinónimos
        const productosConSinonimos = new Set(Object.keys(sinonimosPorProducto));
        const productosSinSinonimos = productos.filter(p => !productosConSinonimos.has(p.id_producto.toString()));
        
        console.log('⚠️ PRODUCTOS SIN SINÓNIMOS:');
        console.log(`Total: ${productosSinSinonimos.length} productos\n`);
        
        productosSinSinonimos.forEach(p => {
            const categoria = p.categoria_nombre || `Cat_${p.id_categoria}`;
            console.log(`- ${p.nombre} ($${p.precio}) [${categoria}]`);
        });
        
        // 4. Análisis de cobertura
        console.log('\n📊 ESTADÍSTICAS:');
        console.log(`• Productos con sinónimos: ${Object.keys(sinonimosPorProducto).length}/${productos.length} (${((Object.keys(sinonimosPorProducto).length/productos.length)*100).toFixed(1)}%)`);
        console.log(`• Productos sin sinónimos: ${productosSinSinonimos.length}/${productos.length} (${((productosSinSinonimos.length/productos.length)*100).toFixed(1)}%)`);
        console.log(`• Promedio sinónimos por producto: ${(sinonimos.length/Object.keys(sinonimosPorProducto).length).toFixed(1)}`);
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
    
    process.exit(0);
}

analyzeSynonyms();
