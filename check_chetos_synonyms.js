import mysql from 'mysql2/promise';

async function checkSynonyms() {
    console.log('🔍 VERIFICANDO SINÓNIMOS PARA CHETOS');
    console.log('=' * 40);
    
    const conn = await mysql.createConnection({
        host: 'localhost',
        user: 'root', 
        password: '',
        database: 'lynxshop'
    });
    
    // Ver todos los sinónimos
    const [synonyms] = await conn.execute(`
        SELECT s.sinonimo, p.nombre 
        FROM producto_sinonimos s 
        JOIN productos p ON s.producto_id = p.id_producto 
        WHERE s.activo = 1 
        ORDER BY s.sinonimo
    `);
    
    console.log('\n📝 SINÓNIMOS ACTIVOS:');
    synonyms.forEach(s => {
        console.log(`${s.sinonimo} -> ${s.nombre.trim()}`);
    });
    
    // Ver productos tipo snacks
    const [snacks] = await conn.execute(`
        SELECT p.nombre, p.precio, c.nombre as categoria
        FROM productos p
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria  
        WHERE p.nombre LIKE '%cruj%' OR p.nombre LIKE '%frito%' OR c.nombre LIKE '%snack%'
        ORDER BY p.nombre
    `);
    
    console.log('\n🥨 PRODUCTOS TIPO SNACKS:');
    snacks.forEach(s => {
        console.log(`${s.nombre.trim()} - $${s.precio} (${s.categoria || 'Sin categoria'})`);
    });
    
    await conn.end();
}

checkSynonyms().catch(console.error);
