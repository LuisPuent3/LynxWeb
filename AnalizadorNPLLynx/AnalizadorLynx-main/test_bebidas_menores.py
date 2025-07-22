#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test específico para bebidas menores a 20 
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_bebidas_menores():
    print("TEST ESPECÍFICO: bebidas menor a 20")
    print("=" * 50)
    
    sistema = SistemaLCLNSimplificado()
    consulta = "bebidas menor a 20"
    
    resultado = sistema.buscar_productos_inteligente(consulta)
    
    print(f"\nConsulta: '{consulta}'")
    print(f"Productos encontrados: {resultado['products_found']}")
    print(f"Estrategia usada: {resultado['interpretation']['estrategia_usada']}")
    print(f"Término búsqueda: {resultado['interpretation']['termino_busqueda']}")
    print(f"Categoría: {resultado['interpretation']['categoria']}")
    print(f"Precio máximo: {resultado['interpretation']['precio_max']}")
    
    print("\nProductos encontrados:")
    for i, p in enumerate(resultado['recommendations'][:10], 1):
        categoria = p.get('categoria', 'N/A')
        print(f"  {i}. {p['nombre']} (${p['precio']}) - {categoria}")
    
    # Verificar si son realmente bebidas
    bebidas_count = 0
    for p in resultado['recommendations']:
        if p['categoria'].lower() == 'bebidas':
            bebidas_count += 1
    
    print(f"\nBebidas reales encontradas: {bebidas_count}/{len(resultado['recommendations'])}")
    
    if bebidas_count == 0:
        print("❌ ERROR: No se encontraron bebidas!")
    else:
        print("✅ Se encontraron bebidas correctamente")

if __name__ == "__main__":
    test_bebidas_menores()