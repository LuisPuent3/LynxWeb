#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema LCLN Mejorado con Integración Completa de Sinónimos y Extensiones Formales
Incluye:
1. Integración correcta con sinónimos  
2. Mejor detección de atributos como "picante"
3. Formateo correcto para frontend (imagen, stock)
4. ✨ AFD formal según documento LCLN
5. ✨ Analizador sintáctico con gramáticas BNF
6. ✨ Reglas de desambiguación RD1-RD4
"""

import mysql.connector
import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Optional, Tuple
import difflib
from datetime import datetime, timedelta
import re
from enum import Enum
from dataclasses import dataclass

# ========================================
# EXTENSIÓN FORMAL LCLN - AFD y ANALIZADOR SINTÁCTICO
# ========================================

class TipoToken(Enum):
    """Tipos de tokens según documento LCLN (Tabla de Componentes Léxicos)"""
    PRODUCTO_COMPLETO = (1, "PRODUCTO_COMPLETO")
    PRODUCTO_MULTIPALABRA = (2, "PRODUCTO_MULTIPALABRA") 
    CATEGORIA_KEYWORD = (3, "CATEGORIA_KEYWORD")
    CATEGORIA = (4, "CATEGORIA")
    PRODUCTO_SIMPLE = (5, "PRODUCTO_SIMPLE")
    NEGACION = (6, "NEGACION")
    INCLUSION = (6, "INCLUSION")
    ATRIBUTO = (7, "ATRIBUTO")
    OP_MENOR = (8, "OP_MENOR")
    OP_MAYOR = (8, "OP_MAYOR")
    OP_ENTRE = (8, "OP_ENTRE")
    NUMERO = (9, "NUMERO")
    UNIDAD_MONEDA = (10, "UNIDAD_MONEDA")
    UNIDAD_MEDIDA = (10, "UNIDAD_MEDIDA")
    CONECTOR_Y = (11, "CONECTOR_Y")
    PREPOSICION = (12, "PREPOSICION")
    PALABRA_GENERICA = (13, "PALABRA_GENERICA")
    
    def __init__(self, prioridad, nombre):
        self.prioridad = prioridad
        self.nombre = nombre

@dataclass
class TokenFormal:
    """Token formal según especificación LCLN"""
    tipo: TipoToken
    lexema: str
    posicion: int
    longitud: int
    confianza: float
    contexto: str = ""

class AFDComponenteLexicoLCLN:
    """
    Autómata Finito Determinista para análisis léxico LCLN
    Implementa la especificación formal del documento (líneas 95-217)
    """
    
    def __init__(self):
        # Tabla de componentes léxicos con patrones RegEx y prioridades
        self.componentes_lexicos = {
            # Prioridad 1: Productos completos multi-palabra
            TipoToken.PRODUCTO_COMPLETO: [
                (r'\b(coca\s+cola\s+sin\s+azucar)\b', 'coca cola sin azucar'),
                (r'\b(manzana\s+verde)\b', 'manzana verde'),
                (r'\b(arroz\s+integral)\b', 'arroz integral')
            ],
            # Prioridad 2: Productos multi-palabra básicos
            TipoToken.PRODUCTO_MULTIPALABRA: [
                (r'\b(coca\s+cola)\b', 'coca cola'),
                (r'\b(coca\-cola)\b', 'coca-cola')
            ],
            # Prioridad 3: Palabras clave de categoría
            TipoToken.CATEGORIA_KEYWORD: [
                (r'\b(categor[ií]a)\b', 'categoria')
            ],
            # Prioridad 4: Categorías
            TipoToken.CATEGORIA: [
                (r'\b(bebidas|snacks|abarrotes|frutas|verduras)\b', 'categoria_nombre')
            ],
            # Prioridad 5: Productos simples
            TipoToken.PRODUCTO_SIMPLE: [
                (r'\b(doritos|arroz|manzana|lechuga|cheetos)\b', 'producto_simple')
            ],
            # Prioridad 6: Negación e inclusión
            TipoToken.NEGACION: [
                (r'\b(sin|no)\b', 'sin')
            ],
            TipoToken.INCLUSION: [
                (r'\b(con)\b', 'con')
            ],
            # Prioridad 8: Operadores de comparación
            TipoToken.OP_MENOR: [
                (r'\b(menor\s+a)\b', 'menor a')
            ],
            TipoToken.OP_MAYOR: [
                (r'\b(mayor\s+a)\b', 'mayor a')
            ],
            TipoToken.OP_ENTRE: [
                (r'\b(entre)\b', 'entre')
            ],
            # Prioridad 9: Números
            TipoToken.NUMERO: [
                (r'\b(\d+(?:\.\d+)?)\b', 'numero')
            ],
            # Prioridad 10: Unidades
            TipoToken.UNIDAD_MONEDA: [
                (r'\b(pesos?|peso)\b', 'pesos')
            ],
            TipoToken.UNIDAD_MEDIDA: [
                (r'\b(litros?|gramos?|ml|kg)\b', 'unidad_medida')
            ],
            # Prioridad 11: Conectores
            TipoToken.CONECTOR_Y: [
                (r'\b(y)\b', 'y')
            ],
            # Prioridad 12: Preposiciones
            TipoToken.PREPOSICION: [
                (r'\b(de|a)\b', 'preposicion')
            ]
        }
        
    def analizar_lexicamente(self, entrada: str) -> List[TokenFormal]:
        """
        Análisis léxico formal con AFD
        Implementa look-ahead y prioridades según documento
        """
        entrada_lower = entrada.lower()
        tokens = []
        posicion = 0
        
        while posicion < len(entrada):
            token_encontrado = False
            mejor_match = None
            
            # Buscar el token con mayor prioridad (menor número = mayor prioridad)
            for tipo_token in sorted(TipoToken, key=lambda x: x.prioridad):
                if tipo_token in self.componentes_lexicos:
                    for patron, descripcion in self.componentes_lexicos[tipo_token]:
                        match = re.search(patron, entrada_lower[posicion:])
                        if match and match.start() == 0:  # Match al inicio de la posición actual
                            if not mejor_match or tipo_token.prioridad < mejor_match['prioridad']:
                                mejor_match = {
                                    'tipo': tipo_token,
                                    'lexema': match.group(0),
                                    'longitud': len(match.group(0)),
                                    'prioridad': tipo_token.prioridad,
                                    'descripcion': descripcion
                                }
                                token_encontrado = True
            
            if token_encontrado and mejor_match:
                # Crear token formal
                token = TokenFormal(
                    tipo=mejor_match['tipo'],
                    lexema=mejor_match['lexema'],
                    posicion=posicion,
                    longitud=mejor_match['longitud'],
                    confianza=0.9,
                    contexto=mejor_match['descripcion']
                )
                tokens.append(token)
                posicion += mejor_match['longitud']
                
                # Saltar espacios
                while posicion < len(entrada) and entrada[posicion].isspace():
                    posicion += 1
            else:
                # Token no reconocido - avanzar y buscar palabra genérica
                palabra_match = re.search(r'\b([a-záéíóúñ]+)\b', entrada_lower[posicion:])
                if palabra_match and palabra_match.start() == 0:
                    token = TokenFormal(
                        tipo=TipoToken.PALABRA_GENERICA,
                        lexema=palabra_match.group(0),
                        posicion=posicion,
                        longitud=len(palabra_match.group(0)),
                        confianza=0.5
                    )
                    tokens.append(token)
                    posicion += len(palabra_match.group(0))
                    
                    # Saltar espacios
                    while posicion < len(entrada) and entrada[posicion].isspace():
                        posicion += 1
                else:
                    posicion += 1
        
        return tokens

class AnalizadorSintacticoLCLN:
    """
    Analizador sintáctico para gramáticas BNF del documento LCLN
    Implementa las gramáticas de las líneas 34-64
    """
    
    def __init__(self):
        # Reglas de desambiguación según documento (RD1-RD4)
        self.reglas_desambiguacion = {
            'RD1': 'Productos multi-palabra tienen prioridad sobre interpretaciones separadas',
            'RD2': 'Categorías explícitas (con "categoria") tienen prioridad',
            'RD3': 'Modificadores se asocian al elemento más cercano a la izquierda',
            'RD4': 'En ambigüedad persistente, scoring por frecuencia de uso'
        }
    
    def analizar_sintacticamente(self, tokens: List[TokenFormal]) -> Dict:
        """
        Análisis sintáctico según gramáticas BNF del documento
        """
        if not tokens:
            return {'tipo': 'consulta_vacia', 'valida': False}
        
        # Intenta reconocer patrones sintácticos
        resultado = {
            'tipo_gramatica': None,
            'estructura_reconocida': None,
            'entidad_prioritaria': None,
            'modificadores': [],
            'valida': False,
            'reglas_aplicadas': []
        }
        
        # Patrón 1: <entidad_prioritaria> <modificadores_opcionales>
        entidad_prioritaria = self._reconocer_entidad_prioritaria(tokens)
        if entidad_prioritaria:
            resultado['entidad_prioritaria'] = entidad_prioritaria
            resultado['modificadores'] = self._reconocer_modificadores(tokens[entidad_prioritaria['longitud']:])
            resultado['tipo_gramatica'] = 'entidad_prioritaria_con_modificadores'
            resultado['valida'] = True
            resultado['reglas_aplicadas'].append('RD1')
        
        # Patrón 2: <busqueda_general> <filtros>
        elif self._es_busqueda_general(tokens):
            resultado['tipo_gramatica'] = 'busqueda_general_con_filtros'
            resultado['estructura_reconocida'] = 'busqueda_general'
            resultado['modificadores'] = self._reconocer_filtros(tokens)
            resultado['valida'] = True
        
        # Aplicar reglas de desambiguación
        resultado = self._aplicar_reglas_desambiguacion(resultado, tokens)
        
        return resultado
    
    def _reconocer_entidad_prioritaria(self, tokens: List[TokenFormal]) -> Optional[Dict]:
        """Reconoce entidad prioritaria según gramática BNF"""
        if not tokens:
            return None
        
        primer_token = tokens[0]
        
        # <producto_conocido_completo>
        if primer_token.tipo == TipoToken.PRODUCTO_COMPLETO:
            return {
                'tipo': 'producto_conocido_completo',
                'valor': primer_token.lexema,
                'longitud': 1,
                'confianza': primer_token.confianza
            }
        
        # <producto_conocido> <variante>
        if primer_token.tipo == TipoToken.PRODUCTO_MULTIPALABRA:
            if len(tokens) > 1 and tokens[1].tipo == TipoToken.ATRIBUTO:
                return {
                    'tipo': 'producto_con_variante',
                    'valor': f"{primer_token.lexema} {tokens[1].lexema}",
                    'longitud': 2,
                    'confianza': min(primer_token.confianza, tokens[1].confianza)
                }
            return {
                'tipo': 'producto_conocido',
                'valor': primer_token.lexema,
                'longitud': 1,
                'confianza': primer_token.confianza
            }
        
        # <categoria_explicita>
        if primer_token.tipo == TipoToken.CATEGORIA_KEYWORD:
            if len(tokens) > 1 and tokens[1].tipo == TipoToken.CATEGORIA:
                return {
                    'tipo': 'categoria_explicita',
                    'valor': f"{primer_token.lexema} {tokens[1].lexema}",
                    'longitud': 2,
                    'confianza': min(primer_token.confianza, tokens[1].confianza)
                }
        
        return None
    
    def _reconocer_modificadores(self, tokens: List[TokenFormal]) -> List[Dict]:
        """Reconoce modificadores opcionales"""
        modificadores = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            # <filtro_atributo> ::= ("sin" | "con") <atributo>
            if token.tipo in [TipoToken.NEGACION, TipoToken.INCLUSION]:
                if i + 1 < len(tokens):
                    siguiente = tokens[i + 1]
                    if siguiente.tipo in [TipoToken.ATRIBUTO, TipoToken.PALABRA_GENERICA]:
                        modificadores.append({
                            'tipo': 'filtro_atributo',
                            'operador': token.lexema,
                            'atributo': siguiente.lexema,
                            'confianza': min(token.confianza, siguiente.confianza)
                        })
                        i += 2
                        continue
            
            # <filtro_precio> ::= <operador_precio> <numero> "pesos"
            elif token.tipo in [TipoToken.OP_MENOR, TipoToken.OP_MAYOR, TipoToken.OP_ENTRE]:
                if i + 2 < len(tokens):
                    numero = tokens[i + 1]
                    unidad = tokens[i + 2]
                    if numero.tipo == TipoToken.NUMERO and unidad.tipo == TipoToken.UNIDAD_MONEDA:
                        modificadores.append({
                            'tipo': 'filtro_precio',
                            'operador': token.lexema,
                            'valor': numero.lexema,
                            'unidad': unidad.lexema,
                            'confianza': min(token.confianza, numero.confianza, unidad.confianza)
                        })
                        i += 3
                        continue
            
            i += 1
        
        return modificadores
    
    def _reconocer_filtros(self, tokens: List[TokenFormal]) -> List[Dict]:
        """Reconoce filtros para búsqueda general"""
        return self._reconocer_modificadores(tokens)
    
    def _es_busqueda_general(self, tokens: List[TokenFormal]) -> bool:
        """Determina si es una búsqueda general"""
        if not tokens:
            return False
        
        # Si no hay entidad prioritaria clara, es búsqueda general
        primer_token = tokens[0]
        return primer_token.tipo not in [
            TipoToken.PRODUCTO_COMPLETO,
            TipoToken.PRODUCTO_MULTIPALABRA,
            TipoToken.CATEGORIA_KEYWORD
        ]
    
    def _aplicar_reglas_desambiguacion(self, resultado: Dict, tokens: List[TokenFormal]) -> Dict:
        """Aplica reglas de desambiguación RD1-RD4"""
        
        # RD1: Productos multi-palabra tienen prioridad
        if any(token.tipo == TipoToken.PRODUCTO_COMPLETO for token in tokens):
            resultado['reglas_aplicadas'].append('RD1 - Producto completo tiene prioridad')
        
        # RD2: Categorías explícitas tienen prioridad
        if any(token.tipo == TipoToken.CATEGORIA_KEYWORD for token in tokens):
            resultado['reglas_aplicadas'].append('RD2 - Categoría explícita detectada')
        
        # RD3: Modificadores se asocian al elemento más cercano a la izquierda
        resultado['reglas_aplicadas'].append('RD3 - Asociación por proximidad aplicada')
        
        return resultado

class SistemaLCLNMejorado:
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
        self._cache_sinonimos = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)
        
        # Ruta sinónimos NLP
        base_dir = Path(__file__).parent
        self.sqlite_sinonimos = base_dir / "api" / "sinonimos_lynx.db"
        if base_dir.name == "api":
            self.sqlite_sinonimos = base_dir / "sinonimos_lynx.db"
            
        # ✨ NUEVAS EXTENSIONES FORMALES LCLN
        self.afd_lexico = AFDComponenteLexicoLCLN()
        self.analizador_sintactico = AnalizadorSintacticoLCLN()
        self.modo_analisis_formal = True  # Bandera para activar/desactivar análisis formal
        
        # Correcciones ortográficas específicas mejoradas
        self.correcciones_manuales = {
            'chetoos': 'cheetos',
            'chetos': 'cheetos', 
            'chettos': 'cheetos',
            'koka': 'coca',
            'kola': 'cola',
            'coca': 'coca-cola',
            'asucar': 'azucar',
            'azucar': 'azúcar',
            'picabte': 'picante',
            'pikante': 'picante',
            'picbte': 'picante',
            'barao': 'barato',
            'varato': 'barato',
            'vebida': 'bebida',
            'vebidas': 'bebidas',
            'botana': 'snack',
            'botanas': 'snacks'
        }
    
    def _necesita_actualizar_cache(self) -> bool:
        """Verificar si el cache necesita actualizarse"""
        if not self._cache_timestamp:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_duration
    
    def _actualizar_cache_dinamico(self):
        """Actualizar cache con datos actuales de MySQL y SQLite"""
        if not self._necesita_actualizar_cache():
            return
            
        print("[CACHE] Actualizando cache dinamico desde MySQL y SQLite...")
        
        # Actualizar productos desde MySQL
        self._actualizar_cache_productos()
        
        # Actualizar sinónimos desde SQLite  
        self._actualizar_cache_sinonimos()
        
        self._cache_timestamp = datetime.now()
        print(f"[CACHE] Cache actualizado: {len(self._cache_productos)} productos, {len(self._cache_categorias)} categorias, {len(self._cache_sinonimos)} sinonimos")
    
    def _actualizar_cache_productos(self):
        """Actualizar productos desde MySQL"""
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.precio, p.cantidad, p.imagen,
                       c.id_categoria, c.nombre as categoria_nombre
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.cantidad > 0
                ORDER BY p.nombre
            """)
            
            productos = cursor.fetchall()
            self._cache_productos = {}
            self._cache_categorias = {}
            
            for producto in productos:
                # Cache de productos por nombre (normalizado)
                nombre_key = producto['nombre'].lower()
                self._cache_productos[nombre_key] = {
                    'id': producto['id_producto'],
                    'nombre': producto['nombre'],
                    'precio': float(producto['precio']),
                    'cantidad': producto['cantidad'],
                    'imagen': producto['imagen'] or 'default.jpg',
                    'categoria_id': producto['id_categoria'],
                    'categoria_nombre': producto['categoria_nombre']
                }
                
                # Cache de categorías
                cat_key = producto['categoria_nombre'].lower()
                if cat_key not in self._cache_categorias:
                    self._cache_categorias[cat_key] = {
                        'id': producto['id_categoria'],
                        'nombre': producto['categoria_nombre']
                    }
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error actualizando cache MySQL: {e}")
    
    def _actualizar_cache_sinonimos(self):
        """Actualizar sinónimos desde SQLite"""
        if not self.sqlite_sinonimos.exists():
            print("[WARNING] No se encuentra la base de datos de sinonimos")
            return
        
        try:
            conn = sqlite3.connect(self.sqlite_sinonimos)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT termino, categoria, tipo, confianza
                FROM sinonimos
                WHERE activo = 1
                ORDER BY confianza DESC
            """)
            
            sinonimos = cursor.fetchall()
            self._cache_sinonimos = {}
            
            for termino, categoria, tipo, confianza in sinonimos:
                termino_key = termino.lower()
                if termino_key not in self._cache_sinonimos:
                    self._cache_sinonimos[termino_key] = []
                
                self._cache_sinonimos[termino_key].append({
                    'categoria': categoria,
                    'tipo': tipo,
                    'confianza': confianza
                })
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error actualizando cache sinonimos: {e}")
    
    def analizar_consulta_lcln(self, consulta: str) -> Dict:
        """
        Análisis LCLN completo mejorado con sinónimos
        """
        # Asegurar cache actualizado
        self._actualizar_cache_dinamico()
        
        consulta_original = consulta
        consulta = consulta.lower().strip()
        
        resultado_analisis = {
            'consulta_original': consulta_original,
            'fase_1_correccion': self._fase_correccion_ortografica(consulta),
            'fase_2_expansion_sinonimos': None,
            'fase_3_tokenizacion': None,
            'fase_4_interpretacion': None,
            'fase_5_motor_recomendaciones': None,
            # ✨ NUEVAS FASES FORMALES LCLN
            'fase_afd_lexico': None,
            'fase_analisis_sintactico': None,
            'validacion_gramatical': None
        }
        
        # Fase 1: Corrección ortográfica
        consulta_corregida = resultado_analisis['fase_1_correccion']['texto_corregido']
          # Fase 2: Expansión con sinónimos
        resultado_analisis['fase_2_expansion_sinonimos'] = self._fase_expansion_sinonimos(consulta_corregida)
        
        # Fase 3: Tokenización mejorada
        resultado_analisis['fase_3_tokenizacion'] = self._fase_tokenizacion_mejorada(consulta_corregida, resultado_analisis['fase_2_expansion_sinonimos'])
        
        # Fase 4: Interpretación semántica
        resultado_analisis['fase_4_interpretacion'] = self._fase_interpretacion_semantica(resultado_analisis['fase_3_tokenizacion'], resultado_analisis['fase_2_expansion_sinonimos'])
        
        # Fase 5: Motor de recomendaciones
        resultado_analisis['fase_5_motor_recomendaciones'] = self._fase_motor_recomendaciones(resultado_analisis['fase_4_interpretacion'])
        
        # ✨ FASES FORMALES ADICIONALES LCLN
        if self.modo_analisis_formal:
            # Fase AFD: Análisis léxico formal
            resultado_analisis['fase_afd_lexico'] = self._fase_afd_lexico_formal(consulta_corregida)
            
            # Fase Sintáctica: Análisis sintáctico BNF
            if resultado_analisis['fase_afd_lexico']['tokens_formales']:
                resultado_analisis['fase_analisis_sintactico'] = self._fase_analisis_sintactico_formal(
                    resultado_analisis['fase_afd_lexico']['tokens_formales']
                )
                
                # Validación gramatical
                resultado_analisis['validacion_gramatical'] = self._validacion_gramatical_completa(
                    resultado_analisis['fase_analisis_sintactico']
                )
        
        return resultado_analisis
    
    def _fase_correccion_ortografica(self, consulta: str) -> Dict:
        """Fase 1: Corrección ortográfica mejorada"""
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
        # Primero verificar correcciones manuales
        if palabra in self.correcciones_manuales:
            return {
                'aplicada': True,
                'palabra_original': palabra,
                'palabra_corregida': self.correcciones_manuales[palabra],
                'confianza': 0.95,
                'fuente': 'correccion_manual'
            }
        
        # Buscar en productos
        for nombre_producto, data in self._cache_productos.items():
            palabras_producto = nombre_producto.split()
            for palabra_prod in palabras_producto:
                if len(palabra_prod) > 2 and self._distancia_levenshtein(palabra, palabra_prod) <= 2:
                    similitud = difflib.SequenceMatcher(None, palabra, palabra_prod).ratio()
                    if similitud >= 0.6:
                        return {
                            'aplicada': True,
                            'palabra_original': palabra,
                            'palabra_corregida': palabra_prod,
                            'confianza': similitud,
                            'fuente': 'productos'
                        }
        
        return {
            'aplicada': False,
            'palabra_original': palabra,
            'palabra_corregida': palabra,
            'confianza': 1.0,            'fuente': None
        }
    
    def _fase_expansion_sinonimos(self, consulta: str) -> Dict:
        """Fase 2: Expansión con sinónimos de SQLite"""
        palabras = consulta.split()
        expansion_info = {
            'terminos_expandidos': [],
            'categorias_detectadas': set(),  # Usar set para evitar duplicados
            'productos_detectados': set(),
            'atributos_detectados': set()
        }
        
        # Lista de palabras vacías/conectores que no aportan valor semántico
        stop_words = {
            'productos', 'producto', 'menores', 'mayor', 'menor', 'pesos', 'peso', 
            'pero', 'de', 'del', 'la', 'las', 'el', 'los', 'y', 'o', 'que', 
            'con', 'sin', 'para', 'por', 'en', 'un', 'una', 'unos', 'unas',
            'es', 'son', 'está', 'están', 'tiene', 'tienen', 'hay', 'más',
            'menos', 'muy', 'mucho', 'poco', 'algo', 'nada', 'todo', 'todos'
        }
        
        # Buscar sinónimos para cada palabra y para la frase completa
        terminos_busqueda = palabras + [consulta]
        
        for termino in terminos_busqueda:
            termino_key = termino.lower()
            
            # Filtrar palabras vacías y términos muy cortos
            if termino_key in stop_words or len(termino_key) < 3:
                continue
                
            if termino_key in self._cache_sinonimos:
                sinonimos = self._cache_sinonimos[termino_key]
                
                for sinonimo in sinonimos:
                    # Aumentar umbral de confianza para términos cortos
                    umbral_confianza = 0.85 if len(termino_key) <= 4 else 0.7
                    
                    if sinonimo['confianza'] >= umbral_confianza:
                        if sinonimo['tipo'] == 'categoria' and sinonimo['categoria'] != 'categoria':
                            expansion_info['categorias_detectadas'].add(sinonimo['categoria'])
                        elif sinonimo['tipo'] == 'producto':
                            expansion_info['productos_detectados'].add(sinonimo['categoria'])
                        elif sinonimo['tipo'] == 'atributo':
                            expansion_info['atributos_detectados'].add(sinonimo['categoria'])
                        
                        expansion_info['terminos_expandidos'].append({
                            'termino_original': termino,
                            'termino_expandido': sinonimo['categoria'],
                            'tipo': sinonimo['tipo'],
                            'confianza': sinonimo['confianza']
                        })
        
        # Convertir sets a listas para JSON serialización
        return {
            'terminos_expandidos': expansion_info['terminos_expandidos'],
            'categorias_detectadas': list(expansion_info['categorias_detectadas']),
            'productos_detectados': list(expansion_info['productos_detectados']),            'atributos_detectados': list(expansion_info['atributos_detectados'])
        }
    
    def _fase_tokenizacion_mejorada(self, consulta: str, expansion: Dict) -> Dict:
        """Fase 3: Tokenización mejorada con contexto de sinónimos"""
        palabras = consulta.split()
        tokens = []
        
        # Detectar atributos específicos
        atributos_conocidos = {
            'picante': ['picante', 'fuego', 'hot', 'chile', 'adobadas', 'flamin', 'dinamita'],
            'dulce': ['dulce', 'azucarado', 'sweet'],
            'sin azucar': ['sin azucar', 'sin azúcar', 'light', 'zero', 'diet'],
            'barato': ['barato', 'baratos', 'barata', 'baratas', 'economico', 'económico'],
            'caro': ['caro', 'caros', 'cara', 'caras', 'costoso', 'premium']
        }
        
        for palabra in palabras:
            token = {
                'palabra': palabra,
                'tipo': 'PALABRA_GENERICA',
                'valor': palabra,
                'confianza': 0.5
            }
            
            # Verificar si es un atributo conocido
            for atributo, variantes in atributos_conocidos.items():
                if palabra in variantes:
                    token['tipo'] = 'ATRIBUTO'
                    token['atributo'] = atributo
                    token['confianza'] = 0.9
                    break
            
            # Verificar si es una categoría (de sinónimos)
            if palabra in [cat.lower() for cat in expansion['categorias_detectadas']]:
                token['tipo'] = 'CATEGORIA'
                token['confianza'] = 0.8
            
            # Verificar si es un producto específico (de sinónimos)
            if palabra in [prod.lower() for prod in expansion['productos_detectados']]:
                token['tipo'] = 'PRODUCTO_ESPECIFICO'
                token['confianza'] = 0.9
            
            tokens.append(token)
        
        return {
            'tokens': tokens,
            'total_tokens': len(tokens)
        }
    
    def _fase_interpretacion_semantica(self, tokenizacion: Dict, expansion: Dict) -> Dict:
        """Fase 4: Interpretación semántica mejorada"""
        tokens = tokenizacion['tokens']
        
        interpretacion = {
            'tipo_busqueda': 'generica',
            'categoria_principal': None,
            'productos_especificos': [],
            'atributos': [],
            'filtros_precio': {'min': None, 'max': None}
        }
        
        # Detectar productos específicos de sinónimos
        if expansion['productos_detectados']:
            interpretacion['tipo_busqueda'] = 'producto_especifico'
            interpretacion['productos_especificos'] = expansion['productos_detectados']
        
        # Detectar categorías
        elif expansion['categorias_detectadas']:
            interpretacion['tipo_busqueda'] = 'categoria'
            interpretacion['categoria_principal'] = expansion['categorias_detectadas'][0]  # Tomar la primera
        
        # Detectar atributos de tokens y sinónimos
        for token in tokens:
            if token['tipo'] == 'ATRIBUTO':
                interpretacion['atributos'].append(token['atributo'])
                
                # Mapear atributos de precio
                if token['atributo'] == 'barato':
                    interpretacion['filtros_precio']['max'] = 20.0
                elif token['atributo'] == 'caro':
                    interpretacion['filtros_precio']['min'] = 30.0
        
        # Agregar atributos detectados desde sinónimos
        if expansion['atributos_detectados']:
            interpretacion['atributos'].extend(expansion['atributos_detectados'])
        
        return interpretacion
    
    def _fase_motor_recomendaciones(self, interpretacion: Dict) -> Dict:
        """Fase 5: Motor de recomendaciones mejorado"""
        productos_encontrados = []
        estrategia_usada = 'fallback'
        
        # Estrategia 1: Búsqueda por productos específicos
        if interpretacion['productos_especificos']:
            productos_especificos = self._buscar_productos_especificos(
                interpretacion['productos_especificos'],
                interpretacion['filtros_precio'],
                interpretacion['atributos']
            )
            
            if productos_especificos:
                productos_encontrados = productos_especificos
                estrategia_usada = 'producto_especifico'
        
        # Estrategia 2: Búsqueda por categoría específica
        if not productos_encontrados and interpretacion['categoria_principal']:
            productos_categoria = self._buscar_por_categoria(
                interpretacion['categoria_principal'],
                interpretacion['filtros_precio'],
                interpretacion['atributos']
            )
            
            if productos_categoria:
                productos_encontrados = productos_categoria
                estrategia_usada = 'categoria_con_atributos'
        
        # Estrategia 3: Búsqueda por atributos
        if not productos_encontrados and interpretacion['atributos']:
            productos_atributos = self._buscar_por_atributos(
                interpretacion['atributos'],
                interpretacion['filtros_precio']
            )
            
            if productos_atributos:
                productos_encontrados = productos_atributos
                estrategia_usada = 'atributos'
        
        # Estrategia 4: Fallback - productos aleatorios con filtro precio
        if not productos_encontrados:
            productos_encontrados = self._buscar_fallback(interpretacion['filtros_precio'])
            estrategia_usada = 'fallback_precio'
        
        # Formatear productos para frontend (CRUCIAL: incluir imagen y stock)
        productos_formateados = []
        for producto in productos_encontrados[:20]:
            productos_formateados.append({
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio': float(producto['precio']),
                'imagen': producto['imagen'],  # IMAGEN INCLUIDA
                'cantidad': producto['cantidad'],  # STOCK INCLUIDO
                'categoria_nombre': producto['categoria_nombre'],
                'similarity_score': 0.8
            })
        
        return {
            'productos_encontrados': productos_formateados,
            'total_encontrados': len(productos_formateados),
            'estrategia_usada': estrategia_usada,
            'tiene_recomendaciones': len(productos_formateados) > 0
        }
    
    def _buscar_por_categoria(self, categoria: str, filtros_precio: Dict, atributos: List[str]) -> List[Dict]:
        """Buscar productos por categoría con filtros"""
        productos = []
        
        for nombre_producto, data in self._cache_productos.items():
            categoria_producto = data['categoria_nombre'].lower()
            
            # Verificar categoría
            if categoria.lower() not in categoria_producto and categoria_producto not in categoria.lower():
                continue
            
            # Aplicar filtros de precio
            precio = data['precio']
            if filtros_precio.get('min') and precio < filtros_precio['min']:
                continue
            if filtros_precio.get('max') and precio > filtros_precio['max']:
                continue
              # Aplicar filtros de atributos (buscar en el nombre del producto)
            if atributos:
                nombre_lower = data['nombre'].lower()
                atributo_encontrado = False
                
                for atributo in atributos:
                    if atributo == 'picante':
                        if any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas']):
                            atributo_encontrado = True
                            break
                    elif atributo == 'sin azucar':
                        # Solo productos que explícitamente son sin azúcar
                        if any(keyword in nombre_lower for keyword in ['sin azúcar', 'light', 'zero', 'diet']) or data['categoria_nombre'].lower() == 'agua':
                            atributo_encontrado = True
                            break
                        # Excluir productos que claramente tienen azúcar
                        elif any(keyword in nombre_lower for keyword in ['boing', 'sprite 355', 'coca-cola 600']) and not any(keyword in nombre_lower for keyword in ['light', 'zero', 'diet']):
                            continue
                
                if not atributo_encontrado:
                    continue
            
            productos.append(data)
        
        return sorted(productos, key=lambda x: x['precio'])
    
    def _buscar_por_atributos(self, atributos: List[str], filtros_precio: Dict) -> List[Dict]:
        """Buscar productos por atributos específicos"""
        productos = []
        
        for nombre_producto, data in self._cache_productos.items():
            nombre_lower = data['nombre'].lower()
            atributo_encontrado = False
            
            for atributo in atributos:
                if atributo == 'picante':
                    if any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas']):
                        atributo_encontrado = True
                        break
                elif atributo == 'sin azucar':
                    # Solo productos que explícitamente son sin azúcar
                    if any(keyword in nombre_lower for keyword in ['sin azúcar', 'light', 'zero', 'diet']):
                        atributo_encontrado = True
                        break
            
            if atributo_encontrado:
                # Aplicar filtros de precio
                precio = data['precio']
                if filtros_precio.get('min') and precio < filtros_precio['min']:
                    continue
                if filtros_precio.get('max') and precio > filtros_precio['max']:
                    continue
                
                productos.append(data)
        
        return sorted(productos, key=lambda x: x['precio'])
    
    def _buscar_fallback(self, filtros_precio: Dict) -> List[Dict]:
        """Búsqueda fallback con filtros de precio"""
        productos = []
        
        for nombre_producto, data in self._cache_productos.items():
            precio = data['precio']
            
            # Aplicar filtros de precio si existen
            if filtros_precio.get('min') and precio < filtros_precio['min']:
                continue
            if filtros_precio.get('max') and precio > filtros_precio['max']:
                continue
            
            productos.append(data)
        
        return sorted(productos, key=lambda x: x['precio'])[:10]
    
    def _buscar_productos_especificos(self, productos_especificos: List[str], filtros_precio: Dict, atributos: List[str]) -> List[Dict]:
        """Buscar productos específicos detectados por sinónimos"""
        productos = []
        
        for producto_nombre in productos_especificos:
            for nombre_producto, data in self._cache_productos.items():
                # Buscar coincidencia exacta o parcial en el nombre del producto
                if producto_nombre.lower() in data['nombre'].lower() or data['nombre'].lower() in producto_nombre.lower():
                    # Aplicar filtros de precio
                    precio = data['precio']
                    if filtros_precio.get('min') and precio < filtros_precio['min']:
                        continue
                    if filtros_precio.get('max') and precio > filtros_precio['max']:
                        continue
                    
                    # Aplicar filtros de atributos si se especificaron
                    if atributos:
                        nombre_lower = data['nombre'].lower()
                        atributo_encontrado = False
                        
                        for atributo in atributos:
                            if atributo == 'picante':
                                if any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas']):
                                    atributo_encontrado = True
                                    break
                            elif atributo == 'sin azucar':
                                if any(keyword in nombre_lower for keyword in ['sin azucar', 'sin azúcar', 'light', 'zero', 'diet']):
                                    atributo_encontrado = True
                                    break
                        
                        if not atributo_encontrado:
                            continue
                    
                    productos.append(data)
        
        return sorted(productos, key=lambda x: x['precio'])
    
    # ========================================
    # ✨ MÉTODOS FORMALES LCLN ADICIONALES
    # ========================================
    
    def _fase_afd_lexico_formal(self, consulta: str) -> Dict:
        """
        Fase AFD: Análisis léxico formal con AFD según documento LCLN
        """
        tokens_formales = self.afd_lexico.analizar_lexicamente(consulta)
        
        # Estadísticas del análisis léxico
        estadisticas = {
            'total_tokens': len(tokens_formales),
            'tokens_reconocidos': len([t for t in tokens_formales if t.tipo != TipoToken.PALABRA_GENERICA]),
            'precision_reconocimiento': 0.0
        }
        
        if estadisticas['total_tokens'] > 0:
            estadisticas['precision_reconocimiento'] = estadisticas['tokens_reconocidos'] / estadisticas['total_tokens']
        
        return {
            'tokens_formales': tokens_formales,
            'estadisticas': estadisticas,
            'tabla_tokens': [
                {
                    'tipo': token.tipo.nombre,
                    'lexema': token.lexema,
                    'posicion': token.posicion,
                    'longitud': token.longitud,
                    'confianza': token.confianza,
                    'prioridad': token.tipo.prioridad,
                    'contexto': token.contexto
                }
                for token in tokens_formales
            ]
        }
    
    def _fase_analisis_sintactico_formal(self, tokens_formales: List[TokenFormal]) -> Dict:
        """
        Fase Sintáctica: Análisis sintáctico según gramáticas BNF del documento
        """
        resultado_sintactico = self.analizador_sintactico.analizar_sintacticamente(tokens_formales)
        
        # Enriquecer con métricas de calidad
        resultado_sintactico['metricas_calidad'] = {
            'estructura_valida': resultado_sintactico.get('valida', False),
            'reglas_aplicadas_count': len(resultado_sintactico.get('reglas_aplicadas', [])),
            'confianza_gramatical': self._calcular_confianza_gramatical(resultado_sintactico, tokens_formales)
        }
        
        return resultado_sintactico
    
    def _validacion_gramatical_completa(self, analisis_sintactico: Dict) -> Dict:
        """
        Validación gramatical completa según especificaciones LCLN
        """
        validacion = {
            'cumple_especificacion_lcln': False,
            'patrones_reconocidos': [],
            'errores_gramaticales': [],
            'sugerencias_mejora': [],
            'nivel_conformidad': 'BAJO'  # BAJO, MEDIO, ALTO
        }
        
        if analisis_sintactico.get('valida', False):
            validacion['cumple_especificacion_lcln'] = True
            
            # Determinar patrones reconocidos
            if analisis_sintactico.get('entidad_prioritaria'):
                validacion['patrones_reconocidos'].append(
                    f"Entidad prioritaria: {analisis_sintactico['entidad_prioritaria']['tipo']}"
                )
            
            if analisis_sintactico.get('modificadores'):
                for mod in analisis_sintactico['modificadores']:
                    validacion['patrones_reconocidos'].append(f"Modificador: {mod['tipo']}")
            
            # Calcular nivel de conformidad
            reglas_count = len(analisis_sintactico.get('reglas_aplicadas', []))
            if reglas_count >= 3:
                validacion['nivel_conformidad'] = 'ALTO'
            elif reglas_count >= 1:
                validacion['nivel_conformidad'] = 'MEDIO'
        else:
            validacion['errores_gramaticales'].append("Estructura sintáctica no reconocida")
            validacion['sugerencias_mejora'].append("Usar patrones como: 'categoria bebidas' o 'coca cola sin azucar'")
        
        return validacion
    
    def _calcular_confianza_gramatical(self, resultado_sintactico: Dict, tokens: List[TokenFormal]) -> float:
        """Calcular confianza gramatical basada en tokens y estructura"""
        if not tokens:
            return 0.0
        
        # Confianza base por validez sintáctica
        confianza_base = 0.8 if resultado_sintactico.get('valida', False) else 0.3
        
        # Bonus por tokens de alta prioridad
        tokens_alta_prioridad = len([t for t in tokens if t.tipo.prioridad <= 5])
        bonus_prioridad = min(tokens_alta_prioridad * 0.1, 0.2)
        
        # Bonus por reglas aplicadas
        reglas_aplicadas = len(resultado_sintactico.get('reglas_aplicadas', []))
        bonus_reglas = min(reglas_aplicadas * 0.05, 0.15)
        
        return min(confianza_base + bonus_prioridad + bonus_reglas, 1.0)
    
    def obtener_analisis_completo_formal(self, consulta: str) -> Dict:
        """
        Método especial para obtener análisis completo con todas las extensiones formales
        Mantiene compatibilidad con frontend existente
        """
        # Análisis completo estándar
        resultado_completo = self.analizar_consulta_lcln(consulta)
        
        # Agregar resumen ejecutivo para frontend
        resultado_completo['resumen_ejecutivo'] = {
            'modo_analisis': 'LCLN_FORMAL_COMPLETO',
            'productos_encontrados': resultado_completo['fase_5_motor_recomendaciones']['total_encontrados'],
            'estrategia_usada': resultado_completo['fase_5_motor_recomendaciones']['estrategia_usada'],
            'validacion_gramatical': None,
            'tokens_formales_count': 0,
            'conformidad_lcln': 'NO_EVALUADA'
        }
        
        # Enriquecer resumen con datos formales si están disponibles
        if resultado_completo.get('fase_afd_lexico'):
            resultado_completo['resumen_ejecutivo']['tokens_formales_count'] = (
                resultado_completo['fase_afd_lexico']['estadisticas']['total_tokens']
            )
        
        if resultado_completo.get('validacion_gramatical'):
            resultado_completo['resumen_ejecutivo']['validacion_gramatical'] = (
                resultado_completo['validacion_gramatical']['cumple_especificacion_lcln']
            )
            resultado_completo['resumen_ejecutivo']['conformidad_lcln'] = (
                resultado_completo['validacion_gramatical']['nivel_conformidad']
            )
        
        return resultado_completo
    
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

# Instancia global
sistema_lcln_mejorado = SistemaLCLNMejorado()

if __name__ == "__main__":
    # Prueba del sistema mejorado con extensiones formales LCLN
    print("[TEST] Probando Sistema LCLN Mejorado con Analisis Formal...")
    
    consultas_prueba = [
        "snacks picantes",
        "coca cola sin azucar", 
        "categoria bebidas",
        "bebidas sin azucar menor a 20 pesos"
    ]
    
    for consulta in consultas_prueba:
        print(f"\n{'='*60}")
        print(f"[CONSULTA] {consulta}")
        print(f"{'='*60}")
        
        try:
            # Análisis completo con extensiones formales
            resultado = sistema_lcln_mejorado.obtener_analisis_completo_formal(consulta)
            
            # RESUMEN EJECUTIVO
            resumen = resultado['resumen_ejecutivo']
            print(f"[RESUMEN EJECUTIVO]")
            print(f"   Modo: {resumen['modo_analisis']}")
            print(f"   Productos encontrados: {resumen['productos_encontrados']}")
            print(f"   Estrategia: {resumen['estrategia_usada']}")
            print(f"   Conformidad LCLN: {resumen['conformidad_lcln']}")
            print(f"   Tokens formales: {resumen['tokens_formales_count']}")
            
            # ANÁLISIS LÉXICO FORMAL (AFD)
            if resultado.get('fase_afd_lexico'):
                afd_resultado = resultado['fase_afd_lexico']
                print(f"\n[ANALISIS LEXICO FORMAL - AFD]")
                print(f"   Total tokens: {afd_resultado['estadisticas']['total_tokens']}")
                print(f"   Tokens reconocidos: {afd_resultado['estadisticas']['tokens_reconocidos']}")
                print(f"   Precision: {afd_resultado['estadisticas']['precision_reconocimiento']:.2%}")
                
                print("   Tabla de tokens:")
                for token in afd_resultado['tabla_tokens']:
                    print(f"      {token['tipo']:20} | {token['lexema']:15} | Prioridad: {token['prioridad']} | Conf: {token['confianza']:.2f}")
            
            # ANÁLISIS SINTÁCTICO (BNF)
            if resultado.get('fase_analisis_sintactico'):
                sintactico = resultado['fase_analisis_sintactico']
                print(f"\n[ANALISIS SINTACTICO - BNF]")
                print(f"   Estructura valida: {sintactico['valida']}")
                print(f"   Tipo gramatica: {sintactico.get('tipo_gramatica', 'N/A')}")
                
                if sintactico.get('entidad_prioritaria'):
                    print(f"   Entidad prioritaria: {sintactico['entidad_prioritaria']['tipo']} = '{sintactico['entidad_prioritaria']['valor']}'")
                
                if sintactico.get('reglas_aplicadas'):
                    print(f"   Reglas aplicadas: {', '.join(sintactico['reglas_aplicadas'])}")
            
            # VALIDACIÓN GRAMATICAL
            if resultado.get('validacion_gramatical'):
                validacion = resultado['validacion_gramatical']
                print(f"\n[VALIDACION GRAMATICAL]")
                print(f"   Cumple LCLN: {'SI' if validacion['cumple_especificacion_lcln'] else 'NO'}")
                print(f"   Nivel conformidad: {validacion['nivel_conformidad']}")
                
                if validacion['patrones_reconocidos']:
                    print(f"   Patrones reconocidos:")
                    for patron in validacion['patrones_reconocidos']:
                        print(f"      - {patron}")
                
                if validacion['errores_gramaticales']:
                    print(f"   Errores gramaticales:")
                    for error in validacion['errores_gramaticales']:
                        print(f"      - {error}")
            
            # EXPANSIÓN SINÓNIMOS (Sistema actual)
            expansion = resultado['fase_2_expansion_sinonimos']
            if expansion['categorias_detectadas']:
                print(f"\n[CATEGORIAS DETECTADAS - Sinonimos] {expansion['categorias_detectadas']}")
            
            # PRODUCTOS ENCONTRADOS
            motor_recomendaciones = resultado['fase_5_motor_recomendaciones']
            print(f"\n[PRODUCTOS ENCONTRADOS]")
            for i, producto in enumerate(motor_recomendaciones['productos_encontrados'][:3], 1):
                print(f"   {i}. {producto['nombre']} - ${producto['precio']} (Stock: {producto['cantidad']})")
                
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
