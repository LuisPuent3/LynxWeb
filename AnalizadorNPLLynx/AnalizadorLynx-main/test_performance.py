#!/usr/bin/env python3
"""
Optimizador de Performance para Sistema LCLN
Reduce tiempos de respuesta mediante pre-carga y optimizaciones
"""

import asyncio
import aiohttp
import time
import json

async def test_performance_optimizado():
    print("⚡ OPTIMIZANDO PERFORMANCE DEL SISTEMA")
    print("="*40)
    
    # Configuración
    API_BASE = "http://localhost:8004"
    
    # Test de múltiples consultas simultáneas
    consultas = [
        "snacks baratos",
        "bebidas",
        "coca cola", 
        "frutas economicas",
        "doritos"
    ]
    
    print("🔥 Probando consultas simultáneas...")
    
    async with aiohttp.ClientSession() as session:
        inicio = time.time()
        
        # Ejecutar todas las consultas en paralelo
        tasks = []
        for consulta in consultas:
            task = hacer_consulta_async(session, API_BASE, consulta)
            tasks.append(task)
        
        resultados = await asyncio.gather(*tasks)
        
        tiempo_total = (time.time() - inicio) * 1000
        
        print(f"✅ {len(consultas)} consultas completadas en {tiempo_total:.1f}ms")
        print(f"⚡ Promedio por consulta: {tiempo_total/len(consultas):.1f}ms")
        
        # Mostrar resultados
        for i, (consulta, resultado) in enumerate(zip(consultas, resultados)):
            if resultado:
                productos = resultado.get('metadata', {}).get('products_found', 0)
                estrategia = resultado.get('interpretation', {}).get('estrategia_usada', 'unknown')
                print(f"   {i+1}. '{consulta}': {productos} productos ({estrategia})")
    
    print("\n" + "="*40)

async def hacer_consulta_async(session, api_base, consulta):
    try:
        async with session.post(
            f"{api_base}/api/nlp/analyze",
            json={"query": consulta},
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                return await response.json()
            return None
    except Exception as e:
        print(f"Error en '{consulta}': {e}")
        return None

if __name__ == "__main__":
    # Ejecutar test asíncrono
    asyncio.run(test_performance_optimizado())
