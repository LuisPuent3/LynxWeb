#!/usr/bin/env python3
"""
Test de conexión MySQL para LYNX NLP
"""

import mysql.connector
import json

def probar_conexion_mysql():
    """Probar conexión con la BD real"""
    config = {
        'host': 'localhost',
        'database': 'lynxshop',
        'user': 'root',
        'password': '12345678',
        'charset': 'utf8mb4'
    }
    
    try:
        print("🔄 Conectando a MySQL lynxshop...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        # Probar consulta de productos
        cursor.execute("""
            SELECT 
                p.id_producto,
                p.nombre,
                p.precio,
                c.nombre as categoria
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.cantidad > 0
            LIMIT 10
        """)
        
        productos = cursor.fetchall()
        
        print(f"✅ Conexión exitosa!")
        print(f"📦 Productos encontrados: {len(productos)}")
        
        for prod in productos:
            print(f"  - {prod['nombre']} ({prod['categoria']}) - ${prod['precio']}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    probar_conexion_mysql()
