#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_mejorado_limpio import sistema_lcln_mejorado
import json

def test_snacks_products():
    """Test to see what snacks are available and which ones are spicy vs non-spicy"""
    sistema = sistema_lcln_mejorado
    
    print("=== TODOS LOS SNACKS DISPONIBLES ===")
    print("Analizando cuáles son picantes y cuáles no...")
    print()
    
    snacks = []
    for nombre_producto, data in sistema._cache_productos.items():
        if data['categoria_nombre'].lower() == 'snacks':
            snacks.append(data)
    
    # Ordenar por precio
    snacks.sort(key=lambda x: x['precio'])
    
    for snack in snacks:
        nombre_lower = snack['nombre'].lower()
        es_picante = any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas'])
        
        etiqueta = "🌶️ PICANTE" if es_picante else "🍯 NO PICANTE"
        print(f"{etiqueta}: {snack['nombre']} - ${snack['precio']}")
    
    print(f"\nTotal snacks: {len(snacks)}")
    print()

def test_botana_sin_picante():
    """Test botana sin picante query"""
    query = "botana sin picante"
    print(f"🧪 PROBANDO: '{query}'")
    print("="*60)
    
    resultado = sistema_lcln_mejorado.analizar_consulta_lcln(query)
    
    productos = resultado.get('productos', [])
    print(f"📦 Productos encontrados: {len(productos)}")
    print("🛍️  Resultados:")
    
    for i, producto in enumerate(productos[:10]):  # Mostrar top 10
        categoria = producto['categoria_nombre']
        precio = producto['precio']
        print(f"   {i+1:2d}. [{categoria:10s}] {producto['nombre']} - ${precio}")
    
    return resultado

if __name__ == "__main__":
    # Mostrar todos los snacks primero
    test_snacks_products()
    
    # Luego probar la búsqueda
    test_botana_sin_picante()
