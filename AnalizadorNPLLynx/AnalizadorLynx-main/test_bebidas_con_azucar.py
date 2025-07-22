#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test bebidas con azucar functionality
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_bebidas_con_azucar():
    print("TEST BEBIDAS CON AZÚCAR")
    print("=" * 40)
    
    sistema = SistemaLCLNSimplificado()
    
    queries = [
        "bebidas con azucar",
        "bebidas dulces",
        "refrescos con azucar", 
        "bebidas endulzadas",
        "bebidas regulares",  # Should find non-diet versions
    ]
    
    for consulta in queries:
        print(f"\nConsulta: '{consulta}'")
        resultado = sistema.buscar_productos_inteligente(consulta)
        
        productos = resultado['recommendations'][:6]
        print(f"Productos encontrados: {len(productos)}")
        print(f"Estrategia: {resultado['interpretation']['estrategia_usada']}")
        print(f"Mensaje: {resultado.get('user_message', 'N/A')}")
        
        has_sugar_count = 0
        water_count = 0
        zero_count = 0
        
        for i, p in enumerate(productos, 1):
            nombre = p['nombre']
            precio = p['precio']
            categoria = p['categoria']
            nombre_lower = nombre.lower()
            
            # Check if it should have sugar
            is_water = nombre_lower.startswith('agua')
            is_zero = any(word in nombre_lower for word in ['zero', 'light', 'diet', 'sin azucar', 'sin azúcar'])
            has_sugar = (categoria.lower() == 'bebidas' and not is_water and not is_zero)
            
            if is_water:
                water_count += 1
                indicator = " 💧"  # Water
            elif is_zero:
                zero_count += 1  
                indicator = " 🚫"  # Zero/diet
            elif has_sugar:
                has_sugar_count += 1
                indicator = " 🍯"  # Sweet/sugar
            else:
                indicator = " ❓"  # Unknown
                
            print(f"  {i}. {nombre:<30} ${precio:>5.1f} - {categoria}{indicator}")
        
        # Analysis
        print(f"  Análisis: {has_sugar_count} con azúcar, {water_count} aguas, {zero_count} zero/diet")
        
        if has_sugar_count > 0 and water_count == 0:
            print(f"  ✓ Correcto: Encontró bebidas con azúcar y excluyó aguas")
        elif water_count > 0:
            print(f"  ⚠️  Advertencia: Incluyó {water_count} aguas")
        else:
            print(f"  ❌ Error: No encontró bebidas con azúcar")

if __name__ == "__main__":
    test_bebidas_con_azucar()