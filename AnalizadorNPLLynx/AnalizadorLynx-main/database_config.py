#!/usr/bin/env python3
"""
Configuración de base de datos para el sistema LCLN
Compatible con las variables de entorno de Railway
"""

import os
import mysql.connector

def get_database_connection():
    """
    Obtiene una conexión a la base de datos MySQL usando las variables de entorno
    """
    config = {
        'host': os.getenv('MYSQL_HOST', 'mysql.railway.internal'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'railway'),
        'ssl_disabled': True,
        'autocommit': True,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except Exception as e:
        print(f"[LCLN DB] Error connecting to database: {e}")
        return None

def get_productos_from_db():
    """
    Obtiene todos los productos de la base de datos para el sistema LCLN
    """
    connection = get_database_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Consulta para obtener productos con información completa
        query = """
        SELECT 
            p.id,
            p.nombre,
            p.descripcion,
            p.precio,
            p.stock,
            p.imagen,
            c.nombre as categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.stock > 0
        ORDER BY p.nombre
        """
        
        cursor.execute(query)
        productos = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        print(f"[LCLN DB] Loaded {len(productos)} products from database")
        return productos
        
    except Exception as e:
        print(f"[LCLN DB] Error fetching products: {e}")
        if connection:
            connection.close()
        return []

def test_database_connection():
    """
    Prueba la conexión a la base de datos
    """
    connection = get_database_connection()
    if connection:
        print("[LCLN DB] Database connection successful")
        connection.close()
        return True
    else:
        print("[LCLN DB] Database connection failed")
        return False
