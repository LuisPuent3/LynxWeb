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

async function insertTestData() {
    try {
        const connection = await mysql.createConnection(dbConfig);
        
        console.log('🌱 Insertando datos de prueba para sinónimos...');
        
        // Verificar que existe el producto ID 1
        const [productos] = await connection.execute('SELECT * FROM productos WHERE id_producto = 1');
        if (productos.length === 0) {
            console.log('❌ No existe producto con ID 1');
            return;
        }
        
        console.log('✅ Producto encontrado:', productos[0].nombre);
        
        // Insertar sinónimos de prueba para el producto ID 1 (Coca-Cola)
        const sinonimos = [
            { sinonimo: 'coca', fuente: 'admin', popularidad: 15, precision_score: 0.95 },
            { sinonimo: 'cola', fuente: 'admin', popularidad: 12, precision_score: 0.90 },
            { sinonimo: 'gaseosa', fuente: 'user_feedback', popularidad: 8, precision_score: 0.85 },
            { sinonimo: 'refresco', fuente: 'auto_learning', popularidad: 6, precision_score: 0.80 }
        ];
        
        // Limpiar sinónimos existentes para el producto 1
        await connection.execute('DELETE FROM producto_sinonimos WHERE producto_id = 1');
        console.log('🧹 Sinónimos anteriores eliminados');
        
        // Insertar nuevos sinónimos
        for (const sin of sinonimos) {
            const [result] = await connection.execute(
                'INSERT INTO producto_sinonimos (producto_id, sinonimo, fuente, popularidad, precision_score, activo) VALUES (?, ?, ?, ?, ?, ?)',
                [1, sin.sinonimo, sin.fuente, sin.popularidad, sin.precision_score, 1]
            );
            console.log(`✅ Sinónimo insertado: "${sin.sinonimo}" (ID: ${result.insertId})`);
        }
        
        // Insertar algunas métricas de búsqueda para sugerencias
        console.log('\n🔍 Insertando métricas de búsqueda...');
        
        const metricas = [
            { termino: 'pepsi', clicks: 3, fecha: '2025-07-20' },
            { termino: 'bebida', clicks: 5, fecha: '2025-07-19' },
            { termino: 'soda', clicks: 2, fecha: '2025-07-18' }
        ];
        
        // Limpiar métricas existentes para el producto 1
        await connection.execute('DELETE FROM busqueda_metricas WHERE producto_id = 1');
        console.log('🧹 Métricas anteriores eliminadas');
        
        // Insertar métricas de prueba
        for (const metrica of metricas) {
            // Insertar varias entradas para simular frecuencia
            for (let i = 0; i < metrica.clicks; i++) {
                await connection.execute(
                    'INSERT INTO busqueda_metricas (producto_id, termino_busqueda, clicks, fecha_busqueda) VALUES (?, ?, ?, ?)',
                    [1, metrica.termino, 1, metrica.fecha]
                );
            }
            console.log(`✅ Métrica insertada: "${metrica.termino}" (${metrica.clicks} clicks)`);
        }
        
        // Verificar los datos insertados
        console.log('\n📊 Verificando datos insertados:');
        const [sinonimosResult] = await connection.execute('SELECT * FROM producto_sinonimos WHERE producto_id = 1');
        console.log(`✅ ${sinonimosResult.length} sinónimos encontrados para producto 1`);
        
        const [metricasResult] = await connection.execute('SELECT DISTINCT termino_busqueda FROM busqueda_metricas WHERE producto_id = 1');
        console.log(`✅ ${metricasResult.length} términos únicos en métricas para producto 1`);
        
        await connection.end();
        console.log('\n🎉 Datos de prueba insertados exitosamente!');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.error(error);
    }
}

insertTestData();
