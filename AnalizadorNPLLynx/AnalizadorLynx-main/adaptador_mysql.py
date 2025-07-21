#!/usr/bin/env python3
"""
Adaptador MySQL para Sistema LYNX NLP
Conecta directamente con la BD real de LynxShop
"""

import mysql.connector
import json
import re
from typing import List, Dict, Optional
from pathlib import Path

class AdaptadorMySQLLYNX:
    def __init__(self):
        self.mysql_config = {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': '12345678',
            'charset': 'utf8mb4'
        }
        
    def conectar(self):
        """Conectar a MySQL"""
        return mysql.connector.connect(**self.mysql_config)
        
    def buscar_productos(self, consulta: str, categoria: Optional[str] = None, 
                        precio_max: Optional[float] = None) -> List[Dict]:
        """Buscar productos en MySQL con consulta NLP"""
        
        conn = self.conectar()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Construir consulta SQL
            sql = """
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
            """
            
            params = []
              # Filtrar por nombre si hay consulta
            if consulta:
                # Buscar cada palabra de la consulta
                palabras = consulta.split()
                condiciones_nombre = []
                for palabra in palabras:
                    condiciones_nombre.append("p.nombre LIKE %s")
                    params.append(f"%{palabra}%")
                
                if condiciones_nombre:
                    sql += " AND (" + " AND ".join(condiciones_nombre) + ")"
            
            # Filtrar por categoría
            if categoria:
                sql += " AND c.nombre LIKE %s"
                params.append(f"%{categoria}%")
                
            # Filtrar por precio
            if precio_max:
                sql += " AND p.precio <= %s"
                params.append(precio_max)
            
            sql += " ORDER BY p.precio ASC LIMIT 20"
            
            cursor.execute(sql, params)
            resultados = cursor.fetchall()
            
            # Convertir a formato esperado por LYNX
            productos_nlp = []
            for prod in resultados:
                productos_nlp.append({
                    'name': prod['nombre'],
                    'category': prod['categoria'].lower(),
                    'price': float(prod['precio']),
                    'match_score': 0.9,  # Alta confianza para coincidencias directas
                    'match_reasons': ['mysql_direct_match', 'producto_real'],
                    'available': prod['cantidad'] > 0,
                    'id': prod['id_producto'],
                    'imagen': prod['imagen']
                })
                
            return productos_nlp
            
        finally:
            cursor.close()
            conn.close()
            
    def obtener_categorias(self) -> List[Dict]:
        """Obtener categorías reales de MySQL"""
        conn = self.conectar()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM categorias ORDER BY nombre")
            categorias = cursor.fetchall()
            
            return [{'id': cat['id_categoria'], 'nombre': cat['nombre']} for cat in categorias]
            
        finally:
            cursor.close()
            conn.close()
            
    def obtener_estadisticas(self) -> Dict:
        """Obtener estadísticas de la BD real"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM productos WHERE cantidad > 0")
            total_productos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM categorias")
            total_categorias = cursor.fetchone()[0]
            
            return {
                'productos_mysql': total_productos,
                'categorias_mysql': total_categorias,
                'source': 'mysql_lynxshop_real'
            }
            
        finally:
            cursor.close()
            conn.close()

# Instancia global del adaptador
adaptador_mysql = AdaptadorMySQLLYNX()

def buscar_productos_mysql(consulta: str, filtros: Dict = None) -> List[Dict]:
    """Función helper para búsqueda directa en MySQL"""
    categoria = filtros.get('categoria') if filtros else None
    precio_max = filtros.get('precio_max') if filtros else None
    
    return adaptador_mysql.buscar_productos(consulta, categoria, precio_max)

def obtener_stats_mysql() -> Dict:
    """Obtener estadísticas de MySQL"""
    return adaptador_mysql.obtener_estadisticas()

if __name__ == "__main__":
    # Prueba del adaptador
    adaptador = AdaptadorMySQLLYNX()
    
    print("🔍 Probando adaptador MySQL...")
    
    # Probar búsqueda
    productos = adaptador.buscar_productos("coca", categoria="bebidas")
    print(f"✅ Productos encontrados: {len(productos)}")
    
    for prod in productos[:3]:
        print(f"  - {prod['name']} (${prod['price']}) [{prod['category']}]")
    
    # Probar estadísticas
    stats = adaptador.obtener_estadisticas()
    print(f"📊 Estadísticas: {stats}")
