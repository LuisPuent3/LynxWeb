#!/usr/bin/env python3
"""
Configurador Híbrido LYNX NLP
- Productos: Directamente de MySQL LynxShop (para flujo de compra)  
- Sinónimos: SQLite (para análisis NLP)
- Configuraciones: SQLite (para AFDs y filtros)
"""

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import mysql.connector
import sqlite3
from typing import List, Dict, Optional
import json

class ConfiguradorHibridoLYNX:
    def __init__(self):
        # Configuración MySQL (productos reales)
        self.mysql_config = {
            'host': 'localhost',
            'database': 'lynxshop', 
            'user': 'root',
            'password': '12345678',
            'charset': 'utf8mb4'
        }
          # Rutas SQLite (sinónimos y configuraciones NLP)
        # Ruta absoluta basada en la ubicación del archivo
        base_dir = Path(__file__).parent
        self.sqlite_sinonimos = base_dir / "api" / "sinonimos_lynx.db"
        
        # Si se ejecuta desde dentro de api/, ajustar la ruta
        if base_dir.name == "api":
            self.sqlite_sinonimos = base_dir / "sinonimos_lynx.db"
        
    def conectar_mysql(self):
        """Conectar a la BD real de productos"""
        return mysql.connector.connect(**self.mysql_config)
        
    def conectar_sqlite_sinonimos(self):
        """Conectar a BD de sinónimos"""
        return sqlite3.connect(self.sqlite_sinonimos)
        
    def buscar_productos_mysql(self, consulta: str = "", categoria: str = "", 
                              precio_max: float = None, precio_min: float = None,
                              limit: int = 20) -> List[Dict]:
        """
        Buscar productos DIRECTAMENTE en MySQL LynxShop
        Estos productos sí pueden comprarse porque existen realmente
        """
        conn = self.conectar_mysql()
        cursor = conn.cursor(dictionary=True)
        
        try:
            sql = """
                SELECT 
                    p.id_producto,
                    p.nombre,
                    p.precio,
                    p.cantidad,
                    p.imagen,
                    c.id_categoria,
                    c.nombre as categoria
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.cantidad > 0
            """
            
            params = []
            
            # Filtro por consulta (buscar en nombre)
            if consulta:
                palabras = consulta.split()
                condiciones = []
                for palabra in palabras:
                    condiciones.append("p.nombre LIKE %s")
                    params.append(f"%{palabra}%")
                
                if condiciones:
                    sql += " AND (" + " AND ".join(condiciones) + ")"
            
            # Filtro por categoría
            if categoria:
                sql += " AND c.nombre LIKE %s"
                params.append(f"%{categoria}%")
                
            # Filtros de precio
            if precio_min is not None:
                sql += " AND p.precio >= %s"
                params.append(precio_min)
                
            if precio_max is not None:
                sql += " AND p.precio <= %s"
                params.append(precio_max)
            
            sql += " ORDER BY p.precio ASC LIMIT %s"
            params.append(limit)
            
            cursor.execute(sql, params)
            productos = cursor.fetchall()
            
            # Convertir a formato NLP
            productos_nlp = []
            for prod in productos:
                productos_nlp.append({
                    # IDs reales para el flujo de compra
                    'id': prod['id_producto'],
                    'id_producto': prod['id_producto'],  # Importante para el frontend
                    'id_categoria': prod['id_categoria'], # Importante para el frontend
                    
                    # Datos del producto
                    'name': prod['nombre'],
                    'nombre': prod['nombre'],  # Para compatibilidad frontend
                    'price': float(prod['precio']),
                    'precio': float(prod['precio']),  # Para compatibilidad frontend
                    'category': prod['categoria'].lower(),
                    'categoria': prod['categoria'],  # Para compatibilidad frontend
                    'cantidad': prod['cantidad'],  # Stock real
                    'imagen': prod['imagen'] or 'default.jpg',
                    
                    # Metadatos NLP
                    'match_score': 0.95,  # Alta confianza - producto real
                    'match_reasons': ['mysql_direct', 'producto_real_comprable'],
                    'available': prod['cantidad'] > 0,
                    'source': 'mysql_lynxshop_real'
                })
                
            return productos_nlp
            
        finally:
            cursor.close()
            conn.close()
            
    def obtener_sinonimos_sqlite(self, termino: str) -> List[Dict]:
        """Obtener sinónimos de SQLite para análisis NLP"""
        if not self.sqlite_sinonimos.exists():
            return []
            
        conn = self.conectar_sqlite_sinonimos()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT termino, categoria, tipo, confianza
                FROM sinonimos 
                WHERE termino LIKE ? OR termino_normalizado LIKE ?
                AND activo = 1
            """, (f"%{termino}%", f"%{termino}%"))
            
            resultados = cursor.fetchall()
            
            sinonimos = []
            for resultado in resultados:                sinonimos.append({
                    'termino': resultado[0],
                    'categoria': resultado[1],
                    'tipo': resultado[2],
                    'confianza': resultado[3]
                })
                
            return sinonimos
            
        finally:
            cursor.close()
            conn.close()
            
    def analizar_consulta_nlp(self, consulta: str) -> Dict:
        """
        Análisis NLP mejorado usando sinónimos de SQLite
        """
        consulta_original = consulta
        consulta = consulta.lower().strip()
        
        # Buscar todos los sinónimos relevantes
        palabras_consulta = consulta.split()
        todos_sinonimos = []
        
        # Buscar sinónimos para palabras individuales y frases completas
        for palabra in palabras_consulta + [consulta]:
            sinonimos = self.obtener_sinonimos_sqlite(palabra)
            todos_sinonimos.extend(sinonimos)
        
        # Detectar categoría específica
        categoria_detectada = None
        for sinonimo in todos_sinonimos:
            if sinonimo['tipo'] == 'categoria' and sinonimo['categoria'] not in ['categoria', '']:
                categoria_detectada = sinonimo['categoria']
                break
        
        # Detectar términos de producto expandidos
        terminos_expandidos = []
        for sinonimo in todos_sinonimos:
            if sinonimo['tipo'] == 'producto' and sinonimo['categoria']:
                terminos_expandidos.append(sinonimo['categoria'])
        
        # Detectar filtros de precio usando sinónimos
        precio_max = None
        precio_min = None
        
        # Buscar filtros de precio en sinónimos
        filtros_precio = [s for s in todos_sinonimos if s['tipo'] == 'filtro_precio']
        
        for palabra in palabras_consulta:
            if palabra in ['barato', 'baratas', 'economico', 'económico', 'cheap']:
                precio_max = 20.0
            elif palabra in ['caro', 'costoso', 'premium', 'expensive']:
                precio_min = 30.0
          # Construir término de búsqueda inteligente
        palabras_filtro = {'barato', 'baratas', 'economico', 'económico', 'caro', 'costoso', 'sin', 'con', 'y', 'de', 'la', 'el'}
        palabras_categoria = set()
        
        # Agregar términos de categoría detectados a las palabras filtro
        if categoria_detectada:
            palabras_categoria.add(consulta.strip().lower())
            palabras_filtro.update(palabras_categoria)
        
        terminos_busqueda = []
        
        # Agregar términos originales (limpiados)
        for palabra in palabras_consulta:
            if palabra not in palabras_filtro and len(palabra) > 2:
                terminos_busqueda.append(palabra)
        
        # Agregar términos expandidos de sinónimos de producto
        terminos_busqueda.extend(terminos_expandidos)
        
        termino_busqueda_final = ' '.join(set(terminos_busqueda))  # Eliminar duplicados
        
        return {
            'termino_busqueda': termino_busqueda_final,
            'categoria': categoria_detectada,
            'precio_max': precio_max,
            'precio_min': precio_min,
            'sinonimos_encontrados': len(todos_sinonimos),
            'sinonimos_usados': len([s for s in todos_sinonimos if s['confianza'] > 0.8]),
            'terminos_expandidos': terminos_expandidos
        }
        
    def buscar_productos_hibrido(self, consulta: str, limit: int = 20) -> Dict:
        """
        Búsqueda híbrida:
        1. Análisis NLP con sinónimos de SQLite
        2. Búsqueda de productos reales en MySQL
        """
        import time
        inicio = time.time()
          # 1. Análisis NLP
        analisis = self.analizar_consulta_nlp(consulta)
        
        # 2. Búsqueda inteligente en MySQL
        # Si se detectó una categoría específica, priorizar búsqueda por categoría
        if analisis['categoria'] and not analisis['termino_busqueda']:
            # Búsqueda pura por categoría (ej: "snacks" → categoría Snacks)
            productos = self.buscar_productos_mysql(
                consulta="",  # No filtrar por nombre
                categoria=analisis['categoria'],
                precio_max=analisis['precio_max'],
                precio_min=analisis['precio_min'],
                limit=limit
            )
        else:
            # Búsqueda híbrida normal
            productos = self.buscar_productos_mysql(
                consulta=analisis['termino_busqueda'],
                categoria=analisis['categoria'],
                precio_max=analisis['precio_max'],
                precio_min=analisis['precio_min'],
                limit=limit
            )
        
        tiempo_proceso = (time.time() - inicio) * 1000
        
        # 3. Preparar respuesta
        mensaje = f"Se encontraron {len(productos)} productos"
        if analisis['categoria']:
            mensaje += f" en {analisis['categoria']}"
        if analisis['precio_max']:
            mensaje += f" hasta ${analisis['precio_max']}"
        if analisis['precio_min']:
            mensaje += f" desde ${analisis['precio_min']}"
            
        return {
            'success': True,
            'processing_time_ms': tiempo_proceso,
            'original_query': consulta,
            'analysis': analisis,
            'products_found': len(productos),
            'products': productos,
            'user_message': mensaje,
            'metadata': {
                'source': 'hybrid_mysql_sqlite',
                'mysql_products': True,
                'sqlite_synonyms': True,
                'real_purchasable': True
            }
        }
        
    def obtener_estadisticas(self) -> Dict:
        """Estadísticas del sistema híbrido"""
        
        # Productos de MySQL
        conn_mysql = self.conectar_mysql()
        cursor_mysql = conn_mysql.cursor()
        cursor_mysql.execute("SELECT COUNT(*) FROM productos WHERE cantidad > 0")
        productos_mysql = cursor_mysql.fetchone()[0]
        cursor_mysql.execute("SELECT COUNT(*) FROM categorias")
        categorias_mysql = cursor_mysql.fetchone()[0]
        cursor_mysql.close()
        conn_mysql.close()
        
        # Sinónimos de SQLite
        sinonimos_sqlite = 0
        if self.sqlite_sinonimos.exists():
            conn_sqlite = self.conectar_sqlite_sinonimos()
            cursor_sqlite = conn_sqlite.cursor()
            cursor_sqlite.execute("SELECT COUNT(*) FROM sinonimos WHERE activo = 1")
            sinonimos_sqlite = cursor_sqlite.fetchone()[0]
            cursor_sqlite.close()
            conn_sqlite.close()
        
        return {
            'productos_reales_mysql': productos_mysql,
            'categorias_mysql': categorias_mysql,
            'sinonimos_nlp_sqlite': sinonimos_sqlite,
            'modo': 'hibrido_comprable'
        }

# Instancia global
configurador_hibrido = ConfiguradorHibridoLYNX()

if __name__ == "__main__":
    # Prueba del sistema híbrido
    print("🔧 Probando configurador híbrido LYNX...")
    
    # Estadísticas
    stats = configurador_hibrido.obtener_estadisticas()
    print(f"📊 Estadísticas:")
    print(f"   Productos MySQL (comprables): {stats['productos_reales_mysql']}")
    print(f"   Categorías MySQL: {stats['categorias_mysql']}")
    print(f"   Sinónimos SQLite: {stats['sinonimos_nlp_sqlite']}")
    
    # Prueba de búsqueda
    print(f"\n🔍 Probando búsqueda híbrida...")
    resultado = configurador_hibrido.buscar_productos_hibrido("coca cola")
    print(f"   Consulta: coca cola")
    print(f"   Productos encontrados: {resultado['products_found']}")
    print(f"   Tiempo: {resultado['processing_time_ms']:.1f}ms")
    
    for prod in resultado['products'][:3]:
        print(f"     - {prod['nombre']} (ID:{prod['id_producto']}) ${prod['precio']}")
    
    print(f"\n✅ Sistema híbrido funcionando correctamente")
