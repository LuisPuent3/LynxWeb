#!/usr/bin/env python3
"""
TEST COMPLETO DEL SISTEMA AFD CON PRIORIDADES
Confirma que el sistema funciona según las especificaciones del usuario
"""

import requests
import json

def test_afd_system():
    """Test del sistema AFD completo"""
    
    base_url = "http://localhost:8006"
    
    # Test cases que el usuario especificó
    test_queries = [
        {
            "query": "coquita barata",
            "descripcion": "Sinónimo específico + precio - debería encontrar Coca-Cola barata"
        },
        {
            "query": "chetos baratos picantes", 
            "descripcion": "Producto + atributos - prioridad completa como especificó el usuario"
        },
        {
            "query": "botana barata",
            "descripcion": "Categoría + precio - debería ir por categoría snacks"
        },
        {
            "query": "coca",
            "descripcion": "Sinónimo simple - debería encontrar Coca-Cola"
        },
        {
            "query": "bebida barata",
            "descripcion": "Categoría bebidas + filtro precio"
        }
    ]
    
    print("🧪 TESTING SISTEMA AFD COMPLETO CON PRIORIDADES")
    print("=" * 60)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. QUERY: '{test_case['query']}'")
        print(f"   EXPECTATIVA: {test_case['descripcion']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/nlp/analyze",
                json={"query": test_case["query"]},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ STATUS: {response.status_code}")
                print(f"   ⚡ TIEMPO: {data.get('processing_time_ms', 0):.2f}ms")
                print(f"   🎯 PRODUCTOS ENCONTRADOS: {data.get('products_found', 0)}")
                print(f"   💬 MENSAJE: {data.get('user_message', 'N/A')}")
                
                # Mostrar tokens y interpretación AFD
                interpretation = data.get('interpretation', {})
                if 'tokens' in interpretation:
                    print(f"   🔍 TOKENS AFD: {interpretation['tokens']}")
                if 'interpretacion' in interpretation:
                    print(f"   🧠 INTERPRETACIÓN: {interpretation['interpretacion']}")
                
                # Mostrar primeros 3 productos
                productos = data.get('recommendations', [])
                if productos:
                    print("   📦 PRODUCTOS:")
                    for j, prod in enumerate(productos[:3], 1):
                        precio = prod.get('precio', prod.get('price', 0))
                        sinonimo = prod.get('sinonimo_usado', '')
                        match_reasons = prod.get('match_reasons', [])
                        print(f"      {j}. {prod.get('nombre', 'N/A')} - ${precio}")
                        if sinonimo:
                            print(f"         📝 Sinónimo usado: {sinonimo}")
                        if match_reasons:
                            print(f"         🎯 Razón: {', '.join(match_reasons)}")
                else:
                    print("   ❌ No se encontraron productos")
            else:
                print(f"   ❌ ERROR HTTP: {response.status_code}")
                print(f"   📄 RESPUESTA: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ ERROR CONEXIÓN: {e}")
        
        print("-" * 60)
    
    # Test de salud del sistema
    print(f"\n🏥 HEALTH CHECK")
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ STATUS: {health_data.get('status', 'unknown')}")
            print(f"   📊 PRODUCTOS: {health_data.get('productos', 0)}")
            print(f"   📝 SINÓNIMOS: {health_data.get('sinonimos', 0)}")
            print(f"   🏷️  VERSIÓN: {health_data.get('version', 'unknown')}")
        else:
            print(f"   ❌ HEALTH CHECK FAILED: {health_response.status_code}")
    except Exception as e:
        print(f"   ❌ HEALTH CHECK ERROR: {e}")

if __name__ == "__main__":
    test_afd_system()