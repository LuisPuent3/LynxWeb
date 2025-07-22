#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test improved synonym integration
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_improved_synonyms():
    print("=== TEST MEJORAS DE SINÓNIMOS ===")
    print("=" * 60)
    
    sistema = SistemaLCLNSimplificado()
    
    # Casos de prueba que antes fallaban o eran limitados
    test_cases = [
        ("papitas", "Debería encontrar productos de papas usando sinónimo 'papitas'"),
        ("refresco", "Debería encontrar bebidas usando sinónimo 'refresco'"),
        ("jugo", "Debería encontrar jugos usando sinónimo directo"),
        ("chesco", "Debería encontrar refrescos por jerga coloquial"),
        ("agua de naranja", "Debería usar sinónimo específico"),
        ("picante", "Debería encontrar productos picantes por sinónimo"),
        ("dulce", "Debería encontrar productos dulces usando sinónimo"),
        ("chips", "Debería encontrar snacks usando sinónimo"),
    ]
    
    for query, expected in test_cases:
        print(f"\nQuery: '{query}'")
        print(f"Expected: {expected}")
        
        result = sistema.buscar_productos_inteligente(query)
        
        print(f"Strategy: {result['interpretation']['estrategia_usada']}")
        print(f"Products found: {len(result['recommendations'])}")
        
        # Show results
        for i, p in enumerate(result['recommendations'][:5]):
            precio = p['precio']
            categoria = p.get('categoria', 'N/A')
            print(f"  {i+1}. {p['nombre']} - ${precio} ({categoria})")
        
        # Analysis based on query
        if query == "papitas":
            has_chips = any("papa" in p['nombre'].lower() or "frito" in p['nombre'].lower() 
                           for p in result['recommendations'][:3])
            print(f"  Found potato chips: {has_chips}")
            
        elif query == "refresco":
            has_drinks = any(p.get('categoria', '').lower() == 'bebidas' 
                           for p in result['recommendations'][:3])
            print(f"  Found beverages: {has_drinks}")
            
        elif query == "dulce":
            has_sweets = any(word in p['nombre'].lower() for p in result['recommendations'][:3]
                           for word in ['dulce', 'chocolate', 'galleta', 'caramelo', 'paleta'])
            print(f"  Found sweet products: {has_sweets}")
            
        elif query == "chips":
            has_snacks = any("papa" in p['nombre'].lower() or "chip" in p['nombre'].lower() or
                           "frito" in p['nombre'].lower() for p in result['recommendations'][:3])
            print(f"  Found chips/snacks: {has_snacks}")
    
    print(f"\n{'='*60}")
    print("SUMMARY OF SYNONYM IMPROVEMENTS:")
    print("- Enhanced exact synonym matching") 
    print("- Flexible partial synonym matching")
    print("- Better integration in semantic search")
    print("- Improved generic search with synonyms")
    print("- Word-by-word synonym analysis")
    print("- Synonym system now fully utilized!")

if __name__ == "__main__":
    test_improved_synonyms()