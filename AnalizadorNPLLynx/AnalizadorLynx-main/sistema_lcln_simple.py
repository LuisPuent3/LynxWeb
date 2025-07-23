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
            'password': '12345678',  # Contraseña XAMPP correcta
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
            
        print("Actualizando cache dinámico desde MySQL...")
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
            print(f"Cache actualizado: {len(self._cache_productos)} productos, {len(self._cache_categorias)} categorías, {len(self._cache_sinonimos)} sinónimos")
            
            # Resetear analizador léxico para que use nuevos datos
            self.analizador_lexico = None
            
        finally:
            cursor.close()
            conn.close()
    
    def _inicializar_analizador_lexico(self):
        """Inicializar el analizador léxico con los datos actuales del cache"""
        if self.analizador_lexico is None:
            try:
                print("Inicializando Analizador Léxico (AFD) con datos actuales...")
                
                # Preparar datos para el AFD - Cargar TODOS los productos dinámicamente
                productos_completos = []
                productos_multi = []
                productos_simples = []
                
                print(f"Cargando productos desde cache: {len(self._cache_productos)} productos")
                
                # Agregar productos desde cache - mejorado para incluir todos los productos
                for nombre, datos in self._cache_productos.items():
                    palabras = nombre.split()
                    if len(palabras) >= 3:
                        productos_completos.append(nombre)
                    elif len(palabras) >= 2:
                        productos_multi.append(nombre)
                    else:
                        # También incluir productos de una palabra para completitud
                        productos_simples.append(nombre)
                
                print(f"Productos completos (3+ palabras): {len(productos_completos)}")
                print(f"Productos multi (2 palabras): {len(productos_multi)}")
                print(f"Productos simples (1 palabra): {len(productos_simples)}")
                
                # Agregar sinónimos desde cache
                for sinonimo in self._cache_sinonimos.keys():
                    palabras = sinonimo.split()
                    if len(palabras) >= 3 and sinonimo not in productos_completos:
                        productos_completos.append(sinonimo)
                    elif len(palabras) >= 2 and sinonimo not in productos_multi:
                        productos_multi.append(sinonimo)
                    elif len(palabras) == 1 and sinonimo not in productos_simples:
                        productos_simples.append(sinonimo)
                
                print(f"Después de agregar sinónimos:")
                print(f"  - Productos completos: {len(productos_completos)}")  
                print(f"  - Productos multi: {len(productos_multi)}")
                print(f"  - Productos simples: {len(productos_simples)}")
                
                # Debug: mostrar algunos ejemplos
                if productos_completos:
                    print(f"Ejemplos productos completos: {productos_completos[:3]}")
                if productos_multi:
                    print(f"Ejemplos productos multi: {productos_multi[:3]}")
                if productos_simples:
                    print(f"Ejemplos productos simples: {productos_simples[:3]}")
                
                # Crear adaptador compatible
                class AdaptadorSimple:
                    def __init__(self, cache_productos, cache_categorias):
                        self.productos_completos = productos_completos
                        self.productos_multi = productos_multi
                        self.productos_simples = productos_simples
                        self.categorias = list(cache_categorias.keys())
                        self.unidades = ['pesos', 'peso', 'ml', 'g', 'kg', 'l']
                        self.cache_productos = cache_productos
                    
                    def obtener_estadisticas(self):
                        return {'productos_total': len(self.cache_productos)}
                    
                    def obtener_todos_productos(self):
                        """Método necesario para AdaptadorBaseDatos"""
                        productos_lista = []
                        for nombre, datos in self.cache_productos.items():
                            productos_lista.append({
                                'nombre': nombre,
                                'categoria': datos.get('categoria', 'General'),
                                'precio': datos.get('precio', 0),
                                'id': datos.get('id', 0)
                            })
                        return productos_lista
                
                # Configuración simplificada
                class ConfiguracionSimple:
                    def __init__(self, cache_productos, cache_categorias):
                        self.bd_escalable = AdaptadorSimple(cache_productos, cache_categorias)
                    
                    def obtener_estadisticas(self):
                        return self.bd_escalable.obtener_estadisticas()
                
                # Inicializar AFD
                config = ConfiguracionSimple(self._cache_productos, self._cache_categorias)
                self.analizador_lexico = AnalizadorLexicoLYNX(config)
                
                print(f"AFD inicializado:")
                print(f"    - Productos completos (>=3 palabras): {len(productos_completos)}")
                print(f"    - Productos multi-palabra (2 palabras): {len(productos_multi)}")
                print(f"    - Total en cache: {len(self._cache_productos)}")
                print(f"    - Categorías disponibles: {len(self._cache_categorias)}")
                print(f"    - Sinónimos disponibles: {len(self._cache_sinonimos)}")
                
            except Exception as e:
                print(f"Error inicializando AFD: {e}")
                print(f"   Continuando con sistema de fallback...")
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
        
        # Mapear botana  ->  snacks para búsquedas (preservar estado de correcciones)
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
        
        # Eliminar duplicados por ID
        productos = self._eliminar_duplicados(productos)
        
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
            
        elif estrategia == 'semantica_bebidas_sin_azucar':
            precio_str = f" <= ${precio_max:.0f}" if precio_max else ""
            if len(productos) > 1:
                return f"Encontradas {len(productos)} bebidas sin azúcar (incluyendo aguas){precio_str}"
            else:
                return f"Encontrada {len(productos)} bebida sin azúcar{precio_str}"
        
        elif estrategia == 'semantica_bebidas_con_azucar':
            precio_str = f" <= ${precio_max:.0f}" if precio_max else ""
            if len(productos) > 1:
                return f"Encontradas {len(productos)} bebidas con azúcar (refrescos regulares){precio_str}"
            else:
                return f"Encontrada {len(productos)} bebida con azúcar{precio_str}"
        
        elif estrategia.startswith('afd_'):
            if 'atributos' in estrategia:
                attrs_str = ', '.join(atributos) if atributos else 'atributos específicos'
                precio_str = f" <= ${precio_max:.0f}" if precio_max else ""
                return f"Encontrados {len(productos)} productos con {attrs_str}{precio_str} (AFD)"
            elif 'producto' in estrategia:
                precio_str = f" con precio <= ${precio_max:.0f}" if precio_max else ""
                return f"Producto encontrado por AFD{precio_str}"
            elif 'categoria' in estrategia:
                categoria = analisis.get('categoria', {}).get('nombre', 'categoría')
                precio_str = f" <= ${precio_max:.0f}" if precio_max else ""
                attrs_str = f" con {', '.join(atributos)}" if atributos else ""
                return f"Encontrados {len(productos)} productos de {categoria}{attrs_str}{precio_str} (AFD)"
            
        elif estrategia == 'sinonimo_directo' and precio_max:
            return f"Encontrado 1 producto por sinónimo con precio <= ${precio_max:.0f}"
            
        elif estrategia == 'sinonimo_directo':
            return f"Encontrado 1 producto por sinónimo"
            
        elif estrategia == 'coincidencia_exacta':
            return f"Producto encontrado por coincidencia exacta"
            
        elif estrategia == 'coincidencia_exacta_multiple':
            termino = analisis.get('termino_busqueda', 'término')
            precio_str = f" con precio <= ${precio_max:.0f}" if precio_max else ""
            return f"Encontrados {len(productos)} productos relacionados con '{termino}'{precio_str}"
            
        elif estrategia == 'filtro_precio':
            return f"Encontrados {len(productos)} productos <= ${precio_max:.0f}"
            
        elif estrategia == 'categoria_con_filtros' and precio_max:
            categoria = analisis.get('categoria', {}).get('nombre', 'categoría')
            return f"Encontrados {len(productos)} productos de {categoria} <= ${precio_max:.0f}"
            
        elif estrategia == 'categoria_semantica_con_atributos':
            categoria = analisis.get('categoria', 'categoría')
            atributo = analisis.get('atributo', 'atributo')
            precio_str = f" <= ${precio_max:.0f}" if precio_max else ""
            return f"Encontrados {len(productos)} productos {categoria} {atributo}{precio_str} (búsqueda semántica)"
            
        elif estrategia == 'busqueda_por_palabra_clave_semantica':
            termino = analisis.get('termino_busqueda', 'término')
            precio_str = f" con precio <= ${precio_max:.0f}" if precio_max else ""
            return f"Encontrados {len(productos)} productos que coinciden con '{termino}'{precio_str} (análisis semántico)"
            
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
                    
                    print(f"AFD activado - {len(tokens)} tokens detectados")
                    
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
                        print(f"AFD encontró producto: {producto_detectado['nombre']}")
                        
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
                        print(f"AFD encontró categoría: {categoria_detectada['nombre']}")
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
                        print(f"AFD encontró atributos: {', '.join(atributos_detectados)}")
                        return {
                            'tipo_busqueda': 'atributos',
                            'categoria': None,
                            'termino_busqueda': consulta,
                            'precio_max': precio_max,
                            'atributos': atributos_detectados,
                            'estrategia_usada': 'afd_busqueda_por_atributos'
                        }
                    
        except Exception as e:
            print(f"Error en AFD (usando fallback): {e}")
        
        # FALLBACK: Si el AFD falla o no encuentra nada, usar nuestro análisis
        print("Usando análisis simplificado como fallback")
        return self._analizar_consulta_fallback(consulta)
    
    def _eliminar_duplicados(self, productos: List[Dict]) -> List[Dict]:
        """Eliminar productos duplicados por ID manteniendo el de mayor score"""
        productos_unicos = {}
        
        for producto in productos:
            producto_id = producto.get('id_producto') or producto.get('id')
            
            if producto_id not in productos_unicos:
                productos_unicos[producto_id] = producto
            else:
                # Mantener el producto con mayor match_score
                score_actual = producto.get('match_score', 0)
                score_existente = productos_unicos[producto_id].get('match_score', 0)
                
                if score_actual > score_existente:
                    productos_unicos[producto_id] = producto
        
        return list(productos_unicos.values())
    
    def _analizar_semanticamente(self, consulta: str) -> Dict:
        """Análisis semántico avanzado para detectar patrones complejos como 'bebidas sin azúcar'"""
        import re  # Import for regex patterns
        
        # Diccionario de categorías semánticas expandidas
        categorias_semanticas = {
            'bebidas': {
                'palabras_clave': ['bebida', 'bebidas', 'liquido', 'refresco', 'agua', 'jugo', 'té', 'te', 'cola'],
                'productos_sin_azucar': [
                    'agua', 'agua natural', 'agua mineral', 'agua purificada',
                    'coca cola zero', 'coca zero', 'pepsi zero', 'sprite zero',
                    'agua con gas', 'agua saborizada',
                    'red bull sin azucar', 'powerade zero', 'gatorade zero'
                ],
                'atributos_sin_azucar': ['sin azucar', 'zero', 'light', 'diet', 'natural', 'pura']
            },
            'snacks': {
                'palabras_clave': ['snack', 'snacks', 'botana', 'botanas', 'papitas', 'chips'],
                'productos_sin_azucar': [],
                'atributos_sin_azucar': ['sin sal', 'light', 'horneado', 'natural']
            }
        }
        
        # Detectar negaciones y modificadores
        modificadores = {
            'sin_azucar': ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'],
            'con_azucar': ['con azucar', 'con azúcar', 'dulce', 'endulzado', 'endulzada', 'regular', 'original'],
            'sin_sal': ['sin sal', 'light'],
            'natural': ['natural', 'organico', 'orgánico', 'puro', 'pura'],
            'frio': ['frio', 'frío', 'helado', 'congelado'],
            'caliente': ['caliente', 'tibio']
        }
        
        resultado = {
            'categoria_detectada': None,
            'modificadores_detectados': [],
            'productos_semanticos_sugeridos': [],
            'expansion_consulta': None
        }
        
        # 1. Detectar categoría principal
        for categoria, config in categorias_semanticas.items():
            if any(palabra in consulta.lower() for palabra in config['palabras_clave']):
                resultado['categoria_detectada'] = categoria
                break
        
        # 2. Detectar modificadores
        for modificador, variantes in modificadores.items():
            if any(variante in consulta.lower() for variante in variantes):
                resultado['modificadores_detectados'].append(modificador)
        
        # 3. LÓGICA ESPECIAL: "bebidas sin azúcar" debe incluir aguas
        if (resultado['categoria_detectada'] == 'bebidas' and 
            'sin_azucar' in resultado['modificadores_detectados']):
            
            resultado['productos_semanticos_sugeridos'] = categorias_semanticas['bebidas']['productos_sin_azucar']
            resultado['expansion_consulta'] = 'bebidas_sin_azucar_incluye_aguas'
            
            print(f"Análisis semántico: bebidas sin azúcar detectado, incluyendo aguas")
        
        # 3B. NUEVA LÓGICA ESPECIAL: "bebidas con azúcar" (refrescos regulares)
        elif (resultado['categoria_detectada'] == 'bebidas' and 
              'con_azucar' in resultado['modificadores_detectados']):
            
            resultado['productos_semanticos_sugeridos'] = [
                'coca cola', 'coca-cola', 'pepsi', 'sprite', 'fanta', 'boing', 
                'limonada', 'naranjada', 'jugos', 'te', 'té', 'fuze tea',
                'powerade', 'gatorade'  # Bebidas deportivas con azúcar
            ]
            resultado['expansion_consulta'] = 'bebidas_con_azucar_excluye_aguas'
            
            print(f"Análisis semántico: bebidas con azúcar detectado, excluyendo aguas y productos zero")
            
        # 4. LÓGICA ESPECIAL: consultas de hidratación
        elif any(palabra in consulta.lower() for palabra in ['hidratacion', 'hidratante', 'sed', 'refrescante']):
            resultado['categoria_detectada'] = 'bebidas'
            resultado['modificadores_detectados'].append('hidratante')
            resultado['productos_semanticos_sugeridos'] = [
                'agua', 'agua mineral', 'agua natural', 'powerade', 'gatorade', 'agua saborizada'
            ]
            resultado['expansion_consulta'] = 'necesidad_hidratacion'
            print(f"Análisis semántico: necesidad de hidratación detectada")
            
        # 5. LÓGICA ESPECIAL: consultas saludables
        elif any(palabra in consulta.lower() for palabra in ['saludable', 'sano', 'dieta', 'fitness', 'cero calorias']):
            resultado['categoria_detectada'] = 'bebidas'
            resultado['modificadores_detectados'].append('saludable')
            resultado['productos_semanticos_sugeridos'] = [
                'agua', 'té verde', 'té negro', 'agua mineral', 'frutas frescas'
            ]
            resultado['expansion_consulta'] = 'opciones_saludables'
            print(f"Análisis semántico: opción saludable detectada")
            
        # 6. LÓGICA ESPECIAL: jerga coloquial (chesco, agüita)
        elif any(palabra in consulta.lower() for palabra in ['chesco', 'chescos', 'aguita', 'agüita']):
            resultado['categoria_detectada'] = 'bebidas'
            if 'chesco' in consulta.lower() or 'chescos' in consulta.lower():
                resultado['productos_semanticos_sugeridos'] = ['coca cola', 'pepsi', 'sprite', 'fanta']
                resultado['expansion_consulta'] = 'jerga_refrescos'
            else:  # agüita
                resultado['productos_semanticos_sugeridos'] = ['agua', 'agua natural', 'agua mineral']
                resultado['expansion_consulta'] = 'jerga_agua'
            print(f"Análisis semántico: jerga coloquial detectada")
            
        # 7. LÓGICA ESPECIAL: "sin picante" (papas/snacks que NO son picantes)
        elif re.search(r'\b(?:papas?|snacks?|botanas?)\s+sin\s+(?:picante|chile|flama|fuego)', consulta.lower()):
            resultado['categoria_detectada'] = 'snacks'
            resultado['modificadores_detectados'].append('sin_picante')
            resultado['productos_semanticos_sugeridos'] = [
                'papas', 'papas originales', 'papas clásicas', 'papas saladas', 'cheetos', 'fritos'
            ]
            resultado['expansion_consulta'] = 'snacks_sin_picante'
            print(f"Análisis semántico: snacks sin picante detectado")
        
        # 8. LÓGICA ESPECIAL: detección de patrones "sin X" más generales
        elif re.search(r'\bsin\s+(?:picante|chile|flama|fuego)', consulta.lower()):
            # Si menciona papas/snacks Y "sin picante"
            if any(palabra in consulta.lower() for palabra in ['papas', 'papa', 'snack', 'snacks', 'botana', 'botanas']):
                resultado['categoria_detectada'] = 'snacks'
                resultado['modificadores_detectados'].append('sin_picante')
                resultado['productos_semanticos_sugeridos'] = [
                    'papas', 'papas originales', 'papas clásicas', 'papas saladas', 'cheetos'
                ]
                resultado['expansion_consulta'] = 'snacks_sin_picante_general'
                print(f"Análisis semántico: productos sin picante detectado")
        
        return resultado
    
    def _analizar_consulta_fallback(self, consulta: str) -> Dict:
        """Análisis inteligente mejorado como sistema principal"""
        
        # Detectar filtros de precio PRIMERO (tanto para compatibilidad como completo)
        precio_max = self._extraer_filtro_precio(consulta)  # Para compatibilidad
        filtro_precio_completo = self._extraer_filtro_precio_completo(consulta)  # Para filtros avanzados
        
        # NUEVA FUNCIONALIDAD: Análisis semántico avanzado
        analisis_semantico = self._analizar_semanticamente(consulta)
        
        # Si hay análisis semántico específico, priorizarlo
        if analisis_semantico.get('expansion_consulta'):
            return {
                'tipo_busqueda': 'busqueda_semantica_avanzada',
                'categoria': analisis_semantico['categoria_detectada'],
                'modificadores': analisis_semantico['modificadores_detectados'],
                'productos_sugeridos': analisis_semantico['productos_semanticos_sugeridos'],
                'termino_busqueda': consulta,
                'precio_max': precio_max,
                'estrategia_usada': f"semantica_{analisis_semantico['expansion_consulta']}"
            }
        
        # PASO 0.5: DETECTAR CATEGORÍA + ATRIBUTO ANTES DE SINÓNIMOS
        # Analizar si tenemos estructura: CATEGORIA + ATRIBUTO
        palabras = consulta.split()
        categoria_detectada = None
        atributo_detectado = None
        
        for palabra in palabras:
            # Detectar categorías
            if palabra in ['bebidas', 'bebida', 'drinks']:
                categoria_detectada = 'bebidas'
            elif palabra in ['snacks', 'snack', 'botanas', 'botana']:
                categoria_detectada = 'snacks'
            
            # Detectar atributos específicos
            if 'sin' in palabras and any(a in palabras for a in ['azucar', 'azúcar']):
                atributo_detectado = 'sin_azucar'
            elif 'con' in palabras and any(a in palabras for a in ['azucar', 'azúcar']):
                atributo_detectado = 'con_azucar'
            elif palabra in ['dulces', 'dulce', 'sweet', 'endulzado', 'endulzada']:
                atributo_detectado = 'con_azucar'  # Dulce implies con azucar for beverages
            elif palabra in ['salados', 'salado', 'sal']:
                atributo_detectado = 'salado'
            elif palabra in ['picantes', 'picante', 'fuego', 'hot']:
                atributo_detectado = 'picante'
        
        # Si detectamos categoría + atributo, buscar en esa categoría CON PRIORIDAD
        if categoria_detectada and atributo_detectado:
            productos_categoria = []
            categoria_id = 1 if categoria_detectada == 'bebidas' else 2  # bebidas=1, snacks=2
            
            print(f"Búsqueda semántica: {categoria_detectada} + {atributo_detectado}")
            
            for nombre_prod, datos_prod in self._cache_productos.items():
                if datos_prod.get('categoria_id') == categoria_id:
                    # Aplicar filtro de atributo
                    incluir_producto = False
                    
                    if atributo_detectado == 'sin_azucar':
                        if 'sin azúcar' in nombre_prod.lower() or 'sin azucar' in nombre_prod.lower():
                            incluir_producto = True
                    elif atributo_detectado == 'con_azucar':
                        # Bebidas con azúcar: refrescos regulares, tés endulzados, etc.
                        nombre_lower = nombre_prod.lower()
                        if (categoria_detectada == 'bebidas' and 
                            not nombre_lower.startswith('agua') and  # Excluir aguas
                            not any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])):
                            incluir_producto = True
                    elif atributo_detectado == 'dulce':
                        # Palabras que indican dulce en snacks
                        palabras_dulces = ['chocolate', 'dulce', 'galleta', 'emperador', 'rancheritos', 'senzo']
                        if any(dulce in nombre_prod.lower() for dulce in palabras_dulces):
                            incluir_producto = True
                    elif atributo_detectado == 'salado':
                        # Palabras que indican salado
                        palabras_saladas = ['sal', 'crujitos', 'fritos', 'limón', 'limon']
                        if any(salado in nombre_prod.lower() for salado in palabras_saladas):
                            incluir_producto = True
                    elif atributo_detectado == 'picante':
                        # Palabras que indican picante
                        palabras_picantes = ['fuego', 'hot', 'picante', 'chile', 'crujitos fuego']
                        if any(picante in nombre_prod.lower() for picante in palabras_picantes):
                            incluir_producto = True
                    
                    if incluir_producto:
                        productos_categoria.append(datos_prod)
            
            if productos_categoria:
                # Aplicar filtro de precio si existe
                if precio_max:
                    productos_categoria = [p for p in productos_categoria if p['precio'] <= precio_max]
                
                print(f"Encontrados {len(productos_categoria)} productos en {categoria_detectada} con atributo {atributo_detectado}")
                
                return {
                    'tipo_busqueda': 'categoria_con_atributos',
                    'productos_encontrados': productos_categoria,
                    'termino_busqueda': consulta,
                    'categoria': categoria_detectada,
                    'atributo': atributo_detectado,
                    'precio_max': precio_max,
                    'estrategia_usada': 'categoria_semantica_con_atributos'
                }

        # PASO 1: BÚSQUEDA EXPANDIDA CON SINÓNIMOS - NO RETORNAR INMEDIATAMENTE
        consulta_normalizada = consulta.lower().strip()
        productos_encontrados_expansion = []
        productos_ids_agregados_expansion = set()
        sinonimos_encontrados = []
        
        print(f"PASO 1: Búsqueda expandida de sinónimos para: '{consulta}'")
        
        # Primera pasada: Encontrar todos los sinónimos relevantes
        for sinonimo, productos_sinonimo in self._cache_sinonimos.items():
            sinonimo_lower = sinonimo.lower()
            
            # FILTRO: Saltar sinónimos muy cortos que causan ambigüedades
            if len(sinonimo_lower) <= 2:
                continue  # Evita problemas como "te" en "menores"
            
            es_relevante = False
            tipo_coincidencia = ""
            
            # Tipos de coincidencias (más restrictivas)
            if consulta_normalizada == sinonimo_lower:
                es_relevante = True
                tipo_coincidencia = "exacta"
            elif len(sinonimo_lower) > 3:
                # Para sinónimos más largos, usar coincidencias de palabra completa
                import re
                
                # Sinónimo contenido en consulta como palabra completa
                patron_sinonimo = r'\b' + re.escape(sinonimo_lower) + r'\b'
                if re.search(patron_sinonimo, consulta_normalizada):
                    es_relevante = True
                    tipo_coincidencia = "parcial"
                
                # Consulta contenida en sinónimo como palabra completa (menos común)
                elif len(consulta_normalizada) > 3:
                    patron_consulta = r'\b' + re.escape(consulta_normalizada) + r'\b'
                    if re.search(patron_consulta, sinonimo_lower):
                        es_relevante = True
                        tipo_coincidencia = "parcial"
            
            if es_relevante:
                print(f"  Sinónimo {tipo_coincidencia}: '{sinonimo}' -> {len(productos_sinonimo)} productos")
                sinonimos_encontrados.append((sinonimo, productos_sinonimo, tipo_coincidencia))
                
                # Agregar productos de este sinónimo
                for prod_info in productos_sinonimo:
                    producto_id = prod_info['producto_id']
                    
                    for nombre_prod, datos_prod in self._cache_productos.items():
                        if datos_prod['id'] == producto_id:
                            if (datos_prod['id'] not in productos_ids_agregados_expansion and
                                (not precio_max or datos_prod['precio'] <= precio_max)):
                                productos_encontrados_expansion.append(datos_prod)
                                productos_ids_agregados_expansion.add(datos_prod['id'])
                                print(f"    + {datos_prod['nombre']} (${datos_prod['precio']})")
                            break
        
        # PASO 2: Buscar productos adicionales que contengan palabras del término
        palabras_busqueda = consulta_normalizada.split()
        for palabra in palabras_busqueda:
            # Filtro más estricto: evitar palabras muy cortas Y palabras comunes
            if (len(palabra) > 3 and 
                palabra not in ['menores', 'menor', 'mayor', 'mayores', 'pesos', 'para', 'tipo', 'como']):
                print(f"  Buscando productos que contengan '{palabra}'...")
                
                # Buscar en nombres de productos usando coincidencia de palabra completa
                import re
                patron_palabra = r'\b' + re.escape(palabra) + r'\b'
                
                for nombre_prod, datos_prod in self._cache_productos.items():
                    # Usar regex para buscar palabra completa, no subcadena
                    if (re.search(patron_palabra, nombre_prod.lower()) and 
                        datos_prod['id'] not in productos_ids_agregados_expansion):
                        
                        if not precio_max or datos_prod['precio'] <= precio_max:
                            productos_encontrados_expansion.append(datos_prod)
                            productos_ids_agregados_expansion.add(datos_prod['id'])
                            print(f"    + {datos_prod['nombre']} (${datos_prod['precio']}) [nombre directo]")
        
        # PASO 3: Para categorías específicas, agregar productos relacionados
        if consulta_normalizada in ['chicle', 'chicles']:
            print(f"  Búsqueda especial para chicles/gomitas...")
            for nombre_prod, datos_prod in self._cache_productos.items():
                nombre_lower = nombre_prod.lower()
                if (('goma' in nombre_lower or 'chicle' in nombre_lower or 'trident' in nombre_lower or
                     'dulcigoma' in nombre_lower) and 
                    datos_prod['id'] not in productos_ids_agregados_expansion):
                    
                    if not precio_max or datos_prod['precio'] <= precio_max:
                        productos_encontrados_expansion.append(datos_prod)
                        productos_ids_agregados_expansion.add(datos_prod['id'])
                        print(f"    + {datos_prod['nombre']} (${datos_prod['precio']}) [chicles/gomitas]")
        
        # PASO 4: Para snacks, buscar categorías relacionadas
        # Detectar búsquedas relacionadas con snacks
        palabras_snacks_en_consulta = [palabra for palabra in palabras_busqueda 
                                      if palabra in ['papitas', 'papas', 'chips', 'cheetos', 'snacks', 'botanas', 'fritos', 'doritos']]
        
        # Detectar si también hay palabras picantes (para ser más selectivo)
        hay_palabras_picantes = any(palabra in ['picante', 'picantes', 'fuego', 'dinamita', 'flama', 'chile', 'ardiente', 'hot'] 
                                   for palabra in palabras_busqueda)
        
        if palabras_snacks_en_consulta or consulta_normalizada in ['papitas', 'papas', 'chips', 'cheetos', 'snacks', 'botanas']:
            if hay_palabras_picantes:
                print(f"  Búsqueda especial para snacks PICANTES (modo selectivo)...")
                # Modo selectivo: solo agregar snacks que sean realmente picantes
                terminos_picantes = ['picante', 'chile', 'fuego', 'flama', 'dinamita', 'ardiente', 'hot']
                for nombre_prod, datos_prod in self._cache_productos.items():
                    nombre_lower = nombre_prod.lower()
                    # Solo snacks que contengan términos picantes
                    es_snack = ('papa' in nombre_lower or 'chip' in nombre_lower or 'frito' in nombre_lower or
                               'dorito' in nombre_lower or 'cheeto' in nombre_lower or 'crujito' in nombre_lower or
                               datos_prod.get('categoria', '').lower() == 'snacks')
                    es_picante = any(termino in nombre_lower for termino in terminos_picantes)
                    
                    if (es_snack and es_picante and datos_prod['id'] not in productos_ids_agregados_expansion):
                        if not precio_max or datos_prod['precio'] <= precio_max:
                            productos_encontrados_expansion.append(datos_prod)
                            productos_ids_agregados_expansion.add(datos_prod['id'])
                            print(f"    + {datos_prod['nombre']} (${datos_prod['precio']}) [snack picante específico]")
            else:
                print(f"  Búsqueda especial para snacks...")
                # Modo normal: agregar todos los snacks
                for nombre_prod, datos_prod in self._cache_productos.items():
                    nombre_lower = nombre_prod.lower()
                    # Buscar todos los snacks relacionados
                    if (('papa' in nombre_lower or 'chip' in nombre_lower or 'frito' in nombre_lower or
                         'dorito' in nombre_lower or 'cheeto' in nombre_lower or 'crujito' in nombre_lower or
                         datos_prod.get('categoria', '').lower() == 'snacks') and 
                        datos_prod['id'] not in productos_ids_agregados_expansion):
                        
                        if not precio_max or datos_prod['precio'] <= precio_max:
                            productos_encontrados_expansion.append(datos_prod)
                            productos_ids_agregados_expansion.add(datos_prod['id'])
                            print(f"    + {datos_prod['nombre']} (${datos_prod['precio']}) [snacks relacionados]")
        
        # PASO 5: Para picantes, buscar todos los productos con términos picantes
        # Detectar búsquedas relacionadas con picante
        palabras_picantes_en_consulta = [palabra for palabra in palabras_busqueda 
                                        if palabra in ['picante', 'picantes', 'fuego', 'dinamita', 'flama', 'chile', 'ardiente', 'hot']]
        
        if palabras_picantes_en_consulta or consulta_normalizada in ['picante', 'picantes']:
            print(f"  Búsqueda especial para productos picantes...")
            terminos_picantes = ['picante', 'chile', 'fuego', 'flama', 'dinamita', 'ardiente', 'hot']
            for nombre_prod, datos_prod in self._cache_productos.items():
                nombre_lower = nombre_prod.lower()
                if (any(termino in nombre_lower for termino in terminos_picantes) and 
                    datos_prod['id'] not in productos_ids_agregados_expansion):
                    
                    if not precio_max or datos_prod['precio'] <= precio_max:
                        productos_encontrados_expansion.append(datos_prod)
                        productos_ids_agregados_expansion.add(datos_prod['id'])
                        print(f"    + {datos_prod['nombre']} (${datos_prod['precio']}) [producto picante]")
        
        # Si encontramos productos en la búsqueda expandida, devolverlos
        if productos_encontrados_expansion:
            print(f"  TOTAL: {len(productos_encontrados_expansion)} productos encontrados en búsqueda expandida")
            return {
                'tipo_busqueda': 'busqueda_expandida_sinonimos',
                'productos_encontrados': productos_encontrados_expansion,
                'termino_busqueda': consulta,
                'sinonimos_encontrados': sinonimos_encontrados,
                'categoria': None,
                'precio_max': precio_max,
                'estrategia_usada': 'busqueda_expandida_con_sinonimos'
            }
        
        # PASO 1.5: BÚSQUEDA MEJORADA PARA PALABRAS SIMPLES 
        # Para casos como "limón" - buscar TODOS los productos relacionados, no solo coincidencia exacta
        if len(consulta.split()) == 1:  # Solo una palabra
            palabra = consulta.strip()
            productos_coincidentes = []
            producto_exacto = None
            
            # Buscar tanto coincidencia exacta como parcial
            for nombre_prod, datos_prod in self._cache_productos.items():
                nombre_lower = nombre_prod.lower()
                # Coincidencia exacta (mayor prioridad)
                if palabra == nombre_lower.strip():
                    producto_exacto = datos_prod
                # Coincidencia parcial (contiene la palabra)
                elif palabra in nombre_lower:
                    productos_coincidentes.append(datos_prod)
            
            # También buscar en sinónimos para coincidencias adicionales
            for sinonimo, productos_sinonimo in self._cache_sinonimos.items():
                # Coincidencias más flexibles: sin acentos y variaciones
                if (palabra in sinonimo.lower() or 
                    sinonimo.lower() in palabra or
                    (palabra == 'limon' and 'limon' in sinonimo.lower()) or
                    (palabra == 'limón' and 'limon' in sinonimo.lower())):
                    # Encontrar el producto completo por ID
                    for prod_info in productos_sinonimo:
                        producto_id = prod_info['producto_id']
                        for nombre_prod, datos_prod in self._cache_productos.items():
                            if datos_prod['id'] == producto_id:
                                # Evitar duplicados
                                if not any(p['id'] == datos_prod['id'] for p in productos_coincidentes):
                                    if not producto_exacto or producto_exacto['id'] != datos_prod['id']:
                                        productos_coincidentes.append(datos_prod)
                                        print(f"Coincidencia por sinónimo '{sinonimo}': {datos_prod['nombre']}")
                                break
            
            # Si encontramos múltiples productos, devolver todos con prioridad al exacto
            if producto_exacto or productos_coincidentes:
                productos_finales = []
                if producto_exacto:
                    productos_finales.append(producto_exacto)
                    print(f"Coincidencia exacta: {producto_exacto['nombre']}")
                
                # Agregar productos parciales que no sean el exacto
                for prod in productos_coincidentes:
                    if not producto_exacto or prod['id'] != producto_exacto['id']:
                        productos_finales.append(prod)
                        print(f"Coincidencia parcial: {prod['nombre']}")
                
                # Aplicar filtro de precio si existe
                if precio_max:
                    productos_finales = [p for p in productos_finales if p['precio'] <= precio_max]
                
                if productos_finales:
                    estrategia = 'coincidencia_exacta_multiple' if len(productos_finales) > 1 else 'coincidencia_exacta'
                    return {
                        'tipo_busqueda': 'productos_multiple_exacta',
                        'productos_encontrados': productos_finales,
                        'termino_busqueda': palabra,
                        'categoria': None,
                        'precio_max': precio_max,
                        'estrategia_usada': estrategia
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
            
            print(f"Producto encontrado por búsqueda parcial: {mejor_producto['nombre']}")
            
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
        
        # PASO 2.5: BÚSQUEDA SEMÁNTICA POR PALABRAS CLAVE ANTES DE CATEGORÍAS
        # Para casos como "limón" que puede ser fruta O ingrediente en snack
        palabras_consulta = consulta.split()
        
        for palabra in palabras_consulta:
            if len(palabra) > 3:  # Solo palabras significativas
                productos_coincidentes = []
                scores_coincidencia = []
                
                # Buscar en todos los productos
                for nombre_prod, datos_prod in self._cache_productos.items():
                    score = 0
                    nombre_lower = nombre_prod.lower()
                    palabra_lower = palabra.lower()
                    
                    # Diferentes tipos de coincidencias con diferentes scores
                    if palabra_lower == nombre_lower:  # Coincidencia exacta
                        score = 100
                    elif palabra_lower in nombre_lower:  # Contiene la palabra
                        # Bonus si la palabra está al inicio (ej: "Limón Verde" vs "Fritos Limón")
                        if nombre_lower.startswith(palabra_lower):
                            score = 80
                        else:
                            score = 60
                    elif any(part in palabra_lower for part in nombre_lower.split()):  # Coincidencia parcial
                        score = 40
                    
                    if score > 0:
                        productos_coincidentes.append(datos_prod)
                        scores_coincidencia.append(score)
                
                # Si encontramos múltiples productos, priorizar por score
                if len(productos_coincidentes) > 1:
                    # Combinar productos con scores
                    productos_con_score = list(zip(productos_coincidentes, scores_coincidencia))
                    productos_con_score.sort(key=lambda x: x[1], reverse=True)
                    
                    # Si el mejor score es significativamente mejor (diferencia > 20), priorizarlo
                    mejor_score = productos_con_score[0][1]
                    productos_finales = [p[0] for p in productos_con_score if p[1] >= mejor_score - 20]
                    
                    # Aplicar filtro de precio si existe
                    if precio_max:
                        productos_finales = [p for p in productos_finales if p['precio'] <= precio_max]
                    
                    if productos_finales:
                        print(f"Búsqueda semántica para '{palabra}': {len(productos_finales)} productos (mejor score: {mejor_score})")
                        return {
                            'tipo_busqueda': 'busqueda_semantica',
                            'productos_encontrados': productos_finales,
                            'termino_busqueda': palabra,
                            'categoria': None,
                            'precio_max': precio_max,
                            'estrategia_usada': 'busqueda_por_palabra_clave_semantica'
                        }

        # PASO 3: Detectar categoría
        for nombre_categoria, datos_categoria in self._cache_categorias.items():
            if nombre_categoria in consulta:
                print(f"Categoría detectada: {datos_categoria['nombre']}")
                return {
                    'tipo_busqueda': 'categoria',
                    'categoria': datos_categoria,
                    'termino_busqueda': '',
                    'precio_max': precio_max,
                    'filtro_precio': filtro_precio_completo,
                    'estrategia_usada': 'categoria_con_filtros'
                }
        
        # PASO 4: Detectar solo filtros de precio
        if precio_max:
            print(f"Solo filtro de precio detectado: <= ${precio_max}")
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
            print(f"Atributos detectados: {', '.join(atributos_detectados)}")
            return {
                'tipo_busqueda': 'atributos',
                'categoria': None,
                'termino_busqueda': consulta,
                'precio_max': precio_max,
                'atributos': atributos_detectados,
                'estrategia_usada': 'busqueda_por_atributos_inteligente'
            }
        
        # PASO 6: Búsqueda genérica por palabras clave
        print(f"Búsqueda genérica para: '{consulta}'")
        return {
            'tipo_busqueda': 'generica',
            'categoria': None,
            'termino_busqueda': consulta,
            'precio_max': None,
            'estrategia_usada': 'busqueda_generica'
        }
    
    def _extraer_filtro_precio(self, consulta: str) -> Optional[float]:
        """Extraer filtros de precio de la consulta usando múltiples estrategias"""
        resultado = self._extraer_filtro_precio_completo(consulta)
        if resultado:
            # Para rangos, devolver el precio máximo para compatibilidad
            if resultado.get('operador') == 'BETWEEN':
                return resultado['precio_max'] 
            else:
                return resultado['precio']
        return None
    
    def _extraer_filtro_precio_completo(self, consulta: str) -> Optional[Dict]:
        """Extraer filtros de precio con operador usando múltiples estrategias"""
        import re
        
        # NUEVA: Estrategia 0: Rangos de precio (mayor a X pero menor a Y)
        patron_rango = r'(?:mayor|mayores?)\s+(?:a|que)\s+(\d+(?:\.\d+)?).{1,15}(?:pero|y|,)?\s*(?:menor|menores?)\s+(?:a|que)\s+(\d+(?:\.\d+)?)'
        match_rango = re.search(patron_rango, consulta, re.IGNORECASE)
        if match_rango:
            precio_min = float(match_rango.group(1))
            precio_max = float(match_rango.group(2))
            print(f"Filtro rango de precio detectado: ${precio_min} - ${precio_max}")
            return {
                'precio_min': precio_min,
                'precio_max': precio_max, 
                'operador': 'BETWEEN',
                'tipo': 'rango'
            }
        
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
            r'(?:hasta|por)\s+(\d+(?:\.\d+)?)',
            r'(?:no\s+)?(?:más|mas)\s+(?:de|que)\s+(\d+(?:\.\d+)?)'
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
        
        # Estrategia 2: Números seguidos de "pesos"
        match = re.search(r'(\d+(?:\.\d+)?)\s*pesos?', consulta, re.IGNORECASE)
        if match:
            precio = float(match.group(1))
            # Si hay palabras como "menor", "menos", "hasta" antes del número
            if any(palabra in consulta for palabra in ['menor', 'menos', 'hasta', 'máximo', 'max', 'barato', 'economico']):
                print(f"Filtro precio detectado (pesos): <= ${precio}")
                return {'precio': precio, 'operador': '<=', 'tipo': 'menor_que'}
        
        # Estrategia 3: Adjetivos de precio
        if any(palabra in consulta for palabra in ['barato', 'baratos', 'barata', 'baratas', 'economico', 'economica']):
            print(f"Filtro precio detectado (adjetivo): <= $20.0")
            return {'precio': 20.0, 'operador': '<=', 'tipo': 'menor_que'}
        elif any(palabra in consulta for palabra in ['caro', 'caros', 'cara', 'caras', 'premium']):
            print(f"Filtro precio detectado (caro): >= $50.0")
            return {'precio': 50.0, 'operador': '>=', 'tipo': 'mayor_que'}
        
        # Estrategia 4: Contexto de números sueltos con palabras clave
        numeros = re.findall(r'\d+(?:\.\d+)?', consulta)
        if numeros and any(palabra in consulta for palabra in ['menor', 'menos', 'bajo', 'hasta', 'máximo', 'max']):
            precio = float(numeros[-1])  # Tomar el último número
            print(f"Filtro precio detectado (contexto): <= ${precio}")
            return {'precio': precio, 'operador': '<=', 'tipo': 'menor_que'}
        
        return None
    
    def _cumple_filtro_precio(self, precio_producto: float, filtro_precio: Optional[Dict]) -> bool:
        """Verifica si un producto cumple con el filtro de precio"""
        if not filtro_precio:
            return True
            
        operador = filtro_precio['operador']
        
        if operador == 'BETWEEN':
            # Rango de precios
            precio_min = filtro_precio['precio_min']
            precio_max = filtro_precio['precio_max']
            return precio_min < precio_producto <= precio_max
        elif operador == '<=':
            precio_filtro = filtro_precio['precio']
            return precio_producto <= precio_filtro
        elif operador == '>=':
            precio_filtro = filtro_precio['precio']
            return precio_producto >= precio_filtro
        else:
            return True  # Por defecto, incluir el producto
    
    def _ejecutar_busqueda_estrategias(self, analisis: Dict, limit: int) -> List[Dict]:
        """Ejecutar búsqueda usando diferentes estrategias"""
        
        if analisis['tipo_busqueda'] == 'producto_especifico':
            return [self._formatear_producto(analisis['producto_encontrado'])]
        
        elif analisis['tipo_busqueda'] == 'productos_multiple_exacta':
            # Nueva estrategia: múltiples productos para una palabra (ej: "limón")
            productos_encontrados = analisis.get('productos_encontrados', [])
            return [self._formatear_producto(prod) for prod in productos_encontrados[:limit]]
        
        elif analisis['tipo_busqueda'] == 'productos_multiple_sinonimo':
            # NUEVA ESTRATEGIA: múltiples productos para un sinónimo (ej: "picante" -> 3 productos)
            productos_encontrados = analisis.get('productos_encontrados', [])
            print(f"Procesando {len(productos_encontrados)} productos de sinónimo '{analisis['termino_busqueda']}'")
            return [self._formatear_producto(prod) for prod in productos_encontrados[:limit]]
        
        elif analisis['tipo_busqueda'] == 'busqueda_expandida_sinonimos':
            # NUEVA ESTRATEGIA: búsqueda expandida que incluye sinónimos + productos relacionados
            productos_encontrados = analisis.get('productos_encontrados', [])
            sinonimos_encontrados = analisis.get('sinonimos_encontrados', [])
            print(f"Procesando {len(productos_encontrados)} productos de búsqueda expandida para '{analisis['termino_busqueda']}'")
            print(f"Sinónimos encontrados: {[s[0] for s in sinonimos_encontrados]}")
            return [self._formatear_producto(prod) for prod in productos_encontrados[:limit]]
        
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
                analisis.get('filtro_precio'),
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
        
        elif analisis['tipo_busqueda'] == 'categoria_con_atributos':
            # Nueva estrategia mejorada: categoría + atributos específicos
            productos_categoria = analisis.get('productos_encontrados', [])
            # Los productos ya están filtrados por la lógica semántica
            return [self._formatear_producto(prod) for prod in productos_categoria[:limit]]
        
        elif analisis['tipo_busqueda'] == 'busqueda_semantica':
            # Nueva estrategia: búsqueda semántica por palabras clave
            productos_semanticos = analisis.get('productos_encontrados', [])
            return [self._formatear_producto(prod) for prod in productos_semanticos[:limit]]
        
        elif analisis['tipo_busqueda'] == 'busqueda_semantica_avanzada':
            # NUEVA ESTRATEGIA: Búsqueda semántica avanzada (ej: bebidas sin azúcar incluyendo aguas)
            return self._buscar_semantica_avanzada(
                analisis.get('categoria'),
                analisis.get('modificadores', []),
                analisis.get('productos_sugeridos', []),
                analisis.get('precio_max'),
                limit
            )

        else:
            # Búsqueda genérica - buscar en nombres de productos
            return self._buscar_generica(analisis['termino_busqueda'], limit)
    
    def _buscar_por_atributos(self, atributos: List[str], precio_max: Optional[float], limit: int) -> List[Dict]:
        """Buscar productos por atributos detectados - mejorado para negaciones"""
        productos = []
        
        print(f"Buscando por atributos: {', '.join(atributos)}")
        
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
            print("Expandiendo búsqueda por palabras clave...")
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
    
    def _buscar_semantica_avanzada(self, categoria: str, modificadores: List[str], productos_sugeridos: List[str], precio_max: Optional[float], limit: int) -> List[Dict]:
        """Búsqueda semántica avanzada que incluye expansión inteligente"""
        productos = []
        
        print(f"Búsqueda semántica avanzada: {categoria} con modificadores {modificadores}")
        
        # ESTRATEGIA 1: Buscar productos específicamente sugeridos por el análisis semántico
        productos_encontrados_directos = []
        productos_ids_agregados = set()  # Usar set para deduplicación O(1)
        
        for producto_sugerido in productos_sugeridos:
            for nombre_prod, datos_prod in self._cache_productos.items():
                # Evitar duplicados desde el inicio
                if datos_prod['id'] in productos_ids_agregados:
                    continue
                    
                # FILTRO ESTRICTO: Solo bebidas para búsqueda de bebidas sin azúcar
                if categoria == 'bebidas':
                    # Verificar que sea realmente una bebida (categoría 1)
                    if datos_prod.get('categoria_id') != 1 and datos_prod.get('id_categoria') != 1:
                        continue  # Skip productos que no sean bebidas
                
                # Buscar coincidencias MÁS ESTRICTAS con los productos sugeridos
                nombre_lower = nombre_prod.lower()
                producto_sugerido_lower = producto_sugerido.lower()
                
                # Para agua: coincidencia exacta de la palabra "agua"
                if producto_sugerido_lower.startswith('agua'):
                    if not nombre_lower.startswith('agua'):
                        continue
                
                # Para coca cola: Diferentes lógicas según el contexto
                elif 'coca' in producto_sugerido_lower:
                    # Si estamos buscando bebidas CON azúcar, excluir versiones sin azúcar
                    if 'con_azucar' in modificadores:
                        if not ('coca' in nombre_lower and not any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])):
                            continue
                    # Si estamos buscando bebidas SIN azúcar, SOLO las versiones sin azúcar
                    else:
                        if not ('coca' in nombre_lower and any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])):
                            continue
                        
                # Para té: Diferentes lógicas según el contexto
                elif 'té' in producto_sugerido_lower or 'te' in producto_sugerido_lower:
                    # Si estamos buscando bebidas CON azúcar, incluir tés CON azúcar
                    if 'con_azucar' in modificadores:
                        if not (('té' in nombre_lower or 'te' in nombre_lower) and 
                               not any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])):
                            continue
                    # Si estamos buscando bebidas SIN azúcar, SOLO tés sin azúcar
                    else:
                        if not (('té' in nombre_lower or 'te' in nombre_lower) and 
                               any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])):
                            continue
                
                # Coincidencia general más estricta
                elif not (producto_sugerido_lower in nombre_lower or 
                         all(palabra in nombre_lower for palabra in producto_sugerido_lower.split() if len(palabra) > 2)):
                    continue
                    
                if not precio_max or datos_prod['precio'] <= precio_max:
                    productos_encontrados_directos.append(datos_prod)
                    productos_ids_agregados.add(datos_prod['id'])
                    print(f"  Producto semántico directo: {datos_prod['nombre']}")
        
        # ESTRATEGIA 2: Buscar en categoría específica con filtros semánticos
        if categoria == 'bebidas' and 'sin_azucar' in modificadores:
            categoria_id = 1  # ID de bebidas
            
            # Buscar todos los productos de bebidas que cumplan criterios semánticos
            for nombre_prod, datos_prod in self._cache_productos.items():
                if datos_prod.get('categoria_id') == categoria_id or datos_prod.get('id_categoria') == categoria_id:
                    nombre_lower = nombre_prod.lower()
                    
                    # Criterios ESTRICTOS para "bebidas sin azúcar":
                    es_sin_azucar = (
                        # Aguas (naturalmente sin azúcar)
                        nombre_lower.startswith('agua') or
                        # Productos explícitamente sin azúcar
                        'sin azucar' in nombre_lower or
                        'sin azúcar' in nombre_lower or
                        'zero' in nombre_lower or
                        'light' in nombre_lower or
                        'diet' in nombre_lower
                    )
                    
                    # EXCLUSIONES: productos que SÍ tienen azúcar
                    tiene_azucar = (
                        # Fuze Tea y otros tés endulzados (sin "sin azúcar" explícito)
                        ('fuze' in nombre_lower and 'sin azucar' not in nombre_lower and 'zero' not in nombre_lower) or
                        ('té' in nombre_lower and 'sin azucar' not in nombre_lower and 'zero' not in nombre_lower and 'diet' not in nombre_lower) or
                        ('te' in nombre_lower and 'sin azucar' not in nombre_lower and 'zero' not in nombre_lower and 'diet' not in nombre_lower) or
                        # Coca-Cola regular (sin "sin azúcar", "zero", "light", "diet")
                        ('coca' in nombre_lower and not any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])) or
                        # Jugos y refrescos regulares (tienen azúcar)
                        (any(palabra in nombre_lower for palabra in ['jugo', 'boing', 'jumex', 'sprite', 'fanta', 'limonada', 'naranjada']) and 
                         not any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet']))
                    )
                    
                    # Solo incluir si es sin azúcar Y NO tiene azúcar
                    es_sin_azucar = es_sin_azucar and not tiene_azucar
                    
                    if es_sin_azucar:
                        if not precio_max or datos_prod['precio'] <= precio_max:
                            # Evitar duplicados usando el set eficiente
                            if datos_prod['id'] not in productos_ids_agregados:
                                productos_encontrados_directos.append(datos_prod)
                                productos_ids_agregados.add(datos_prod['id'])
                                print(f"  Bebida sin azúcar: {datos_prod['nombre']}")
        
        # NUEVA ESTRATEGIA 2B: Buscar bebidas CON azúcar (refrescos regulares)
        elif categoria == 'bebidas' and 'con_azucar' in modificadores:
            categoria_id = 1  # ID de bebidas
            
            # Buscar todos los productos de bebidas que contengan azúcar
            for nombre_prod, datos_prod in self._cache_productos.items():
                if datos_prod.get('categoria_id') == categoria_id or datos_prod.get('id_categoria') == categoria_id:
                    nombre_lower = nombre_prod.lower()
                    
                    # Criterios para "bebidas con azúcar": 
                    es_con_azucar = (
                        # Refrescos regulares (Coca-Cola normal, Sprite normal, etc.)
                        ('coca' in nombre_lower and not any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])) or
                        # Tés endulzados
                        ('té' in nombre_lower and 'sin azucar' not in nombre_lower and 'zero' not in nombre_lower and 'diet' not in nombre_lower) or
                        ('te' in nombre_lower and 'sin azucar' not in nombre_lower and 'zero' not in nombre_lower and 'diet' not in nombre_lower) or
                        # Jugos y refrescos con azúcar
                        (any(palabra in nombre_lower for palabra in ['jugo', 'boing', 'jumex', 'sprite', 'fanta', 'limonada', 'naranjada']) and 
                         not any(palabra in nombre_lower for palabra in ['sin azucar', 'sin azúcar', 'zero', 'light', 'diet'])) or
                        # Bebidas deportivas regulares
                        ('powerade' in nombre_lower and not any(palabra in nombre_lower for palabra in ['zero', 'light'])) or
                        ('gatorade' in nombre_lower and not any(palabra in nombre_lower for palabra in ['zero', 'light']))
                    )
                    
                    # EXCLUSIONES: No incluir aguas (naturalmente sin azúcar)
                    es_agua = nombre_lower.startswith('agua')
                    
                    # Solo incluir si tiene azúcar Y NO es agua
                    es_con_azucar = es_con_azucar and not es_agua
                    
                    if es_con_azucar:
                        if not precio_max or datos_prod['precio'] <= precio_max:
                            # Evitar duplicados
                            if datos_prod['id'] not in productos_ids_agregados:
                                productos_encontrados_directos.append(datos_prod)
                                productos_ids_agregados.add(datos_prod['id'])
                                print(f"  Bebida con azúcar: {datos_prod['nombre']}")
        
        # NUEVA ESTRATEGIA 2C: Buscar snacks SIN picante (papas normales, etc.)
        elif categoria == 'snacks' and 'sin_picante' in modificadores:
            categoria_id = 2  # ID de snacks
            
            # Buscar todos los snacks que NO sean picantes
            for nombre_prod, datos_prod in self._cache_productos.items():
                if datos_prod.get('categoria_id') == categoria_id or datos_prod.get('id_categoria') == categoria_id:
                    nombre_lower = nombre_prod.lower()
                    
                    # Criterios para "snacks sin picante":
                    # INCLUSIONES: snacks básicos/normales
                    es_snack_normal = (
                        # Papas básicas (sin palabras picantes)
                        ('papa' in nombre_lower and not any(palabra in nombre_lower for palabra in ['picante', 'flama', 'dinamita', 'fuego', 'chile', 'ardiente'])) or
                        # Cheetos originales (no flamin hot)
                        ('cheetos' in nombre_lower and not any(palabra in nombre_lower for palabra in ['flama', 'flamin', 'hot', 'picante'])) or
                        # Fritos básicos
                        ('fritos' in nombre_lower and not any(palabra in nombre_lower for palabra in ['picante', 'chile', 'flama'])) or
                        # Otros snacks que no contengan términos picantes
                        (any(palabra in nombre_lower for palabra in ['galleta', 'oreo', 'emperador']) and 
                         not any(palabra in nombre_lower for palabra in ['picante', 'flama', 'dinamita', 'fuego', 'chile']))
                    )
                    
                    # EXCLUSIONES: productos explícitamente picantes
                    es_picante = (
                        any(palabra in nombre_lower for palabra in ['picante', 'flama', 'flamas', 'dinamita', 'fuego', 'chile', 'ardiente', 'hot']) or
                        'crujitos fuego' in nombre_lower or
                        'doritos dinamita' in nombre_lower or
                        'susalia flama' in nombre_lower
                    )
                    
                    # Solo incluir si es snack normal Y NO es picante
                    es_snack_sin_picante = es_snack_normal and not es_picante
                    
                    if es_snack_sin_picante:
                        if not precio_max or datos_prod['precio'] <= precio_max:
                            # Evitar duplicados
                            if datos_prod['id'] not in productos_ids_agregados:
                                productos_encontrados_directos.append(datos_prod)
                                productos_ids_agregados.add(datos_prod['id'])
                                print(f"  Snack sin picante: {datos_prod['nombre']}")
        
        # ESTRATEGIA 3: Si no encuentra suficientes, expandir búsqueda con SINÓNIMOS MEJORADA
        if len(productos_encontrados_directos) < 5:  # Buscar más productos para mejor calidad
            print("  Expandiendo búsqueda semántica con sinónimos...")
            
            # Crear términos de búsqueda relacionados según la categoría y modificadores
            terminos_busqueda = []
            
            if categoria == 'bebidas':
                if 'sin_azucar' in modificadores:
                    terminos_busqueda.extend(['agua', 'natural', 'zero', 'light', 'diet', 'sin azucar'])
                elif 'con_azucar' in modificadores:
                    terminos_busqueda.extend(['cola', 'refresco', 'jugo', 'té', 'te'])
                else:
                    terminos_busqueda.extend(['bebida', 'refresco', 'agua', 'jugo', 'cola'])
            elif categoria == 'snacks':
                if 'sin_picante' in modificadores:
                    terminos_busqueda.extend(['papa', 'chips', 'galleta', 'dulce'])
                else:
                    terminos_busqueda.extend(['snack', 'botana', 'papa', 'chips'])
            
            # Buscar sinónimos que contengan estos términos
            for sinonimo, productos_sinonimo in self._cache_sinonimos.items():
                sinonimo_lower = sinonimo.lower()
                
                # Verificar si el sinónimo es relevante
                es_relevante = False
                
                # Coincidencia con términos específicos
                if any(termino in sinonimo_lower for termino in terminos_busqueda):
                    es_relevante = True
                
                # También buscar sinónimos que contengan palabras de los productos sugeridos
                elif productos_sugeridos:
                    for producto_sugerido in productos_sugeridos:
                        if (producto_sugerido.lower() in sinonimo_lower or 
                            any(palabra in sinonimo_lower for palabra in producto_sugerido.lower().split())):
                            es_relevante = True
                            break
                
                if es_relevante:
                    for prod_info in productos_sinonimo:
                        producto_id = prod_info['producto_id']
                        for nombre_prod, datos_prod in self._cache_productos.items():
                            if datos_prod['id'] == producto_id:
                                # Aplicar filtros de categoría y modificadores
                                include_producto = True
                                
                                # Filtros específicos por categoría
                                if categoria == 'bebidas':
                                    if datos_prod.get('categoria_id') != 1 and datos_prod.get('id_categoria') != 1:
                                        include_producto = False
                                elif categoria == 'snacks':
                                    if datos_prod.get('categoria_id') != 2 and datos_prod.get('id_categoria') != 2:
                                        include_producto = False
                                
                                # Filtros por modificadores
                                if include_producto and 'sin_azucar' in modificadores:
                                    nombre_lower = nombre_prod.lower()
                                    if not (nombre_lower.startswith('agua') or 
                                           any(palabra in nombre_lower for palabra in ['sin azucar', 'zero', 'light', 'diet'])):
                                        include_producto = False
                                
                                if include_producto and 'sin_picante' in modificadores:
                                    nombre_lower = nombre_prod.lower()
                                    if any(palabra in nombre_lower for palabra in ['picante', 'flama', 'dinamita', 'fuego', 'chile']):
                                        include_producto = False
                                
                                if (include_producto and 
                                    (not precio_max or datos_prod['precio'] <= precio_max) and
                                    datos_prod['id'] not in productos_ids_agregados):
                                    productos_encontrados_directos.append(datos_prod)
                                    productos_ids_agregados.add(datos_prod['id'])
                                    print(f"  Por sinónimo semántico '{sinonimo}': {datos_prod['nombre']}")
                                    break
        
        # Formatear productos encontrados
        for producto in productos_encontrados_directos[:limit]:
            producto_formateado = self._formatear_producto(producto)
            # Ajustar score y reasons para búsqueda semántica
            producto_formateado['match_score'] = 0.9
            producto_formateado['match_reasons'] = ['semantica_avanzada', 'expansion_inteligente', 'imagen_incluida']
            producto_formateado['source'] = 'mysql_lcln_semantico'
            productos.append(producto_formateado)
        
        print(f"  Total productos semánticos encontrados: {len(productos)}")
        return productos
    
    def _buscar_por_categoria(self, categoria: str, filtro_precio: Optional[Dict], limit: int) -> List[Dict]:
        """Buscar productos por categoría con filtros de precio completos"""
        productos = []
        
        # Mostrar información del filtro
        if filtro_precio:
            operador = filtro_precio.get('operador', 'N/A')
            precio = filtro_precio.get('precio', 'N/A')
            print(f"Búsqueda por categoría: '{categoria}', filtro precio: {operador} ${precio}")
        else:
            print(f"Búsqueda por categoría: '{categoria}', sin filtro precio")
        
        for producto in self._cache_productos.values():
            if producto['categoria'].lower() == categoria.lower():
                # Aplicar filtro de precio si existe
                if filtro_precio and not self._cumple_filtro_precio(producto['precio'], filtro_precio):
                    continue
                
                productos.append(self._formatear_producto(producto))
                print(f"  Producto encontrado: {producto['nombre']} (${producto['precio']})")
        
        # Ordenar por precio y limitar
        productos.sort(key=lambda x: x['precio'])
        print(f"  Total productos en categoría '{categoria}': {len(productos)}")
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
        """Búsqueda genérica mejorada con soporte completo de sinónimos"""
        productos = []
        productos_ids_agregados = set()
        termino_lower = termino.lower().strip()
        
        print(f"Búsqueda genérica mejorada para: '{termino}'")
        
        # PASO 1: Búsqueda directa en nombres de productos
        for producto in self._cache_productos.values():
            if termino_lower in producto['nombre'].lower():
                if producto['id'] not in productos_ids_agregados:
                    productos.append(self._formatear_producto(producto))
                    productos_ids_agregados.add(producto['id'])
                    print(f"  Coincidencia directa: {producto['nombre']}")
        
        # PASO 2: Búsqueda en sinónimos (MEJORADO y FILTRADO)
        for sinonimo, productos_sinonimo in self._cache_sinonimos.items():
            sinonimo_lower = sinonimo.lower()
            
            # FILTRO: Evitar sinónimos problemáticos muy cortos
            if len(sinonimo_lower) <= 2:
                continue  # Saltar palabras como "te", "de", "la", etc.
            
            # Coincidencias flexibles de sinónimos
            coincidencia_sinonimo = False
            
            # Tipo 1: Coincidencia exacta
            if termino_lower == sinonimo_lower:
                coincidencia_sinonimo = True
                print(f"  Sinónimo exacto encontrado: '{sinonimo}'")
            
            # Tipo 2: Término contenido en sinónimo (más estricto)
            elif len(termino_lower) > 3 and termino_lower in sinonimo_lower:
                # Verificar que sea una palabra significativa, no solo subcadena
                import re
                patron = r'\b' + re.escape(termino_lower) + r'\b'
                if re.search(patron, sinonimo_lower):
                    coincidencia_sinonimo = True
                    print(f"  Sinónimo parcial encontrado: '{sinonimo}' (contiene palabra completa '{termino}')")
            
            # Tipo 3: Sinónimo contenido en término (SOLO como palabra completa)
            elif len(sinonimo_lower) > 3:
                # Usar regex para buscar palabra completa, no subcadena
                import re
                patron = r'\b' + re.escape(sinonimo_lower) + r'\b'
                if re.search(patron, termino_lower):
                    coincidencia_sinonimo = True
                    print(f"  Sinónimo contenido encontrado: '{sinonimo}' (palabra completa en '{termino}')")
            
            # Tipo 4: Coincidencias por palabras individuales
            elif len(termino_lower) > 3:
                palabras_termino = termino_lower.split()
                palabras_sinonimo = sinonimo_lower.split()
                
                # Si alguna palabra coincide exactamente
                if any(palabra in palabras_sinonimo for palabra in palabras_termino if len(palabra) > 2):
                    coincidencia_sinonimo = True
                    print(f"  Sinónimo por palabra encontrado: '{sinonimo}' (palabras comunes)")
            
            if coincidencia_sinonimo:
                # Agregar todos los productos de este sinónimo
                for prod_info in productos_sinonimo:
                    producto_id = prod_info['producto_id']
                    for nombre_prod, datos_prod in self._cache_productos.items():
                        if datos_prod['id'] == producto_id:
                            if datos_prod['id'] not in productos_ids_agregados:
                                productos.append(self._formatear_producto(datos_prod))
                                productos_ids_agregados.add(datos_prod['id'])
                                print(f"    -> Producto por sinónimo: {datos_prod['nombre']}")
                            break
        
        # PASO 3: Si aún no encuentra suficientes, búsqueda ampliada
        if len(productos) < 3:
            print(f"  Solo {len(productos)} productos encontrados, expandiendo búsqueda...")
            
            # Búsqueda más flexible: palabras parciales
            palabras_termino = termino_lower.split()
            for palabra in palabras_termino:
                if len(palabra) > 2:  # Evitar palabras muy cortas
                    # Buscar en nombres de productos
                    for producto in self._cache_productos.values():
                        if (palabra in producto['nombre'].lower() and 
                            producto['id'] not in productos_ids_agregados):
                            productos.append(self._formatear_producto(producto))
                            productos_ids_agregados.add(producto['id'])
                            print(f"    Coincidencia expandida: {producto['nombre']} (por '{palabra}')")
                            if len(productos) >= 10:  # Límite para no saturar
                                break
                    
                    # Buscar en sinónimos más flexible
                    for sinonimo, productos_sinonimo in self._cache_sinonimos.items():
                        if (palabra in sinonimo.lower() and 
                            len(productos) < 10):  # Límite
                            
                            for prod_info in productos_sinonimo:
                                producto_id = prod_info['producto_id']
                                for nombre_prod, datos_prod in self._cache_productos.items():
                                    if datos_prod['id'] == producto_id:
                                        if datos_prod['id'] not in productos_ids_agregados:
                                            productos.append(self._formatear_producto(datos_prod))
                                            productos_ids_agregados.add(datos_prod['id'])
                                            print(f"      Sinónimo expandido: {datos_prod['nombre']} ('{sinonimo}' por '{palabra}')")
                                        break
        
        # PASO 4: Si todavía no hay resultados, mostrar productos populares/económicos
        if not productos:
            print(f"  No se encontraron coincidencias, mostrando productos económicos")
            for producto in self._cache_productos.values():
                if producto['precio'] <= 25.0:
                    productos.append(self._formatear_producto(producto))
        
        # Ordenar por precio y limitar
        productos.sort(key=lambda x: x['precio'])
        print(f"  Total productos encontrados: {len(productos)}")
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
        print(f"\nConsulta: '{consulta}'")
        resultado = sistema_lcln_simple.buscar_productos_inteligente(consulta)
        
        print(f"   Estrategia: {resultado['interpretation']['estrategia_usada']}")
        print(f"   Productos encontrados: {resultado['products_found']}")
        
        for prod in resultado['recommendations'][:3]:
            print(f"     - {prod['nombre']} ${prod['precio']} (imagen: {prod['imagen']})")
    
    print(f"\nSistema LCLN simplificado funcionando con imágenes incluidas")
