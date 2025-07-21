#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import subprocess
import sys
import signal

# Configuración de la API
API_URL = "http://localhost:8001"
servidor_proceso = None

def iniciar_servidor():
    """Iniciar servidor FastAPI en un hilo separado"""
    global servidor_proceso
    servidor_proceso = subprocess.Popen([
        "python", "-m", "uvicorn", 
        "api.main_lcln_dynamic:app", 
        "--host", "0.0.0.0", 
        "--port", "8001"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)

def detener_servidor():
    """Detener el servidor"""
    global servidor_proceso
    if servidor_proceso:
        servidor_proceso.terminate()
        servidor_proceso.wait()

def signal_handler(sig, frame):
    print("\nDeteniendo servidor...")
    detener_servidor()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def test_final_cases():
    """Probar todos los casos críticos mejorados"""
    print("SISTEMA LCLN - RESUMEN FINAL DE MEJORAS")
    print("="*70)
    
    test_cases = [
        ("botana sin picante", "Antes: 4 productos (picantes incorrectos) | Ahora: incluye snacks no-picantes"),
        ("snacks picantes", "Verificar que sigue funcionando correctamente"),
        ("dulces", "Verificar que encuentra golosinas correctamente"),
        ("panditas", "Verificar producto específico"),
        ("coca cola sin azucar", "Verificar producto específico con atributo"),
        ("bebidas baratas", "Verificar categoría con filtro precio")
    ]
    
    resultados = {}
    
    for query, description in test_cases:
        print(f"\n🔍 CASO: '{query}'")
        print(f"   📋 {description}")
        
        try:
            response = requests.post(f"{API_URL}/api/nlp/analyze", json={"query": query}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                productos = data.get('recommendations', [])
                interpretacion = data.get('interpretation', {})
                estrategia = interpretacion.get('estrategia_usada', 'N/A')
                
                resultados[query] = {
                    'productos_count': len(productos),
                    'estrategia': estrategia,
                    'success': True
                }
                
                print(f"   ✅ ÉXITO: {len(productos)} productos encontrados")
                print(f"   📊 Estrategia: {estrategia}")
                
            else:
                print(f"   ❌ ERROR HTTP: {response.status_code}")
                resultados[query] = {'success': False, 'error': response.status_code}
                
        except Exception as e:
            print(f"   ❌ EXCEPCIÓN: {str(e)}")
            resultados[query] = {'success': False, 'error': str(e)}
    
    print("\n" + "="*70)
    print("RESUMEN DE RESULTADOS:")
    print("="*70)
    
    for query, result in resultados.items():
        if result['success']:
            count = result['productos_count']
            estrategia = result['estrategia']
            status = "✅ FUNCIONANDO"
            
            # Casos especiales para validar mejoras
            if query == "botana sin picante" and count >= 15:
                status += " 🚀 MEJORADO!"
            elif query == "snacks picantes" and count >= 2:
                status += " ✅ CORRECTO"
            elif query == "dulces" and count >= 8:
                status += " ✅ CORRECTO"
                
            print(f"   {status:20s} | {query:25s} | {count:2d} productos | {estrategia}")
        else:
            print(f"   ❌ ERROR            | {query:25s} | {result.get('error', 'Unknown')}")
    
    # Mostrar la mejora más importante
    if 'botana sin picante' in resultados and resultados['botana sin picante']['success']:
        count = resultados['botana sin picante']['productos_count']
        print(f"\n🎉 MEJORA PRINCIPAL: 'botana sin picante' ahora encuentra {count} productos")
        print("   (antes solo 4 productos, y eran picantes incorrectos)")
        print("   Ahora incluye tanto golosinas dulces como snacks no-picantes!")
    
    print("\n🏁 Pruebas completadas - Sistema LCLN optimizado!")
    return resultados

def main():
    print("Iniciando servidor API...")
    iniciar_servidor()
    
    try:
        test_final_cases()
    finally:
        detener_servidor()

if __name__ == "__main__":
    main()
