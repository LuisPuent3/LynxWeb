#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_mejorado_limpio import sistema_lcln_mejorado
import json

def test_botana_sin_picante_detailed():
    """Test detallado para botana sin picante"""
    query = "botana sin picante"
    print(f"🧪 ANÁLISIS DETALLADO: '{query}'")
    print("="*70)
    
    resultado = sistema_lcln_mejorado.analizar_consulta_lcln(query)
    
    productos = resultado.get('productos', [])
    print(f"📦 Total de productos encontrados: {len(productos)}")
    print("\n🛍️  RESULTADOS COMPLETOS:")
    
    golosinas_count = 0
    snacks_count = 0
    otros_count = 0
    
    for i, producto in enumerate(productos):
        categoria = producto['categoria_nombre']
        precio = producto['precio']
        nombre = producto['nombre']
        
        if categoria == 'Golosinas':
            icono = "🍭"
            golosinas_count += 1
        elif categoria == 'Snacks':
            icono = "🥨"
            snacks_count += 1
        else:
            icono = "📦"
            otros_count += 1
            
        print(f"   {i+1:2d}. {icono} [{categoria:10s}] {nombre} - ${precio}")
    
    print(f"\n📊 RESUMEN POR CATEGORÍA:")
    print(f"   🍭 Golosinas: {golosinas_count}")
    print(f"   🥨 Snacks: {snacks_count}")
    print(f"   📦 Otros: {otros_count}")
    
    # Mostrar algunos snacks específicos que deberían aparecer
    print(f"\n🎯 VERIFICACIÓN: ¿Aparecen snacks no-picantes esperados?")
    snacks_names = [p['nombre'].lower() for p in productos if p['categoria_nombre'] == 'Snacks']
    
    expected_snacks = ['flor de naranjo', 'fritos', 'cheetos', 'original']
    for expected in expected_snacks:
        encontrado = any(expected in name for name in snacks_names)
        status = "✅" if encontrado else "❌"
        print(f"   {status} Productos con '{expected}' en el nombre")
    
    return resultado

if __name__ == "__main__":
    test_botana_sin_picante_detailed()
