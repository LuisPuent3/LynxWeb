const db = require('./config/db');

async function checkStructure() {
    console.log('🔍 VERIFICANDO ESTRUCTURA DE TABLAS\n');
    
    try {
        // Verificar estructura de productos
        const [productosStructure] = await db.query('DESCRIBE productos');
        console.log('📦 ESTRUCTURA TABLA PRODUCTOS:');
        productosStructure.forEach(col => {
            console.log(`  - ${col.Field}: ${col.Type} (${col.Null === 'YES' ? 'NULL' : 'NOT NULL'})`);
        });
        console.log();
        
        // Verificar estructura de sinónimos
        const [sinonymStructure] = await db.query('DESCRIBE producto_sinonimos');
        console.log('📝 ESTRUCTURA TABLA PRODUCTO_SINONIMOS:');
        sinonymStructure.forEach(col => {
            console.log(`  - ${col.Field}: ${col.Type} (${col.Null === 'YES' ? 'NULL' : 'NOT NULL'})`);
        });
        console.log();
        
        // Verificar algunas muestras
        const [sampleProducts] = await db.query('SELECT * FROM productos LIMIT 5');
        console.log('📦 MUESTRA PRODUCTOS:');
        sampleProducts.forEach((p, i) => {
            console.log(`${i+1}. ID: ${p.id_producto}, Nombre: ${p.nombre}, Precio: ${p.precio}`);
        });
        console.log();
        
        const [sampleSynonyms] = await db.query('SELECT * FROM producto_sinonimos LIMIT 5');
        console.log('📝 MUESTRA SINÓNIMOS:');
        sampleSynonyms.forEach((s, i) => {
            console.log(`${i+1}. "${s.sinonimo}" → Producto ID: ${s.producto_id}, Fuente: ${s.fuente}, Activo: ${s.activo}`);
        });
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
    
    process.exit(0);
}

checkStructure();
