#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Revisar productos picantes en el sistema
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def check_spicy_products():
    print("PRODUCTOS PICANTES EN EL SISTEMA")
    print("=" * 40)
    
    sistema = SistemaLCLNSimplificado()
    # Acceder al cache de productos
    productos = sistema._cache_productos
    
    spicy_keywords = ['flama', 'fuego', 'dinamita', 'picante', 'chile', 'jalapeño', 'habanero']
    
    print("\nProductos con palabras relacionadas a picante:")
    spicy_products = []
    
    for nombre, datos in productos.items():
        nombre_lower = nombre.lower()
        for keyword in spicy_keywords:
            if keyword in nombre_lower:
                spicy_products.append((datos['id'], nombre, datos['precio'], datos['categoria']))
                print(f"  ID {datos['id']}: {nombre} (${datos['precio']}) - {datos['categoria']}")
                break
    
    print(f"\nTotal productos picantes encontrados: {len(spicy_products)}")
    
    # También buscar en descripciones o nombres que puedan ser picantes
    print("\nBúsqueda manual por productos que podrían ser picantes:")
    all_products = []
    for nombre, datos in productos.items():
        all_products.append((datos['id'], nombre, datos['precio'], datos['categoria']))
    
    # Ordenar por nombre
    all_products.sort(key=lambda x: x[1])
    
    potential_spicy = []
    for id_prod, nombre, precio, categoria in all_products:
        nombre_lower = nombre.lower()
        # Buscar palabras que puedan indicar que es picante
        if any(word in nombre_lower for word in ['dorito', 'cheeto', 'crujito', 'susalia', 'nacho', 'chip']):
            potential_spicy.append((id_prod, nombre, precio, categoria))
            print(f"  ID {id_prod}: {nombre} (${precio}) - {categoria}")
    
    print(f"\nTotal productos potencialmente picantes: {len(potential_spicy)}")
    
    return spicy_products + potential_spicy

if __name__ == "__main__":
    productos = check_spicy_products()