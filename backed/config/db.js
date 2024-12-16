require('dotenv').config();
const mysql = require('mysql2/promise');

const createPool = async () => {
  try {
    const pool = await mysql.createPool({
      host: process.env.DB_HOST,
      user: process.env.DB_USER,
      password: process.env.DB_PASS,
      database: process.env.DB_NAME,
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0
    });

    console.log('Conexión exitosa a la base de datos');
    return pool;
  } catch (err) {
    console.error('Error conectando a la base de datos:', err);
    throw err;
  }
};

module.exports = createPool();