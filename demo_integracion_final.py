#!/usr/bin/env python3
"""
DEMO FINAL: LYNX NLP Integration Test
Demuestra la integración completa funcionando
"""

import requests
import json
from datetime import datetime

def test_nlp_integration():
    """Prueba completa del sistema NLP integrado"""
    
    print("🚀 LYNX NLP - DEMO DE INTEGRACIÓN COMPLETA")
    print("=" * 50)
    
    # URLs de los servicios
    nlp_url = "http://localhost:8004"
    backend_url = "http://localhost:5000"
    frontend_url = "http://localhost:5173"
    
    # 1. Test de salud de servicios
    print("\n📋 1. VERIFICANDO SERVICIOS...")
    
    services_status = {
        "NLP API": test_service_health(f"{nlp_url}/api/health"),
        "Backend": test_service_health(f"{backend_url}/api/health"), 
        "Frontend": test_frontend_status(frontend_url)
    }
    
    for service, status in services_status.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {service}: {'ONLINE' if status else 'OFFLINE'}")
    
    if not all(services_status.values()):
        print("\n⚠️ Algunos servicios no están disponibles")
        return False
    
    # 2. Test de búsquedas NLP
    print("\n🔍 2. PROBANDO BÚSQUEDAS NLP...")
    
    test_queries = [
        ("bebidas sin azucar", "Búsqueda por categoría y atributo"),
        ("snacks picantes baratos", "Búsqueda con múltiples filtros"),
        ("productos menos de 20 pesos", "Filtro por precio"),
        ("coca cola", "Búsqueda específica de producto"),
        ("doritos", "Búsqueda por nombre exacto")
    ]
    
    successful_searches = 0
    total_products_found = 0
    
    for query, description in test_queries:
        print(f"\n   🔍 Probando: '{query}' ({description})")
        
        result = test_nlp_search(nlp_url, query)
        if result:
            products_count = len(result.get('recommendations', []))
            processing_time = result.get('processing_time_ms', 0)
            
            print(f"      ✅ {products_count} productos encontrados en {processing_time}ms")
            
            # Mostrar algunos productos de ejemplo
            if products_count > 0:
                for i, product in enumerate(result['recommendations'][:2]):
                    name = product.get('nombre', 'N/A')
                    price = product.get('precio', 0)
                    category = product.get('categoria', 'N/A')
                    print(f"         • {name} - ${price} ({category})")
                
                if products_count > 2:
                    print(f"         ... y {products_count - 2} productos más")
            
            successful_searches += 1
            total_products_found += products_count
            
            # Mostrar correcciones si las hay
            corrections = result.get('corrections', {})
            if corrections.get('applied'):
                original = result.get('original_query', query)
                corrected = corrections.get('corrected_query', '')
                print(f"      🔧 Corrección: '{original}' → '{corrected}'")
        else:
            print(f"      ❌ Búsqueda fallida")
    
    # 3. Resumen de resultados
    print("\n📊 3. RESUMEN DE RESULTADOS:")
    print(f"   • Búsquedas exitosas: {successful_searches}/{len(test_queries)}")
    print(f"   • Total productos encontrados: {total_products_found}")
    print(f"   • Promedio por búsqueda: {total_products_found/len(test_queries):.1f}")
    
    # 4. Test de estadísticas del sistema
    print("\n📈 4. ESTADÍSTICAS DEL SISTEMA:")
    stats_result = test_system_stats(nlp_url)
    if stats_result:
        components = stats_result.get('components', {})
        print(f"   • Base de datos: {components.get('database', 'N/A')}")
        print(f"   • Productos cargados: {components.get('products', 'N/A')}")
        print(f"   • Motor NLP: {components.get('nlp_engine', 'N/A')}")
        
        version = stats_result.get('version', 'N/A')
        print(f"   • Versión del sistema: {version}")
    
    # 5. Conclusión
    success_rate = successful_searches / len(test_queries)
    print(f"\n🎯 5. CONCLUSIÓN:")
    
    if success_rate >= 0.8:
        print(f"   🎉 ¡INTEGRACIÓN EXITOSA! ({success_rate*100:.0f}% de éxito)")
        print("   ✅ El sistema NLP está completamente funcional")
        print("   ✅ La integración con el frontend está lista")
        print("   ✅ Los 3 servicios están coordinados correctamente")
        
        # Instrucciones para el usuario
        print(f"\n🌐 PARA PROBAR EN EL NAVEGADOR:")
        print(f"   1. Visita: {frontend_url}")
        print("   2. Usa la barra de búsqueda con IA activada")
        print("   3. Prueba consultas como: 'bebidas sin azúcar baratas'")
        print("   4. Ve el componente de demo en la página principal")
        
        return True
    else:
        print(f"   ⚠️ Integración parcial ({success_rate*100:.0f}% de éxito)")
        print("   🔧 Algunos componentes necesitan ajustes")
        return False

def test_service_health(url):
    """Prueba si un servicio está disponible"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def test_frontend_status(url):
    """Prueba si el frontend está disponible"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def test_nlp_search(base_url, query):
    """Prueba una búsqueda NLP específica"""
    try:
        url = f"{base_url}/api/nlp/analyze"
        payload = {
            "query": query,
            "options": {
                "max_recommendations": 10,
                "enable_correction": True,
                "enable_recommendations": True
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"      Error: {e}")
        return None

def test_system_stats(base_url):
    """Obtiene estadísticas del sistema"""
    try:
        url = f"{base_url}/api/health"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

if __name__ == "__main__":
    print(f"Iniciando demo a las {datetime.now().strftime('%H:%M:%S')}")
    success = test_nlp_integration()
    
    if success:
        print("\n🚀 ¡EL SISTEMA LYNX NLP ESTÁ COMPLETAMENTE OPERATIVO!")
    else:
        print("\n🔧 El sistema necesita algunos ajustes")
    
    print(f"\nDemo completado a las {datetime.now().strftime('%H:%M:%S')}")
