#!/usr/bin/env python3
"""
Test de detección de chetos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'AnalizadorNPLLynx', 'AnalizadorLynx-main'))

from sistema_lcln_simple import SistemaLCLNSimple

def test_chetos():
    print("🧪 TESTING DETECCIÓN DE CHETOS")
    print("=" * 40)
    
    sistema = SistemaLCLNSimple()
    
    queries = [
        "chetos",
        "cheetos", 
        "chetos baratos",
        "chetos picantes",
        "crujitos"
    ]
    
    for query in queries:
        print(f"\n🔍 QUERY: '{query}'")
        result = sistema.buscar_productos_inteligente(query)
        print(f"   📦 ENCONTRADOS: {len(result['productos'])}")
        
        if result['productos']:
            for i, producto in enumerate(result['productos'][:3], 1):
                print(f"   {i}. {producto['nombre']} - ${producto['precio']}")
        else:
            print("   ❌ Sin resultados")

if __name__ == "__main__":
    test_chetos()
