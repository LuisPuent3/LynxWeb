#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test synonyms for spicy products
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_picante_synonyms():
    print("TEST SINÓNIMOS PICANTES")
    print("=" * 40)
    
    sistema = SistemaLCLNSimplificado()
    
    # Queries to test
    queries = [
        "botanas picantes",
        "snacks con flama", 
        "picoso", 
        "flamas",
        "ardiente",
        "takis",
        "botanas sin picante"  # This should NOT return spicy products
    ]
    
    for consulta in queries:
        print(f"\nConsulta: '{consulta}'")
        resultado = sistema.buscar_productos_inteligente(consulta)
        
        productos = resultado['recommendations'][:5]
        print(f"Productos encontrados: {len(productos)}")
        
        # Show products
        for i, p in enumerate(productos, 1):
            nombre = p['nombre']
            precio = p['precio']
            categoria = p['categoria']
            
            # Check if it's spicy
            is_spicy = any(word in nombre.lower() for word in ['dinamita', 'fuego', 'flama', 'crujitos', 'susalia', 'doritos'])
            spicy_indicator = "🌶️" if is_spicy else "  "
            
            print(f"  {spicy_indicator}{i}. {nombre} (${precio}) - {categoria}")
        
        # Analysis for "sin picante" query
        if "sin picante" in consulta.lower():
            spicy_found = 0
            for p in productos:
                if any(word in p['nombre'].lower() for word in ['dinamita', 'fuego', 'flama', 'crujitos doritos', 'susalia']):
                    spicy_found += 1
            
            if spicy_found == 0:
                print(f"  ✅ Correcto: No se encontraron productos picantes")
            else:
                print(f"  ❌ Error: Se encontraron {spicy_found} productos picantes")

if __name__ == "__main__":
    test_picante_synonyms()