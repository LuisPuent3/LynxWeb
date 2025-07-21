const http = require('http');

const req = http.request({
    hostname: 'localhost',
    port: 5000,
    path: '/api/productos',
    method: 'GET'
}, (res) => {
    let body = '';
    res.on('data', chunk => body += chunk);
    res.on('end', () => {
        try {
            const productos = JSON.parse(body);
            if (productos && productos.length > 0) {
                console.log('📊 Estructura del primer producto:');
                console.log(JSON.stringify(productos[0], null, 2));
                
                console.log('\n🔍 Posibles campos de ID:');
                const producto = productos[0];
                Object.keys(producto).forEach(key => {
                    if (key.toLowerCase().includes('id')) {
                        console.log(`- ${key}: ${producto[key]}`);
                    }
                });
            }
        } catch (e) {
            console.log('Error parsing:', e.message);
            console.log('Raw response:', body.substring(0, 200));
        }
    });
});

req.on('error', err => console.error('Error:', err.message));
req.end();
