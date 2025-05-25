const mysql = require('mysql2');
require('dotenv').config();

// Configuración para Railway (variables automáticas) y local
const dbConfig = {
    host: process.env.MYSQLHOST || process.env.DB_HOST || 'localhost',
    port: process.env.MYSQLPORT || process.env.DB_PORT || 3306,
    user: process.env.MYSQLUSER || process.env.DB_USER || 'root',
    password: process.env.MYSQLPASSWORD || process.env.DB_PASSWORD || '',
    database: process.env.MYSQLDATABASE || process.env.DB_NAME || 'lynxshop',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
    // Configuraciones adicionales para Railway
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
    connectTimeout: 60000,
    acquireTimeout: 60000,
    timeout: 60000
};

// Verificar variables de entorno
console.log('Configuración de base de datos:');
console.log('Host:', dbConfig.host);
console.log('Puerto:', dbConfig.port);
console.log('Usuario:', dbConfig.user);
console.log('Base de datos:', dbConfig.database);
console.log('¿Contraseña definida?:', dbConfig.password ? 'Sí' : 'No');
console.log('SSL:', dbConfig.ssl);

const pool = mysql.createPool(dbConfig);

// Probar la conexión
pool.getConnection((err, connection) => {
    if (err) {
        console.error('Error al conectar con la base de datos:', err);
        return;
    }
    console.log('Conexión exitosa a la base de datos');
    connection.release();
});

// Promisify para usar async/await
const promisePool = pool.promise();

module.exports = promisePool;