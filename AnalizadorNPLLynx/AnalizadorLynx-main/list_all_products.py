#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Listar todos los productos en el sistema
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def list_all_products():
    print("TODOS LOS PRODUCTOS EN EL SISTEMA")
    print("=" * 50)
    
    sistema = SistemaLCLNSimplificado()
    productos = sistema._cache_productos
    
    print(f"Total productos en cache: {len(productos)}")
    print("\nListado completo:")
    
    # Ordenar por ID
    productos_ordenados = []
    for nombre, datos in productos.items():
        productos_ordenados.append((datos['id'], nombre, datos['precio'], datos['categoria']))
    
    productos_ordenados.sort()
    
    for id_prod, nombre, precio, categoria in productos_ordenados:
        print(f"  ID {id_prod:2d}: {nombre:<30} ${precio:>5.1f} - {categoria}")

if __name__ == "__main__":
    list_all_products()