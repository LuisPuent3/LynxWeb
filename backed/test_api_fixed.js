const http = require('http');

function makeRequest(options, data = null) {
    return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(body);
                    resolve({ status: res.statusCode, data: jsonData });
                } catch (e) {
                    resolve({ status: res.statusCode, data: body });
                }
            });
        });

        req.on('error', reject);
        
        if (data) {
            req.write(JSON.stringify(data));
        }
        
        req.end();
    });
}

async function testSynonymAPI() {
    try {
        console.log('🧪 Probando APIs del sistema de sinónimos...\n');
        
        // 1. Probar endpoint de productos para obtener un ID válido
        console.log('1️⃣ Obteniendo lista de productos...');
        const productosRes = await makeRequest({
            hostname: 'localhost',
            port: 5000,
            path: '/api/productos',
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (productosRes.status !== 200) {
            console.log('❌ Error obteniendo productos:', productosRes.status);
            return;
        }
        
        const productos = productosRes.data;
        if (!productos || productos.length === 0) {
            console.log('❌ No hay productos disponibles');
            return;
        }
        
        const producto = productos[0];
        const productoId = producto.id_producto || producto.ID || producto.id;
        console.log(`✅ Producto seleccionado: ${producto.nombre} (ID: ${productoId})`);
        
        if (!productoId) {
            console.log('❌ No se pudo obtener el ID del producto');
            console.log('Estructura:', Object.keys(producto));
            return;
        }
        
        // 2. Probar obtener sinónimos (probablemente vacío al principio)
        console.log('\n2️⃣ Probando obtener sinónimos...');
        const sinRes = await makeRequest({
            hostname: 'localhost',
            port: 5000,
            path: `/api/test/sinonimos/producto/${productoId}`,
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        console.log(`📝 Respuesta sinónimos [${sinRes.status}]:`, sinRes.data);
        
        // 3. Probar agregar un sinónimo
        console.log('\n3️⃣ Probando agregar sinónimo...');
        const addRes = await makeRequest({
            hostname: 'localhost',
            port: 5000,
            path: '/api/test/sinonimos',
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }, {
            producto_id: productoId,
            sinonimo: 'test_sinonimo_api',
            fuente: 'admin'
        });
        
        console.log(`➕ Respuesta agregar [${addRes.status}]:`, addRes.data);
        
        // 4. Probar sugerencias
        console.log('\n4️⃣ Probando obtener sugerencias...');
        const sugRes = await makeRequest({
            hostname: 'localhost',
            port: 5000,
            path: `/api/test/sinonimos/sugerencias/producto/${productoId}`,
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        console.log(`💡 Respuesta sugerencias [${sugRes.status}]:`, sugRes.data);
        
        // 5. Verificar que el sinónimo fue agregado
        if (addRes.status === 201) {
            console.log('\n5️⃣ Verificando sinónimo agregado...');
            const verifyRes = await makeRequest({
                hostname: 'localhost',
                port: 5000,
                path: `/api/test/sinonimos/producto/${productoId}`,
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            console.log(`🔍 Sinónimos después de agregar [${verifyRes.status}]:`, verifyRes.data);
        }
        
        console.log('\n✨ Prueba de APIs completada!');
        
    } catch (error) {
        console.error('❌ Error en la prueba:', error.message);
    }
}

testSynonymAPI();
