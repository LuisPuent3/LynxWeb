#!/usr/bin/env python3

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import requests
import json
import time
from threading import Thread
import subprocess

def start_api():
    """Función para iniciar la API en un hilo separado"""
    import uvicorn
    from api.main_lcln_dynamic import app
    
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

def test_api_queries():
    """Probar las consultas críticas"""
    # Esperar a que la API esté lista
    time.sleep(3)
    
    base_url = "http://127.0.0.1:8001"
    
    # Consultas de prueba críticas
    test_queries = [
        {"query": "snacks picantes", "expected_products": ["Crujitos Fuego", "Doritos Dinamita"]},
        {"query": "coca cola", "expected_products": ["Coca-Cola"]},
        {"query": "bebidas sin azucar", "expected_products": ["sin azúcar", "Sprite"]},
        {"query": "chetoos picantes", "expected_products": ["Crujitos Fuego", "Doritos"]}
    ]
    
    print("🧪 PROBANDO API LCLN CON CONSULTAS CRÍTICAS")
    print("=" * 50)
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected = test_case["expected_products"]
        
        try:
            print(f"\n{i}. 🔍 Consulta: '{query}'")
            
            # Hacer request a la API
            response = requests.post(
                f"{base_url}/api/nlp/analyze", 
                json={"query": query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Respuesta exitosa")
                print(f"   📄 Estructura: {list(data.keys())}")
                
                # Extraer información de la nueva estructura API
                if "recommendations" in data and "interpretation" in data:
                    estrategia = data["interpretation"].get("estrategia_usada", "unknown")
                    productos = data["recommendations"]
                    total = len(productos)
                    
                    print(f"   📊 Estrategia: {estrategia}")
                    print(f"   📦 Productos encontrados: {total}")
                    
                    # Verificar si hay productos
                    if productos:
                        print(f"   🎯 Productos:")
                        for j, producto in enumerate(productos[:3], 1):
                            nombre = producto.get("name", "Sin nombre")
                            precio = producto.get("price", 0)
                            stock = producto.get("stock", 0)
                            imagen = producto.get("image", "default.jpg")
                            print(f"      {j}. {nombre} - ${precio}")
                            print(f"         Stock: {stock}, Imagen: {imagen}")
                        
                        # Verificar expectativas
                        productos_nombres = [p.get("name", "") for p in productos[:3]]
                        found_expected = any(
                            any(exp.lower() in prod_nombre.lower() for exp in expected)
                            for prod_nombre in productos_nombres
                        )
                        
                        if found_expected:
                            print(f"   ✅ Encontrados productos esperados!")
                        else:
                            print(f"   ⚠️  No se encontraron productos esperados: {expected}")
                    else:
                        print(f"   ⚠️  No se encontraron productos")
                        
                else:
                    print(f"   ❌ Estructura de respuesta inesperada")
                    print(f"   📋 Keys disponibles: {list(data.keys())}")
                    
            else:
                print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*50}")
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    print("🚀 Iniciando servidor API en puerto 8001...")
    
    # Iniciar API en hilo separado
    api_thread = Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Ejecutar pruebas
    test_api_queries()
