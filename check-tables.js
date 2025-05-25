// Script para verificar qué tablas existen en Railway
const mysql = require('mysql2/promise');

async function checkTables() {
  try {
    console.log('🔍 Conectando a Railway MySQL...');
    
    const connection = await mysql.createConnection({
      host: 'switchback.proxy.rlwy.net',
      port: 23417,
      user: 'root',
      password: 'SzDfFMPuRwasMuvIJrWXvOGnLiLbjVhI',
      database: 'railway',
      ssl: { rejectUnauthorized: false }
    });

    console.log('✅ Conectado exitosamente');

    // Mostrar todas las tablas
    console.log('\n📋 Tablas existentes:');
    const [tables] = await connection.execute('SHOW TABLES');
    tables.forEach((table, index) => {
      console.log(`${index + 1}. ${table[`Tables_in_railway`]}`);
    });

    // Verificar si hay alguna tabla específica
    if (tables.length === 0) {
      console.log('❌ No hay tablas en la base de datos');
    }

    await connection.end();
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

checkTables();