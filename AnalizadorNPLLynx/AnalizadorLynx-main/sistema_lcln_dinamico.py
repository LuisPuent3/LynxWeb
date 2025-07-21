#!/usr/bin/env python3
"""
Sistema LCLN (Lenguaje de Consulta en Lenguaje Natural) - LYNX
Motor dinámico que se adapta automáticamente a cambios en la BD
"""

import mysql.connector
import sqlite3
from pathlib import Path
import json
import re
from typing import List, Dict, Optional, Tuple
import difflib
from datetime import datetime, timedelta

class SistemaLCLN:
    def __init__(self):
        # Configuración MySQL (productos reales)
        self.mysql_config = {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root', 
            'password': '12345678',
            'charset': 'utf8mb4'
        }
        
        # Cache dinámico de la BD
        self._cache_productos = {}
        self._cache_categorias = {}
        self._cache_atributos = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)  # Cache por 5 minutos
        
        # Ruta sinónimos NLP
        base_dir = Path(__file__).parent
        self.sqlite_sinonimos = base_dir / "api" / "sinonimos_lynx.db"
        if base_dir.name == "api":
            self.sqlite_sinonimos = base_dir / "sinonimos_lynx.db"
    
    def _necesita_actualizar_cache(self) -> bool:
        """Verificar si el cache necesita actualizarse"""
        if self._cache_timestamp is None:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_duration
    
    def _actualizar_cache_dinamico(self):
        """Actualizar cache con datos actuales de la BD MySQL"""
        if not self._necesita_actualizar_cache():
            return
            
        print("🔄 Actualizando cache dinámico desde MySQL...")
        conn = mysql.connector.connect(**self.mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        try:
            # 1. Cargar todas las categorías dinámicamente
            cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
            categorias = cursor.fetchall()
            
            self._cache_categorias = {}
            for cat in categorias:
                nombre_norm = cat['nombre'].lower()
                self._cache_categorias[nombre_norm] = {
                    'id': cat['id_categoria'],
                    'nombre': cat['nombre'],
                    'sinonimos': [nombre_norm, cat['nombre']]
                }
              # 2. Cargar todos los productos dinámicamente  
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
                    'descripcion': '',  # No hay descripción en la BD actual
                    'categoria_id': prod['id_categoria'],
                    'categoria': prod['categoria']
                }
            
            # 3. Extraer atributos dinámicamente de nombres y descripciones
            self._cache_atributos = self._extraer_atributos_dinamicos()
            
            self._cache_timestamp = datetime.now()
            print(f"✅ Cache actualizado: {len(self._cache_productos)} productos, {len(self._cache_categorias)} categorías")
            
        finally:
            cursor.close()
            conn.close()
    
    def _extraer_atributos_dinamicos(self) -> Dict:
        """Extraer atributos dinámicamente de productos existentes"""
        atributos = {
            'sabores': set(),
            'tamaños': set(), 
            'marcas': set(),
            'caracteristicas': set()
        }
          # Palabras comunes de sabores/características
        sabores_comunes = ['picante', 'dulce', 'salado', 'agrio', 'chocolate', 'vainilla', 'fresa', 'limón', 'naranja']
        tamaños_comunes = ['pequeño', 'mediano', 'grande', 'familiar', 'jumbo', 'mini', 'xl', 'xxl']
        caracteristicas_comunes = ['sin azúcar', 'light', 'zero', 'diet', 'orgánico', 'natural', 'artificial']
        
        for producto in self._cache_productos.values():
            texto_completo = producto['nombre'].lower()  # Solo usar nombre ya que no hay descripción
            
            # Extraer sabores
            for sabor in sabores_comunes:
                if sabor in texto_completo:
                    atributos['sabores'].add(sabor)
            
            # Extraer tamaños  
            for tamaño in tamaños_comunes:
                if tamaño in texto_completo:
                    atributos['tamaños'].add(tamaño)
                    
            # Extraer características
            for carac in caracteristicas_comunes:
                if carac in texto_completo:
                    atributos['caracteristicas'].add(carac)
        
        # Convertir sets a listas para JSON serializable
        return {k: list(v) for k, v in atributos.items()}
    
    def analizar_consulta_lcln(self, consulta: str) -> Dict:
        """
        Análisis LCLN completo según documentación técnica
        1. Corrección ortográfica
        2. Análisis léxico multi-AFD
        3. Análisis contextual
        4. Interpretación semántica
        """
        # Asegurar cache actualizado
        self._actualizar_cache_dinamico()
        
        consulta_original = consulta
        consulta = consulta.lower().strip()
        
        resultado_analisis = {
            'consulta_original': consulta_original,
            'fase_1_correccion': self._fase_correccion_ortografica(consulta),
            'fase_2_tokenizacion': None,
            'fase_3_analisis_contextual': None,
            'fase_4_interpretacion_semantica': None,
            'fase_5_motor_recomendaciones': None
        }
        
        # Fase 1: Corrección ortográfica
        consulta_corregida = resultado_analisis['fase_1_correccion']['texto_corregido']
        
        # Fase 2: Tokenización multi-AFD
        resultado_analisis['fase_2_tokenizacion'] = self._fase_tokenizacion_multi_afd(consulta_corregida)
        
        # Fase 3: Análisis contextual  
        resultado_analisis['fase_3_analisis_contextual'] = self._fase_analisis_contextual(
            resultado_analisis['fase_2_tokenizacion']
        )
        
        # Fase 4: Interpretación semántica
        resultado_analisis['fase_4_interpretacion_semantica'] = self._fase_interpretacion_semantica(
            resultado_analisis['fase_3_analisis_contextual']
        )
        
        # Fase 5: Motor de recomendaciones
        resultado_analisis['fase_5_motor_recomendaciones'] = self._fase_motor_recomendaciones(
            resultado_analisis['fase_4_interpretacion_semantica']
        )
        
        return resultado_analisis
    
    def _fase_correccion_ortografica(self, consulta: str) -> Dict:
        """Fase 1: Corrección ortográfica con distancia de Levenshtein"""
        palabras = consulta.split()
        correcciones = []
        texto_corregido_palabras = []
        
        for palabra in palabras:
            mejor_correccion = self._encontrar_mejor_correccion(palabra)
            if mejor_correccion['aplicada']:
                correcciones.append(mejor_correccion)
                texto_corregido_palabras.append(mejor_correccion['palabra_corregida'])
            else:
                texto_corregido_palabras.append(palabra)
        
        return {
            'correcciones_aplicadas': len(correcciones) > 0,
            'correcciones': correcciones,
            'texto_corregido': ' '.join(texto_corregido_palabras)
        }
    
    def _encontrar_mejor_correccion(self, palabra: str) -> Dict:
        """Encontrar la mejor corrección para una palabra"""
        # Buscar en productos
        for nombre_producto in self._cache_productos.keys():
            if self._distancia_levenshtein(palabra, nombre_producto) <= 2:
                similitud = difflib.SequenceMatcher(None, palabra, nombre_producto).ratio()
                if similitud >= 0.7:
                    return {
                        'aplicada': True,
                        'palabra_original': palabra,
                        'palabra_corregida': nombre_producto,
                        'confianza': similitud,
                        'fuente': 'productos'
                    }
        
        # Buscar en categorías
        for nombre_categoria in self._cache_categorias.keys():
            if self._distancia_levenshtein(palabra, nombre_categoria) <= 2:
                similitud = difflib.SequenceMatcher(None, palabra, nombre_categoria).ratio()
                if similitud >= 0.7:
                    return {
                        'aplicada': True,
                        'palabra_original': palabra,
                        'palabra_corregida': nombre_categoria,
                        'confianza': similitud,
                        'fuente': 'categorias'
                    }
        
        return {
            'aplicada': False,
            'palabra_original': palabra,
            'palabra_corregida': palabra,
            'confianza': 1.0,
            'fuente': None
        }
    
    def _distancia_levenshtein(self, s1: str, s2: str) -> int:
        """Calcular distancia de Levenshtein"""
        if len(s1) < len(s2):
            return self._distancia_levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _fase_tokenizacion_multi_afd(self, consulta: str) -> Dict:
        """Fase 2: Tokenización usando múltiples AFDs"""
        tokens = []
        palabras = consulta.split()
        
        i = 0
        while i < len(palabras):
            # AFD Multipalabra (mayor prioridad)
            token_multipalabra = self._afd_multipalabra(palabras, i)
            if token_multipalabra['encontrado']:
                tokens.append(token_multipalabra)
                i += token_multipalabra['palabras_consumidas']
                continue
            
            # AFD Operadores
            token_operador = self._afd_operadores(palabras, i)
            if token_operador['encontrado']:
                tokens.append(token_operador)
                i += token_operador['palabras_consumidas']
                continue
            
            # AFD Números
            token_numero = self._afd_numeros(palabras[i])
            if token_numero['encontrado']:
                tokens.append(token_numero)
                i += 1
                continue
            
            # AFD Unidades
            token_unidad = self._afd_unidades(palabras[i])
            if token_unidad['encontrado']:
                tokens.append(token_unidad)
                i += 1
                continue
            
            # AFD Palabras (menor prioridad)
            token_palabra = self._afd_palabras(palabras[i])
            tokens.append(token_palabra)
            i += 1
        
        return {
            'tokens': tokens,
            'total_tokens': len(tokens)
        }
    
    def _afd_multipalabra(self, palabras: List[str], indice: int) -> Dict:
        """AFD para productos de múltiples palabras"""
        # Intentar combinaciones de 2-4 palabras
        for longitud in range(min(4, len(palabras) - indice), 0, -1):
            frase = ' '.join(palabras[indice:indice + longitud]).lower()
            
            # Buscar coincidencia exacta en productos
            if frase in self._cache_productos:
                return {
                    'encontrado': True,
                    'tipo': 'PRODUCTO_COMPLETO',
                    'valor': frase,
                    'producto_data': self._cache_productos[frase],
                    'palabras_consumidas': longitud,
                    'prioridad': 1
                }
        
        return {'encontrado': False}
    
    def _afd_operadores(self, palabras: List[str], indice: int) -> Dict:
        """AFD para operadores de comparación"""
        operadores = {
            'menor a': 'OP_MENOR',
            'menos de': 'OP_MENOR', 
            'menor que': 'OP_MENOR',
            'mayor a': 'OP_MAYOR',
            'más de': 'OP_MAYOR',
            'mayor que': 'OP_MAYOR',
            'igual a': 'OP_IGUAL',
            'entre': 'OP_ENTRE'
        }
        
        # Intentar operadores de 2 palabras
        if indice + 1 < len(palabras):
            frase_2 = f"{palabras[indice]} {palabras[indice + 1]}"
            if frase_2 in operadores:
                return {
                    'encontrado': True,
                    'tipo': operadores[frase_2],
                    'valor': frase_2,
                    'palabras_consumidas': 2,
                    'prioridad': 8
                }
        
        # Intentar operadores de 1 palabra
        if palabras[indice] in operadores:
            return {
                'encontrado': True,
                'tipo': operadores[palabras[indice]],
                'valor': palabras[indice],
                'palabras_consumidas': 1,
                'prioridad': 8
            }
        
        return {'encontrado': False}
    
    def _afd_numeros(self, palabra: str) -> Dict:
        """AFD para números"""
        # Número decimal
        if re.match(r'^\d+\.\d+$', palabra):
            return {
                'encontrado': True,
                'tipo': 'NUMERO_DECIMAL',
                'valor': float(palabra),
                'prioridad': 9
            }
        
        # Número entero
        if re.match(r'^\d+$', palabra):
            return {
                'encontrado': True,
                'tipo': 'NUMERO_ENTERO',
                'valor': int(palabra),
                'prioridad': 9
            }
        
        return {'encontrado': False}
    
    def _afd_unidades(self, palabra: str) -> Dict:
        """AFD para unidades de medida y moneda"""
        unidades_moneda = ['peso', 'pesos', '$', 'dollar', 'dollars']
        unidades_medida = ['ml', 'l', 'litro', 'litros', 'g', 'gr', 'gramo', 'gramos', 'kg', 'kilo', 'kilos']
        
        if palabra in unidades_moneda:
            return {
                'encontrado': True,
                'tipo': 'UNIDAD_MONEDA',
                'valor': palabra,
                'prioridad': 10
            }
        
        if palabra in unidades_medida:
            return {
                'encontrado': True,
                'tipo': 'UNIDAD_MEDIDA',
                'valor': palabra,
                'prioridad': 10
            }
        
        return {'encontrado': False}
    
    def _afd_palabras(self, palabra: str) -> Dict:
        """AFD para palabras individuales"""
        # Buscar en categorías
        if palabra in self._cache_categorias:
            return {
                'encontrado': True,
                'tipo': 'CATEGORIA',
                'valor': palabra,
                'categoria_data': self._cache_categorias[palabra],
                'prioridad': 4
            }
        
        # Buscar en productos individuales
        if palabra in self._cache_productos:
            return {
                'encontrado': True,
                'tipo': 'PRODUCTO_SIMPLE',
                'valor': palabra,
                'producto_data': self._cache_productos[palabra],
                'prioridad': 3
            }
        
        # Filtros de precio
        filtros_precio = {
            'barato': 'FILTRO_PRECIO',
            'baratos': 'FILTRO_PRECIO', 
            'barata': 'FILTRO_PRECIO',
            'baratas': 'FILTRO_PRECIO',
            'economico': 'FILTRO_PRECIO',
            'económico': 'FILTRO_PRECIO',
            'economica': 'FILTRO_PRECIO',
            'económica': 'FILTRO_PRECIO',
            'caro': 'FILTRO_PRECIO',
            'cara': 'FILTRO_PRECIO',
            'caros': 'FILTRO_PRECIO',
            'caras': 'FILTRO_PRECIO'
        }
        
        if palabra in filtros_precio:
            return {
                'encontrado': True,
                'tipo': filtros_precio[palabra],
                'valor': palabra,
                'prioridad': 5
            }
        
        # Modificadores
        modificadores = ['con', 'sin', 'de', 'extra']
        if palabra in modificadores:
            return {
                'encontrado': True,
                'tipo': 'MODIFICADOR',
                'valor': palabra,
                'prioridad': 7
            }
        
        # Palabra no reconocida
        return {
            'encontrado': True,
            'tipo': 'PALABRA_NO_RECONOCIDA',
            'valor': palabra,
            'prioridad': 15
        }
    
    def _fase_analisis_contextual(self, tokenizacion: Dict) -> Dict:
        """Fase 3: Análisis contextual para refinar tokens"""
        tokens = tokenizacion['tokens']
        tokens_refinados = []
        
        for i, token in enumerate(tokens):
            if not token.get('encontrado'):
                continue
                
            token_refinado = token.copy()
            
            # Regla: MODIFICADOR + PALABRA → ATRIBUTO
            if (token['tipo'] == 'MODIFICADOR' and i + 1 < len(tokens) and 
                tokens[i + 1].get('tipo') == 'PALABRA_NO_RECONOCIDA'):
                token_refinado['tipo'] = 'ATRIBUTO_MODIFICADO'
                token_refinado['atributo'] = f"{token['valor']} {tokens[i + 1]['valor']}"
                tokens_refinados.append(token_refinado)
                # Saltear el siguiente token porque ya se procesó
                if i + 1 < len(tokens):
                    tokens[i + 1]['procesado'] = True
                continue
            
            # Regla: NUMERO + UNIDAD_MONEDA → PRECIO
            if (token['tipo'] in ['NUMERO_ENTERO', 'NUMERO_DECIMAL'] and 
                i + 1 < len(tokens) and tokens[i + 1].get('tipo') == 'UNIDAD_MONEDA'):
                token_refinado['tipo'] = 'PRECIO'
                token_refinado['precio'] = token['valor']
                tokens_refinados.append(token_refinado)
                continue
            
            # Saltear tokens ya procesados
            if token.get('procesado'):
                continue
                
            tokens_refinados.append(token_refinado)
        
        return {
            'tokens_refinados': tokens_refinados,
            'reglas_aplicadas': len(tokens) - len(tokens_refinados)
        }
    
    def _fase_interpretacion_semantica(self, analisis_contextual: Dict) -> Dict:
        """Fase 4: Interpretación semántica"""
        tokens = analisis_contextual['tokens_refinados']
        
        interpretacion = {
            'tipo_busqueda': None,
            'producto_especifico': None,
            'categoria': None,
            'atributos': [],
            'filtros_precio': {'min': None, 'max': None},
            'operadores': []
        }
        
        for token in tokens:
            tipo = token['tipo']
            
            if tipo == 'PRODUCTO_COMPLETO':
                interpretacion['tipo_busqueda'] = 'producto_especifico'
                interpretacion['producto_especifico'] = token['producto_data']
            
            elif tipo == 'CATEGORIA':
                interpretacion['categoria'] = token['categoria_data']
                if not interpretacion['tipo_busqueda']:
                    interpretacion['tipo_busqueda'] = 'categoria'
            
            elif tipo == 'ATRIBUTO_MODIFICADO':
                interpretacion['atributos'].append(token['atributo'])
            
            elif tipo == 'FILTRO_PRECIO':
                if token['valor'] in ['barato', 'baratos', 'barata', 'baratas', 'economico', 'económico']:
                    interpretacion['filtros_precio']['max'] = 20.0
                elif token['valor'] in ['caro', 'cara', 'caros', 'caras']:
                    interpretacion['filtros_precio']['min'] = 30.0
            
            elif tipo in ['OP_MENOR', 'OP_MAYOR', 'OP_IGUAL']:
                interpretacion['operadores'].append(token)
        
        # Si no se determinó tipo de búsqueda, usar genérica
        if not interpretacion['tipo_busqueda']:
            interpretacion['tipo_busqueda'] = 'generica'
        
        return interpretacion
    
    def _fase_motor_recomendaciones(self, interpretacion: Dict) -> Dict:
        """Fase 5: Motor de recomendaciones con 5 estrategias"""
        productos_encontrados = []
        estrategia_usada = None
        
        # Estrategia 1: Producto específico
        if interpretacion['tipo_busqueda'] == 'producto_especifico':
            productos_encontrados = [interpretacion['producto_especifico']]
            estrategia_usada = 'producto_especifico'
        
        # Estrategia 2: Búsqueda por categoría
        elif interpretacion['categoria']:
            productos_encontrados = self._buscar_por_categoria(
                interpretacion['categoria']['nombre'],
                interpretacion['filtros_precio']
            )
            estrategia_usada = 'categoria'
        
        # Estrategia 3: Búsqueda combinada por atributos
        elif interpretacion['atributos']:
            productos_encontrados = self._buscar_por_atributos(
                interpretacion['atributos'],
                interpretacion['filtros_precio']
            )
            estrategia_usada = 'atributos'
        
        # Estrategia 4: Solo filtros de precio
        elif any(interpretacion['filtros_precio'].values()):
            productos_encontrados = self._buscar_por_precio(interpretacion['filtros_precio'])
            estrategia_usada = 'precio'
        
        # Estrategia 5: Fallback - productos populares
        else:
            productos_encontrados = self._buscar_fallback()
            estrategia_usada = 'fallback'
        
        return {
            'productos_encontrados': productos_encontrados[:20],  # Límite 20
            'total_encontrados': len(productos_encontrados),
            'estrategia_usada': estrategia_usada,
            'tiene_recomendaciones': len(productos_encontrados) > 0
        }
    
    def _buscar_por_categoria(self, categoria: str, filtros_precio: Dict) -> List[Dict]:
        """Buscar productos por categoría con filtros de precio"""
        productos = []
        
        for producto in self._cache_productos.values():
            if producto['categoria'].lower() == categoria.lower():
                # Aplicar filtros de precio
                if filtros_precio['min'] and producto['precio'] < filtros_precio['min']:
                    continue
                if filtros_precio['max'] and producto['precio'] > filtros_precio['max']:
                    continue
                    
                productos.append(self._formatear_producto_respuesta(producto))
        
        # Ordenar por precio
        return sorted(productos, key=lambda x: x['precio'])
      def _buscar_por_atributos(self, atributos: List[str], filtros_precio: Dict) -> List[Dict]:
        """Buscar productos por atributos"""
        productos = []
        
        for producto in self._cache_productos.values():
            texto_busqueda = producto['nombre'].lower()  # Solo usar nombre
            
            # Verificar que contenga al menos uno de los atributos
            tiene_atributo = any(atributo.lower() in texto_busqueda for atributo in atributos)
            
            if tiene_atributo:
                # Aplicar filtros de precio
                if filtros_precio['min'] and producto['precio'] < filtros_precio['min']:
                    continue
                if filtros_precio['max'] and producto['precio'] > filtros_precio['max']:
                    continue
                    
                productos.append(self._formatear_producto_respuesta(producto))
        
        return sorted(productos, key=lambda x: x['precio'])
    
    def _buscar_por_precio(self, filtros_precio: Dict) -> List[Dict]:
        """Buscar productos solo por precio"""
        productos = []
        
        for producto in self._cache_productos.values():
            # Aplicar filtros de precio
            if filtros_precio['min'] and producto['precio'] < filtros_precio['min']:
                continue
            if filtros_precio['max'] and producto['precio'] > filtros_precio['max']:
                continue
                
            productos.append(self._formatear_producto_respuesta(producto))
        
        return sorted(productos, key=lambda x: x['precio'])
    
    def _buscar_fallback(self) -> List[Dict]:
        """Búsqueda fallback - productos populares/económicos"""
        productos = []
        
        for producto in self._cache_productos.values():
            if producto['precio'] <= 25.0:  # Productos económicos
                productos.append(self._formatear_producto_respuesta(producto))
        
        return sorted(productos, key=lambda x: x['precio'])[:10]
    
    def _formatear_producto_respuesta(self, producto: Dict) -> Dict:
        """Formatear producto para respuesta con imagen incluida"""
        return {
            'id': producto['id'],
            'id_producto': producto['id'],
            'nombre': producto['nombre'],
            'precio': producto['precio'],
            'categoria': producto['categoria'],
            'categoria_id': producto['categoria_id'],
            'cantidad': producto['cantidad'],
            'imagen': producto['imagen'],
            'descripcion': producto['descripcion'],
            'disponible': producto['cantidad'] > 0,
            'source': 'mysql_lynxshop_lcln'
        }

# Instancia global
sistema_lcln = SistemaLCLN()

if __name__ == "__main__":
    # Prueba del sistema LCLN completo
    print("🔬 Probando Sistema LCLN dinámico...")
    
    consultas_prueba = [
        "coca cola sin azucar", 
        "snacks baratos",
        "bebidas menor a 15 pesos",
        "productos con chocolate"
    ]
    
    for consulta in consultas_prueba:
        print(f"\n🔍 Consulta: '{consulta}'")
        resultado = sistema_lcln.analizar_consulta_lcln(consulta)
        
        recomendaciones = resultado['fase_5_motor_recomendaciones']
        print(f"   Estrategia: {recomendaciones['estrategia_usada']}")
        print(f"   Productos: {recomendaciones['total_encontrados']}")
        
        for prod in recomendaciones['productos_encontrados'][:3]:
            print(f"     - {prod['nombre']} ${prod['precio']} ({prod['imagen']})")
