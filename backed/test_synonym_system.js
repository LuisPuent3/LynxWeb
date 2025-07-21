const mysql = require('mysql2/promise');
require('dotenv').config();

// Configuración de base de datos
const dbConfig = {
    host: process.env.MYSQLHOST || process.env.DB_HOST || 'localhost',
    port: process.env.MYSQLPORT || process.env.DB_PORT || 3306,
    user: process.env.MYSQLUSER || process.env.DB_USER || 'root',
    password: process.env.MYSQLPASSWORD || process.env.DB_PASSWORD || '',
    database: process.env.MYSQLDATABASE || process.env.DB_NAME || 'lynxshop'
};

async function testSynonymSystem() {
    try {
        const connection = await mysql.createConnection(dbConfig);
        
        console.log('🧪 Iniciando prueba del sistema de sinónimos...\n');
        
        // 1. Verificar que tenemos productos
        console.log('1️⃣ Verificando productos disponibles...');
        const [productos] = await connection.execute('SELECT id, nombre FROM productos LIMIT 5');
        
        if (productos.length === 0) {
            console.log('❌ No hay productos en la base de datos');
            await connection.end();
            return;
        }
        
        const producto = productos[0];
        console.log(`✅ Usando producto: ${producto.nombre} (ID: ${producto.id})`);
        
        // 2. Limpiar datos de prueba anteriores
        console.log('\n2️⃣ Limpiando datos de prueba anteriores...');
        await connection.execute('DELETE FROM producto_sinonimos WHERE producto_id = ? AND sinonimo LIKE "test_%"', [producto.id]);
        
        // 3. Insertar sinónimos de prueba
        console.log('\n3️⃣ Insertando sinónimos de prueba...');
        const sinonimosPrueba = ['test_sinonimo1', 'test_sinonimo2', 'test_popular'];
        
        for (const sinonimo of sinonimosPrueba) {
            await connection.execute(
                'INSERT INTO producto_sinonimos (producto_id, sinonimo, popularidad, precision_score, fuente, activo) VALUES (?, ?, ?, ?, ?, ?)',
                [producto.id, sinonimo, Math.floor(Math.random() * 50), 0.8 + Math.random() * 0.2, 'admin', true]
            );
            console.log(`   ➕ Agregado: ${sinonimo}`);
        }
        
        // 4. Verificar inserción
        console.log('\n4️⃣ Verificando sinónimos insertados...');
        const [sinonimosBD] = await connection.execute(
            'SELECT id, sinonimo, popularidad, precision_score FROM producto_sinonimos WHERE producto_id = ?',
            [producto.id]
        );
        
        console.log(`✅ Total sinónimos para ${producto.nombre}: ${sinonimosBD.length}`);
        sinonimosBD.forEach(s => {
            console.log(`   📝 ${s.sinonimo} (Popular: ${s.popularidad}, Precisión: ${Math.round(s.precision_score * 100)}%)`);
        });
        
        // 5. Simular métricas de búsqueda
        console.log('\n5️⃣ Insertando métricas de búsqueda simuladas...');
        const terminosBusqueda = ['test_busqueda1', 'test_busqueda2', 'popular_term'];
        
        for (const termino of terminosBusqueda) {
            await connection.execute(
                'INSERT INTO busqueda_metricas (termino_busqueda, producto_id, clicks, fecha_busqueda) VALUES (?, ?, ?, NOW())',
                [termino, producto.id, Math.floor(Math.random() * 10) + 1]
            );
            console.log(`   📊 Métrica agregada: ${termino}`);
        }
        
        // 6. Probar consulta de sugerencias
        console.log('\n6️⃣ Probando consulta de sugerencias...');
        const [sugerencias] = await connection.execute(`
            SELECT termino_busqueda, 
                   COUNT(*) as frecuencia, 
                   AVG(clicks) as promedio_clicks,
                   MAX(fecha_busqueda) as ultima_busqueda
            FROM busqueda_metricas 
            WHERE producto_id = ? 
            GROUP BY termino_busqueda 
            ORDER BY frecuencia DESC, promedio_clicks DESC 
            LIMIT 5
        `, [producto.id]);
        
        console.log(`✅ Sugerencias encontradas: ${sugerencias.length}`);
        sugerencias.forEach(s => {
            console.log(`   💡 ${s.termino_busqueda} (Frecuencia: ${s.frecuencia}, Clicks: ${s.promedio_clicks.toFixed(1)})`);
        });
        
        await connection.end();
        
        console.log('\n✨ ¡Prueba del sistema de sinónimos completada exitosamente!');
        console.log('🚀 El sistema está listo para probar desde la interfaz web');
        
    } catch (error) {
        console.error('❌ Error en la prueba:', error.message);
    }
}

testSynonymSystem();
