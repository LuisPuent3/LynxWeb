#!/usr/bin/env python3
"""
Investigar productos con limón
"""

import mysql.connector

def investigar_limon():
    config = {
        'host': 'localhost',
        'database': 'lynxshop',
        'user': 'root',
        'password': '12345678',
        'charset': 'utf8mb4'
    }
    
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    print("🔍 INVESTIGANDO PRODUCTOS CON LIMÓN")
    print("=" * 40)
    
    # Buscar productos con limón
    cursor.execute("""
        SELECT nombre, precio, id_categoria, cantidad
        FROM productos 
        WHERE nombre LIKE '%limón%' OR nombre LIKE '%limon%'
        ORDER BY nombre
    """)
    productos_limon = cursor.fetchall()
    
    print(f"\n📦 PRODUCTOS CON LIMÓN ENCONTRADOS: {len(productos_limon)}")
    for prod in productos_limon:
        print(f"  - {prod['nombre'].strip()} - ${prod['precio']} (Cat: {prod['id_categoria']}, Stock: {prod['cantidad']})")
    
    # Buscar categorías
    cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY id_categoria")
    categorias = cursor.fetchall()
    
    print(f"\n🏷️ CATEGORÍAS DISPONIBLES:")
    for cat in categorias:
        print(f"  {cat['id_categoria']}: {cat['nombre']}")
    
    # Verificar si existe producto "Limón" directamente
    cursor.execute("""
        SELECT nombre, precio, id_categoria 
        FROM productos 
        WHERE nombre LIKE 'Lim%' 
        ORDER BY LENGTH(nombre), nombre
    """)
    productos_lim = cursor.fetchall()
    
    print(f"\n🍋 PRODUCTOS QUE EMPIEZAN CON 'LIM':")
    for prod in productos_lim:
        print(f"  - {prod['nombre'].strip()} - ${prod['precio']} (Cat: {prod['id_categoria']})")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    investigar_limon()
