// Test script to verify Railway deployment
const https = require('https');

const testUrl = 'https://lynxweb-app-production.up.railway.app';

console.log('🔍 Testing deployment at:', testUrl);

// Test the main application
https.get(testUrl, (res) => {
  console.log('✅ Main app status:', res.statusCode);
    // Test API endpoint
  https.get(testUrl + '/api/health', (apiRes) => {
    console.log('✅ API health:', apiRes.statusCode);
    
    let data = '';
    apiRes.on('data', (chunk) => data += chunk);
    apiRes.on('end', () => {
      console.log('📊 API Response:', data);
    });
    
  }).on('error', (err) => {
    console.log('❌ API Error:', err.message);
  });
  
}).on('error', (err) => {
  console.log('❌ Main app error:', err.message);
});

// Test a few more endpoints (using correct Spanish routes)
const endpoints = ['/api/productos', '/api/categorias', '/api/test'];

endpoints.forEach(endpoint => {
  setTimeout(() => {
    https.get(testUrl + endpoint, (res) => {
      console.log(`✅ ${endpoint} status:`, res.statusCode);
    }).on('error', (err) => {
      console.log(`❌ ${endpoint} error:`, err.message);
    });
  }, 1000);
});
