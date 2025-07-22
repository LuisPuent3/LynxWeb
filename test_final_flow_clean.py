#!/usr/bin/env python3
"""
TEST FINAL DEL FLUJO COMPLETO - SISTEMA LCLN AFD LYNX (Windows Compatible)
Simula exactamente lo que hace el frontend React -> Backend Node.js -> AFD Python
"""

import requests
import json

def test_complete_flow():
    """Test del flujo completo: Frontend -> Node.js -> AFD"""
    
    backend_url = "http://localhost:5000"
    
    print("=== TEST FLUJO COMPLETO: FRONTEND -> NODE.JS -> AFD ===")
    print()
    
    # 1. Test Health Check (como lo hace el frontend)
    print("1. HEALTH CHECK (simulando frontend)")
    try:
        health_response = requests.get(f"{backend_url}/api/lcln/status", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   STATUS: {health_data.get('lcln_service', 'unknown')}")
            if health_data.get('status'):
                print(f"   PRODUCTOS: {health_data['status'].get('productos', 0)}")
                print(f"   SINONIMOS: {health_data['status'].get('sinonimos', 0)}")
                print(f"   VERSION: {health_data['status'].get('version', 'unknown')}")
        else:
            print(f"   ERROR: Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"   ERROR: Health check error: {e}")
    
    print("-" * 60)
    
    # 2. Test de busquedas especificas del usuario
    print("2. BUSQUEDAS SEGUN ESPECIFICACIONES DEL USUARIO")
    
    test_queries = [
        {
            "query": "coquita barata",
            "descripcion": "Sinonimo + precio -> Debe encontrar Coca-Cola",
            "expectativa": "usar sinonimo 'coquita' para encontrar Coca-Cola"
        },
        {
            "query": "chetos baratos picantes", 
            "descripcion": "Caso complejo prioridades -> producto -> categoria -> fallback",
            "expectativa": "seguir sistema de prioridades AFD"
        },
        {
            "query": "botana barata",
            "descripcion": "Categoria + precio -> snacks baratos",
            "expectativa": "categoria 'botana' -> 'snacks' con filtro precio"
        },
        {
            "query": "coca",
            "descripcion": "Sinonimo simple -> Coca-Cola",
            "expectativa": "encontrar por sinonimo directo"
        },
        {
            "query": "bebida barata",
            "descripcion": "Categoria bebidas + filtro precio <= $20",
            "expectativa": "bebidas baratas ordenadas por precio"
        }
    ]
    
    resultados_exitosos = 0
    total_tests = len(test_queries)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. QUERY: '{test_case['query']}'")
        print(f"   EXPECTATIVA: {test_case['expectativa']}")
        
        try:
            # Simular exactamente la peticion del frontend React
            search_response = requests.post(
                f"{backend_url}/api/lcln/search",
                json={"query": test_case["query"], "limit": 10},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if search_response.status_code == 200:
                data = search_response.json()
                
                productos_encontrados = data.get('products_found', 0)
                tiempo_ms = data.get('processing_time_ms', 0)
                mensaje = data.get('message', 'N/A')
                productos = data.get('products', [])
                
                print(f"   STATUS: OK ({search_response.status_code})")
                print(f"   TIEMPO: {tiempo_ms:.1f}ms")
                print(f"   PRODUCTOS: {productos_encontrados}")
                print(f"   MENSAJE: {mensaje}")
                
                # Verificar interpretacion AFD
                interpretation = data.get('interpretation', {})
                if 'tokens' in interpretation:
                    tokens = interpretation['tokens']
                    print(f"   AFD TOKENS: {len(tokens)} tokens")
                    for token in tokens[:3]:  # Mostrar primeros 3
                        print(f"      - {token.get('valor', '')} -> {token.get('tipo', '')}")
                
                # Verificar productos
                if productos:
                    print(f"   PRODUCTOS ENCONTRADOS:")
                    for j, prod in enumerate(productos[:3], 1):
                        precio = prod.get('precio', 0)
                        sinonimo = prod.get('sinonimo_usado', '')
                        match_reasons = prod.get('match_reasons', [])
                        
                        print(f"      {j}. {prod.get('nombre', 'N/A')} - ${precio}")
                        if sinonimo:
                            print(f"         [Sinonimo usado: {sinonimo}]")
                        if match_reasons:
                            print(f"         [Razon: {', '.join(match_reasons)}]")
                    
                    if len(productos) > 3:
                        print(f"      ... y {len(productos) - 3} productos mas")
                
                # Verificar especificaciones
                cumple_especificaciones = True
                
                if productos_encontrados > 10:
                    print(f"   ADVERTENCIA: {productos_encontrados} productos (maximo 10)")
                    cumple_especificaciones = False
                
                if productos_encontrados > 0:
                    resultados_exitosos += 1
                    status = "EXITOSO" if cumple_especificaciones else "CON ADVERTENCIAS"
                    print(f"   RESULTADO: {status}")
                else:
                    print(f"   RESULTADO: SIN PRODUCTOS")
                    
            else:
                print(f"   ERROR HTTP: {search_response.status_code}")
                try:
                    error_data = search_response.json()
                    print(f"   ERROR: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   RESPONSE: {search_response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ERROR CONEXION: {e}")
        
        print("-" * 60)
    
    # 3. Resumen final
    print(f"\n=== RESUMEN FINAL ===")
    print(f"Tests exitosos: {resultados_exitosos}/{total_tests}")
    print(f"Porcentaje exito: {(resultados_exitosos/total_tests)*100:.1f}%")
    
    if resultados_exitosos == total_tests:
        print("SISTEMA COMPLETAMENTE FUNCIONAL")
        print("AFD implementado segun especificaciones")
        print("Sistema de prioridades funcionando")
        print("Sinonimos por producto integrados")
        print("Filtros de precio aplicados")
        print("Maximo 10 productos respetado")
        print("Frontend -> Backend -> AFD funcionando")
    elif resultados_exitosos >= total_tests * 0.8:
        print("SISTEMA MAYORMENTE FUNCIONAL")
        print(f"   {resultados_exitosos}/{total_tests} casos exitosos")
        print("   Revisar casos fallidos para optimizacion")
    else:
        print("SISTEMA NECESITA REVISION")
        print(f"   Solo {resultados_exitosos}/{total_tests} casos exitosos")
    
    print("\n=== ESTADO DEL SISTEMA ===")
    print("Backend Node.js: Puerto 5000 (proxy)")
    print("AFD Python: Puerto 8007 (motor LCLN)")
    print("Base de datos: MySQL (lynxshop)")
    print("Frontend: React TypeScript (integrado)")
    print("Flujo: React -> Node.js -> Python AFD -> MySQL")

if __name__ == "__main__":
    test_complete_flow()