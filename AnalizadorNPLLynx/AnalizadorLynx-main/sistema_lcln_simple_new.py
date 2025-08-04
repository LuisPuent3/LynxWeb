#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema LCLN Simplificado para LYNX - Integración con Frontend
"""

import mysql.connector
from pathlib import Path
import json
import os
from typing import List, Dict, Optional
import difflib
from datetime import datetime, timedelta

class SistemaLCLNSimplificado:
    def __init__(self):
        # Configuración MySQL para Railway
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'mysql.railway.internal'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'database': os.getenv('MYSQL_DATABASE', 'railway'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'charset': 'utf8mb4',
            'ssl_disabled': True,
            'autocommit': True
        }
        
        # Cache dinámico
        self._cache_productos = {}
        self._cache_categorias = {}
        self._cache_sinonimos = {}
        self._cache_timestamp = None
        self._cache_expiry = timedelta(minutes=5)
        
        # Patrones semánticos básicos
        self.categorias_semanticas = {
            'dulces': ['dulce', 'chocolate', 'caramelo', 'azucar', 'golosina', 'candy', 'goma', 'chicle'],
            'bebidas': ['bebida', 'refresco', 'agua', 'jugo', 'soda', 'cola', 'coca', 'pepsi', 'sprite'],
            'snacks': ['botana', 'snack', 'papas', 'chips', 'doritos', 'sabritas', 'cheetos'],
            'frutas': ['fruta', 'manzana', 'naranja', 'platano', 'uva', 'pera', 'mango', 'fresa'],
            'lacteos': ['leche', 'queso', 'yogurt', 'crema', 'mantequilla', 'lacteo'],
            'escolar': ['lapiz', 'pluma', 'cuaderno', 'marcador', 'borrador', 'escolar', 'papel']
        }
        
        # Modificadores de búsqueda
        self.modificadores = {
            'azucar': ['sin azucar', 'zero', 'diet', 'light', 'natural', 'puro', 'pura'],
            'frio': ['frio', 'helado', 'congelado'],
            'caliente': ['caliente', 'tibio']
        }

    def _conectar_bd(self):
        """Conectar a la base de datos MySQL"""
        try:
            conexion = mysql.connector.connect(**self.mysql_config)
            return conexion
        except mysql.connector.Error as e:
            print(f"Error conectando a MySQL: {e}")
            return None

    def _cargar_cache_productos(self):
        """Cargar productos desde la base de datos al cache"""
        if (self._cache_timestamp and 
            datetime.now() - self._cache_timestamp < self._cache_expiry):
            return
            
        conexion = self._conectar_bd()
        if not conexion:
            return
            
        try:
            cursor = conexion.cursor(dictionary=True)
            
            # Cargar productos
            cursor.execute("""
                SELECT p.*, c.nombre as categoria_nombre 
                FROM productos p 
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.activo = 1
            """)
            productos = cursor.fetchall()
            
            self._cache_productos = {}
            for producto in productos:
                self._cache_productos[producto['id']] = producto
                
            # Cargar sinónimos
            cursor.execute("SELECT * FROM producto_sinonimos")
            sinonimos = cursor.fetchall()
            
            self._cache_sinonimos = {}
            for sinonimo in sinonimos:
                if sinonimo['producto_id'] not in self._cache_sinonimos:
                    self._cache_sinonimos[sinonimo['producto_id']] = []
                self._cache_sinonimos[sinonimo['producto_id']].append(sinonimo['sinonimo'])
                
            self._cache_timestamp = datetime.now()
            
        except mysql.connector.Error as e:
            print(f"Error cargando cache: {e}")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

    def analizar_consulta(self, consulta: str) -> Dict:
        """Análisis principal de la consulta"""
        consulta = consulta.lower().strip()
        
        resultado = {
            'categoria_detectada': None,
            'modificadores_detectados': [],
            'productos_sugeridos': [],
            'expansion_consulta': None
        }
        
        # 1. Detectar categoría principal
        for categoria, palabras_clave in self.categorias_semanticas.items():
            if any(palabra in consulta for palabra in palabras_clave):
                resultado['categoria_detectada'] = categoria
                break
                
        # 2. Detectar modificadores
        for modificador, variantes in self.modificadores.items():
            if any(variante in consulta for variante in variantes):
                resultado['modificadores_detectados'].append(modificador)
                
        # 3. Lógica específica para bebidas que puede incluir aguas
        if (resultado['categoria_detectada'] == 'bebidas' and 
            not any(mod in resultado['modificadores_detectados'] for mod in ['azucar'])):
            
            resultado['productos_sugeridos'] = [
                'coca cola', 'pepsi', 'sprite', 'agua', 'jugo de naranja', 'boing',
                'agua mineral', 'fuze tea', 
                '# Todas las bebidas con azúcar'
            ]
            resultado['busqueda_incluye_aguas'] = True
            
            print("Detectando bebidas incluyendo aguas")
            
        # 3B. No azúcar = refrescos regulares
        elif (resultado['categoria_detectada'] == 'bebidas' and 
              'azucar' in resultado['modificadores_detectados']):
            
            resultado['productos_sugeridos'] = [
                'coca cola zero', 'pepsi light', 'sprite zero', 'agua pura',
                'agua mineral', 'fuze tea',
                '# Bebidas sin azúcar'
            ]
            resultado['busqueda_excluye_aguas'] = True
            
            print("Detectando refrescos sin azúcar, excluyendo productos zero")
            
        # 4. Lógica de hidratación
        elif any(palabra in consulta for palabra in ['agua', 'hidratante', 'refrescante']):
            resultado['categoria_detectada'] = 'bebidas'
            resultado['modificadores_detectados'].append('hidratante')
            
        return resultado

    def buscar_productos(self, consulta: str, limite: int = 10) -> List[Dict]:
        """Búsqueda de productos usando análisis semántico"""
        self._cargar_cache_productos()
        
        # Análisis semántico
        analisis = self.analizar_consulta(consulta)
        
        productos_encontrados = []
        consulta_lower = consulta.lower()
        
        # Buscar en productos y sinónimos
        for producto_id, producto in self._cache_productos.items():
            score = 0
            
            # Coincidencia exacta en nombre
            if consulta_lower in producto['nombre'].lower():
                score += 100
                
            # Coincidencia en descripción
            if producto['descripcion'] and consulta_lower in producto['descripcion'].lower():
                score += 50
                
            # Coincidencia en sinónimos
            if producto_id in self._cache_sinonimos:
                for sinonimo in self._cache_sinonimos[producto_id]:
                    if consulta_lower in sinonimo.lower():
                        score += 75
                        
            # Coincidencia por categoría detectada
            if analisis['categoria_detectada']:
                categoria_producto = producto.get('categoria_nombre', '').lower()
                if analisis['categoria_detectada'] in categoria_producto:
                    score += 30
                    
            # Aplicar filtros de modificadores
            if 'azucar' in analisis['modificadores_detectados']:
                nombre_lower = producto['nombre'].lower()
                if any(word in nombre_lower for word in ['zero', 'light', 'diet', 'sin azucar']):
                    score += 20
                elif any(word in nombre_lower for word in ['coca', 'pepsi', 'sprite']) and 'zero' not in nombre_lower:
                    score -= 30  # Penalizar refrescos con azúcar
                    
            if score > 0:
                producto_resultado = producto.copy()
                producto_resultado['score'] = score
                producto_resultado['analisis'] = analisis
                productos_encontrados.append(producto_resultado)
                
        # Ordenar por score y limitar resultados
        productos_encontrados.sort(key=lambda x: x['score'], reverse=True)
        return productos_encontrados[:limite]

    def obtener_sugerencias(self, consulta_parcial: str) -> List[str]:
        """Obtener sugerencias de autocompletado"""
        self._cargar_cache_productos()
        
        sugerencias = set()
        consulta_lower = consulta_parcial.lower()
        
        # Sugerencias desde nombres de productos
        for producto in self._cache_productos.values():
            nombre = producto['nombre'].lower()
            if consulta_lower in nombre:
                sugerencias.add(producto['nombre'])
                
        # Sugerencias desde sinónimos
        for sinonimos_lista in self._cache_sinonimos.values():
            for sinonimo in sinonimos_lista:
                if consulta_lower in sinonimo.lower():
                    sugerencias.add(sinonimo)
                    
        return sorted(list(sugerencias))[:10]

    def registrar_busqueda(self, consulta: str, productos_encontrados: int):
        """Registrar métricas de búsqueda"""
        conexion = self._conectar_bd()
        if not conexion:
            return
            
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO busqueda_metricas (consulta, productos_encontrados, timestamp)
                VALUES (%s, %s, %s)
            """, (consulta, productos_encontrados, datetime.now()))
            conexion.commit()
        except mysql.connector.Error as e:
            print(f"Error registrando búsqueda: {e}")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

# Función de utilidad para uso directo
def buscar_productos_lcln(consulta: str, limite: int = 10) -> Dict:
    """Función de conveniencia para búsqueda directa"""
    sistema = SistemaLCLNSimplificado()
    productos = sistema.buscar_productos(consulta, limite)
    
    # Registrar la búsqueda
    sistema.registrar_busqueda(consulta, len(productos))
    
    return {
        'consulta': consulta,
        'productos': productos,
        'total_encontrados': len(productos),
        'timestamp': datetime.now().isoformat()
    }

def obtener_sugerencias_lcln(consulta_parcial: str) -> List[str]:
    """Función de conveniencia para sugerencias"""
    sistema = SistemaLCLNSimplificado()
    return sistema.obtener_sugerencias(consulta_parcial)

# Test básico
if __name__ == "__main__":
    sistema = SistemaLCLNSimplificado()
    
    # Test de conexión
    conexion = sistema._conectar_bd()
    if conexion:
        print("✅ Conexión a MySQL exitosa")
        conexion.close()
    else:
        print("❌ Error de conexión a MySQL")
        
    # Test de búsqueda básica
    try:
        resultados = sistema.buscar_productos("coca")
        print(f"✅ Búsqueda exitosa: {len(resultados)} productos encontrados")
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
