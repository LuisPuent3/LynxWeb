#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api_structure():
    """Probar la estructura exacta que devuelve la API"""
    api_url = "http://localhost:8001/api/nlp/analyze"
    
    test_queries = [
        "botana sin picante",
        "coca cola",
        "dulces"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"CONSULTANDO: '{query}'")
        print('='*60)
        
        try:
            response = requests.post(api_url, 
                json={"query": query}, 
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ SUCCESS: {response.status_code}")
                print(f"📊 Total productos: {len(data.get('recommendations', []))}")
                
                # Mostrar estructura del primer producto
                if data.get('recommendations'):
                    first_product = data['recommendations'][0]
                    print(f"\n📦 ESTRUCTURA DEL PRIMER PRODUCTO:")
                    for key, value in first_product.items():
                        print(f"   {key}: {value} ({type(value).__name__})")
                    
                    print(f"\n🎯 PRIMEROS 3 PRODUCTOS:")
                    for i, prod in enumerate(data['recommendations'][:3], 1):
                        nombre = prod.get('nombre') or prod.get('name', 'N/A')
                        precio = prod.get('precio') or prod.get('price', 0)
                        imagen = prod.get('imagen') or prod.get('image', 'N/A')
                        cantidad = prod.get('cantidad') or prod.get('stock', 0)
                        categoria = prod.get('categoria_nombre') or prod.get('category', 'N/A')
                        
                        print(f"   {i}. {nombre}")
                        print(f"      💰 Precio: ${precio}")
                        print(f"      🖼️  Imagen: {imagen}")
                        print(f"      📦 Stock: {cantidad}")
                        print(f"      🏷️  Categoría: {categoria}")
                        print()
                
            else:
                print(f"❌ ERROR: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPCIÓN: {e}")

if __name__ == "__main__":
    test_api_structure()
