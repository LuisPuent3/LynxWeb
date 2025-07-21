#!/usr/bin/env python3
"""
Migración Simple: Conectar LYNX NLP con BD Real MySQL LynxShop
"""

import mysql.connector
import json
from pathlib import Path

# Configuraciones MySQL para probar
mysql_configs = [
    {
        'host': 'localhost',
        'database': 'lynxshop',
        'user': 'root',
        'password': '',
        'charset': 'utf8mb4'
    },
    {
        'host': 'localhost',
        'database': 'lynxshop',
        'user': 'root',
        'password': 'root',
        'charset': 'utf8mb4'
    },
    {
        'host': 'localhost',
        'database': 'lynxshop',
        'user': 'root',
        'password': 'password',
        'charset': 'utf8mb4'
    }
]

def probar_conexion():
    """Probar conexión a MySQL con diferentes configuraciones"""
    
    # Configuraciones MySQL para probar
    mysql_configs = [
        {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': '',
            'charset': 'utf8mb4'
        },
        {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': 'root',
            'charset': 'utf8mb4'
        },
        {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': 'password',
            'charset': 'utf8mb4'
        }
    ]
    
    for i, config in enumerate(mysql_configs):
        try:
            print(f"🔍 Probando configuración {i+1}: user='{config['user']}', password='{config['password']}'")
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor(dictionary=True)
            
            # Obtener productos
            cursor.execute("""
                SELECT 
                    p.id_producto,
                    p.nombre as nombre_producto,
                    p.precio,
                    p.cantidad,
                    c.nombre as categoria
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.cantidad > 0
                LIMIT 5
            """)
            
            productos = cursor.fetchall()
            
            print(f"✅ Conexión exitosa a MySQL lynxshop!")
            print(f"📦 Productos encontrados: {len(productos)}")
            
            for prod in productos:
                print(f"  - {prod['nombre_producto']} ({prod['categoria']}) - ${prod['precio']}")
                
            cursor.close()
            conn.close()
            
            # Guardar configuración exitosa
            global mysql_config_exitosa
            mysql_config_exitosa = config
            return True
            
        except Exception as e:
            print(f"❌ Config {i+1} falló: {e}")
            continue
    
    print("❌ No se pudo conectar con ninguna configuración")
    return False

def obtener_estadisticas_bd():
    """Obtener estadísticas de la BD real"""
    try:
        # Usar configuración exitosa
        conn = mysql.connector.connect(**mysql_config_exitosa)
        cursor = conn.cursor()
        
        # Contar productos
        cursor.execute("SELECT COUNT(*) FROM productos WHERE cantidad > 0")
        total_productos = cursor.fetchone()[0]
        
        # Contar categorías
        cursor.execute("SELECT COUNT(*) FROM categorias")
        total_categorias = cursor.fetchone()[0]
        
        # Productos por categoría
        cursor.execute("""
            SELECT c.nombre, COUNT(p.id_producto) as total
            FROM categorias c
            LEFT JOIN productos p ON c.id_categoria = p.id_categoria AND p.cantidad > 0
            GROUP BY c.id_categoria, c.nombre
            ORDER BY total DESC
        """)
        
        categorias_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 ESTADÍSTICAS BD LYNXSHOP:")
        print(f"📦 Total productos disponibles: {total_productos}")
        print(f"📁 Total categorías: {total_categorias}")
        print(f"\n📈 Productos por categoría:")
        
        for cat_name, count in categorias_stats:
            print(f"  - {cat_name}: {count} productos")
            
        return {
            'total_productos': total_productos,
            'total_categorias': total_categorias,
            'categorias': dict(categorias_stats)
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return None

def crear_configuracion_bd_real():
    """Crear configuración para que el NLP use la BD real"""        config_bd_real = {
            'database_config': {
                'type': 'mysql',
                'host': 'localhost',
                'database': 'lynxshop',
                'user': 'root',
                'password': '12345678',
                'charset': 'utf8mb4'
            },
        'queries': {
            'productos': """
                SELECT 
                    p.id_producto,
                    p.nombre,
                    p.precio,
                    p.cantidad,
                    c.nombre as categoria
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.cantidad > 0
            """,
            'categorias': "SELECT * FROM categorias",
            'buscar_producto': """
                SELECT 
                    p.id_producto,
                    p.nombre,
                    p.precio,
                    p.cantidad,
                    c.nombre as categoria,
                    p.imagen
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.cantidad > 0 
                AND (p.nombre LIKE %s OR c.nombre LIKE %s)
                ORDER BY p.precio
            """
        },
        'nlp_config': {
            'use_real_database': True,
            'fallback_to_sqlite': False,
            'cache_queries': True,
            'max_results': 20
        }
    }
    
    # Guardar configuración
    config_path = Path("config_bd_real.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_bd_real, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Configuración guardada en: {config_path}")
    return config_bd_real

def main():
    """Función principal"""
    print("🔄 Probando conexión LYNX NLP -> BD Real MySQL...")
    
    # 1. Probar conexión
    if not probar_conexion():
        print("❌ No se puede conectar a la BD. Verificar XAMPP MySQL.")
        return
    
    # 2. Obtener estadísticas
    stats = obtener_estadisticas_bd()
    if not stats:
        print("❌ Error obteniendo estadísticas.")
        return
    
    # 3. Crear configuración
    config = crear_configuracion_bd_real()
    
    print("\n✅ CONFIGURACIÓN COMPLETADA")
    print("🚀 El sistema NLP ahora puede consumir la BD real de LynxShop")
    print(f"📦 {stats['total_productos']} productos disponibles")
    print(f"📁 {stats['total_categorias']} categorías")
    
    print("\n🔧 Próximos pasos:")
    print("1. Actualizar utilidades.py para usar MySQL")
    print("2. Reiniciar servidor FastAPI")
    print("3. Probar búsquedas con productos reales")

if __name__ == "__main__":
    main()
