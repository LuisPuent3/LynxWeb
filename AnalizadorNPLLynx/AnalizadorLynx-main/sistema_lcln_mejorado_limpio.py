#!/usr/bin/env python3
"""
Sistema LCLN Mejorado con Integración Completa de Sinónimos
Adaptado para Railway con MySQL dinámico
"""
import mysql.connector
import os
from pathlib import Path
import json
from typing import List, Dict, Optional
import difflib
from datetime import datetime, timedelta

class SistemaLCLNMejorado:
    def __init__(self):
        # Configuración MySQL dinámica para Railway
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

        # Cache dinámico de la BD
        self._cache_productos = {}
        self._cache_categorias = {}
        self._cache_sinonimos = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)

        # Correcciones ortográficas específicas mejoradas - SEGÚN DOCUMENTACIÓN TÉCNICA LCLN
        self.correcciones_manuales = {
            # Productos comunes mal escritos
            'chetoos': 'cheetos',
            'chetos': 'cheetos',
            'chettos': 'cheetos',
            'koka': 'coca-cola',
            'coka': 'coca-cola',
            'kola': 'cola',
            'coca': 'coca-cola',
            'votana': 'botana',  # CRÍTICO: votana → botana
            'botana': 'botana',   # Mantener botana como botana
            'botanas': 'botanas', # Mantener plurales
            # Errores de escritura comunes
            'asucar': 'azucar',
            'azucar': 'azúcar',
            'picabte': 'picante', # CRÍTICO: picabte → picante
            'pikante': 'picante',
            'picbte': 'picante',
            'barata': 'barata',   # NO cambiar barata por karate!
            'varata': 'barata',
            'brata': 'barata',
            'vebida': 'bebida',
            'vebidas': 'bebidas',
            'mansana': 'manzana'
        }

        # Sinónimos básicos integrados (fallback si no hay SQLite)
        self.sinonimos_basicos = {
            'sin azucar': [{'categoria': 'sin azucar', 'tipo': 'atributo', 'confianza': 0.9}],
            'sin azúcar': [{'categoria': 'sin azucar', 'tipo': 'atributo', 'confianza': 0.9}],
            'light': [{'categoria': 'sin azucar', 'tipo': 'atributo', 'confianza': 0.9}],
            'zero': [{'categoria': 'sin azucar', 'tipo': 'atributo', 'confianza': 0.9}],
            'diet': [{'categoria': 'sin azucar', 'tipo': 'atributo', 'confianza': 0.9}],
            'bebidas sin azucar': [{'categoria': 'bebidas', 'tipo': 'categoria', 'confianza': 0.9}, {'categoria': 'sin azucar', 'tipo': 'atributo', 'confianza': 0.9}],
            'bebidas sin azúcar': [{'categoria': 'bebidas', 'tipo': 'categoria', 'confianza': 0.9}, {'categoria': 'sin azucar', 'tipo': 'atributo', 'confianza': 0.9}],
            'bebidas': [{'categoria': 'bebidas', 'tipo': 'categoria', 'confianza': 0.9}],
            'bebida': [{'categoria': 'bebidas', 'tipo': 'categoria', 'confianza': 0.9}],
            'botana': [{'categoria': 'snacks', 'tipo': 'categoria', 'confianza': 0.9}],
            'botanas': [{'categoria': 'snacks', 'tipo': 'categoria', 'confianza': 0.9}],
            'chetos': [{'categoria': 'cheetos', 'tipo': 'producto', 'confianza': 0.9}],
            'chettos': [{'categoria': 'cheetos', 'tipo': 'producto', 'confianza': 0.9}],
            'dulces': [{'categoria': 'golosinas', 'tipo': 'categoria', 'confianza': 0.9}],
            'dulce': [{'categoria': 'golosinas', 'tipo': 'categoria', 'confianza': 0.9}],
            'picante': [{'categoria': 'picante', 'tipo': 'atributo', 'confianza': 0.9}]
        }

    def _necesita_actualizar_cache(self) -> bool:
        """Verificar si el cache necesita actualizarse"""
        if not self._cache_timestamp:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_duration

    def _actualizar_cache_dinamico(self):
        """Actualizar cache con datos actuales de MySQL"""
        if not self._necesita_actualizar_cache():
            return

        print("Actualizando cache dinamico desde MySQL...")

        # Actualizar productos desde MySQL
        self._actualizar_cache_productos()

        # Usar sinónimos básicos integrados
        self._cache_sinonimos = self.sinonimos_basicos.copy()

        self._cache_timestamp = datetime.now()
        print(f"Cache actualizado: {len(self._cache_productos)} productos, {len(self._cache_categorias)} categorias, {len(self._cache_sinonimos)} sinonimos")

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
            'fase_5_motor_recomendaciones': None
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

        return resultado_analisis

    def _fase_correccion_ortografica(self, consulta: str) -> Dict:
        """Fase 1: Corrección ortográfica mejorada"""
        palabras = consulta.split()
        correcciones = []
        texto_corregido_palabras = []

        for palabra in palabras:
            if palabra in self.correcciones_manuales:
                correcciones.append({
                    'aplicada': True,
                    'palabra_original': palabra,
                    'palabra_corregida': self.correcciones_manuales[palabra],
                    'confianza': 0.95,
                    'fuente': 'correccion_manual'
                })
                texto_corregido_palabras.append(self.correcciones_manuales[palabra])
            else:
                texto_corregido_palabras.append(palabra)

        return {
            'correcciones_aplicadas': len(correcciones) > 0,
            'correcciones': correcciones,
            'texto_corregido': ' '.join(texto_corregido_palabras)
        }

    def _fase_expansion_sinonimos(self, consulta: str) -> Dict:
        """Fase 2: Expansión con sinónimos"""
        print(f"[DEBUG] Expansión sinónimos para: '{consulta}'")
        palabras = consulta.split()
        expansion_info = {
            'terminos_expandidos': [],
            'categorias_detectadas': set(),
            'productos_detectados': set(),
            'atributos_detectados': set()
        }

        # Buscar sinónimos para palabras individuales y frases completas
        terminos_busqueda = []
        terminos_busqueda.extend(palabras)
        terminos_busqueda.append(consulta)

        # Buscar combinaciones de 2 palabras
        for i in range(len(palabras) - 1):
            combinacion = ' '.join(palabras[i:i+2])
            terminos_busqueda.append(combinacion)

        print(f"[DEBUG] Términos a buscar: {terminos_busqueda}")

        for termino in terminos_busqueda:
            termino_key = termino.lower()
            if termino_key in self._cache_sinonimos:
                print(f"[DEBUG] Encontrado sinónimo para '{termino_key}'")
                sinonimos_del_termino = self._cache_sinonimos[termino_key]
                
                # Si el sinónimo es una lista (multiple sinónimos para una frase)
                if isinstance(sinonimos_del_termino, list):
                    for sinonimo in sinonimos_del_termino:
                        if sinonimo['confianza'] >= 0.7:
                            print(f"[DEBUG] Agregando sinónimo: {sinonimo}")
                            if sinonimo['tipo'] == 'categoria':
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

        resultado = {
            'terminos_expandidos': expansion_info['terminos_expandidos'],
            'categorias_detectadas': list(expansion_info['categorias_detectadas']),
            'productos_detectados': list(expansion_info['productos_detectados']),
            'atributos_detectados': list(expansion_info['atributos_detectados'])
        }
        
        print(f"[DEBUG] Resultado expansión: {resultado}")
        return resultado

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
            interpretacion['productos_especificos'] = list(expansion['productos_detectados'])

        # Detectar categorías
        elif expansion['categorias_detectadas']:
            interpretacion['tipo_busqueda'] = 'categoria'
            interpretacion['categoria_principal'] = list(expansion['categorias_detectadas'])[0]

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
            interpretacion['atributos'].extend(list(expansion['atributos_detectados']))

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

        # Estrategia 4: Fallback
        if not productos_encontrados:
            productos_encontrados = self._buscar_fallback(interpretacion['filtros_precio'])
            estrategia_usada = 'fallback_precio'

        # Formatear productos para frontend
        productos_formateados = []
        for producto in productos_encontrados[:20]:
            productos_formateados.append({
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio': float(producto['precio']),
                'imagen': producto['imagen'],
                'cantidad': producto['cantidad'],
                'categoria_nombre': producto['categoria_nombre'],
                'similarity_score': 0.8
            })

        return {
            'productos_encontrados': productos_formateados,
            'total_encontrados': len(productos_formateados),
            'estrategia_usada': estrategia_usada,
            'tiene_recomendaciones': len(productos_formateados) > 0
        }

    def _buscar_productos_especificos(self, productos_especificos: List[str], filtros_precio: Dict, atributos: List[str]) -> List[Dict]:
        """Buscar productos específicos detectados por sinónimos"""
        productos = []

        for producto_nombre in productos_especificos:
            for nombre_producto, data in self._cache_productos.items():
                # Normalizar nombres para mejor coincidencia
                producto_normalizado = producto_nombre.lower().replace('-', ' ').replace('  ', ' ').strip()
                nombre_normalizado = data['nombre'].lower().replace('-', ' ').replace('  ', ' ').strip()

                # Buscar coincidencia
                if (producto_normalizado in nombre_normalizado or 
                    any(palabra in nombre_normalizado for palabra in producto_normalizado.split())):
                    
                    # Aplicar filtros de precio
                    precio = data['precio']
                    if filtros_precio.get('min') and precio < filtros_precio['min']:
                        continue
                    if filtros_precio.get('max') and precio > filtros_precio['max']:
                        continue

                    # Aplicar filtros de atributos
                    if atributos and not self._producto_cumple_atributos(data, atributos):
                        continue

                    productos.append(data)

        return sorted(productos, key=lambda x: x['precio'])

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

            # Aplicar filtros de atributos
            if atributos and not self._producto_cumple_atributos(data, atributos):
                continue

            productos.append(data)

        return sorted(productos, key=lambda x: x['precio'])

    def _buscar_por_atributos(self, atributos: List[str], filtros_precio: Dict) -> List[Dict]:
        """Buscar productos por atributos específicos"""
        productos = []

        for nombre_producto, data in self._cache_productos.items():
            if self._producto_cumple_atributos(data, atributos):
                # Aplicar filtros de precio
                precio = data['precio']
                if filtros_precio.get('min') and precio < filtros_precio['min']:
                    continue
                if filtros_precio.get('max') and precio > filtros_precio['max']:
                    continue

                productos.append(data)

        return sorted(productos, key=lambda x: x['precio'])

    def _producto_cumple_atributos(self, producto: Dict, atributos: List[str]) -> bool:
        """Verificar si un producto cumple con los atributos especificados"""
        nombre_lower = producto['nombre'].lower()
        categoria_lower = producto['categoria_nombre'].lower()

        for atributo in atributos:
            if atributo == 'picante':
                if any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas']):
                    return True
            elif atributo == 'dulce':
                es_picante = any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas'])
                if not es_picante and (categoria_lower in ['golosinas', 'snacks']):
                    return True
            elif atributo == 'sin azucar':
                # LÓGICA CLAVE: Solo productos que explícitamente son sin azúcar
                sin_azucar_keywords = ['sin azúcar', 'light', 'zero', 'diet']
                
                # NUEVO: El agua es naturalmente sin azúcar
                es_agua = 'agua' in nombre_lower
                
                cumple_sin_azucar = (any(keyword in nombre_lower for keyword in sin_azucar_keywords) or es_agua)
                
                if cumple_sin_azucar:
                    if es_agua:
                        print(f"[DEBUG] Producto '{producto['nombre']}' SÍ cumple 'sin azucar' (es agua)")
                    else:
                        print(f"[DEBUG] Producto '{producto['nombre']}' SÍ cumple 'sin azucar' (keywords)")
                    return True
                else:
                    print(f"[DEBUG] Producto '{producto['nombre']}' NO cumple 'sin azucar' - keywords buscadas: {sin_azucar_keywords}, es_agua: {es_agua}")
            elif atributo == 'barato':
                if producto['precio'] <= 15.0:
                    return True
            elif atributo == 'caro':
                if producto['precio'] >= 25.0:
                    return True

        return False

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

# Instancia global
sistema_lcln_mejorado = SistemaLCLNMejorado()
