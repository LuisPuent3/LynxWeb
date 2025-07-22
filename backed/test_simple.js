const db = require('./config/db');

async function test() {
    console.log('🔍 Verificando conexión y datos...');
    
    try {
        // Test básico de conexión
        const [result] = await db.query('SELECT 1 as test');
        console.log('✅ Conexión exitosa:', result);
        
        // Verificar productos
        const productos = await db.query('SELECT id_producto, nombre FROM productos LIMIT 3');
        console.log('📦 Productos encontrados:', productos.length);
        productos.forEach(p => console.log(`- ${p.id_producto}: ${p.nombre}`));
        
        // Verificar si existe la tabla producto_sinonimos
        const [tablas] = await db.query(`
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'producto_sinonimos'
        `);
        console.log('📋 Tabla producto_sinonimos existe:', tablas[0].count > 0);
        
        if (tablas[0].count > 0) {
            // Verificar sinónimos existentes
            const sinonimos = await db.query('SELECT * FROM producto_sinonimos WHERE producto_id = 1');
            console.log('📝 Sinónimos para producto 1:', sinonimos.length);
            sinonimos.forEach(s => console.log(`- ${s.sinonimo} (${s.fuente})`));
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
    
    // Prueba de búsqueda semántica inteligente
    const { BusquedaSemanticaLCLN } = require('./semantic_search_engine');
    const buscador = new BusquedaSemanticaLCLN();
    const queries = [
        'chettos picantes baratos',
        'sin picante barato',
        'votana bara',
        'fruta fresca',
        'bebidas sin azucar'
    ];
    for (const query of queries) {
        console.log(`\n🔎 Prueba búsqueda semántica: "${query}"`);
        const resultado = await buscador.buscarProductosSemantico(query);
        if (resultado.productos.length > 0) {
            resultado.productos.slice(0, 3).forEach((p, i) => {
                console.log(`  ${i+1}. ${p.emoji || '📦'} ${p.nombre} - $${p.precio} (${p.categoria}) [${p.coincidencias.join(', ')}]`);
            });
        } else {
            console.log('  ⚠️ Sin resultados');
        }
        if (resultado.analisis?.contradicciones?.length > 0) {
            resultado.analisis.contradicciones.forEach(cont => {
                console.log(`  ⚠️ ${cont.mensaje} | 💡 ${cont.sugerencia}`);
            });
        }
    }
    
    process.exit(0);
}

test();
