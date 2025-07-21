#!/usr/bin/env python3
"""
Test de Integración NLP-Backend
Prueba la integración entre el sistema NLP y el backend
"""

import requests
import json
import time

def test_nlp_backend_integration():
    """Test específico de integración NLP-Backend"""
    
    print("🧪 PRUEBA DE INTEGRACIÓN NLP-BACKEND")
    print("=" * 45)
    
    api_nlp = "http://localhost:8004"
    api_backend = "http://localhost:5000"
    
    # 1. Verificar servicios
    print("\n1️⃣ VERIFICANDO SERVICIOS...")
    
    # NLP Service
    try:
        health_nlp = requests.get(f"{api_nlp}/api/health", timeout=5)
        if health_nlp.status_code == 200:
            data = health_nlp.json()
            print(f"   ✅ NLP Service: {data['status']}")
            print(f"      • Productos: {data['components']['products']}")
        else:
            print(f"   ❌ NLP Service: Error {health_nlp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ NLP Service: {e}")
        return False
    
    # Backend Service  
    try:
        health_backend = requests.get(f"{api_backend}/api/health", timeout=5)
        print(f"   ✅ Backend Service: {health_backend.status_code}")
    except Exception as e:
        print(f"   ❌ Backend Service: {e}")
        return False
    
    # 2. Probar consultas NLP con productos reales
    print("\n2️⃣ PROBANDO CONSULTAS CON PRODUCTOS REALES...")
    
    consultas = [
        "bebidas coca cola",
        "snacks doritos", 
        "dulces mexicanos",
        "productos baratos menos de 20 pesos",
        "papelería cuadernos"
    ]
    
    resultados_exitosos = 0
    
    for consulta in consultas:
        print(f"\n   🔍 '{consulta}':")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{api_nlp}/api/nlp/analyze",
                json={"query": consulta},
                timeout=10
            )
            tiempo = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                productos = data.get('recommendations', [])
                
                print(f"      ✅ {len(productos)} productos en {tiempo:.2f}s")
                  # Mostrar productos con imágenes
                productos_con_imagen = sum(1 for p in productos if p.get('imagen'))
                print(f"      🖼️ Productos con imagen: {productos_con_imagen}/{len(productos)}")
                
                # Mostrar top 3
                for i, producto in enumerate(productos[:3]):
                    nombre = producto.get('nombre', producto.get('name', 'N/A'))
                    precio = producto.get('price', producto.get('precio', 0))
                    imagen = "✅" if producto.get('imagen', producto.get('image')) else "❌"
                    print(f"         {i+1}. {nombre} - ${precio} - Img:{imagen}")
                
                resultados_exitosos += 1
                
            else:
                print(f"      ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 3. Probar funciones dinámicas
    print("\n3️⃣ PROBANDO FUNCIONES DINÁMICAS...")
    
    # Stats
    try:
        stats = requests.get(f"{api_nlp}/api/stats", timeout=5)
        if stats.status_code == 200:
            stats_data = stats.json()
            print(f"   ✅ Stats: {stats_data.get('total_products', 0)} productos")
        else:
            print(f"   ❌ Stats: Error {stats.status_code}")
    except Exception as e:
        print(f"   ❌ Stats: {e}")
    
    # Cache refresh
    try:
        refresh = requests.post(f"{api_nlp}/api/force-cache-refresh", timeout=15)
        if refresh.status_code == 200:
            refresh_data = refresh.json()
            print(f"   ✅ Cache refresh: {refresh_data.get('message', 'Exitoso')}")
        else:
            print(f"   ❌ Cache refresh: Error {refresh.status_code}")
    except Exception as e:
        print(f"   ❌ Cache refresh: {e}")
    
    # 4. Resumen
    print("\n4️⃣ RESUMEN")
    print("=" * 15)
    print(f"   📊 Consultas exitosas: {resultados_exitosos}/{len(consultas)}")
    
    if resultados_exitosos == len(consultas):
        print("   🎉 INTEGRACIÓN NLP-BACKEND: ✅ EXITOSA")
        print("   🚀 Sistema listo para uso en producción!")
        return True
    else:
        print(f"   ⚠️ Integración parcial: {resultados_exitosos}/{len(consultas)}")
        return False

if __name__ == "__main__":
    success = test_nlp_backend_integration()
    exit(0 if success else 1)
