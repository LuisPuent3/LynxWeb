#!/usr/bin/env python3
"""
Test completo del sistema híbrido LYNX NLP
"""

import requests
import json
import time

def test_api_endpoint(query, description):
    """Probar un endpoint de la API"""
    print(f"\n🔍 {description}")
    print(f"   Consulta: '{query}'")
    
    try:
        response = requests.post(
            "http://localhost:8003/api/nlp/analyze",
            json={"query": query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"   ✅ Productos encontrados: {data['metadata']['products_found']}")
            print(f"   ⏱️ Tiempo: {data['processing_time_ms']:.1f}ms")
            
            # Mostrar interpretación NLP
            interp = data.get('interpretation', {})
            if interp.get('categoria'):
                print(f"   🎯 Categoría detectada: {interp['categoria']}")
            if interp.get('precio_max'):
                print(f"   💰 Precio máximo: ${interp['precio_max']}")
            if interp.get('sinonimos_usados'):
                print(f"   🔤 Sinónimos usados: {interp['sinonimos_usados']}")
            
            # Mostrar primeros productos
            products = data.get('recommendations', [])
            if products:
                print(f"   📦 Primeros productos:")
                for i, prod in enumerate(products[:3]):
                    print(f"      {i+1}. {prod['nombre']} (ID:{prod['id_producto']}) ${prod['precio']} [{prod['categoria']}] Stock:{prod['cantidad']}")
            else:
                print(f"   ❌ No se encontraron productos")
                
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   💥 Error de conexión: {e}")

def main():
    print("🚀 TESTE COMPLETO DEL SISTEMA HÍBRIDO LYNX NLP")
    print("=" * 60)
    
    # Verificar estado de la API
    try:
        health = requests.get("http://localhost:8003/api/health", timeout=5).json()
        print(f"📊 Estado de la API: {health['status']}")
        comp = health['components']
        print(f"   💾 Base de datos: {comp['database']}")
        print(f"   📦 Productos: {comp['products']}")
        print(f"   📁 Categorías: {comp['categories']}")  
        print(f"   🔤 Sinónimos: {comp['synonyms']}")
        print(f"   ⚙️ Modo: {comp['mode']}")
    except:
        print("❌ No se puede conectar a la API en puerto 8003")
        return
    
    # Casos de prueba
    test_cases = [
        # Búsquedas por categoría
        ("snacks", "Búsqueda por categoría - Snacks"),
        ("bebidas", "Búsqueda por categoría - Bebidas"),
        ("golosinas", "Búsqueda por categoría - Golosinas"),
        ("frutas", "Búsqueda por categoría - Frutas"),
        
        # Búsquedas por producto específico
        ("coca cola", "Búsqueda de producto específico - Coca Cola"),
        ("doritos", "Búsqueda de producto específico - Doritos"),
        ("oreo", "Búsqueda de producto específico - Oreo"),
        
        # Búsquedas con filtros de precio
        ("bebidas baratas", "Búsqueda con filtro de precio - Bebidas baratas"),
        ("snacks economicos", "Búsqueda con filtro de precio - Snacks económicos"),
        
        # Búsquedas combinadas
        ("coca barata", "Búsqueda combinada - Producto + Precio"),
        ("dulces", "Búsqueda con sinónimo - Dulces"),
    ]
    
    # Ejecutar pruebas
    for query, description in test_cases:
        test_api_endpoint(query, description)
        time.sleep(0.1)  # Pequeña pausa entre pruebas
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("\n💡 RESUMEN:")
    print("   - Sistema híbrido: Productos reales MySQL + Sinónimos SQLite")
    print("   - Productos comprables con IDs reales para flujo de compra")
    print("   - Análisis NLP inteligente con detección de categorías y precios")

if __name__ == "__main__":
    main()
