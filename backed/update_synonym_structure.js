const mysql = require('mysql2/promise');
require('dotenv').config();

const dbConfig = {
    host: process.env.MYSQLHOST || process.env.DB_HOST || 'localhost',
    port: process.env.MYSQLPORT || process.env.DB_PORT || 3306,
    user: process.env.MYSQLUSER || process.env.DB_USER || 'root',
    password: process.env.MYSQLPASSWORD || process.env.DB_PASSWORD || '',
    database: process.env.MYSQLDATABASE || process.env.DB_NAME || 'lynxshop'
};

async function updateSynonymTables() {
    try {
        const connection = await mysql.createConnection(dbConfig);
        
        console.log('🔧 Actualizando estructura de tablas de sinónimos...\n');
        
        // 1. Verificar columnas faltantes en producto_sinonimos
        const [columns] = await connection.execute('DESCRIBE producto_sinonimos');
        const existingColumns = columns.map(col => col.Field);
        console.log('📋 Columnas actuales en producto_sinonimos:', existingColumns);
        
        // 2. Agregar columnas faltantes
        const requiredColumns = {
            'precision_score': 'DECIMAL(3,2) DEFAULT 0.80',
            'fuente': "ENUM('admin', 'auto_learning', 'user_feedback') DEFAULT 'admin'",
            'fecha_creacion': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'fecha_ultima_actualizacion': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        };
        
        for (const [columnName, definition] of Object.entries(requiredColumns)) {
            if (!existingColumns.includes(columnName)) {
                console.log(`➕ Agregando columna: ${columnName}`);
                await connection.execute(`ALTER TABLE producto_sinonimos ADD COLUMN ${columnName} ${definition}`);
            } else {
                console.log(`✅ Columna ${columnName} ya existe`);
            }
        }
        
        // 3. Verificar resultado final
        console.log('\n🔍 Verificando estructura final...');
        const [newColumns] = await connection.execute('DESCRIBE producto_sinonimos');
        console.log('📋 Columnas finales:');
        newColumns.forEach(col => {
            console.log(`   - ${col.Field} (${col.Type}) ${col.Null === 'YES' ? 'NULL' : 'NOT NULL'} ${col.Default ? `DEFAULT ${col.Default}` : ''}`);
        });
        
        await connection.end();
        console.log('\n✨ Actualización completada exitosamente!');
        
    } catch (error) {
        console.error('❌ Error actualizando tablas:', error.message);
    }
}

updateSynonymTables();
