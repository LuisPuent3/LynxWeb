#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rápido para verificar AFD operadores con 'menores a'
"""

from sistema_lcln_simple import SistemaLCLNSimplificado
import time

def test_operadores():
    print("TEST AFD OPERADORES - MENORES A")
    print("=" * 40)
    
    sistema = SistemaLCLNSimplificado()
    
    consultas_test = [
        "bebidas menores a 20",
        "que bebidas tienes menores a 20", 
        "productos menores a 15 pesos",
        "bebidas menor a 20",
        "bebidas mayores a 10"
    ]
    
    for consulta in consultas_test:
        print(f"\nConsulta: '{consulta}'")
        
        try:
            inicio = time.time()
            resultado = sistema.buscar_productos_inteligente(consulta)
            tiempo_ms = (time.time() - inicio) * 1000
            
            productos = resultado.get('recommendations', [])
            print(f"Productos encontrados: {len(productos)}")
            print(f"Tiempo: {tiempo_ms:.1f}ms")
            
            # Mostrar primeros productos
            for i, p in enumerate(productos[:3], 1):
                nombre = p.get('nombre', 'N/A')
                precio = p.get('precio', 'N/A')
                categoria = p.get('categoria', 'N/A')
                print(f"  {i}. {nombre} (${precio}) - {categoria}")
                
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_operadores()