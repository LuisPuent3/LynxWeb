#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import subprocess
import threading
from threading import Thread
import signal
import sys

# Configuración de la API
API_URL = "http://localhost:8001"
servidor_proceso = None

def iniciar_servidor():
    """Iniciar servidor FastAPI en un hilo separado"""
    global servidor_proceso
    import subprocess
    servidor_proceso = subprocess.Popen([
        "python", "-m", "uvicorn", 
        "api.main_lcln_dynamic:app", 
        "--host", "0.0.0.0", 
        "--port", "8001"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)  # Dar tiempo para que inicie

def detener_servidor():
    """Detener el servidor"""
    global servidor_proceso
    if servidor_proceso:
        servidor_proceso.terminate()
        servidor_proceso.wait()

def signal_handler(sig, frame):
    print("\n🛑 Deteniendo servidor...")
    detener_servidor()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def test_query(query, description):
    """Probar una consulta específica"""
    print(f"🔍 Consulta: '{query}'")
    print(f"   📋 {description}")
    
    try:
        response = requests.post(f"{API_URL}/api/nlp/analyze", json={"query": query}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Respuesta exitosa")
              # Mostrar información clave
            productos = data.get('recommendations', [])
            interpretacion = data.get('interpretation', {})
            estrategia = interpretacion.get('estrategia_usada', 'N/A')
            
            print(f"   📊 Estrategia: {estrategia}")
            print(f"   📦 Productos encontrados: {len(productos)}")
            
            if productos:
                print("   🎯 Productos (Top 10):")
                for i, producto in enumerate(productos[:10]):
                    categoria = producto.get('categoria_nombre', 'N/A')
                    nombre = producto.get('nombre', 'N/A')
                    precio = producto.get('precio', 0)
                    
                    if categoria == 'Golosinas':
                        icono = "🍭"
                    elif categoria == 'Snacks':
                        icono = "🥨"
                    else:
                        icono = "📦"
                    
                    print(f"      {i+1:2d}. {icono} [{categoria:10s}] {nombre} - ${precio}")
                
                # Contar por categoría
                golosinas = sum(1 for p in productos if p.get('categoria_nombre') == 'Golosinas')
                snacks = sum(1 for p in productos if p.get('categoria_nombre') == 'Snacks')
                otros = len(productos) - golosinas - snacks
                
                print(f"   📊 Por categoría: 🍭{golosinas} 🥨{snacks} 📦{otros}")
            else:
                print("   ❌ No se encontraron productos")
            print("   ✅ Resultado")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()

def main():
    print("🚀 Iniciando servidor API en puerto 8001...")
    iniciar_servidor()
    
    try:
        print("🧪 PROBANDO 'BOTANA SIN PICANTE' CON API")
        print("=" * 60)
        
        # Probar botana sin picante
        test_query(
            "botana sin picante",
            "Debería incluir tanto golosinas dulces como snacks no-picantes"
        )
        
        # Comparar con la búsqueda anterior
        test_query(
            "snacks",
            "Todos los snacks para comparación"
        )
        
        test_query(
            "dulces",
            "Golosinas para comparación"
        )
        
        print("🏁 Pruebas completadas")
        
    finally:
        detener_servidor()

if __name__ == "__main__":
    main()
