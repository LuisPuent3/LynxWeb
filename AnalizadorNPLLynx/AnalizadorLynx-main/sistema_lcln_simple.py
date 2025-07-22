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
from corrector_ortografico import CorrectorOrtografico

# Importar el analizador léxico completo
from analizador_lexico import AnalizadorLexicoLYNX
from adaptador_bd import AdaptadorBaseDatos

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
        self._cache_sinonimos = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)
        
        # Inicializar corrector ortográfico
        self.corrector = CorrectorOrtografico()
        
        # Inicializar analizador léxico (se hará lazy loading)
        self.analizador_lexico = None
    
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
            
            # Cargar productos con imágenes (TODOS, no solo los que tienen stock)
            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.precio, p.cantidad, p.imagen,
                       c.id_categoria, c.nombre as categoria
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
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
            
            # Cargar sinónimos para integración con AFD
            cursor.execute("""
                SELECT ps.sinonimo, ps.producto_id, p.nombre as producto_nombre
                FROM producto_sinonimos ps
                JOIN productos p ON ps.producto_id = p.id_producto
                WHERE ps.activo = 1
                ORDER BY ps.popularidad DESC
            """)
            sinonimos = cursor.fetchall()
            
            self._cache_sinonimos = {}
            for sin in sinonimos:
                sinonimo_norm = sin['sinonimo'].lower()
                if sinonimo_norm not in self._cache_sinonimos:
                    self._cache_sinonimos[sinonimo_norm] = []
                self._cache_sinonimos[sinonimo_norm].append({
                    'producto_id': sin['producto_id'],
                    'producto_nombre': sin['producto_nombre']
                })
            
            self._cache_timestamp = datetime.now()
            print(f"✅ Cache actualizado: {len(self._cache_productos)} productos, {len(self._cache_categorias)} categorías, {len(self._cache_sinonimos)} sinónimos")
            
            # Resetear analizador léxico para que use nuevos datos
            self.analizador_lexico = None
            
        finally:
            cursor.close()
            conn.close()
    
    def _inicializar_analizador_lexico(self):
        """Inicializar el analizador léxico con los datos actuales del cache"""
        if self.analizador_lexico is None:
            try:
                print("🧠 Inicializando Analizador Léxico (AFD) con datos actuales...")
                
                # Preparar datos para el AFD
                productos_completos = []
                productos_multi = []
                
                # Agregar productos desde cache
                for nombre, datos in self._cache_productos.items():
                    palabras = nombre.split()
                    if len(palabras) >= 3:
                        productos_completos.append(nombre)
                    elif len(palabras) >= 2:
                        productos_multi.append(nombre)
                
                # Agregar sinónimos desde cache
                for sinonimo in self._cache_sinonimos.keys():
                    palabras = sinonimo.split()
                    if len(palabras) >= 3:
                        productos_completos.append(sinonimo)
                    elif len(palabras) >= 2:
                        productos_multi.append(sinonimo)
                
                # Crear adaptador compatible
                class AdaptadorSimple:
                    def __init__(self, cache_productos, cache_categorias):
                        self.productos_completos = productos_completos
                        self.productos_multi = productos_multi
                        self.categorias = list(cache_categorias.keys())
                        self.unidades = ['pesos', 'peso', 'ml', 'g', 'kg', 'l']
                        self.cache_productos = cache_productos
                    
                    def obtener_estadisticas(self):
                        return {'productos_total': len(self.cache_productos)}
                
                # Configuración simplificada
                class ConfiguracionSimple:
                    def __init__(self, cache_productos, cache_categorias):
                        self.bd_escalable = AdaptadorSimple(cache_productos, cache_categorias)
                    
                    def obtener_estadisticas(self):
                        return self.bd_escalable.obtener_estadisticas()
                
                # Inicializar AFD
                config = ConfiguracionSimple(self._cache_productos, self._cache_categorias)
                self.analizador_lexico = AnalizadorLexicoLYNX(config)
                
                print(f"✅ AFD inicializado: {len(productos_completos)} productos completos, {len(productos_multi)} productos multi-palabra")
                
            except Exception as e:
                print(f"⚠️ Error inicializando AFD: {e}")
                self.analizador_lexico = None
    
    def buscar_productos_inteligente(self, consulta: str, limit: int = 20) -> Dict:
        """
        Búsqueda inteligente que se adapta dinámicamente a la BD
        """        # Actualizar cache si es necesario
        self._actualizar_cache_dinamico()
        consulta_original = consulta
          # Aplicar correcciones ortográficas críticas
        resultado_correcciones = self.corrector.corregir_consulta(consulta)
        consulta_corregida = resultado_correcciones.get('corrected_query', consulta)
        
        # Mapear botana → snacks para búsquedas (preservar estado de correcciones)
        if 'botana' in consulta_corregida.lower():
            consulta_corregida = consulta_corregida.replace('botana', 'snacks').replace('botanas', 'snacks')
            # Preservar el estado original de correcciones aplicadas
            if not resultado_correcciones.get('applied', False):
                resultado_correcciones['applied'] = True
        
        consulta = consulta_corregida.lower().strip()
        
        import time
        inicio = time.time()
        
        # Análisis de la consulta usando el analizador léxico avanzado
        analisis = self._analizar_consulta_con_afd(consulta)
          # Búsqueda con múltiples estrategias
        productos = self._ejecutar_busqueda_estrategias(analisis, limit)
        
        tiempo_proceso = (time.time() - inicio) * 1000
        
        # Generar mensaje personalizado según la estrategia
        mensaje_usuario = self._generar_mensaje_usuario(analisis, productos)
        
        return {
            'success': True,
            'processing_time_ms': tiempo_proceso,
            'original_query': consulta_original,
            'corrections': {
                'applied': resultado_correcciones.get('applied', False),
                'original_query': consulta_original,
                'corrected_query': resultado_correcciones.get('corrected_query', consulta_original),
                'corrections_details': resultado_correcciones.get('changes', [])
            },
            'interpretation': {
                'termino_busqueda': analisis['termino_busqueda'],
                'categoria': analisis.get('categoria', ''),
                'precio_max': analisis.get('precio_max'),
                'tipo': 'busqueda_dinamica_lcln',
                'estrategia_usada': analisis['estrategia_usada']
            },
            'recommendations': productos,
            'products_found': len(productos),
            'user_message': mensaje_usuario,
            'metadata': {
                'database': 'mysql_dynamic',
                'cache_timestamp': self._cache_timestamp.isoformat(),
                'imagenes_incluidas': True,
                'filtro_precio_aplicado': analisis.get('precio_max') is not None,
                'producto_original_rechazado': analisis.get('tipo_busqueda') == 'producto_con_filtro_precio_no_cumplido'
            }
        }
    
    def _generar_mensaje_usuario(self, analisis: Dict, productos: List[Dict]) -> str:
        """Generar mensaje personalizado según el análisis y resultados"""
        estrategia = analisis['estrategia_usada']
        precio_max = analisis.get('precio_max')
        atributos = analisis.get('atributos', [])
        
        if estrategia == 'sinonimo_con_filtro_precio_rechazado':
            producto_original = analisis['producto_encontrado']
            return f"'{producto_original['nombre']}' cuesta ${producto_original['precio']:.0f} (más de ${precio_max:.0f}). Te mostramos {len(productos)} alternativas más baratas"
            
        elif estrategia == 'producto_con_filtro_precio_rechazado':
            producto_original = analisis['producto_encontrado']
            return f"'{producto_original['nombre']}' cuesta ${producto_original['precio']:.0f} (más de ${precio_max:.0f}). Te mostramos {len(productos)} alternativas más baratas"
            
        elif estrategia.startswith('afd_'):
            if 'atributos' in estrategia:
                attrs_str = ', '.join(atributos) if atributos else 'atributos específicos'
                precio_str = f" ≤ ${precio_max:.0f}" if precio_max else ""
                return f"Encontrados {len(productos)} productos con {attrs_str}{precio_str} (AFD)"
            elif 'producto' in estrategia:
                precio_str = f" con precio ≤ ${precio_max:.0f}" if precio_max else ""
                return f"Producto encontrado por AFD{precio_str}"
            elif 'categoria' in estrategia:
                categoria = analisis.get('categoria', {}).get('nombre', 'categoría')
                precio_str = f" ≤ ${precio_max:.0f}" if precio_max else ""
                attrs_str = f" con {', '.join(atributos)}" if atributos else ""
                return f"Encontrados {len(productos)} productos de {categoria}{attrs_str}{precio_str} (AFD)"
            
        elif estrategia == 'sinonimo_directo' and precio_max:
            return f"Encontrado 1 producto por sinónimo con precio ≤ ${precio_max:.0f}"
            
        elif estrategia == 'sinonimo_directo':
            return f"Encontrado 1 producto por sinónimo"
            
        elif estrategia == 'filtro_precio':
            return f"Encontrados {len(productos)} productos ≤ ${precio_max:.0f}"
            
        elif estrategia == 'categoria_con_filtros' and precio_max:
            categoria = analisis.get('categoria', {}).get('nombre', 'categoría')
            return f"Encontrados {len(productos)} productos de {categoria} ≤ ${precio_max:.0f}"
            
        else:
            return f"Encontrados {len(productos)} productos dinámicamente"
    
    def _analizar_consulta_con_afd(self, consulta: str) -> Dict:
        """Análisis avanzado usando AFD con fallback inteligente"""
        
        # Intentar análisis AFD PRIMERO (es más potente)
        try:
            self._inicializar_analizador_lexico()
            
            if self.analizador_lexico:
                # Usar el método correcto del AFD
                resultado_afd = self.analizador_lexico.analizar_con_correccion(consulta)
                
                if resultado_afd and resultado_afd.get('success', False):
                    tokens = resultado_afd.get('tokens', [])
                    
                    print(f"🧠 AFD activado - {len(tokens)} tokens detectados")
                    
                    # Procesar tokens del AFD para extraer información
                    producto_detectado = None
                    categoria_detectada = None
                    atributos_detectados = []
                    precio_max = self._extraer_filtro_precio(consulta)  # Usar nuestro extractor de precio
                    
                    for token in tokens:
                        tipo_token = token.get('tipo', '')
                        valor_token = token.get('valor', '').lower()
                        
                        # Productos detectados por AFD
                        if tipo_token in ['PRODUCTO_COMPLETO', 'PRODUCTO_MULTIPALABRA', 'PRODUCTO_INDIVIDUAL']:
                            # Buscar en nuestro cache
                            if valor_token in self._cache_productos:
                                producto_detectado = self._cache_productos[valor_token]
                            else:
                                # Buscar en sinónimos
                                for sin, prods in self._cache_sinonimos.items():
                                    if sin == valor_token or valor_token in sin:
                                        prod_id = prods[0]['producto_id']
                                        for nombre, datos in self._cache_productos.items():
                                            if datos['id'] == prod_id:
                                                producto_detectado = datos
                                                break
                        
                        # Categorías detectadas por AFD
                        elif tipo_token == 'CATEGORIA':
                            if valor_token in self._cache_categorias:
                                categoria_detectada = self._cache_categorias[valor_token]
                        
                        # Atributos detectados por AFD
                        elif tipo_token in ['ATRIBUTO', 'SABOR', 'TEXTURA', 'TEMPERATURA']:
                            atributos_detectados.append(valor_token)
                    
                    # Si el AFD encontró un producto específico
                    if producto_detectado:
                        print(f"🎯 AFD encontró producto: {producto_detectado['nombre']}")
                        
                        if precio_max and producto_detectado['precio'] > precio_max:
                            return {
                                'tipo_busqueda': 'producto_con_filtro_precio_no_cumplido',
                                'producto_encontrado': producto_detectado,
                                'termino_busqueda': consulta,
                                'categoria': None,
                                'precio_max': precio_max,
                                'atributos': atributos_detectados,
                                'estrategia_usada': 'afd_producto_filtro_precio_rechazado'
                            }
                        
                        return {
                            'tipo_busqueda': 'producto_especifico',
                            'producto_encontrado': producto_detectado,
                            'termino_busqueda': consulta,
                            'categoria': categoria_detectada,
                            'precio_max': precio_max,
                            'atributos': atributos_detectados,
                            'estrategia_usada': 'afd_producto_directo'
                        }
                    
                    # Si el AFD encontró una categoría
                    elif categoria_detectada:
                        print(f"🎯 AFD encontró categoría: {categoria_detectada['nombre']}")
                        return {
                            'tipo_busqueda': 'categoria',
                            'categoria': categoria_detectada,
                            'termino_busqueda': consulta,
                            'precio_max': precio_max,
                            'atributos': atributos_detectados,
                            'estrategia_usada': 'afd_categoria_con_atributos'
                        }
                    
                    # Si el AFD encontró atributos complejos
                    elif atributos_detectados:
                        print(f"🎯 AFD encontró atributos: {', '.join(atributos_detectados)}")
                        return {
                            'tipo_busqueda': 'atributos',
                            'categoria': None,
                            'termino_busqueda': consulta,
                            'precio_max': precio_max,
                            'atributos': atributos_detectados,
                            'estrategia_usada': 'afd_busqueda_por_atributos'
                        }
                    
        except Exception as e:
            print(f"⚠️ Error en AFD (usando fallback): {e}")
        
        # FALLBACK: Si el AFD falla o no encuentra nada, usar nuestro análisis
        print("🔧 Usando análisis simplificado como fallback")
        return self._analizar_consulta_fallback(consulta)
    
    def _analizar_consulta_fallback(self, consulta: str) -> Dict:
        """Análisis inteligente mejorado como sistema principal"""
        
        # Detectar filtros de precio PRIMERO
        precio_max = self._extraer_filtro_precio(consulta)
        
        # PASO 1: Verificar sinónimos directamente (MÁXIMA PRIORIDAD)
        for sinonimo, productos_sinonimo in self._cache_sinonimos.items():
            if sinonimo in consulta:
                # Tomar el primer producto asociado al sinónimo
                primer_producto = productos_sinonimo[0]
                producto_id = primer_producto['producto_id']
                
                # Encontrar el producto completo por ID
                for nombre_prod, datos_prod in self._cache_productos.items():
                    if datos_prod['id'] == producto_id:
                        print(f"✅ Producto encontrado por sinónimo: '{sinonimo}' → {datos_prod['nombre']}")
                        
                        # Si hay filtro de precio, verificar si el producto lo cumple
                        if precio_max and datos_prod['precio'] > precio_max:
                            # Producto encontrado pero no cumple filtro de precio
                            return {
                                'tipo_busqueda': 'producto_con_filtro_precio_no_cumplido',
                                'producto_encontrado': datos_prod,
                                'termino_busqueda': sinonimo,
                                'categoria': None,
                                'precio_max': precio_max,
                                'precio_producto': datos_prod['precio'],
                                'estrategia_usada': 'sinonimo_con_filtro_precio_rechazado'
                            }
                        
                        return {
                            'tipo_busqueda': 'producto_especifico',
                            'producto_encontrado': datos_prod,
                            'termino_busqueda': sinonimo,
                            'categoria': None,
                            'precio_max': precio_max,
                            'estrategia_usada': 'sinonimo_directo'
                        }
        
        # PASO 2: Detectar producto específico por nombre parcial
        productos_encontrados = []
        for nombre_producto, datos_producto in self._cache_productos.items():
            # Buscar coincidencias parciales más inteligentes
            palabras_consulta = consulta.split()
            palabras_producto = nombre_producto.split()
            
            coincidencias = 0
            for palabra_consulta in palabras_consulta:
                if len(palabra_consulta) > 2:  # Ignorar palabras muy cortas
                    for palabra_producto in palabras_producto:
                        if palabra_consulta in palabra_producto.lower():
                            coincidencias += 1
                            break
            
            # Si hay al menos 1 coincidencia fuerte, considerar el producto
            if coincidencias > 0:
                productos_encontrados.append((datos_producto, coincidencias))
        
        # Si encontramos productos por nombre, tomar el de mejor coincidencia
        if productos_encontrados:
            # Ordenar por coincidencias y tomar el mejor
            productos_encontrados.sort(key=lambda x: x[1], reverse=True)
            mejor_producto = productos_encontrados[0][0]
            
            print(f"✅ Producto encontrado por búsqueda parcial: {mejor_producto['nombre']}")
            
            # Verificar filtro de precio si existe
            if precio_max and mejor_producto['precio'] > precio_max:
                return {
                    'tipo_busqueda': 'producto_con_filtro_precio_no_cumplido',
                    'producto_encontrado': mejor_producto,
                    'termino_busqueda': consulta,
                    'categoria': None,
                    'precio_max': precio_max,
                    'precio_producto': mejor_producto['precio'],
                    'estrategia_usada': 'producto_con_filtro_precio_rechazado'
                }
            
            return {
                'tipo_busqueda': 'producto_especifico',
                'producto_encontrado': mejor_producto,
                'termino_busqueda': consulta,
                'categoria': None,
                'precio_max': precio_max,
                'estrategia_usada': 'producto_especifico'
            }
        
        # PASO 3: Detectar categoría
        for nombre_categoria, datos_categoria in self._cache_categorias.items():
            if nombre_categoria in consulta:
                print(f"✅ Categoría detectada: {datos_categoria['nombre']}")
                return {
                    'tipo_busqueda': 'categoria',
                    'categoria': datos_categoria,
                    'termino_busqueda': '',
                    'precio_max': precio_max,
                    'estrategia_usada': 'categoria_con_filtros'
                }
        
        # PASO 4: Detectar solo filtros de precio
        if precio_max:
            print(f"✅ Solo filtro de precio detectado: ≤ ${precio_max}")
            return {
                'tipo_busqueda': 'precio',
                'categoria': None,
                'termino_busqueda': '',
                'precio_max': precio_max,
                'estrategia_usada': 'filtro_precio'
            }
        
        # PASO 5: ANÁLISIS INTELIGENTE DE ATRIBUTOS (mejora para casos complejos)
        # Detectar patrones complejos antes de la búsqueda genérica
        atributos_detectados = []
        
        if any(palabra in consulta for palabra in ['picante', 'hot', 'fuego', 'spicy']):
            atributos_detectados.append('picante')
        if any(palabra in consulta for palabra in ['dulce', 'dulces', 'sweet', 'chocolate']):
            atributos_detectados.append('dulce')
        if any(palabra in consulta for palabra in ['popular', 'populares', 'famoso', 'conocido']):
            atributos_detectados.append('popular')
        if any(palabra in consulta for palabra in ['fresco', 'frescas', 'frescos']):
            atributos_detectados.append('fresco')
        if any(palabra in consulta for palabra in ['temporada']):
            atributos_detectados.append('temporada')
        if any(palabra in consulta for palabra in ['sin']):
            atributos_detectados.append('sin')
            
        # Si detectamos atributos, hacer búsqueda por atributos
        if atributos_detectados:
            print(f"✅ Atributos detectados: {', '.join(atributos_detectados)}")
            return {
                'tipo_busqueda': 'atributos',
                'categoria': None,
                'termino_busqueda': consulta,
                'precio_max': precio_max,
                'atributos': atributos_detectados,
                'estrategia_usada': 'busqueda_por_atributos_inteligente'
            }
        
        # PASO 6: Búsqueda genérica por palabras clave
        print(f"✅ Búsqueda genérica para: '{consulta}'")
        return {
            'tipo_busqueda': 'generica',
            'categoria': None,
            'termino_busqueda': consulta,
            'precio_max': None,
            'estrategia_usada': 'busqueda_generica'
        }
    
    def _extraer_filtro_precio(self, consulta: str) -> Optional[float]:
        """Extraer filtros de precio de la consulta usando múltiples estrategias"""
        import re
        
        # Estrategia 1: Operadores explícitos con números
        # "menor a 15", "menos de 20", "máximo 25", etc.
        patrones_operadores = [
            r'menor\s+(?:a|que)\s+(\d+(?:\.\d+)?)',
            r'menos\s+(?:de|que)\s+(\d+(?:\.\d+)?)',
            r'(?:máximo|max|tope)\s+(\d+(?:\.\d+)?)',
            r'(?:hasta|por)\s+(\d+(?:\.\d+)?)',
            r'(?:no\s+)?(?:más|mas)\s+(?:de|que)\s+(\d+(?:\.\d+)?)'
        ]
        
        for patron in patrones_operadores:
            match = re.search(patron, consulta, re.IGNORECASE)
            if match:
                precio = float(match.group(1))
                print(f"🔍 Filtro precio detectado (operador): ≤ ${precio}")
                return precio
        
        # Estrategia 2: Números seguidos de "pesos"
        match = re.search(r'(\d+(?:\.\d+)?)\s*pesos?', consulta, re.IGNORECASE)
        if match:
            precio = float(match.group(1))
            # Si hay palabras como "menor", "menos", "hasta" antes del número
            if any(palabra in consulta for palabra in ['menor', 'menos', 'hasta', 'máximo', 'max', 'barato', 'economico']):
                print(f"🔍 Filtro precio detectado (pesos): ≤ ${precio}")
                return precio
        
        # Estrategia 3: Adjetivos de precio
        if any(palabra in consulta for palabra in ['barato', 'baratos', 'barata', 'baratas', 'economico', 'economica']):
            print(f"🔍 Filtro precio detectado (adjetivo): ≤ $20.0")
            return 20.0
        elif any(palabra in consulta for palabra in ['caro', 'caros', 'cara', 'caras', 'premium']):
            print(f"🔍 Filtro precio detectado (caro): ≥ $50.0")
            return 100.0  # Productos caros hasta $100
        
        # Estrategia 4: Contexto de números sueltos con palabras clave
        numeros = re.findall(r'\d+(?:\.\d+)?', consulta)
        if numeros and any(palabra in consulta for palabra in ['menor', 'menos', 'bajo', 'hasta', 'máximo', 'max']):
            precio = float(numeros[-1])  # Tomar el último número
            print(f"🔍 Filtro precio detectado (contexto): ≤ ${precio}")
            return precio
        
        return None
    
    def _ejecutar_busqueda_estrategias(self, analisis: Dict, limit: int) -> List[Dict]:
        """Ejecutar búsqueda usando diferentes estrategias"""
        
        if analisis['tipo_busqueda'] == 'producto_especifico':
            return [self._formatear_producto(analisis['producto_encontrado'])]
        
        elif analisis['tipo_busqueda'] == 'producto_con_filtro_precio_no_cumplido':
            # El producto específico no cumple el filtro de precio
            # Buscar productos alternativos que sí lo cumplan
            producto_original = analisis['producto_encontrado']
            precio_max = analisis['precio_max']
            
            # Buscar en la misma categoría productos que cumplan el filtro
            productos_alternativos = []
            for producto in self._cache_productos.values():
                if (producto['categoria_id'] == producto_original['categoria_id'] and 
                    producto['precio'] <= precio_max):
                    productos_alternativos.append(self._formatear_producto(producto))
            
            # Si no hay productos en la misma categoría, buscar en todas las categorías
            if not productos_alternativos:
                productos_alternativos = self._buscar_por_precio(precio_max, limit)
            
            # Agregar el producto original al final con una nota especial
            if productos_alternativos:
                productos_alternativos[0]['match_reasons'].append(f'alternativa_a_{producto_original["nombre"]}_${producto_original["precio"]}')
            
            return productos_alternativos[:limit]
        
        elif analisis['tipo_busqueda'] == 'categoria':
            return self._buscar_por_categoria(
                analisis['categoria']['nombre'],
                analisis.get('precio_max'),
                limit
            )
        
        elif analisis['tipo_busqueda'] == 'precio':
            return self._buscar_por_precio(analisis['precio_max'], limit)
        
        elif analisis['tipo_busqueda'] == 'atributos':
            # Nueva estrategia para búsqueda por atributos (AFD)
            return self._buscar_por_atributos(
                analisis.get('atributos', []),
                analisis.get('precio_max'),
                limit
            )
        
        else:
            # Búsqueda genérica - buscar en nombres de productos
            return self._buscar_generica(analisis['termino_busqueda'], limit)
    
    def _buscar_por_atributos(self, atributos: List[str], precio_max: Optional[float], limit: int) -> List[Dict]:
        """Buscar productos por atributos detectados - mejorado para negaciones"""
        productos = []
        
        print(f"🔍 Buscando por atributos: {', '.join(atributos)}")
        
        # Detectar si hay negación
        tiene_negacion = 'sin' in atributos
        atributos_sin_negacion = [attr for attr in atributos if attr != 'sin']
        
        for producto in self._cache_productos.values():
            nombre_lower = producto['nombre'].lower()
            categoria_lower = producto['categoria'].lower()
            incluir_producto = True
            
            for atributo in atributos_sin_negacion:
                atributo_lower = atributo.lower()
                tiene_atributo = False
                
                # Detectar si el producto tiene el atributo
                if atributo_lower in ['picante', 'hot', 'fuego', 'spicy']:
                    tiene_atributo = any(palabra in nombre_lower for palabra in 
                        ['picante', 'fuego', 'hot', 'dinamita', 'incognita', 'flamin', 'chile', 'chili'])
                elif atributo_lower in ['dulce', 'dulces', 'sweet']:
                    tiene_atributo = (categoria_lower == 'dulces' or
                        any(palabra in nombre_lower for palabra in 
                            ['dulce', 'chocolate', 'azucar', 'miel', 'caramelo', 'galleta']))
                elif atributo_lower in ['popular', 'populares']:
                    tiene_atributo = any(palabra in nombre_lower for palabra in 
                        ['coca', 'pepsi', 'doritos', 'sabritas', 'boing', 'chocolate', 'galletas'])
                elif atributo_lower in ['fresco', 'frescas', 'frescos']:
                    tiene_atributo = (categoria_lower in ['frutas', 'verduras'] or
                        any(palabra in nombre_lower for palabra in ['fresco', 'natural']))
                elif atributo_lower in ['temporada']:
                    tiene_atributo = categoria_lower == 'frutas'
                
                # Lógica de inclusión/exclusión basada en negación
                if tiene_negacion:
                    # Si hay negación y el producto TIENE el atributo, excluirlo
                    if tiene_atributo:
                        incluir_producto = False
                        break
                else:
                    # Si NO hay negación y el producto NO TIENE el atributo, excluirlo
                    if not tiene_atributo:
                        incluir_producto = False
                        break
            
            # Si el producto pasa los filtros de atributos, verificar precio
            if incluir_producto:
                if precio_max and producto['precio'] > precio_max:
                    continue
                productos.append(self._formatear_producto(producto))
        
        # Si no encuentra productos específicos, hacer búsqueda más amplia
        if not productos and not tiene_negacion:
            print("🔄 Expandiendo búsqueda por palabras clave...")
            for atributo in atributos_sin_negacion:
                for producto in self._cache_productos.values():
                    if atributo.lower() in producto['nombre'].lower():
                        if precio_max and producto['precio'] > precio_max:
                            continue
                        if producto not in [p['id'] for p in productos]:  # Evitar duplicados
                            productos.append(self._formatear_producto(producto))
        
        # Ordenar por precio y limitar
        productos.sort(key=lambda x: x['precio'])
        return productos[:limit]
    
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
