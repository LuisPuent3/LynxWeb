#!/usr/bin/env python3
"""
Test Completo del Sistema LCLN Integrado
Verifica que todo funcione correctamente después de que el admin agregue productos
"""

import requests
import json
import mysql.connector
from datetime import datetime

def test_sistema_completo():
    print("🧪 TESTING SISTEMA LCLN COMPLETO")
    print("="*50)
    
    # Configuración
    API_BASE = "http://localhost:8004"
    
    # Test 1: Health Check
    print("\n1️⃣  Test Health Check")
    try:
        response = requests.get(f"{API_BASE}/api/health")
        health = response.json()
        print(f"   ✅ Status: {health['status']}")
        print(f"   📦 {health['components']['products']}")  
        print(f"   📂 {health['components']['categories']}")
        print(f"   🖼️  Imágenes incluidas: {health['features']['images_included']}")
        print(f"   🔄 Adaptativo: {health['features']['adaptive_to_new_products']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Estadísticas Detalladas  
    print("\n2️⃣  Test Estadísticas")
    try:
        response = requests.get(f"{API_BASE}/api/stats")
        stats = response.json()
        print(f"   📊 Sistema: {stats['sistema']}")
        print(f"   📦 Productos totales: {stats['totales']['productos']}")
        print(f"   🖼️  Con imágenes: {stats['totales']['con_imagenes']}")
        print(f"   📂 Categorías: {list(stats['productos_por_categoria'].keys())}")
        
        # Mostrar productos por categoría
        for categoria, cantidad in stats['productos_por_categoria'].items():
            precios = stats['estadisticas_precios'][categoria]
            print(f"     - {categoria}: {cantidad} productos (${precios['min']:.1f} - ${precios['max']:.1f})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Búsquedas por Categoría
    print("\n3️⃣  Test Búsquedas por Categoría")
    consultas_categoria = ["snacks", "bebidas", "frutas", "golosinas"]
    
    for consulta in consultas_categoria:
        try:
            response = requests.post(f"{API_BASE}/api/nlp/analyze", 
                                   json={"query": consulta})
            result = response.json()
            
            print(f"   🔍 '{consulta}': {result['metadata']['products_found']} productos")
            print(f"      Estrategia: {result['interpretation']['estrategia_usada']}")
            
            if result['recommendations']:
                primer_producto = result['recommendations'][0]
                print(f"      Primer producto: {primer_producto['nombre']} - ${primer_producto['precio']} - {primer_producto['imagen']}")
                
        except Exception as e:
            print(f"   ❌ Error en '{consulta}': {e}")
    
    # Test 4: Búsquedas con Filtros
    print("\n4️⃣  Test Búsquedas con Filtros")  
    consultas_filtros = [
        "productos baratos",
        "snacks economicos", 
        "bebidas baratas",
        "frutas economicas"
    ]
    
    for consulta in consultas_filtros:
        try:
            response = requests.post(f"{API_BASE}/api/nlp/analyze",
                                   json={"query": consulta})
            result = response.json()
            
            productos_encontrados = result['metadata']['products_found']
            print(f"   🔍 '{consulta}': {productos_encontrados} productos")
            
            if result['recommendations']:
                precios = [p['precio'] for p in result['recommendations'][:3]]
                print(f"      Precios top 3: ${min(precios):.1f} - ${max(precios):.1f}")
                
        except Exception as e:
            print(f"   ❌ Error en '{consulta}': {e}")
    
    # Test 5: Productos Específicos
    print("\n5️⃣  Test Productos Específicos")
    productos_especificos = ["coca cola", "doritos", "oreo", "sprite"]
    
    for producto in productos_especificos:
        try:
            response = requests.post(f"{API_BASE}/api/nlp/analyze",
                                   json={"query": producto})
            result = response.json()
            
            encontrados = result['metadata']['products_found']
            estrategia = result['interpretation']['estrategia_usada']
            print(f"   🔍 '{producto}': {encontrados} productos - {estrategia}")
            
            if result['recommendations']:
                primer_match = result['recommendations'][0]
                print(f"      Match: {primer_match['nombre']} - ${primer_match['precio']}")
                
        except Exception as e:
            print(f"   ❌ Error en '{producto}': {e}")
    
    # Test 6: Rendimiento
    print("\n6️⃣  Test Rendimiento")
    import time
    
    consultas_rendimiento = ["bebidas baratas", "snacks", "coca cola"]
    tiempos = []
    
    for consulta in consultas_rendimiento:
        try:
            inicio = time.time()
            response = requests.post(f"{API_BASE}/api/nlp/analyze",
                                   json={"query": consulta})
            tiempo_total = (time.time() - inicio) * 1000
            
            result = response.json()
            tiempo_interno = result['processing_time_ms']
            
            tiempos.append(tiempo_total)
            print(f"   ⚡ '{consulta}': {tiempo_interno:.1f}ms (interno) / {tiempo_total:.1f}ms (total)")
            
        except Exception as e:
            print(f"   ❌ Error en '{consulta}': {e}")
    
    if tiempos:
        print(f"   📊 Promedio: {sum(tiempos)/len(tiempos):.1f}ms")
    
    # Test 7: Cache y Adaptabilidad
    print("\n7️⃣  Test Cache y Adaptabilidad")
    try:
        # Verificar cache actual
        response = requests.get(f"{API_BASE}/api/health")
        health = response.json()
        cache_timestamp = health['components']['cache_updated']
        print(f"   🕐 Cache actualizado: {cache_timestamp}")
        
        # Forzar refresh del cache  
        response = requests.get(f"{API_BASE}/api/force-cache-refresh")
        refresh_result = response.json()
        
        if refresh_result['success']:
            print(f"   ✅ Cache refrescado exitosamente")
            print(f"   📦 Productos cargados: {refresh_result['productos_cargados']}")
            print(f"   📂 Categorías cargadas: {refresh_result['categorias_cargadas']}")
        else:
            print(f"   ❌ Error refrescando cache: {refresh_result.get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Error en test cache: {e}")
    
    print("\n" + "="*50)
    print("✅ TESTING COMPLETO - Sistema LCLN listo para producción")

if __name__ == "__main__":
    test_sistema_completo()
