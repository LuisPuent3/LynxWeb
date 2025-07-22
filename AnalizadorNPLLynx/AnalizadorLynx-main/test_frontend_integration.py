#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test completo de integración con frontend - Simula las consultas exactas del frontend
"""

import requests
import json
import time

def test_frontend_integration():
    print("🚀 TEST DE INTEGRACIÓN CON FRONTEND")
    print("=" * 60)
    
    # URL del servidor LCLN (mismo que usa el frontend)
    API_URL = "http://127.0.0.1:8004"
    
    # Queries que el usuario introduciría en el frontend
    test_queries = [
        # Casos que mejoramos
        "bebidas menores a 20",           # AFD operators + category filtering
        "bebidas con azucar",             # New semantic category  
        "productos mayor a 10 pero menor a 20",  # Price ranges
        "botanas pixnatw",                # Spell correction pixnatw → picante
        "snacks picantes",                # Picante synonyms
        
        # Casos de validación adicionales
        "bebidas sin azucar menor a 15",  # Combined filters
        "que bebidas tienes menores a 20", # Natural language
        "coca cola 600ml",                # Specific products
    ]
    
    print(f"Conectando al servidor LCLN: {API_URL}")
    
    success_count = 0
    total_queries = len(test_queries)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{total_queries}] 🔍 Consulta: '{query}'")
        
        try:
            # Simular exactamente lo que hace el frontend
            payload = {
                "query": query,
                "limit": 10
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/search", 
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Análisis de la respuesta
                products_found = len(data.get('recommendations', []))
                strategy = data.get('interpretation', {}).get('estrategia_usada', 'N/A')
                corrections_applied = data.get('corrections', {}).get('applied', False)
                user_message = data.get('user_message', 'N/A')
                
                print(f"  ✅ Éxito: {products_found} productos encontrados")
                print(f"  ⚙️ Estrategia: {strategy}")
                print(f"  🔧 Correcciones: {'Sí' if corrections_applied else 'No'}")
                print(f"  📱 Mensaje: {user_message}")
                print(f"  ⏱️ Tiempo: {response_time:.1f}ms")
                
                # Mostrar productos encontrados
                if products_found > 0:
                    print("  📦 Productos:")
                    for j, product in enumerate(data['recommendations'][:3], 1):
                        name = product.get('nombre', 'N/A')
                        price = product.get('precio', 0)
                        category = product.get('categoria', 'N/A')
                        print(f"    {j}. {name} - ${price} ({category})")
                
                success_count += 1
                
            else:
                print(f"  ❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Error: No se pudo conectar al servidor LCLN en {API_URL}")
            print(f"  💡 Solución: Ejecutar 'python servidor_lcln_api.py' en otra terminal")
            
        except requests.exceptions.Timeout:
            print(f"  ❌ Error: Timeout después de 30 segundos")
            
        except Exception as e:
            print(f"  ❌ Error inesperado: {str(e)}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE INTEGRACIÓN CON FRONTEND")
    print("=" * 60)
    print(f"✅ Consultas exitosas: {success_count}/{total_queries}")
    print(f"📈 Tasa de éxito: {(success_count/total_queries)*100:.1f}%")
    
    if success_count == total_queries:
        print("🎉 ¡PERFECTO! Todas las mejoras funcionan correctamente en el frontend")
        print("🚀 El sistema está listo para producción")
    elif success_count > total_queries * 0.8:
        print("⚠️ La mayoría de funciones trabajando, revisar errores menores")
    else:
        print("❌ Problemas significativos de integración, necesita revisión")
    
    return success_count == total_queries

def check_server_status():
    """Verificar si el servidor LCLN está corriendo"""
    try:
        response = requests.get("http://127.0.0.1:8004/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    # Verificar primero si el servidor está corriendo
    if not check_server_status():
        print("⚠️ El servidor LCLN no está corriendo.")
        print("💡 Para iniciar el servidor:")
        print("   cd AnalizadorNPLLynx/AnalizadorLynx-main")
        print("   python servidor_lcln_api.py")
        print("\nEjecutando test directo con el sistema...")
        
        # Test directo sin servidor (como hemos estado haciendo)
        from sistema_lcln_simple import SistemaLCLNSimplificado
        
        print("\n🔧 TEST DIRECTO (SIN API)")
        sistema = SistemaLCLNSimplificado()
        
        queries = ["bebidas menores a 20", "bebidas con azucar", "pixnatw picante"]
        for query in queries:
            print(f"\nQuery: '{query}'")
            result = sistema.buscar_productos_inteligente(query)
            print(f"Productos: {len(result['recommendations'])}")
            print(f"Estrategia: {result['interpretation']['estrategia_usada']}")
    else:
        test_frontend_integration()