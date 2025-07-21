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

async function checkTables() {
  try {
    const connection = await mysql.createConnection(dbConfig);
    
    console.log('🔍 Verificando tablas del sistema de sinónimos...\n');
    
    const tables = ['producto_sinonimos', 'busqueda_metricas', 'producto_atributos'];
    
    for (const table of tables) {
      const [result] = await connection.execute(
        'SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = ?',
        [table]
      );
      
      if (result[0].count > 0) {
        console.log(`✅ Tabla ${table} existe`);
        
        // Mostrar estructura
        const [columns] = await connection.execute(`DESCRIBE ${table}`);
        console.log(`   Columnas: ${columns.map(c => c.Field).join(', ')}`);
      } else {
        console.log(`❌ Tabla ${table} no existe`);
      }
    }
    
    await connection.end();
    console.log('\n✨ Verificación completada');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

checkTables();
