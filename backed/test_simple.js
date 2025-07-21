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
    
    process.exit(0);
}

test();
