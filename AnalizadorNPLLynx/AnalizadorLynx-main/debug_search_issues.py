#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script for search quality issues
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def debug_search_issues():
    print("DEBUG: SEARCH QUALITY ISSUES")
    print("=" * 50)
    
    sistema = SistemaLCLNSimplificado()
    
    # Test cases que están fallando
    failing_queries = [
        "picante",                # Should return spicy snacks, not Fuze tea
        "bebidas con azucar",     # Being interpreted too broadly
        "papas sin picante",      # Returning Fuze tea incorrectly
    ]
    
    for query in failing_queries:
        print(f"\n=== QUERY: '{query}' ===")
        
        result = sistema.buscar_productos_inteligente(query)
        
        print(f"Estrategia: {result['interpretation']['estrategia_usada']}")
        print(f"Categoria detectada: {result['interpretation'].get('categoria_detectada', 'N/A')}")
        print(f"Modificadores: {result['interpretation'].get('modificadores_detectados', 'N/A')}")
        print(f"Productos encontrados: {len(result['recommendations'])}")
        
        print("\nProductos retornados:")
        for i, p in enumerate(result['recommendations'][:5]):
            categoria = p.get('categoria', 'N/A')
            print(f"  {i+1}. {p['nombre']} - ${p['precio']} ({categoria})")
        
        # Analysis: Check if results make sense
        print("\nANÁLISIS:")
        if query == "picante":
            has_spicy = False
            has_fuze_tea = False
            for p in result['recommendations'][:5]:
                if any(word in p['nombre'].lower() for word in ['fuze', 'té', 'te']):
                    has_fuze_tea = True
                    print(f"  ❌ Fuze tea encontrado: {p['nombre']}")
                if any(word in p['nombre'].lower() for word in ['picante', 'flama', 'dinamita', 'chile', 'picoso']):
                    has_spicy = True
                    print(f"  ✅ Producto picante: {p['nombre']}")
            
            if has_fuze_tea and not has_spicy:
                print("  🚨 PROBLEMA: Devuelve Fuze tea pero no productos picantes")
                
        elif query == "bebidas con azucar":
            sugar_drinks = 0
            all_beverages = 0
            for p in result['recommendations'][:5]:
                if p.get('categoria', '').lower() in ['bebidas', 'bebida']:
                    all_beverages += 1
                    # Check if it's a sugary drink
                    nombre = p['nombre'].lower()
                    if (any(word in nombre for word in ['coca', 'sprite', 'fanta', 'jugo', 'té', 'te']) and 
                        not any(word in nombre for word in ['zero', 'light', 'diet', 'sin azucar'])):
                        sugar_drinks += 1
                        print(f"  ✅ Bebida con azúcar: {p['nombre']}")
            
            if all_beverages > sugar_drinks:
                print(f"  ⚠️ PROBLEMA: {all_beverages - sugar_drinks} bebidas que podrían no tener azúcar")
                
        elif query == "papas sin picante":
            has_chips = False
            has_fuze_tea = False
            for p in result['recommendations'][:5]:
                if any(word in p['nombre'].lower() for word in ['papa', 'papas', 'sabritas', 'chip']):
                    has_chips = True
                    nombre = p['nombre'].lower()
                    if any(word in nombre for word in ['picante', 'flama', 'chile', 'dinamita']):
                        print(f"  ❌ Papa picante encontrada: {p['nombre']}")
                    else:
                        print(f"  ✅ Papa sin picante: {p['nombre']}")
                        
                if any(word in p['nombre'].lower() for word in ['fuze', 'té', 'te']):
                    has_fuze_tea = True
                    print(f"  ❌ Fuze tea encontrado: {p['nombre']}")
            
            if has_fuze_tea:
                print("  🚨 PROBLEMA: Devuelve Fuze tea para búsqueda de papas")
            if not has_chips:
                print("  🚨 PROBLEMA: No encuentra papas/chips")

if __name__ == "__main__":
    debug_search_issues()