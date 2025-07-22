#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test enhanced spell checker functionality
"""

from corrector_ortografico import CorrectorOrtografico

def test_spell_checker():
    print("TEST CORRECTOR ORTOGRÁFICO MEJORADO")
    print("=" * 50)
    
    corrector = CorrectorOrtografico()
    
    # Test cases for spell correction
    test_cases = [
        # Original requirement case
        ("pixnatw", "picante"),
        
        # Other picante variations
        ("picabte", "picante"),
        ("pikante", "picante"),  
        ("pixante", "picante"),
        ("picamte", "picante"),
        
        # Other common typos
        ("koka kola", "coca-cola"),
        ("chetoos", "cheetos"),
        ("vebidas", "bebidas"),
        ("asucar", "azúcar"),
        
        # Test full queries
        ("botanas pixnatw", "expected: botanas picante"),
        ("snacks picabte", "expected: snacks picante"),
    ]
    
    print("CASOS DE CORRECCIÓN INDIVIDUAL:")
    for palabra_incorrecta, palabra_esperada in test_cases:
        if not palabra_esperada.startswith("expected:"):
            palabra_corregida, confianza = corrector.corregir_palabra(palabra_incorrecta)
            
            if palabra_corregida != palabra_incorrecta:  # If correction was applied
                if palabra_corregida.lower() == palabra_esperada.lower():
                    status = "OK"
                else:
                    status = "ERR"
                    
                print(f"  {status} '{palabra_incorrecta}' -> '{palabra_corregida}' (esperado: '{palabra_esperada}') [confianza: {confianza:.2f}]")
            else:
                print(f"  ERR '{palabra_incorrecta}' -> SIN CORRECCIÓN (esperado: '{palabra_esperada}')")
    
    print(f"\nCASOS DE CORRECCIÓN DE CONSULTAS COMPLETAS:")
    
    from sistema_lcln_simple import SistemaLCLNSimplificado
    sistema = SistemaLCLNSimplificado()
    
    queries_test = [
        "botanas pixnatw",  # Should find spicy snacks
        "snacks picabte",   # Should find spicy snacks  
        "pixnatw productos", # Should find spicy products
    ]
    
    for consulta in queries_test:
        print(f"\nConsulta: '{consulta}'")
        resultado = sistema.buscar_productos_inteligente(consulta)
        
        corrections = resultado.get('corrections', {})
        if corrections.get('applied'):
            original = corrections['original_query'] 
            corrected = corrections['corrected_query']
            print(f"  Corrección aplicada: '{original}' -> '{corrected}'")
        else:
            print(f"  Sin correcciones aplicadas")
            
        productos = resultado['recommendations'][:3]
        print(f"  Productos encontrados: {len(productos)}")
        
        # Check if any spicy products were found
        spicy_found = 0
        for p in productos:
            nombre = p['nombre'].lower()
            if any(word in nombre for word in ['dinamita', 'fuego', 'flama', 'picante', 'chile']):
                spicy_found += 1
                print(f"    - {p['nombre']} (${p['precio']}) [PICANTE]")
            else:
                print(f"    - {p['nombre']} (${p['precio']})")
        
        if spicy_found > 0:
            print(f"  ✓ Encontró {spicy_found} productos picantes")
        else:
            print(f"  ⚠️ No encontró productos picantes")

if __name__ == "__main__":
    test_spell_checker()