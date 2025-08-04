#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema LCLN Simplificado para LYNX - Integración con Frontend
"""

import mysql.connector
from pathlib import Path
import json
import os
import re
from typing import List, Dict, Optional
import difflib
from datetime import datetime, timedelta

class SistemaLCLNSimplificado:
    def __init__(self):
        # Configuración MySQL para Railway
        self.mysql_config = {
            'host': os.getenv('MYSQLHOST', os.getenv('MYSQL_HOST', 'mysql.railway.internal')),
            'port': int(os.getenv('MYSQLPORT', os.getenv('MYSQL_PORT', 3306))),
            'database': os.getenv('MYSQLDATABASE', os.getenv('MYSQL_DATABASE', 'railway')),
            'user': os.getenv('MYSQLUSER', os.getenv('MYSQL_USER', 'root')),
            'password': os.getenv('MYSQLPASSWORD', os.getenv('MYSQL_PASSWORD', '')),
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
            'dulces': ['dulce', 'dulces', 'chocolate', 'caramelo', 'azucar', 'golosina', 'candy', 'goma', 'chicle', 'mazapan', 'oreo', 'nutella', 'panditas', 'dulcigomas', 'paleton'],
            'bebidas': ['bebida', 'bebidas', 'refresco', 'agua', 'jugo', 'soda', 'cola', 'coca', 'pepsi', 'sprite', 'boing', 'fuze'],
            'snacks': ['botana', 'botanas', 'snack', 'snacks', 'papas', 'chips', 'doritos', 'sabritas', 'cheetos', 'chetos', 'chettos', 'fritos', 'karate'],
            'frutas': ['fruta', 'frutas', 'manzana', 'naranja', 'platano', 'uva', 'pera', 'mango', 'fresa', 'durazno', 'guayaba', 'limon', 'mandarina'],
            'lacteos': ['leche', 'queso', 'yogurt', 'crema', 'mantequilla', 'lacteo'],
            'escolar': ['lapiz', 'pluma', 'cuaderno', 'marcador', 'borrador', 'escolar', 'papel', 'boli', 'boligrafo']
        }
        
        # Modificadores de búsqueda
        self.modificadores = {
            'azucar': ['sin azucar', 'zero', 'diet', 'light', 'natural', 'puro', 'pura'],
            'frio': ['frio', 'helado', 'congelado'],
            'caliente': ['caliente', 'tibio'],
            'picante': ['picante', 'picantes', 'fuego', 'dinamita', 'flama', 'chile', 'ardiente', 'hot']
        }

    def _conectar_bd(self):
        """Conectar a la base de datos MySQL"""
        try:
            print(f"[DB] Intentando conectar a MySQL:")
            print(f"[DB] Host: {self.mysql_config['host']}")
            print(f"[DB] Port: {self.mysql_config['port']}")
            print(f"[DB] Database: {self.mysql_config['database']}")
            print(f"[DB] User: {self.mysql_config['user']}")
            
            conexion = mysql.connector.connect(**self.mysql_config)
            print(f"[DB] ✅ Conexión exitosa a MySQL")
            return conexion
        except mysql.connector.Error as e:
            print(f"[DB] ❌ Error conectando a MySQL: {e}")
            print(f"[DB] ❌ Config: {self.mysql_config}")
            return None

    def _cargar_cache_productos(self):
        """Cargar productos desde la base de datos al cache"""
        if (self._cache_timestamp and 
            datetime.now() - self._cache_timestamp < self._cache_expiry):
            print(f"[CACHE] Usando cache existente con {len(self._cache_productos)} productos")
            return
            
        print("[CACHE] Cargando productos desde base de datos...")
        conexion = self._conectar_bd()
        if not conexion:
            print("[CACHE] ❌ No se pudo conectar a la base de datos")
            return
            
        try:
            cursor = conexion.cursor(dictionary=True)
            
            # Cargar productos
            cursor.execute("""
                SELECT p.id_producto as id, p.nombre, p.precio, p.cantidad, p.id_categoria, p.imagen,
                       c.nombre as categoria_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            """)
            productos = cursor.fetchall()
            
            print(f"[CACHE] ✅ Obtenidos {len(productos)} productos de la base de datos")
            
            self._cache_productos = {}
            for producto in productos:
                self._cache_productos[producto['id']] = producto
                
            print(f"[CACHE] Productos en cache: {[p['nombre'] for p in list(self._cache_productos.values())[:5]]}")
                
            # Cargar sinónimos (opcional, puede no existir la tabla)
            try:
                cursor.execute("SELECT * FROM producto_sinonimos")
                sinonimos = cursor.fetchall()
                
                self._cache_sinonimos = {}
                for sinonimo in sinonimos:
                    if sinonimo['producto_id'] not in self._cache_sinonimos:
                        self._cache_sinonimos[sinonimo['producto_id']] = []
                    self._cache_sinonimos[sinonimo['producto_id']].append(sinonimo['sinonimo'])
            except mysql.connector.Error:
                print("Tabla producto_sinonimos no existe, usando solo productos")
                
            self._cache_timestamp = datetime.now()
            
        except mysql.connector.Error as e:
            print(f"Error cargando cache: {e}")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

    def _extraer_filtro_precio_completo(self, consulta: str) -> Optional[Dict]:
        """Extraer filtros de precio avanzados con operadores"""
        consulta = consulta.lower()
        
        # Estrategia 1: Operadores explícitos con números
        # "menor a 15", "menores a 20", "mayor a 10", "mayor 20", "más de 15", etc.
        patrones_operadores = [
            r'menor(?:es)?\s+(?:a|que)\s+(\d+(?:\.\d+)?)',      # menores a, menor a, menor que
            r'menor(?:es)?\s+(\d+(?:\.\d+)?)',                  # menor 20 (sin "a")
            r'mayor(?:es)?\s+(?:a|que)\s+(\d+(?:\.\d+)?)',      # mayores a, mayor a, mayor que  
            r'mayor(?:es)?\s+(\d+(?:\.\d+)?)',                  # mayor 20 (sin "a")
            r'menos\s+(?:de|que)\s+(\d+(?:\.\d+)?)',
            r'(?:más|mas)\s+de\s+(\d+(?:\.\d+)?)',
            r'(?:máximo|max|tope)\s+(\d+(?:\.\d+)?)',
            r'hasta\s+(\d+(?:\.\d+)?)',
            r'no\s+(?:más|mas)\s+de\s+(\d+(?:\.\d+)?)'
        ]
        
        for i, patron in enumerate(patrones_operadores):
            match = re.search(patron, consulta, re.IGNORECASE)
            if match:
                precio = float(match.group(1))
                # Identificar si es "mayor a" vs "menor a" basado en el índice del patrón
                if i in [2, 3]:  # mayores? patrones (con y sin "a")
                    print(f"Filtro precio detectado (mayor a): >= ${precio}")
                    return {'precio': precio, 'operador': '>=', 'tipo': 'mayor_que'}
                elif i == 5:  # más de patrón
                    print(f"Filtro precio detectado (más de): >= ${precio}")
                    return {'precio': precio, 'operador': '>=', 'tipo': 'mayor_que'}
                else:  # menores?, menos, máximo, hasta, no más de
                    print(f"Filtro precio detectado (operador): <= ${precio}")
                    return {'precio': precio, 'operador': '<=', 'tipo': 'menor_que'}
        
        return None

    def _cumple_filtro_precio(self, precio_producto: float, filtro_precio: Dict) -> bool:
        """Verificar si un producto cumple con el filtro de precio"""
        precio_filtro = filtro_precio['precio']
        operador = filtro_precio['operador']
        
        if operador == '<=':
            return precio_producto <= precio_filtro
        elif operador == '>=':
            return precio_producto >= precio_filtro
        elif operador == '<':
            return precio_producto < precio_filtro
        elif operador == '>':
            return precio_producto > precio_filtro
        elif operador == '==':
            return abs(precio_producto - precio_filtro) < 0.01
        
        return True

    def analizar_consulta(self, consulta: str) -> Dict:
        """Análisis principal de la consulta con filtros avanzados"""
        consulta = consulta.lower().strip()
        
        # Detectar filtros de precio PRIMERO (tanto para compatibilidad como completo)
        precio_max = self._extraer_filtro_precio(consulta)  # Para compatibilidad
        filtro_precio_completo = self._extraer_filtro_precio_completo(consulta)  # Para filtros avanzados
        
        resultado = {
            'categoria_detectada': None,
            'modificadores_detectados': [],
            'productos_sugeridos': [],
            'expansion_consulta': None,
            'precio_max': precio_max,
            'filtro_precio': filtro_precio_completo
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
                
        # 3. Lógica específica para bebidas sin azúcar
        if (resultado['categoria_detectada'] == 'bebidas' and 
            'azucar' in resultado['modificadores_detectados']):
            
            resultado['productos_sugeridos'] = [
                'coca cola zero', 'pepsi light', 'sprite zero', 'agua pura',
                'agua mineral', 'fuze tea',
                '# Bebidas sin azúcar'
            ]
            print("Detectando bebidas sin azúcar")
            
        # 4. Lógica específica para snacks picantes
        elif (resultado['categoria_detectada'] == 'snacks' and 
              'picante' in resultado['modificadores_detectados']):
            
            resultado['productos_sugeridos'] = [
                'cheetos flamin hot', 'doritos dinamita', 'fritos con chile',
                'crujitos fuegos', '# Snacks picantes'
            ]
            print("Detectando snacks picantes")
            
        # 5. Lógica de hidratación
        elif any(palabra in consulta for palabra in ['agua', 'hidratante', 'refrescante']):
            resultado['categoria_detectada'] = 'bebidas'
            resultado['modificadores_detectados'].append('hidratante')
            
        return resultado

    def _extraer_filtro_precio(self, consulta: str) -> Optional[float]:
        """Extraer filtro de precio básico (compatibilidad)"""
        filtro_completo = self._extraer_filtro_precio_completo(consulta)
        if filtro_completo and filtro_completo['operador'] == '<=':
            return filtro_completo['precio']
        return None

    def _coincidencia_inteligente(self, consulta: str, nombre_producto: str) -> bool:
        """Análisis léxico inteligente para coincidencias parciales"""
        # Mapeo de términos comunes que tu sistema debe reconocer
        mapeo_sinonimos = {
            'chetos': ['cheetos', 'cheetosmix'],
            'chettos': ['cheetos', 'cheetosmix'],  # Agregado
            'coquita': ['coca', 'coca-cola', 'coca cola'],
            'dulce': ['dulci', 'mazapan', 'oreo', 'nutella', 'panditas', 'dulcigomas'],
            'dulces': ['dulci', 'mazapan', 'oreo', 'nutella', 'panditas', 'dulcigomas', 'paleton'],
            'agua': ['aguaciel'],
            'mango': ['boingmango'],
            'limon': ['fuzetealimon', 'fritoslimon'],
            'durazno': ['durazno'],
            'boli': ['boligrafo', 'boli', 'fashioboli'],
            'cuaderno': ['cuaderno', 'cuadernorayado'],
            'marcador': ['marcador', 'marcatextos'],
            'botana': ['doritos', 'sabritas', 'cheetos', 'fritos', 'karate'],
            'botanas': ['doritos', 'sabritas', 'cheetos', 'fritos', 'karate'],
            'snack': ['doritos', 'sabritas', 'cheetos', 'fritos', 'karate'],
            'snacks': ['doritos', 'sabritas', 'cheetos', 'fritos', 'karate'],
            'sin azucar': ['sin azucar', 'zero', 'diet', 'light'],
            'zero': ['sin azucar', 'zero', 'diet'],
            'light': ['sin azucar', 'zero', 'light'],
            'niños': ['panditas', 'dulcigomas', 'paleton', 'oreo']
        }
        
        # Verificar mapeo directo
        if consulta in mapeo_sinonimos:
            for sinonimo in mapeo_sinonimos[consulta]:
                if sinonimo.lower() in nombre_producto.lower():
                    print(f"[SINÓNIMO] ✅ '{consulta}' -> '{sinonimo}' encontrado en '{nombre_producto}'")
                    return True
        
        # Verificar cada palabra de la consulta individualmente
        palabras_consulta = consulta.split()
        for palabra in palabras_consulta:
            if palabra in mapeo_sinonimos:
                for sinonimo in mapeo_sinonimos[palabra]:
                    if sinonimo.lower() in nombre_producto.lower():
                        print(f"[SINÓNIMO] ✅ Palabra '{palabra}' -> '{sinonimo}' encontrado en '{nombre_producto}'")
                        return True
        
        # Análisis de similitud fonética/ortográfica
        if len(consulta) >= 4:
            # Coincidencias por inicio de palabra
            if nombre_producto.startswith(consulta[:4]):
                return True
            
            # Coincidencias por similitud de caracteres (tolerancia de 1-2 caracteres)
            if self._similitud_caracteres(consulta, nombre_producto) >= 0.7:
                return True
                
        return False
    
    def _similitud_caracteres(self, str1: str, str2: str) -> float:
        """Calcula similitud entre dos strings"""
        if not str1 or not str2:
            return 0.0
            
        # Usar difflib para calcular similitud
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    def buscar_productos(self, consulta: str, limite: int = 10) -> List[Dict]:
        """Búsqueda de productos usando análisis semántico"""
        print(f"[BÚSQUEDA] Iniciando búsqueda para: '{consulta}' (límite: {limite})")
        self._cargar_cache_productos()
        
        print(f"[BÚSQUEDA] Cache tiene {len(self._cache_productos)} productos")
        
        # Análisis semántico
        analisis = self.analizar_consulta(consulta)
        print(f"[ANÁLISIS] Resultado: {analisis}")
        
        productos_encontrados = []
        consulta_lower = consulta.lower()
        
        # Buscar en productos y sinónimos
        for producto_id, producto in self._cache_productos.items():
            score = 0
            nombre_producto = producto['nombre'].lower()
            
            # 1. Coincidencia exacta en nombre
            if consulta_lower in nombre_producto:
                score += 100
                print(f"[MATCH] ✅ Coincidencia exacta en '{producto['nombre']}' - Score: {score}")
            
            # 2. Coincidencia parcial inteligente (NUEVA FUNCIONALIDAD)
            elif self._coincidencia_inteligente(consulta_lower, nombre_producto):
                score += 80
                print(f"[MATCH] 🧠 Coincidencia inteligente en '{producto['nombre']}' - Score: {score}")
                
            # 3. Coincidencia en sinónimos
            if producto_id in self._cache_sinonimos:
                for sinonimo in self._cache_sinonimos[producto_id]:
                    if consulta_lower in sinonimo.lower():
                        score += 75
                        print(f"[MATCH] ✅ Coincidencia en sinónimo '{sinonimo}' para '{producto['nombre']}' - Score: {score}")
                        
            # 4. Coincidencia por categoría detectada
            if analisis['categoria_detectada']:
                categoria_producto = producto.get('categoria_nombre', '').lower()
                if analisis['categoria_detectada'] in categoria_producto:
                    score += 30
                    print(f"[MATCH] ✅ Coincidencia de categoría '{analisis['categoria_detectada']}' en '{producto['nombre']}' - Score: {score}")
                    
            if score > 0:
                producto_resultado = producto.copy()
                producto_resultado['score'] = score
                producto_resultado['analisis'] = analisis
                productos_encontrados.append(producto_resultado)
                
        print(f"[BÚSQUEDA] Encontrados {len(productos_encontrados)} productos con score > 0")
        
        # Ordenar por score y limitar resultados
        productos_encontrados.sort(key=lambda x: x['score'], reverse=True)
        resultado_final = productos_encontrados[:limite]
        
        print(f"[BÚSQUEDA] Devolviendo {len(resultado_final)} productos finales")
        return resultado_final

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
