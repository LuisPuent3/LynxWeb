#!/usr/bin/env python3
"""
TEST COMPLETO DEL SISTEMA AFD CON PRIORIDADES (Windows Compatible)
Confirma que el sistema funciona segun las especificaciones del usuario
"""

import requests
import json

def test_afd_system():
    """Test del sistema AFD completo"""
    
    base_url = "http://localhost:8007"
    
    # Test cases que el usuario especifico
    test_queries = [
        {
            "query": "coquita barata",
            "descripcion": "Sinonimo especifico + precio - deberia encontrar Coca-Cola barata"
        },
        {
            "query": "chetos baratos picantes", 
            "descripcion": "Producto + atributos - prioridad completa como especifico el usuario"
        },
        {
            "query": "botana barata",
            "descripcion": "Categoria + precio - deberia ir por categoria snacks"
        },
        {
            "query": "coca",
            "descripcion": "Sinonimo simple - deberia encontrar Coca-Cola"
        },
        {
            "query": "bebida barata",
            "descripcion": "Categoria bebidas + filtro precio"
        }
    ]
    
    print("TESTING SISTEMA AFD COMPLETO CON PRIORIDADES")
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
                
                print(f"   STATUS: {response.status_code}")
                print(f"   TIEMPO: {data.get('processing_time_ms', 0):.2f}ms")
                print(f"   PRODUCTOS ENCONTRADOS: {data.get('products_found', 0)}")
                print(f"   MENSAJE: {data.get('user_message', 'N/A')}")
                
                # Mostrar tokens y interpretacion AFD
                interpretation = data.get('interpretation', {})
                if 'tokens' in interpretation:
                    print(f"   TOKENS AFD: {interpretation['tokens']}")
                if 'interpretacion' in interpretation:
                    print(f"   INTERPRETACION: {interpretation['interpretacion']}")
                
                # Mostrar primeros 3 productos
                productos = data.get('recommendations', [])
                if productos:
                    print("   PRODUCTOS:")
                    for j, prod in enumerate(productos[:3], 1):
                        precio = prod.get('precio', prod.get('price', 0))
                        sinonimo = prod.get('sinonimo_usado', '')
                        match_reasons = prod.get('match_reasons', [])
                        print(f"      {j}. {prod.get('nombre', 'N/A')} - ${precio}")
                        if sinonimo:
                            print(f"         Sinonimo usado: {sinonimo}")
                        if match_reasons:
                            print(f"         Razon: {', '.join(match_reasons)}")
                else:
                    print("   No se encontraron productos")
            else:
                print(f"   ERROR HTTP: {response.status_code}")
                print(f"   RESPUESTA: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ERROR CONEXION: {e}")
        
        print("-" * 60)
    
    # Test de salud del sistema
    print(f"\nHEALTH CHECK")
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   STATUS: {health_data.get('status', 'unknown')}")
            print(f"   PRODUCTOS: {health_data.get('productos', 0)}")
            print(f"   SINONIMOS: {health_data.get('sinonimos', 0)}")
            print(f"   VERSION: {health_data.get('version', 'unknown')}")
        else:
            print(f"   HEALTH CHECK FAILED: {health_response.status_code}")
    except Exception as e:
        print(f"   HEALTH CHECK ERROR: {e}")

if __name__ == "__main__":
    test_afd_system()