const mysql = require('mysql');

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root', // Ajusta según tus credenciales
  password: '12345678', // Ajusta según tus credenciales
  database: 'lynxshop'
});

module.exports = db;