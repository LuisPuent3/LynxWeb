const mysql = require('mysql2/promise');
require('dotenv').config();

const dbConfig = {
    host: process.env.MYSQLHOST || 'localhost',
    port: process.env.MYSQLPORT || 3306,
    user: process.env.MYSQLUSER || 'root',
    password: process.env.MYSQLPASSWORD || '',
    database: process.env.MYSQLDATABASE || 'lynxshop'
};

(async () => {
    try {
        const connection = await mysql.createConnection(dbConfig);
        
        console.log('📊 Verificando estructura de tablas...\n');
        
        const [result] = await connection.execute('DESCRIBE productos');
        console.log('Estructura tabla productos:');
        result.forEach(col => console.log(`- ${col.Field} (${col.Type})`));
        
        await connection.end();
    } catch (error) {
        console.error('Error:', error.message);
    }
})();
