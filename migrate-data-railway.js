const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

// Configuración de la base de datos usando variables de entorno de Railway
const dbConfig = {
  host: process.env.MYSQLHOST || 'mysql.railway.internal',
  user: process.env.MYSQLUSER || 'root',
  password: process.env.MYSQLPASSWORD,
  database: process.env.MYSQLDATABASE || 'railway',
  port: process.env.MYSQLPORT || 3306,
  ssl: {
    rejectUnauthorized: false
  },
  connectTimeout: 60000,
  acquireTimeout: 60000,
  timeout: 60000
};

async function migrateData() {
  let connection;
  
  try {
    console.log('🔄 Conectando a la base de datos Railway...');
    console.log('Host:', dbConfig.host);
    console.log('Database:', dbConfig.database);
    
    connection = await mysql.createConnection(dbConfig);
    console.log('✅ Conexión exitosa a la base de datos');
    
    // Leer el archivo SQL
    const sqlPath = path.join(__dirname, 'database', 'lynxshop.sql');
    console.log('📁 Leyendo archivo SQL:', sqlPath);
    
    if (!fs.existsSync(sqlPath)) {
      throw new Error(`Archivo SQL no encontrado: ${sqlPath}`);
    }
    
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    console.log('📄 Archivo SQL leído correctamente');
    
    // Dividir el contenido en statements individuales
    const statements = sqlContent
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));
    
    console.log(`🔄 Ejecutando ${statements.length} statements SQL...`);
    
    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      if (statement.length > 0) {
        try {
          await connection.execute(statement);
          console.log(`✅ Statement ${i + 1}/${statements.length} ejecutado correctamente`);
        } catch (err) {
          console.log(`⚠️  Error en statement ${i + 1}: ${err.message}`);
          // Continuar con el siguiente statement
        }
      }
    }
    
    console.log('✅ Migración completada exitosamente');
    
    // Verificar que los datos se migraron correctamente
    const [rows] = await connection.execute('SHOW TABLES');
    console.log('📊 Tablas creadas:', rows.map(row => Object.values(row)[0]));
    
    // Verificar algunos datos
    const [users] = await connection.execute('SELECT COUNT(*) as count FROM usuarios');
    const [products] = await connection.execute('SELECT COUNT(*) as count FROM productos');
    const [categories] = await connection.execute('SELECT COUNT(*) as count FROM categorias');
    
    console.log('📈 Registros migrados:');
    console.log(`   - Usuarios: ${users[0].count}`);
    console.log(`   - Productos: ${products[0].count}`);
    console.log(`   - Categorías: ${categories[0].count}`);
    
  } catch (error) {
    console.error('❌ Error durante la migración:', error.message);
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
      console.log('🔌 Conexión cerrada');
    }
  }
}

// Ejecutar la migración
migrateData();
