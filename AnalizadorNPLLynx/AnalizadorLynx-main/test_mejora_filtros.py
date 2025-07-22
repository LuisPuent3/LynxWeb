#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_bebidas_sin_azucar():
    print("Testing filtros mejorados para 'bebidas sin azucar'")
    
    sistema = SistemaLCLNSimplificado()
    resultado = sistema.buscar_productos_inteligente('bebidas sin azucar')
    productos = resultado.get('recommendations', [])
    
    print(f"\nProductos encontrados: {len(productos)}")
    print("\nLista de productos:")
    
    for i, p in enumerate(productos[:10], 1):
        nombre = p.get('nombre', 'N/A')
        precio = p.get('precio', 'N/A')
        categoria = p.get('categoria', 'N/A')
        print(f"  {i}. {nombre} (${precio}) - Cat: {categoria}")
    
    print("\nAnalisis de filtros:")
    productos_problematicos = []
    productos_correctos = []
    
    for p in productos:
        nombre = p.get('nombre', '').lower()
        # Verificar si es realmente sin azúcar
        es_correcto = (
            nombre.startswith('agua') or
            'sin azucar' in nombre or 'sin azúcar' in nombre or
            'zero' in nombre or 'light' in nombre or 'diet' in nombre
        )
        
        # Verificar si tiene azúcar (problemático)
        es_problematico = (
            ('coca' in nombre and not any(palabra in nombre for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])) or
            ('té' in nombre and not any(palabra in nombre for palabra in ['sin azucar', 'zero', 'diet'])) or
            'bolígrafo' in nombre or 'marcador' in nombre  # No es bebida
        )
        
        if es_problematico:
            productos_problematicos.append(p.get('nombre', 'N/A'))
        elif es_correcto:
            productos_correctos.append(p.get('nombre', 'N/A'))
    
    print(f"\nProductos CORRECTOS: {len(productos_correctos)}")
    for p in productos_correctos[:5]:
        print(f"    [OK] {p}")
    
    print(f"\nProductos PROBLEMATICOS: {len(productos_problematicos)}")
    for p in productos_problematicos:
        print(f"    [ERROR] {p}")
    
    return len(productos_problematicos) == 0

if __name__ == "__main__":
    test_bebidas_sin_azucar()