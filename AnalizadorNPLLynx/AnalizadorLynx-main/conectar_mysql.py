#!/usr/bin/env python3
"""
Migración LYNX NLP -> BD Real MySQL LynxShop
Con contraseña correcta
"""

import mysql.connector
import json
from pathlib import Path

def conectar_mysql():
    """Conectar a MySQL con contraseña correcta"""
    try:
        config = {
            'host': 'localhost',
            'database': 'lynxshop', 
            'user': 'root',
            'password': '123456789',
            'charset': 'utf8mb4'
        }
        
        conn = mysql.connector.connect(**config)
        print("✅ Conexión exitosa a MySQL lynxshop!")
        return conn, config
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None, None

def extraer_datos_reales():
    """Extraer productos y categorías reales"""
    conn, config = conectar_mysql()
    if not conn:
        return None, None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener productos
        query_productos = """
        SELECT 
            p.id_producto,
            p.nombre,
            p.precio,
            p.cantidad,
            c.nombre as categoria
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        WHERE p.cantidad > 0
        ORDER BY c.nombre, p.nombre
        """
        
        cursor.execute(query_productos)
        productos = cursor.fetchall()
        
        # Obtener categorías
        cursor.execute("SELECT * FROM categorias ORDER BY nombre")
        categorias = cursor.fetchall()
        
        print(f"📦 Productos extraídos: {len(productos)}")
        print(f"📁 Categorías extraídas: {len(categorias)}")
        
        # Mostrar algunos ejemplos
        print(f"\n📊 Primeros 5 productos:")
        for prod in productos[:5]:
            print(f"  - {prod['nombre']} ({prod['categoria']}) - ${prod['precio']}")
        
        print(f"\n📁 Categorías encontradas:")
        for cat in categorias:
            print(f"  - {cat['nombre']}")
        
        cursor.close()
        conn.close()
        
        return productos, categorias
        
    except Exception as e:
        print(f"❌ Error extrayendo datos: {e}")
        cursor.close()
        conn.close()
        return None, None

def crear_configuracion_nlp(productos, categorias):
    """Crear configuración para el sistema NLP"""
    
    config_nlp = {
        'database': {
            'type': 'mysql',
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': '123456789',
            'charset': 'utf8mb4'
        },
        'productos_reales': len(productos),
        'categorias_reales': len(categorias),
        'categorias_lista': [cat['nombre'] for cat in categorias],
        'productos_muestra': [
            {
                'id': prod['id_producto'],
                'nombre': prod['nombre'],
                'precio': float(prod['precio']),
                'categoria': prod['categoria']
            }
            for prod in productos[:10]  # Muestra de 10 productos
        ],
        'configuracion_nlp': {
            'usar_bd_real': True,
            'conectar_mysql_directo': True,
            'cache_consultas': True,
            'max_resultados': 20
        }
    }
    
    # Guardar configuración
    config_path = Path("config_nlp_mysql.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_nlp, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Configuración NLP guardada en: {config_path}")
    return config_nlp

def main():
    """Función principal"""
    print("🚀 Conectando LYNX NLP con BD Real MySQL LynxShop...")
    
    # 1. Extraer datos
    productos, categorias = extraer_datos_reales()
    
    if not productos or not categorias:
        print("❌ No se pudieron extraer los datos.")
        return False
    
    # 2. Crear configuración
    config = crear_configuracion_nlp(productos, categorias)
    
    print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*50)
    print(f"📦 {len(productos)} productos disponibles")
    print(f"📁 {len(categorias)} categorías configuradas")
    print("📄 Configuración MySQL lista para NLP")
    print("="*50)
    
    print("\n🔧 Próximos pasos:")
    print("1. Actualizar utilidades.py para usar MySQL")
    print("2. Reiniciar servidor FastAPI")
    print("3. Probar búsquedas con productos reales")
    
    return True

if __name__ == "__main__":
    main()
