const mysql = require('mysql2');
require('dotenv').config();

// Verificar variables de entorno
console.log('Configuración de base de datos:');
console.log('Host:', process.env.DB_HOST);
console.log('Usuario:', process.env.DB_USER);
console.log('Base de datos:', process.env.DB_NAME);
console.log('¿Contraseña definida?:', process.env.DB_PASSWORD ? 'Sí' : 'No');

const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD || '', // Asegurarse de que no sea undefined
    database: process.env.DB_NAME,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

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