#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test price range functionality
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_price_ranges():
    print("TEST DE RANGOS DE PRECIO")
    print("=" * 50)
    
    sistema = SistemaLCLNSimplificado()
    
    # Test queries with price ranges
    queries = [
        "productos mayor a 10 pero menor a 20",
        "bebidas mayor a 5 pero menor a 15", 
        "mayor a 15 y menor a 25",
        "snacks mayor a 20 pero menor a 30",
        "bebidas menores a 20",  # Single operator (for comparison)
        "productos mayores a 10"  # Single operator (for comparison)
    ]
    
    for consulta in queries:
        print(f"\nConsulta: '{consulta}'")
        
        # Test the price extraction function directly
        filtro_precio = sistema._extraer_filtro_precio_completo(consulta)
        print(f"Filtro extraído: {filtro_precio}")
        
        resultado = sistema.buscar_productos_inteligente(consulta)
        productos = resultado['recommendations'][:8]
        
        print(f"Productos encontrados: {len(productos)}")
        print(f"Estrategia: {resultado['interpretation']['estrategia_usada']}")
        
        for i, p in enumerate(productos, 1):
            precio = p['precio']
            nombre = p['nombre'][:30]
            categoria = p['categoria']
            
            # Check if price is in range
            in_range = ""
            if filtro_precio and filtro_precio.get('operador') == 'BETWEEN':
                min_price = filtro_precio['precio_min']
                max_price = filtro_precio['precio_max']
                if min_price < precio <= max_price:
                    in_range = " ✓"
                else:
                    in_range = " ✗"
            elif filtro_precio and filtro_precio.get('operador') == '<=':
                if precio <= filtro_precio['precio']:
                    in_range = " ✓"
                else:
                    in_range = " ✗"
            elif filtro_precio and filtro_precio.get('operador') == '>=':
                if precio >= filtro_precio['precio']:
                    in_range = " ✓"
                else:
                    in_range = " ✗"
            
            print(f"  {i}. {nombre:<30} ${precio:>5.1f} - {categoria}{in_range}")

if __name__ == "__main__":
    test_price_ranges()