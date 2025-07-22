#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test expanded synonym search that finds ALL related products
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_expanded_search():
    print("=== TEST BÚSQUEDA EXPANDIDA DE SINÓNIMOS ===")
    print("=" * 60)
    
    sistema = SistemaLCLNSimplificado()
    
    # Casos de prueba donde esperamos búsqueda expandida
    test_cases = [
        ("chicle", "Debería mostrar Trident Y gomitas"),
        ("picante", "Debería mostrar TODOS los productos picantes, no solo los del sinónimo"),
        ("papitas", "Debería mostrar papitas Y otros snacks relacionados"),
        ("cheetos", "Debería mostrar Cheetos Y recomendar otros snacks similares"),
        ("chips", "Debería mostrar todos los chips disponibles")
    ]
    
    for query, expected in test_cases:
        print(f"\n=== Query: '{query}' ===")
        print(f"Expected: {expected}")
        
        result = sistema.buscar_productos_inteligente(query)
        
        print(f"Strategy: {result['interpretation']['estrategia_usada']}")
        print(f"Products found: {len(result['recommendations'])}")
        
        # Mostrar todos los productos encontrados
        print("Products:")
        for i, p in enumerate(result['recommendations']):
            precio = p['precio']
            categoria = p.get('categoria', 'N/A')
            print(f"  {i+1}. {p['nombre']} - ${precio} ({categoria})")
        
        # Análisis específico por query
        if query == "chicle":
            trident_found = any("trident" in p['nombre'].lower() for p in result['recommendations'])
            gomas_found = any("goma" in p['nombre'].lower() or "dulcigoma" in p['nombre'].lower() 
                             for p in result['recommendations'])
            print(f"  Trident encontrado: {trident_found}")
            print(f"  Gomitas encontradas: {gomas_found}")
            print(f"  SUCCESS: {trident_found and gomas_found}")
            
        elif query == "picante":
            picante_productos = []
            for p in result['recommendations']:
                nombre = p['nombre'].lower()
                if any(termino in nombre for termino in ['picante', 'chile', 'fuego', 'flama', 'dinamita']):
                    picante_productos.append(p['nombre'])
            
            print(f"  Productos picantes encontrados: {len(picante_productos)}")
            for prod in picante_productos:
                print(f"    - {prod}")
            
        elif query in ["papitas", "cheetos", "chips"]:
            snacks_count = sum(1 for p in result['recommendations'] 
                              if p.get('categoria', '').lower() in ['snacks', 'golosinas'])
            print(f"  Snacks encontrados: {snacks_count}/{len(result['recommendations'])}")
            
            # Mostrar variedad de snacks
            snack_names = [p['nombre'] for p in result['recommendations'] 
                          if p.get('categoria', '').lower() in ['snacks', 'golosinas']]
            print(f"  Variedad: {len(set(snack_names))}")

    print(f"\n{'='*60}")
    print("SUMMARY:")
    print("Testing if search now expands beyond just exact synonym matches")
    print("to include ALL related products in the same category/theme")

if __name__ == "__main__":
    test_expanded_search()