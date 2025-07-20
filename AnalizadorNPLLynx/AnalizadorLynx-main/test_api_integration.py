#!/usr/bin/env python3
# Test rápido de la API LYNX NLP

import requests
import json

def test_nlp_api():
    base_url = 'http://localhost:8000'
    
    print('=== PRUEBA INTEGRAL API LYNX NLP ===')
    print()
    
    # Test health check
    print('🔍 1. Health Check...')
    try:
        health = requests.get(f'{base_url}/api/health')
        if health.status_code == 200:
            health_data = health.json()
            print(f'   ✅ Status: {health_data["status"]}')
            print(f'   📊 Components: {health_data["components"]}')
        else:
            print(f'   ❌ Error: {health.status_code}')
            return
    except Exception as e:
        print(f'   ❌ Connection error: {e}')
        return
    
    print()
    
    # Test búsquedas NLP
    queries = [
        'bebidas sin azucar',
        'snacks picantes baratos',
        'coca cola',
        'productos menos de 15 pesos'
    ]
    
    for i, query in enumerate(queries, 2):
        print(f'🔍 {i}. Testing: "{query}"')
        
        try:
            result = requests.post(f'{base_url}/api/nlp/analyze', json={
                'query': query,
                'options': {
                    'max_recommendations': 3,
                    'enable_correction': True,
                    'enable_recommendations': True
                }
            })
            
            if result.status_code == 200:
                data = result.json()
                print(f'   ⏱️  Time: {data["processing_time_ms"]:.1f}ms')
                print(f'   🎯 Products: {len(data["recommendations"])}')
                
                if data.get('corrections', {}).get('applied'):
                    print(f'   🔧 Corrected: {data["corrections"]["corrected_query"]}')
                
                # Mostrar top 3 productos
                for j, product in enumerate(data['recommendations'][:3], 1):
                    score = int(product['match_score'] * 100)
                    print(f'      {j}. {product["name"]} - ${product["price"]} ({score}%)')
                    
            else:
                print(f'   ❌ Error: {result.status_code} - {result.text}')
                
        except Exception as e:
            print(f'   ❌ Error: {e}')
        
        print()
    
    print('✅ Pruebas completadas')

if __name__ == "__main__":
    test_nlp_api()
