#!/usr/bin/env python3
"""
Sistema LCLN Mejorado con Integración Completa de Sinónimos
Corrige los problemas identificados:
1. Integración correcta con sinónimos
2. Mejor detección de atributos como "picante"
3. Formateo correcto para frontend (imagen, stock)
"""

import mysql.connector
import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Optional
import difflib
from datetime import datetime, timedelta

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
    
    def _necesita_actualizar_cache(self) -> bool:
        """Verificar si el cache necesita actualizarse"""
        if not self._cache_timestamp:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_duration
    
    def _actualizar_cache_dinamico(self):
        """Actualizar cache con datos actuales de MySQL y SQLite"""
        if not self._necesita_actualizar_cache():
            return
            
        print("Actualizando cache dinamico desde MySQL y SQLite...")
        
        # Actualizar productos desde MySQL
        self._actualizar_cache_productos()
        
        # Actualizar sinónimos desde SQLite  
        self._actualizar_cache_sinonimos()
        
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
                if cat_key not in self._cache_categorias:                    self._cache_categorias[cat_key] = {
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
            print("[WARNING] No se encuentra la base de datos de sinónimos")
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
            print(f"[ERROR] Error actualizando cache sinónimos: {e}")
    
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
        """Encontrar la mejor corrección para una palabra - MEJORADO según documentación LCLN"""
        # Primero verificar correcciones manuales (PRIORIDAD ALTA)
        if palabra in self.correcciones_manuales:
            return {
                'aplicada': True,
                'palabra_original': palabra,
                'palabra_corregida': self.correcciones_manuales[palabra],
                'confianza': 0.95,
                'fuente': 'correccion_manual'
            }
        
        # NO corregir números a menos que sea específico
        if palabra.isdigit() or any(c.isdigit() for c in palabra):
            # Solo permitir correcciones numéricas específicas conocidas
            correcciones_numericas = {
                '200g': '20',  # Caso específico documentado
                '2000': '20'   # Variación común
            }
            if palabra in correcciones_numericas:
                return {
                    'aplicada': True,
                    'palabra_original': palabra,
                    'palabra_corregida': correcciones_numericas[palabra],
                    'confianza': 0.8,
                    'fuente': 'correccion_numerica'
                }
            # No corregir otros números
            return {
                'aplicada': False,
                'palabra_original': palabra,
                'palabra_corregida': palabra,
                'confianza': 1.0,
                'fuente': None
            }
        
        # Buscar en productos con criterios más estrictos
        mejor_correccion = None
        mejor_similitud = 0
        
        for nombre_producto, data in self._cache_productos.items():
            palabras_producto = nombre_producto.lower().split()
            for palabra_prod in palabras_producto:
                if len(palabra_prod) > 3:  # Palabras más largas
                    distancia = self._distancia_levenshtein(palabra.lower(), palabra_prod.lower())
                    if distancia <= 1:  # Más restrictivo: solo 1 carácter diferente
                        similitud = difflib.SequenceMatcher(None, palabra.lower(), palabra_prod.lower()).ratio()
                        if similitud >= 0.8 and similitud > mejor_similitud:  # Más restrictivo
                            mejor_similitud = similitud
                            mejor_correccion = {
                                'aplicada': True,
                                'palabra_original': palabra,
                                'palabra_corregida': palabra_prod,
                                'confianza': similitud,
                                'fuente': 'productos'
                            }
        
        if mejor_correccion:
            return mejor_correccion
        
        return {
            'aplicada': False,
            'palabra_original': palabra,
            'palabra_corregida': palabra,
            'confianza': 1.0,
            'fuente': None
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
          # Buscar sinónimos para cada palabra, todas las combinaciones de palabras, y para la frase completa
        terminos_busqueda = []
        
        # Agregar palabras individuales
        terminos_busqueda.extend(palabras)
        
        # Agregar todas las combinaciones contíguas de 2 o más palabras (n-grams)
        for i in range(len(palabras)):
            for j in range(i + 2, len(palabras) + 1):  # Desde 2 palabras en adelante
                combinacion = ' '.join(palabras[i:j])
                terminos_busqueda.append(combinacion)
        
        # Agregar la frase completa si no está ya incluida
        if consulta not in terminos_busqueda:
            terminos_busqueda.append(consulta)
        
        for termino in terminos_busqueda:
            termino_key = termino.lower()
            if termino_key in self._cache_sinonimos:
                sinonimos = self._cache_sinonimos[termino_key]
                
                for sinonimo in sinonimos:
                    if sinonimo['confianza'] >= 0.7:  # Solo sinónimos de alta confianza
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
            'productos_detectados': list(expansion_info['productos_detectados']),
            'atributos_detectados': list(expansion_info['atributos_detectados'])
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
            interpretacion['productos_especificos'] = list(expansion['productos_detectados'])
        
        # Detectar categorías
        elif expansion['categorias_detectadas']:
            interpretacion['tipo_busqueda'] = 'categoria'
            interpretacion['categoria_principal'] = list(expansion['categorias_detectadas'])[0]  # Tomar la primera
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
        
        # Resolver conflictos de atributos (negaciones tienen prioridad) al final
        if interpretacion['atributos']:
            # Mapeo de conflictos: atributo positivo -> atributo negativo (prioridad)
            conflictos = {
                'picante': 'dulce',
                'con azucar': 'sin azucar',
            }
            
            # Si hay conflictos, priorizar el atributo de negación
            atributos_finales = interpretacion['atributos'][:]
            for positivo, negativo in conflictos.items():
                if positivo in atributos_finales and negativo in atributos_finales:
                    # Remover el atributo positivo, mantener el negativo
                    atributos_finales = [attr for attr in atributos_finales if attr != positivo]
            
            interpretacion['atributos'] = atributos_finales
        
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
                'precio': float(producto['precio']),                'imagen': producto['imagen'],  # IMAGEN INCLUIDA
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
    
    def _buscar_productos_especificos(self, productos_especificos: List[str], filtros_precio: Dict, atributos: List[str]) -> List[Dict]:
        """Buscar productos específicos detectados por sinónimos"""
        productos = []
        
        for producto_nombre in productos_especificos:
            for nombre_producto, data in self._cache_productos.items():
                # Normalizar nombres para mejor coincidencia (quitar guiones, espacios extra)
                producto_normalizado = producto_nombre.lower().replace('-', ' ').replace('  ', ' ').strip()
                nombre_normalizado = data['nombre'].lower().replace('-', ' ').replace('  ', ' ').strip()
                
                # Buscar coincidencia mejorada
                palabras_producto = producto_normalizado.split()
                coincidencia_encontrada = False
                
                # Si todas las palabras del producto buscado están en el nombre del producto
                if all(palabra in nombre_normalizado for palabra in palabras_producto):
                    coincidencia_encontrada = True
                # O si el producto normalizado está contenido en el nombre
                elif producto_normalizado in nombre_normalizado:
                    coincidencia_encontrada = True
                # O si el nombre del producto está contenido en el término buscado
                elif any(palabra in producto_normalizado for palabra in nombre_normalizado.split()[:2]):  # Solo las primeras 2 palabras
                    coincidencia_encontrada = True
                
                if not coincidencia_encontrada:
                    continue
                
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
                            if any(keyword in nombre_lower for keyword in ['sin azúcar', 'light', 'zero', 'diet']):
                                atributo_encontrado = True
                                break
                    
                    if not atributo_encontrado:
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
            
            # Aplicar filtros de atributos (lógica mejorada)
            if atributos:
                nombre_lower = data['nombre'].lower()
                categoria_lower = data['categoria_nombre'].lower()
                atributo_encontrado = False
                
                for atributo in atributos:
                    if atributo == 'picante':
                        if any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas']):
                            atributo_encontrado = True
                            break
                    elif atributo == 'dulce':
                        # Productos dulces (NO picantes)
                        es_picante = any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas'])
                        if not es_picante and (categoria_lower in ['golosinas', 'snacks'] or 
                                             any(keyword in nombre_lower for keyword in ['dulce', 'gomitas', 'panditas', 'emperador', 'cheetos', 'original'])):
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
                    elif atributo == 'barato':
                        # Productos baratos (precio <= 15)
                        if data['precio'] <= 15.0:
                            atributo_encontrado = True
                            break
                    elif atributo == 'caro':                        # Productos caros (precio >= 25)
                        if data['precio'] >= 25.0:
                            atributo_encontrado = True
                            break
                
                if not atributo_encontrado:
                    continue
            
            productos.append(data)
        
        return sorted(productos, key=lambda x: x['precio'])
    
    def _buscar_por_atributos(self, atributos: List[str], filtros_precio: Dict) -> List[Dict]:
        """Buscar productos por atributos específicos"""
        productos = []
        
        for nombre_producto, data in self._cache_productos.items():
            nombre_lower = data['nombre'].lower()
            categoria_lower = data['categoria_nombre'].lower()
            atributo_encontrado = False
            
            for atributo in atributos:
                if atributo == 'picante':                    # Productos explícitamente picantes
                    if any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas']):
                        atributo_encontrado = True
                        break
                elif atributo == 'dulce':
                    # Productos dulces (NO picantes) - incluye golosinas Y snacks no-picantes
                    es_picante = any(keyword in nombre_lower for keyword in ['fuego', 'picante', 'hot', 'flamin', 'dinamita', 'chile', 'adobadas'])
                    
                    # Si es de categoría golosinas, siempre incluir (son dulces por naturaleza)
                    if categoria_lower == 'golosinas':
                        atributo_encontrado = True
                        break
                    
                    # Si es de categoría snacks, incluir solo si NO es picante
                    elif categoria_lower == 'snacks' and not es_picante:
                        atributo_encontrado = True
                        break
                    
                    # También incluir productos con keywords dulces específicas
                    elif any(keyword in nombre_lower for keyword in ['dulce', 'gomitas', 'panditas', 'emperador', 'original', 'sal y limon', 'queso', 'natural']):
                        if not es_picante:
                            atributo_encontrado = True
                            break
                            break
                elif atributo == 'sin azucar':
                    # Solo productos que explícitamente son sin azúcar
                    if any(keyword in nombre_lower for keyword in ['sin azúcar', 'light', 'zero', 'diet']):
                        atributo_encontrado = True
                        break
                elif atributo == 'barato':
                    # Productos con precio menor al promedio (menos de $15)
                    if data['precio'] <= 15.0:
                        atributo_encontrado = True
                        break
                elif atributo == 'caro':
                    # Productos con precio mayor al promedio (más de $25)
                    if data['precio'] >= 25.0:
                        atributo_encontrado = True
                        break
            
            if atributo_encontrado:
                # Aplicar filtros de precio adicionales
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
    # Prueba del sistema mejorado
    print("[TEST] Probando Sistema LCLN Mejorado...")
    
    consultas_prueba = [
        "snacks picantes",
        "coca cola", 
        "bebidas sin azucar",
        "chetoos picantes baratos"
    ]
    
    for consulta in consultas_prueba:
        print(f"\n[QUERY] Consulta: '{consulta}'")
        resultado = sistema_lcln_mejorado.analizar_consulta_lcln(consulta)
        
        # Mostrar expansión de sinónimos
        expansion = resultado['fase_2_expansion_sinonimos']
        if expansion['categorias_detectadas']:
            print(f"[CATEGORIES] Categorías detectadas: {expansion['categorias_detectadas']}")
        if expansion['productos_detectados']:            print(f"[PRODUCTS] Productos detectados: {expansion['productos_detectados']}")
        
        # Mostrar resultados
        motor_recomendaciones = resultado['fase_5_motor_recomendaciones']
        print(f"[STRATEGY] Estrategia: {motor_recomendaciones['estrategia_usada']}")
        print(f"[RESULTS] Productos encontrados: {motor_recomendaciones['total_encontrados']}")
        
        for i, producto in enumerate(motor_recomendaciones['productos_encontrados'][:3], 1):
            print(f"   {i}. {producto['nombre']} - ${producto['precio']} (Stock: {producto['cantidad']}, Imagen: {producto['imagen']})")
