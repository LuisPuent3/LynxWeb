#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test multiple products per synonym
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_multiple_synonyms():
    print("=== TEST MÚLTIPLES PRODUCTOS POR SINÓNIMO ===")
    print("=" * 60)
    
    sistema = SistemaLCLNSimplificado()
    
    # Casos de prueba donde esperamos múltiples productos
    test_cases = [
        "picante",    # Sabemos que tiene 3 productos: Crujitos Fuego, Pelon Pelo Rico, Paleta Rockaleta
        "dulce",      # También debería tener múltiples productos
        "tropical",   # Sabemos que tiene 4 productos según análisis anterior
        "chips",      # Podría tener múltiples productos
    ]
    
    for query in test_cases:
        print(f"\n=== Query: '{query}' ===")
        
        result = sistema.buscar_productos_inteligente(query)
        
        print(f"Strategy: {result['interpretation']['estrategia_usada']}")
        print(f"Products found: {len(result['recommendations'])}")
        
        # Mostrar todos los productos encontrados
        for i, p in enumerate(result['recommendations']):
            precio = p['precio']
            categoria = p.get('categoria', 'N/A')
            print(f"  {i+1}. {p['nombre']} - ${precio} ({categoria})")
        
        # Análisis específico para "picante"
        if query == "picante":
            expected_products = ["Crujitos Fuego", "Pelon Pelo Rico", "Paleta Rockaleta"]
            found_expected = []
            
            for expected in expected_products:
                for product in result['recommendations']:
                    if expected.lower() in product['nombre'].lower():
                        found_expected.append(expected)
                        break
            
            print(f"  Expected products found: {len(found_expected)}/{len(expected_products)}")
            for found in found_expected:
                print(f"    - {found} OK")
            
            if len(found_expected) == len(expected_products):
                print("  SUCCESS: All expected products found!")
            else:
                print("  ISSUE: Some expected products missing")

    print(f"\n{'='*60}")
    print("SUMMARY:")
    print("Testing if synonyms now show ALL associated products")
    print("instead of just the first one")

if __name__ == "__main__":
    test_multiple_synonyms()