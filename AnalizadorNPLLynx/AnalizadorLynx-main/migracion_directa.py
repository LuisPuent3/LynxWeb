#!/usr/bin/env python3
"""
Migración Directa: LYNX NLP -> MySQL LynxShop Real
"""

import mysql.connector
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime

class MigracionNLPDirecta:
    def __init__(self):
        self.mysql_config = {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': '12345678',
            'charset': 'utf8mb4'
        }
        
    def obtener_productos_reales(self):
        """Obtener productos de MySQL"""
        print("📦 Extrayendo productos de MySQL lynxshop...")
        
        conn = mysql.connector.connect(**self.mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
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
        """)
        
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"✅ Extraídos {len(productos)} productos reales")
        return productos
        
    def obtener_categorias_reales(self):
        """Obtener categorías de MySQL"""
        print("📁 Extrayendo categorías de MySQL...")
        
        conn = mysql.connector.connect(**self.mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM categorias ORDER BY nombre")
        categorias = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Extraídas {len(categorias)} categorías")
        return categorias
        
    def generar_sinonimos_categorias(self, categorias):
        """Generar sinónimos para categorías"""
        print("🔍 Generando sinónimos de categorías...")
        
        mapeo_sinonimos = {
            'bebidas': ['refresco', 'refrescos', 'bebida', 'liquido', 'drink', 'agua', 'jugo', 'soda', 'cola'],
            'snacks': ['botana', 'botanas', 'snack', 'papitas', 'papas', 'fritos', 'galletas'],
            'golosinas': ['dulce', 'dulces', 'chocolate', 'caramelo', 'goma', 'paleta'],
            'frutas': ['fruta', 'fresco', 'natural', 'vitamina'],
            'papeleria': ['utiles', 'escolar', 'oficina', 'boligrafo', 'pluma', 'cuaderno', 'lapiz']
        }
        
        sinonimos = []
        for cat in categorias:
            cat_nombre = cat['nombre'].lower()
            
            # Agregar sinónimos específicos
            if cat_nombre in mapeo_sinonimos:
                for sinonimo in mapeo_sinonimos[cat_nombre]:
                    sinonimos.append({
                        'termino': sinonimo,
                        'sinonimo_de': cat_nombre,
                        'tipo': 'categoria',
                        'confianza': 0.9
                    })
            
            # Agregar variaciones
            sinonimos.append({
                'termino': cat_nombre,
                'sinonimo_de': cat_nombre,
                'tipo': 'categoria',
                'confianza': 1.0
            })
            
        print(f"✅ Generados {len(sinonimos)} sinónimos de categorías")
        return sinonimos
        
    def generar_sinonimos_productos(self, productos):
        """Generar sinónimos para productos"""
        print("🔍 Generando sinónimos de productos...")
        
        sinonimos = []
        
        for prod in productos:
            nombre = prod['nombre'].lower()
            palabras = nombre.split()
            
            # Sinónimos por palabras clave
            for palabra in palabras:
                if len(palabra) > 3 and palabra not in ['sin', 'con', 'para']:
                    sinonimos.append({
                        'termino': palabra,
                        'sinonimo_de': nombre,
                        'tipo': 'producto',
                        'categoria': prod['categoria'].lower(),
                        'confianza': 0.8
                    })
            
            # Sinónimos específicos
            if 'coca' in nombre:
                sinonimos.extend([
                    {'termino': 'cola', 'sinonimo_de': nombre, 'tipo': 'producto', 'categoria': prod['categoria'].lower(), 'confianza': 0.85},
                    {'termino': 'coke', 'sinonimo_de': nombre, 'tipo': 'producto', 'categoria': prod['categoria'].lower(), 'confianza': 0.85}
                ])
            
            if 'sin azucar' in nombre or 'sin azúcar' in nombre:
                sinonimos.extend([
                    {'termino': 'light', 'sinonimo_de': nombre, 'tipo': 'producto', 'categoria': prod['categoria'].lower(), 'confianza': 0.9},
                    {'termino': 'diet', 'sinonimo_de': nombre, 'tipo': 'producto', 'categoria': prod['categoria'].lower(), 'confianza': 0.9},
                    {'termino': 'zero', 'sinonimo_de': nombre, 'tipo': 'producto', 'categoria': prod['categoria'].lower(), 'confianza': 0.9}
                ])
                
        print(f"✅ Generados {len(sinonimos)} sinónimos de productos")
        return sinonimos
        
    def generar_filtros_precio(self):
        """Generar filtros de precio"""
        print("💰 Generando filtros de precio...")
        
        filtros = [
            {'termino': 'barato', 'tipo': 'filtro_precio', 'valor_max': 15, 'confianza': 0.95},
            {'termino': 'economico', 'tipo': 'filtro_precio', 'valor_max': 20, 'confianza': 0.95},
            {'termino': 'caro', 'tipo': 'filtro_precio', 'valor_min': 30, 'confianza': 0.95},
            {'termino': 'costoso', 'tipo': 'filtro_precio', 'valor_min': 40, 'confianza': 0.95}
        ]
        
        print(f"✅ Generados {len(filtros)} filtros de precio")
        return filtros
        
    def actualizar_sqlite_productos(self, productos):
        """Actualizar BD SQLite de productos"""
        print("🔄 Actualizando productos en SQLite...")
        
        db_path = Path("api/productos_lynx_escalable.db")
        if not db_path.exists():
            print(f"⚠️  BD productos no existe: {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpiar tabla
        cursor.execute("DELETE FROM productos")        # Insertar productos reales
        for prod in productos:
            nombre = prod['nombre']
            nombre_normalizado = re.sub(r'[^\w\s]', ' ', nombre.lower())
            nombre_normalizado = re.sub(r'\s+', ' ', nombre_normalizado).strip()
            
            cursor.execute("""
                INSERT INTO productos (nombre, nombre_normalizado, categoria, precio, activo)
                VALUES (?, ?, ?, ?, 1)
            """, (nombre, nombre_normalizado, prod['categoria'].lower(), float(prod['precio'])))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Actualizados {len(productos)} productos en SQLite")
        
    def actualizar_sqlite_sinonimos(self, sinonimos_todos):
        """Actualizar BD SQLite de sinónimos"""
        print("🔄 Actualizando sinónimos en SQLite...")
        
        db_path = Path("api/sinonimos_lynx.db")
        if not db_path.exists():
            print(f"⚠️  BD sinónimos no existe: {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
          # Limpiar tabla
        cursor.execute("DELETE FROM sinonimos")
        
        # Solo insertar sinónimos de categorías y filtros (no necesitan producto_id específico)
        sinonimos_simples = [s for s in sinonimos_todos if s['tipo'] in ['categoria', 'filtro_precio']]
        
        # Insertar sinónimos
        for sin in sinonimos_simples:
            termino_normalizado = re.sub(r'[^\w\s]', ' ', sin['termino'].lower())
            termino_normalizado = re.sub(r'\s+', ' ', termino_normalizado).strip()
            
            cursor.execute("""
                INSERT INTO sinonimos (termino, termino_normalizado, producto_id, categoria, tipo, confianza, activo)
                VALUES (?, ?, 0, ?, ?, ?, 1)
            """, (
                sin['termino'],
                termino_normalizado,
                sin.get('categoria', sin.get('tipo', 'general')),
                sin.get('tipo', 'general'),
                sin['confianza']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Actualizados {len(sinonimos_simples)} sinónimos en SQLite")
        
    def crear_configuracion_nlp(self, productos, categorias, sinonimos_todos):
        """Crear configuración NLP para BD real"""
        print("📄 Creando configuración NLP...")
        
        config = {
            'database': {
                'type': 'mysql',
                'config': self.mysql_config
            },
            'metadata': {
                'total_productos': len(productos),
                'total_categorias': len(categorias),
                'total_sinonimos': len(sinonimos_todos),
                'fecha_migracion': datetime.now().isoformat(),
                'source': 'mysql_lynxshop'
            },
            'consultas_sql': {
                'buscar_productos': """
                    SELECT p.*, c.nombre as categoria
                    FROM productos p 
                    JOIN categorias c ON p.id_categoria = c.id_categoria
                    WHERE p.cantidad > 0 AND p.nombre LIKE %s
                    ORDER BY p.precio
                """,
                'buscar_categoria': """
                    SELECT p.*, c.nombre as categoria
                    FROM productos p 
                    JOIN categorias c ON p.id_categoria = c.id_categoria
                    WHERE p.cantidad > 0 AND c.nombre LIKE %s
                    ORDER BY p.precio
                """
            }
        }
        
        # Guardar configuración
        config_path = Path("config_nlp_mysql.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Configuración guardada en {config_path}")
        return config
        
    def ejecutar_migracion(self):
        """Ejecutar migración completa"""
        print("🚀 INICIANDO MIGRACIÓN LYNX NLP -> MYSQL REAL")
        print("="*60)
        
        try:
            # 1. Extraer datos de MySQL
            productos = self.obtener_productos_reales()
            categorias = self.obtener_categorias_reales()
            
            # 2. Generar sinónimos
            sin_categorias = self.generar_sinonimos_categorias(categorias)
            sin_productos = self.generar_sinonimos_productos(productos)
            sin_filtros = self.generar_filtros_precio()
            
            todos_sinonimos = sin_categorias + sin_productos + sin_filtros
            
            # 3. Actualizar SQLite
            self.actualizar_sqlite_productos(productos)
            self.actualizar_sqlite_sinonimos(todos_sinonimos)
            
            # 4. Crear configuración
            config = self.crear_configuracion_nlp(productos, categorias, todos_sinonimos)
            
            # 5. Reporte final
            print("\n" + "="*60)
            print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            print(f"📦 Productos migrados: {len(productos)}")
            print(f"📁 Categorías: {len(categorias)}")
            print(f"🔍 Sinónimos generados: {len(todos_sinonimos)}")
            print("="*60)
            
            print("\n✅ El sistema LYNX NLP ahora consume la BD real de LynxShop")
            print("🚀 Reiniciar el servidor FastAPI para aplicar cambios")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR EN MIGRACIÓN: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Función principal"""
    migrador = MigracionNLPDirecta()
    migrador.ejecutar_migracion()

if __name__ == "__main__":
    main()
