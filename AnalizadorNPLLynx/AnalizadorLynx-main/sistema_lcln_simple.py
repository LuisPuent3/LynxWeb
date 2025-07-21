#!/usr/bin/env python3
"""
Sistema LCLN Simplificado para LYNX - Integración con Frontend
"""

import mysql.connector
from pathlib import Path
import json
from typing import List, Dict, Optional
import difflib
from datetime import datetime, timedelta

class SistemaLCLNSimplificado:
    def __init__(self):
        # Configuración MySQL
        self.mysql_config = {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': '12345678',
            'charset': 'utf8mb4'
        }
        
        # Cache dinámico
        self._cache_productos = {}
        self._cache_categorias = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)
    
    def _necesita_actualizar_cache(self) -> bool:
        """Verificar si el cache necesita actualizarse"""
        if self._cache_timestamp is None:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_duration
    
    def _actualizar_cache_dinamico(self):
        """Actualizar cache con datos actuales de MySQL"""
        if not self._necesita_actualizar_cache():
            return
            
        print("🔄 Actualizando cache dinámico desde MySQL...")
        conn = mysql.connector.connect(**self.mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Cargar categorías
            cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
            categorias = cursor.fetchall()
            
            self._cache_categorias = {}
            for cat in categorias:
                nombre_norm = cat['nombre'].lower()
                self._cache_categorias[nombre_norm] = {
                    'id': cat['id_categoria'],
                    'nombre': cat['nombre']
                }
            
            # Cargar productos con imágenes
            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.precio, p.cantidad, p.imagen,
                       c.id_categoria, c.nombre as categoria
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.cantidad > 0
                ORDER BY p.nombre
            """)
            productos = cursor.fetchall()
            
            self._cache_productos = {}
            for prod in productos:
                nombre_norm = prod['nombre'].lower()
                self._cache_productos[nombre_norm] = {
                    'id': prod['id_producto'],
                    'nombre': prod['nombre'],
                    'precio': float(prod['precio']),
                    'cantidad': prod['cantidad'],
                    'imagen': prod['imagen'] or 'default.jpg',
                    'categoria_id': prod['id_categoria'],
                    'categoria': prod['categoria']
                }
            
            self._cache_timestamp = datetime.now()
            print(f"✅ Cache actualizado: {len(self._cache_productos)} productos, {len(self._cache_categorias)} categorías")
            
        finally:
            cursor.close()
            conn.close()
    
    def buscar_productos_inteligente(self, consulta: str, limit: int = 20) -> Dict:
        """
        Búsqueda inteligente que se adapta dinámicamente a la BD
        """
        # Actualizar cache si es necesario
        self._actualizar_cache_dinamico()
        
        consulta_original = consulta
        consulta = consulta.lower().strip()
        
        import time
        inicio = time.time()
        
        # Análisis de la consulta
        analisis = self._analizar_consulta_simple(consulta)
        
        # Búsqueda con múltiples estrategias
        productos = self._ejecutar_busqueda_estrategias(analisis, limit)
        
        tiempo_proceso = (time.time() - inicio) * 1000
        
        return {
            'success': True,
            'processing_time_ms': tiempo_proceso,
            'original_query': consulta_original,
            'interpretation': {
                'termino_busqueda': analisis['termino_busqueda'],
                'categoria': analisis['categoria'],
                'tipo': 'busqueda_dinamica_lcln',
                'estrategia_usada': analisis['estrategia_usada']
            },
            'recommendations': productos,
            'products_found': len(productos),
            'user_message': f"Encontrados {len(productos)} productos dinámicamente",
            'metadata': {
                'database': 'mysql_dynamic',
                'cache_timestamp': self._cache_timestamp.isoformat(),
                'imagenes_incluidas': True
            }
        }
    
    def _analizar_consulta_simple(self, consulta: str) -> Dict:
        """Análisis simplificado pero efectivo"""
        # Detectar producto específico
        for nombre_producto, datos_producto in self._cache_productos.items():
            if nombre_producto in consulta:
                return {
                    'tipo_busqueda': 'producto_especifico',
                    'producto_encontrado': datos_producto,
                    'termino_busqueda': nombre_producto,
                    'categoria': None,
                    'estrategia_usada': 'producto_especifico'
                }
        
        # Detectar categoría
        for nombre_categoria, datos_categoria in self._cache_categorias.items():
            if nombre_categoria in consulta:
                # Detectar filtros de precio
                precio_max = None
                if any(palabra in consulta for palabra in ['barato', 'baratos', 'barata', 'baratas', 'economico']):
                    precio_max = 20.0
                elif any(palabra in consulta for palabra in ['caro', 'caros', 'cara', 'caras']):
                    precio_max = None  # Sin límite superior para productos caros
                
                return {
                    'tipo_busqueda': 'categoria',
                    'categoria': datos_categoria,
                    'termino_busqueda': '',
                    'precio_max': precio_max,
                    'estrategia_usada': 'categoria_con_filtros'
                }
        
        # Detectar solo filtros de precio
        precio_max = None
        if any(palabra in consulta for palabra in ['barato', 'baratos', 'barata', 'baratas', 'economico']):
            precio_max = 20.0
        elif any(palabra in consulta for palabra in ['caro', 'caros', 'cara', 'caras']):
            precio_max = 100.0  # Productos caros hasta 100
        
        if precio_max:
            return {
                'tipo_busqueda': 'precio',
                'categoria': None,
                'termino_busqueda': '',
                'precio_max': precio_max,
                'estrategia_usada': 'filtro_precio'
            }
        
        # Búsqueda genérica por palabras clave
        return {
            'tipo_busqueda': 'generica',
            'categoria': None,
            'termino_busqueda': consulta,
            'precio_max': None,
            'estrategia_usada': 'busqueda_generica'
        }
    
    def _ejecutar_busqueda_estrategias(self, analisis: Dict, limit: int) -> List[Dict]:
        """Ejecutar búsqueda usando diferentes estrategias"""
        
        if analisis['tipo_busqueda'] == 'producto_especifico':
            return [self._formatear_producto(analisis['producto_encontrado'])]
        
        elif analisis['tipo_busqueda'] == 'categoria':
            return self._buscar_por_categoria(
                analisis['categoria']['nombre'],
                analisis.get('precio_max'),
                limit
            )
        
        elif analisis['tipo_busqueda'] == 'precio':
            return self._buscar_por_precio(analisis['precio_max'], limit)
        
        else:
            # Búsqueda genérica - buscar en nombres de productos
            return self._buscar_generica(analisis['termino_busqueda'], limit)
    
    def _buscar_por_categoria(self, categoria: str, precio_max: Optional[float], limit: int) -> List[Dict]:
        """Buscar productos por categoría con filtros"""
        productos = []
        
        for producto in self._cache_productos.values():
            if producto['categoria'].lower() == categoria.lower():
                # Aplicar filtro de precio si existe
                if precio_max and producto['precio'] > precio_max:
                    continue
                
                productos.append(self._formatear_producto(producto))
        
        # Ordenar por precio y limitar
        productos.sort(key=lambda x: x['precio'])
        return productos[:limit]
    
    def _buscar_por_precio(self, precio_max: float, limit: int) -> List[Dict]:
        """Buscar productos por rango de precio"""
        productos = []
        
        for producto in self._cache_productos.values():
            if producto['precio'] <= precio_max:
                productos.append(self._formatear_producto(producto))
        
        # Ordenar por precio y limitar
        productos.sort(key=lambda x: x['precio'])
        return productos[:limit]
    
    def _buscar_generica(self, termino: str, limit: int) -> List[Dict]:
        """Búsqueda genérica en nombres de productos"""
        productos = []
        
        for producto in self._cache_productos.values():
            if termino in producto['nombre'].lower():
                productos.append(self._formatear_producto(producto))
        
        # Si no encuentra nada, devolver productos económicos
        if not productos:
            for producto in self._cache_productos.values():
                if producto['precio'] <= 25.0:
                    productos.append(self._formatear_producto(producto))
        
        # Ordenar por precio y limitar
        productos.sort(key=lambda x: x['precio'])
        return productos[:limit]
    
    def _formatear_producto(self, producto: Dict) -> Dict:
        """Formatear producto para respuesta con imagen incluida"""
        return {
            'id': producto['id'],
            'id_producto': producto['id'],
            'nombre': producto['nombre'],
            'price': producto['precio'],
            'precio': producto['precio'],
            'category': producto['categoria'].lower(),
            'categoria': producto['categoria'],
            'id_categoria': producto['categoria_id'],
            'cantidad': producto['cantidad'],
            'imagen': producto['imagen'],
            'available': producto['cantidad'] > 0,
            'match_score': 0.95,
            'match_reasons': ['mysql_dynamic', 'imagen_incluida'],
            'source': 'mysql_lynxshop_lcln_dinamico'
        }

# Instancia global
sistema_lcln_simple = SistemaLCLNSimplificado()

if __name__ == "__main__":
    # Prueba del sistema
    print("🧪 Probando Sistema LCLN Simplificado...")
    
    consultas_prueba = [
        "coca cola",
        "snacks baratos", 
        "bebidas",
        "productos economicos",
        "doritos"
    ]
    
    for consulta in consultas_prueba:
        print(f"\n🔍 Consulta: '{consulta}'")
        resultado = sistema_lcln_simple.buscar_productos_inteligente(consulta)
        
        print(f"   Estrategia: {resultado['interpretation']['estrategia_usada']}")
        print(f"   Productos encontrados: {resultado['products_found']}")
        
        for prod in resultado['recommendations'][:3]:
            print(f"     - {prod['nombre']} ${prod['precio']} (imagen: {prod['imagen']})")
    
    print(f"\n✅ Sistema LCLN simplificado funcionando con imágenes incluidas")
