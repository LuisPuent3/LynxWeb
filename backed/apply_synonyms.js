const db = require('./config/db');
const fs = require('fs');

async function applySynonyms() {
    console.log('📝 APLICANDO SINÓNIMOS A LA BASE DE DATOS');
    console.log('=========================================\n');
    
    try {
        // Leer archivo SQL
        const sqlContent = fs.readFileSync('sinonimos_inteligentes_generados.sql', 'utf8');
        
        // Extraer solo la parte de INSERT
        const insertMatch = sqlContent.match(/INSERT INTO[^;]+;/s);
        if (!insertMatch) {
            throw new Error('No se encontró el INSERT en el archivo SQL');
        }
        
        const insertQuery = insertMatch[0];
        
        console.log('🚀 Ejecutando inserción de sinónimos...');
        const startTime = Date.now();
        
        const result = await db.query(insertQuery);
        
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        console.log(`✅ Sinónimos aplicados exitosamente!`);
        console.log(`   • Tiempo de ejecución: ${duration}ms`);
        console.log(`   • Filas afectadas: ${result[0].affectedRows || 'N/A'}`);
        
        // Verificar el nuevo total
        const [count] = await db.query('SELECT COUNT(*) as total FROM producto_sinonimos WHERE activo = 1');
        console.log(`   • Total sinónimos activos: ${count[0].total}`);
        
        // Mostrar algunos ejemplos
        const [samples] = await db.query(`
            SELECT ps.sinonimo, ps.popularidad, p.nombre as producto 
            FROM producto_sinonimos ps 
            JOIN productos p ON ps.producto_id = p.id_producto 
            WHERE ps.fuente = 'auto_learning' 
            ORDER BY ps.popularidad DESC 
            LIMIT 10
        `);
        
        console.log('\n📝 EJEMPLOS DE SINÓNIMOS APLICADOS:');
        samples.forEach((s, i) => {
            console.log(`  ${i+1}. "${s.sinonimo}" → ${s.producto} (pop: ${s.popularidad})`);
        });
        
    } catch (error) {
        console.error('❌ Error aplicando sinónimos:', error.message);
    }
    
    process.exit(0);
}

applySynonyms();
