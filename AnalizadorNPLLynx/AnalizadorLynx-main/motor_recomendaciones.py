# motor_recomendaciones.py
import json
from typing import Dict, List, Any, Optional
import re

class MotorRecomendaciones:
    """
    Motor de recomendaciones inteligente para productos LYNX
    """
    
    def __init__(self, configuracion):
        self.configuracion = configuracion
        
        # Usar el adaptador de base de datos que tiene todos los métodos necesarios
        if hasattr(configuracion, 'adaptador_bd'):
            self.base_datos = configuracion.adaptador_bd
        elif hasattr(configuracion, 'bd_escalable'):
            # Crear el adaptador aquí si no existe
            from adaptador_bd import AdaptadorBaseDatos
            self.base_datos = AdaptadorBaseDatos(configuracion.bd_escalable)
        else:
            self.base_datos = configuracion.base_datos
        
        # Usar el simulador que viene con la configuración (puede ser escalable)
        self.simulador = configuracion.simulador
        
        # Configuración del motor
        self.max_resultados = 10  # Incrementamos para aprovechar la BD
        self.umbral_similitud_minima = 0.4  # Bajamos el umbral
        
        # Mapeo de categorías genéricas a específicas
        self.mapeo_categorias = {
            'botana': 'snacks',
            'snack': 'snacks', 
            'bebida': 'bebidas',
            'refresco': 'bebidas',
            'fruta': 'frutas',
            'verdura': 'verduras',
            'lacteo': 'lacteos',
            'pan': 'panaderia',
            'carne': 'carnes'
        }
        
        # Productos similares conocidos
        self.productos_similares = {
            'cheetos': ['doritos', 'papas sabritas', 'ruffles'],
            'coca-cola': ['pepsi', 'sprite', 'fanta'],
            'doritos': ['cheetos', 'ruffles', 'papas sabritas'],
            'leche': ['yogurt', 'queso', 'crema'],
            'manzana': ['pera', 'naranja', 'plátano']
        }
    
    def inferir_categoria_de_producto(self, producto: str) -> Optional[str]:
        """Infiere la categoría de un producto genérico"""
        producto = producto.lower().strip()
        
        # Mapeo directo
        if producto in self.mapeo_categorias:
            return self.mapeo_categorias[producto]
        
        # Buscar en productos conocidos
        for categoria, productos in self.base_datos.items():
            if isinstance(productos, list):
                for p in productos:
                    if isinstance(p, str) and producto in p.lower():
                        if categoria == 'productos_simples':
                            return 'productos'
                        elif categoria == 'productos_multi':
                            return 'productos'
                        return categoria.replace('_', '')
        
        return None
    
    def calcular_similitud_nombre(self, nombre1: str, nombre2: str) -> float:
        """Calcula similitud entre nombres usando n-gramas"""
        nombre1 = nombre1.lower().strip()
        nombre2 = nombre2.lower().strip()
        
        if nombre1 == nombre2:
            return 1.0
        
        # Crear n-gramas de 2 caracteres
        def crear_bigramas(texto):
            texto = f" {texto} "  # Padding
            return set(texto[i:i+2] for i in range(len(texto)-1))
        
        bigramas1 = crear_bigramas(nombre1)
        bigramas2 = crear_bigramas(nombre2)
        
        if not bigramas1 or not bigramas2:
            return 0.0
        
        interseccion = bigramas1.intersection(bigramas2)
        union = bigramas1.union(bigramas2)
        
        return len(interseccion) / len(union) if union else 0.0
    
    def calcular_similitud_atributos(self, consulta_atributos: List[str], 
                                   producto_atributos: List[str]) -> float:
        """Calcula similitud por atributos compartidos"""
        if not consulta_atributos:
            return 0.5  # Neutro si no hay filtros
        
        consulta_set = set(attr.lower() for attr in consulta_atributos)
        producto_set = set(attr.lower() for attr in producto_atributos)
        
        interseccion = consulta_set.intersection(producto_set)
        union = consulta_set.union(producto_set)
        
        return len(interseccion) / len(union) if union else 0.0
    
    def precio_en_rango(self, precio_producto: float, filtro_precio: Dict) -> bool:
        """Verifica si un precio está en el rango especificado"""
        if 'min' in filtro_precio and precio_producto < filtro_precio['min']:
            return False
        if 'max' in filtro_precio and precio_producto > filtro_precio['max']:
            return False
        if 'exacto' in filtro_precio and abs(precio_producto - filtro_precio['exacto']) > 0.01:
            return False
        return True
    
    def calcular_similitud_precio(self, precio_producto: float, filtro_precio: Dict) -> float:
        """Calcula un score de similitud por precio"""
        if not filtro_precio:
            return 0.0
        
        if self.precio_en_rango(precio_producto, filtro_precio):
            return 0.3  # Bonus por estar en rango
        
        # Calcular qué tan cerca está del rango
        if 'max' in filtro_precio:
            diferencia = abs(precio_producto - filtro_precio['max'])
            if diferencia <= filtro_precio['max'] * 0.2:  # Dentro del 20%
                return 0.1
        
        return 0.0
    
    def calcular_similitud(self, consulta: Dict, producto_simulado: Dict) -> float:
        """
        Calcula el score de similitud total entre consulta y producto
        """
        score = 0.0
        
        # 1. Similitud por categoría (40%)
        if consulta.get('categoria') and producto_simulado.get('categoria'):
            if consulta['categoria'] == producto_simulado['categoria']:
                score += 0.4
        
        # 2. Similitud por nombre/producto (30%)
        if consulta.get('producto') and producto_simulado.get('nombre'):
            similitud_nombre = self.calcular_similitud_nombre(
                consulta['producto'], 
                producto_simulado['nombre']
            )
            score += similitud_nombre * 0.3
        
        # 3. Similitud por atributos (20%)
        if consulta.get('atributos'):
            producto_atributos = producto_simulado.get('atributos', [])
            similitud_atributos = self.calcular_similitud_atributos(
                consulta['atributos'], 
                producto_atributos
            )
            score += similitud_atributos * 0.2
        
        # 4. Similitud por precio (10%)
        if consulta.get('filtro_precio') and producto_simulado.get('precio'):
            similitud_precio = self.calcular_similitud_precio(
                producto_simulado['precio'],
                consulta['filtro_precio']
            )
            score += similitud_precio
        
        return min(score, 1.0)
    
    def generar_productos_simulados(self, categoria: str) -> List[Dict]:
        """
        Genera productos simulados para demostrar el sistema
        (En producción esto vendría de la base de datos real)
        """
        productos_demo = {
            'snacks': [
                {
                    'product_id': 1,
                    'nombre': 'Doritos Nacho',
                    'categoria': 'snacks',
                    'precio': 18.50,
                    'atributos': ['picante', 'crujiente'],
                    'disponible': True
                },
                {
                    'product_id': 2,
                    'nombre': 'Cheetos Flamin Hot',
                    'categoria': 'snacks',
                    'precio': 22.00,
                    'atributos': ['picante', 'extra-chile'],
                    'disponible': True
                },
                {
                    'product_id': 3,
                    'nombre': 'Papas Sabritas Originales',
                    'categoria': 'snacks',
                    'precio': 15.00,
                    'atributos': ['salado', 'crujiente'],
                    'disponible': True
                }
            ],
            'bebidas': [
                {
                    'product_id': 4,
                    'nombre': 'Coca-Cola',
                    'categoria': 'bebidas',
                    'precio': 25.00,
                    'atributos': ['gaseosa', 'dulce'],
                    'disponible': True
                },
                {
                    'product_id': 5,
                    'nombre': 'Coca-Cola Sin Azúcar',
                    'categoria': 'bebidas',
                    'precio': 28.00,
                    'atributos': ['gaseosa', 'sin-azucar', 'diet'],
                    'disponible': True
                },
                {
                    'product_id': 6,
                    'nombre': 'Sprite',
                    'categoria': 'bebidas',
                    'precio': 23.00,
                    'atributos': ['gaseosa', 'limon'],
                    'disponible': True
                }
            ]
        }
        
        return productos_demo.get(categoria, [])
    
    def generar_recomendaciones(self, interpretacion: Dict, 
                              max_recomendaciones: Optional[int] = None) -> List[Dict]:
        """
        MOTOR DE RECOMENDACIONES MEJORADO - Funciona como buscador real
        Aprovecha TODA la arquitectura escalable: 1,304 productos + 82,768 sinónimos
        """
        if max_recomendaciones is None:
            max_recomendaciones = self.max_resultados
        
        recomendaciones = []
        
        # Extraer información de la consulta
        categoria_solicitada = interpretacion.get('categoria')
        producto_solicitado = interpretacion.get('producto')
        atributos_solicitados = interpretacion.get('atributos', [])
        filtros = interpretacion.get('filtros', {})
        
        # Debug: ver qué llega del análisis
        print(f"🔍 MOTOR RECOMENDACIONES - Procesando consulta:")
        print(f"   • Producto: {producto_solicitado}")
        print(f"   • Categoría: {categoria_solicitada}")
        print(f"   • Atributos: {atributos_solicitados}")
        print(f"   • Filtros: {filtros}")
        
        # ESTRATEGIA 1: BÚSQUEDA POR ATRIBUTOS (PRIORIDAD ALTA)
        # Ejemplo: "bebidas sin azucar" -> buscar bebidas + filtrar sin_azucar
        if atributos_solicitados:
            print(f"🎯 ESTRATEGIA 1: Búsqueda por atributos")
            
            for atributo in atributos_solicitados:
                print(f"   📍 Procesando atributo: {atributo}")
                try:
                    # Usar el sistema escalable para buscar por atributo
                    productos_atributo = self.base_datos.buscar_por_atributo(atributo, limite=max_recomendaciones * 2)
                    print(f"      → Encontrados {len(productos_atributo)} productos con atributo '{atributo}'")
                    
                    # Si también hay categoría, filtrar por ella
                    if categoria_solicitada:
                        productos_atributo = [p for p in productos_atributo 
                                           if p['categoria'].lower() == categoria_solicitada.lower()]
                        print(f"      → Filtrados por categoría '{categoria_solicitada}': {len(productos_atributo)} productos")
                    
                    # Agregar productos encontrados
                    for producto in productos_atributo:
                        if len(recomendaciones) >= max_recomendaciones:
                            break
                            
                        # Evitar duplicados
                        if any(r['product_id'] == producto.get('id', 0) for r in recomendaciones):
                            continue
                        
                        # Score alto para matches exactos de atributos
                        score = 0.9 if atributo in producto.get('atributos', []) else 0.75
                        razones = [f'atributo_{atributo}', 'busqueda_inteligente']
                        
                        if categoria_solicitada and producto['categoria'].lower() == categoria_solicitada.lower():
                            score += 0.05
                            razones.append('categoria_correcta')
                        
                        recomendacion = {
                            'product_id': producto.get('id', 0),
                            'name': producto['nombre'],
                            'category': producto['categoria'],
                            'price': producto['precio'],
                            'available': producto.get('disponible', True),
                            'stock': producto.get('stock', producto.get('cantidad', 100)),
                            'match_score': round(min(score, 1.0), 2),
                            'match_reasons': razones
                        }
                        recomendaciones.append(recomendacion)
                        print(f"      ✅ Agregado: {producto['nombre']} (score: {score:.2f})")
                        
                except Exception as e:
                    print(f"      ❌ Error buscando atributo '{atributo}': {e}")
        
        # ESTRATEGIA 2: BÚSQUEDA POR PRODUCTO ESPECÍFICO
        # Ejemplo: "coca cola", "papitas sabritas"
        if producto_solicitado and len(recomendaciones) < max_recomendaciones:
            print(f"🎯 ESTRATEGIA 2: Búsqueda por producto específico")
            print(f"   📍 Buscando: {producto_solicitado}")
            
            try:
                # Usar búsqueda inteligente del sistema escalable
                productos_similares = self.base_datos.buscar_productos_inteligente(
                    producto_solicitado, limite=max_recomendaciones * 2
                )
                print(f"      → Encontrados {len(productos_similares)} productos similares")
                
                for producto in productos_similares:
                    if len(recomendaciones) >= max_recomendaciones:
                        break
                    
                    # Evitar duplicados
                    if any(r['product_id'] == producto.get('id', 0) for r in recomendaciones):
                        continue
                    
                    # Calcular score basado en similitud de nombre
                    score = producto.get('similitud', self.calcular_similitud_nombre(
                        producto_solicitado, producto['nombre']
                    ))
                    
                    # Bonus si coinciden atributos solicitados
                    if atributos_solicitados:
                        atributos_producto = producto.get('atributos', [])
                        coincidencias_atributos = len(set(atributos_solicitados) & set(atributos_producto))
                        if coincidencias_atributos > 0:
                            score += 0.1 * coincidencias_atributos
                    
                    razones = ['producto_similar', 'busqueda_inteligente']
                    if score > 0.8:
                        razones.append('alta_similitud')
                    
                    recomendacion = {
                        'product_id': producto.get('id', 0),
                        'name': producto['nombre'],
                        'category': producto['categoria'],
                        'price': producto['precio'],
                        'available': producto.get('disponible', True),
                        'stock': producto.get('stock', producto.get('cantidad', 100)),
                        'match_score': round(min(score, 1.0), 2),
                        'match_reasons': razones
                    }
                    recomendaciones.append(recomendacion)
                    print(f"      ✅ Agregado: {producto['nombre']} (score: {score:.2f})")
                    
            except Exception as e:
                print(f"      ❌ Error buscando producto '{producto_solicitado}': {e}")
        
        # ESTRATEGIA 3: BÚSQUEDA POR CATEGORÍA
        # Ejemplo: "bebidas", "snacks", "lacteos"
        if categoria_solicitada and len(recomendaciones) < max_recomendaciones:
            print(f"🎯 ESTRATEGIA 3: Búsqueda por categoría")
            print(f"   📍 Categoría: {categoria_solicitada}")
            
            try:
                # Normalizar categoría y buscar
                categoria_normalizada = self.normalizar_categoria(categoria_solicitada)
                productos_categoria = self.base_datos.obtener_productos_por_categoria(
                    categoria_normalizada, max_recomendaciones * 2
                )
                print(f"      → Encontrados {len(productos_categoria)} productos en categoría '{categoria_normalizada}'")
                
                for producto in productos_categoria:
                    if len(recomendaciones) >= max_recomendaciones:
                        break
                    
                    # Evitar duplicados
                    if any(r['product_id'] == producto.get('id', 0) for r in recomendaciones):
                        continue
                    
                    score = 0.8  # Score alto para categoría exacta
                    razones = ['categoria_correcta', 'busqueda_por_categoria']
                    
                    # Bonus si coinciden atributos
                    if atributos_solicitados:
                        atributos_producto = producto.get('atributos', [])
                        coincidencias_atributos = len(set(atributos_solicitados) & set(atributos_producto))
                        if coincidencias_atributos > 0:
                            score += 0.1 * coincidencias_atributos
                            razones.append('atributos_coinciden')
                    
                    recomendacion = {
                        'product_id': producto.get('id', 0),
                        'name': producto['nombre'],
                        'category': producto['categoria'],
                        'price': producto['precio'],
                        'available': producto.get('disponible', True),
                        'stock': producto.get('stock', producto.get('cantidad', 100)),
                        'match_score': round(min(score, 1.0), 2),
                        'match_reasons': razones
                    }
                    recomendaciones.append(recomendacion)
                    print(f"      ✅ Agregado: {producto['nombre']} (score: {score:.2f})")
                    
            except Exception as e:
                print(f"      ❌ Error buscando categoría '{categoria_solicitada}': {e}")
        
        # ESTRATEGIA 4: BÚSQUEDA INTELIGENTE COMBINADA
        # Si aún no hay suficientes resultados, hacer búsqueda más amplia
        if len(recomendaciones) < max_recomendaciones // 2:
            print(f"🎯 ESTRATEGIA 4: Búsqueda inteligente combinada")
            
            # Construir query combinada
            terminos_busqueda = []
            if producto_solicitado:
                terminos_busqueda.append(producto_solicitado)
            if categoria_solicitada:
                terminos_busqueda.append(categoria_solicitada)
            if atributos_solicitados:
                terminos_busqueda.extend(atributos_solicitados)
            
            if terminos_busqueda:
                query_combinada = ' '.join(terminos_busqueda)
                print(f"   📍 Query combinada: {query_combinada}")
                
                try:
                    productos_combinados = self.base_datos.buscar_productos_inteligente(
                        query_combinada, limite=max_recomendaciones
                    )
                    print(f"      → Encontrados {len(productos_combinados)} productos con búsqueda combinada")
                    
                    for producto in productos_combinados:
                        if len(recomendaciones) >= max_recomendaciones:
                            break
                        
                        # Evitar duplicados
                        if any(r['product_id'] == producto.get('id', 0) for r in recomendaciones):
                            continue
                        
                        score = producto.get('similitud', 0.7)
                        razones = ['busqueda_combinada', 'busqueda_inteligente']
                        
                        recomendacion = {
                            'product_id': producto.get('id', 0),
                            'name': producto['nombre'],
                            'category': producto['categoria'],
                            'price': producto['precio'],
                            'available': producto.get('disponible', True),
                            'stock': producto.get('stock', producto.get('cantidad', 100)),
                            'match_score': round(min(score, 1.0), 2),
                            'match_reasons': razones
                        }
                        recomendaciones.append(recomendacion)
                        print(f"      ✅ Agregado: {producto['nombre']} (score: {score:.2f})")
                        
                except Exception as e:
                    print(f"      ❌ Error en búsqueda combinada: {e}")
        
        # ESTRATEGIA 5: FALLBACK A PRODUCTOS POPULARES (solo si no hay nada)
        if not recomendaciones:
            print(f"🎯 ESTRATEGIA 5: Fallback a productos populares")
            try:
                productos_populares = self.base_datos.obtener_productos_populares(max_recomendaciones)
                print(f"      → Mostrando {len(productos_populares)} productos populares como fallback")
                
                for producto in productos_populares:
                    razones = ['producto_popular', 'recomendacion_general']
                    
                    recomendacion = {
                        'product_id': producto.get('id', 0),
                        'name': producto['nombre'],
                        'category': producto['categoria'],
                        'price': producto['precio'],
                        'available': producto.get('disponible', True),
                        'stock': producto.get('stock', producto.get('cantidad', 100)),
                        'match_score': 0.5,  # Score bajo para populares
                        'match_reasons': razones
                    }
                    recomendaciones.append(recomendacion)
                    
            except Exception as e:
                print(f"      ❌ Error obteniendo productos populares: {e}")
        
        # APLICAR FILTROS DE PRECIO
        if filtros.get('precio') and recomendaciones:
            print(f"💰 Aplicando filtros de precio: {filtros['precio']}")
            filtro_precio = filtros['precio']
            recomendaciones_filtradas = []
            
            for rec in recomendaciones:
                precio = rec['price']
                cumple_filtro = True
                
                if 'max' in filtro_precio and precio > filtro_precio['max']:
                    cumple_filtro = False
                if 'min' in filtro_precio and precio < filtro_precio['min']:
                    cumple_filtro = False
                
                if cumple_filtro:
                    # Bonus por cumplir filtro de precio
                    if 'precio_en_rango' not in rec['match_reasons']:
                        rec['match_reasons'].append('precio_en_rango')
                        rec['match_score'] = min(1.0, rec['match_score'] + 0.05)
                    recomendaciones_filtradas.append(rec)
                    
            recomendaciones = recomendaciones_filtradas
            print(f"      → {len(recomendaciones)} productos cumplen filtros de precio")
        
        # ORDENAR Y LIMITAR RESULTADOS
        recomendaciones.sort(key=lambda x: x['match_score'], reverse=True)
        recomendaciones_finales = recomendaciones[:max_recomendaciones]
        
        print(f"✅ MOTOR COMPLETADO: {len(recomendaciones_finales)} recomendaciones generadas")
        for i, rec in enumerate(recomendaciones_finales[:3], 1):  # Mostrar top 3
            print(f"   {i}. {rec['name']} (score: {rec['match_score']:.2f})")
        
        return recomendaciones_finales
    
    def calcular_score_producto(self, producto: Dict, interpretacion: Dict) -> float:
        """Calcula el score de relevancia de un producto para la consulta"""
        score = 0.3  # Base score reducido
        
        categoria_consulta = interpretacion.get('categoria', '').lower()
        producto_consulta = interpretacion.get('producto')
        if producto_consulta:
            producto_consulta = producto_consulta.lower().strip()
        else:
            producto_consulta = ''  # Asegurar que no sea None
        
        # Normalizar categorías para que coincidan
        categoria_producto = producto['categoria'].lower()
        if categoria_consulta:
            categoria_normalizada = self.normalizar_categoria(categoria_consulta)
            
            # Score alto por categoría exacta
            if categoria_producto == categoria_normalizada:
                score += 0.5  # Bonus significativo por categoría correcta
            
        # Score por similitud de nombre de producto específico
        if producto_consulta:
            nombre_producto = producto['nombre'].lower()
            
            # Score máximo si el producto está en el nombre
            if producto_consulta in nombre_producto:
                score += 0.6  # Bonus alto para producto específico
            elif any(palabra in nombre_producto for palabra in producto_consulta.split()):
                score += 0.3  # Bonus medio para coincidencia parcial
            
            # Bonus adicional para productos de la misma familia
            if self.son_productos_relacionados(producto_consulta, nombre_producto):
                score += 0.2
        
        # Score por disponibilidad
        if producto.get('disponible', True):
            score += 0.05
        
        # Penalizar si stock muy bajo
        stock = producto.get('cantidad', 0)
        if stock < 5:
            score -= 0.1
        elif stock > 50:
            score += 0.05  # Bonus por stock alto
        
        return min(1.0, max(0.0, score))
    
    def normalizar_categoria(self, categoria: str) -> str:
        """Normaliza categorías para que coincidan entre interpretador y BD"""
        mapeo = {
            'snacks salados': 'snacks',
            'bebidas': 'bebidas',
            'lácteos': 'lacteos',
            'lacteos': 'lacteos',
            'frutas': 'frutas',
            'verduras': 'verduras',
            'panadería': 'panaderia',
            'panaderia': 'panaderia',
            'carnes': 'carnes',
            'limpieza': 'limpieza',
            'dulcería': 'dulceria',
            'dulceria': 'dulceria'
        }
        return mapeo.get(categoria.lower(), categoria.lower())
    
    def son_productos_relacionados(self, producto_consulta: str, nombre_producto: str) -> bool:
        """Determina si dos productos están relacionados (misma familia) - 20+ familias"""
        familias = {
            # Snacks salados (30+ productos)
            'papitas': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'takis'],
            'papas': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'takis'], 
            'snacks': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'takis', 'palomitas'],
            'botanas': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'takis', 'palomitas'],
            'picante': ['takis', 'cheetos', 'doritos', 'jalapeños'],
            'picantes': ['takis', 'cheetos', 'doritos', 'jalapeños'],
            'salado': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'cacahuates'],
            'crujiente': ['sabritas', 'doritos', 'ruffles', 'palomitas'],
            
            # Bebidas (25+ productos)
            'refrescos': ['coca', 'pepsi', 'sprite', 'fanta'],
            'colas': ['coca', 'pepsi'], 'cola': ['coca', 'pepsi'],
            'gaseosas': ['coca', 'pepsi', 'sprite', 'fanta'],
            'bebida': ['coca', 'pepsi', 'agua', 'jugo', 'electrolit'],
            'bebidas': ['coca', 'pepsi', 'agua', 'jugo', 'electrolit'],
            'jugos': ['jumex', 'boing', 'naranja', 'mango'],
            'agua': ['bonafont', 'ciel', 'epura', 'electrolit'],
            'energizante': ['electrolit', 'gatorade', 'powerade'],
            'sin-azucar': ['coca zero', 'pepsi light', 'sprite zero'],
            
            # Lácteos (15+ productos)
            'lacteos': ['leche', 'yogurt', 'queso'], 'lácteos': ['leche', 'yogurt', 'queso'],
            'leche': ['lala', 'alpura', 'lactaid', 'deslactosada'],
            'yogurt': ['danone', 'yoplait', 'chobani', 'fresa'],
            'queso': ['philadelphia', 'oaxaca', 'manchego', 'panela'],
            'cremoso': ['yogurt', 'queso', 'crema'],
            'light': ['yogurt light', 'leche descremada', 'queso light'],
            
            # Dulces y chocolates (20+ productos)
            'chocolate': ['emperador', 'chokis', 'carlos', 'hersheys'],
            'chocolates': ['emperador', 'chokis', 'carlos', 'hersheys'],
            'dulce': ['paleta', 'gomitas', 'chocolate', 'caramelo'],
            'dulces': ['paleta', 'gomitas', 'chocolate', 'caramelo'],
            'gomitas': ['panditas', 'haribo', 'ricolino'],
            'galletas': ['gamesa', 'nabisco', 'chokis', 'marías'],
            'paletas': ['payaso', 'paleta rica', 'michoacana'],
            
            # Panadería (10+ productos)
            'pan': ['bimbo', 'wonder', 'tía rosa'],
            'pastel': ['marinela', 'bimbo', 'gansito'],
            'dona': ['bimbo', 'dunkin'],
            'integral': ['pan integral', 'galletas integrales']
        }
        
        for familia, productos in familias.items():
            if any(p in producto_consulta for p in productos) and any(p in nombre_producto for p in productos):
                return True
            # También verificar si el producto consultado es el nombre de la familia
            if producto_consulta == familia and any(p in nombre_producto for p in productos):
                return True
            # Verificar sinónimos inversos
            if familia in producto_consulta and any(p in nombre_producto for p in productos):
                return True
        return False
    
    def generar_razones_match(self, producto: Dict, interpretacion: Dict, score: float) -> List[str]:
        """Genera las razones por las que un producto coincide con la consulta"""
        razones = []
        
        # Razón por categoría
        categoria_consulta = interpretacion.get('categoria')
        if categoria_consulta and producto['categoria'] == categoria_consulta:
            razones.append('categoria_correcta')
        
        # Razón por producto
        producto_consulta = interpretacion.get('producto', '')
        if producto_consulta:
            nombre_producto = producto['nombre'].lower()
            if producto_consulta.lower() in nombre_producto:
                razones.append('producto_exacto')
            else:
                razones.append('producto_similar')
        
        # Razón por precio
        precio = producto['precio']
        if precio <= 15.0:
            razones.append('precio_economico')
        elif precio <= 30.0:
            razones.append('precio_moderado')
        
        # Razón por disponibilidad
        if producto.get('disponible', True):
            razones.append('disponible')
        
        # Razón por score alto
        if score >= 0.8:
            razones.append('alta_similitud')
        elif score >= 0.6:
            razones.append('buena_similitud')
        
        return razones[:4]  # Máximo 4 razones
    
    def _generar_razones_match(self, consulta: Dict, producto: Dict, similitud: float) -> List[str]:
        """Genera las razones por las que un producto hace match"""
        razones = []
        
        if consulta.get('categoria') == producto.get('categoria'):
            razones.append('categoria_correcta')
        
        if consulta.get('filtro_precio') and self.precio_en_rango(
            producto.get('precio', 0), consulta['filtro_precio']
        ):
            razones.append('precio_en_rango')
        elif consulta.get('filtro_precio'):
            razones.append('precio_cercano')
        
        if consulta.get('atributos'):
            consulta_attrs = set(consulta['atributos'])
            producto_attrs = set(producto.get('atributos', []))
            if consulta_attrs.intersection(producto_attrs):
                razones.append('atributos_coinciden')
        
        if similitud > 0.8:
            razones.append('alta_similitud')
        elif similitud > 0.6:
            razones.append('buena_similitud')
        
        return razones if razones else ['producto_similar']
    
    def generar_mensaje_usuario(self, interpretacion: Dict, 
                              recomendaciones: List[Dict]) -> str:
        """Genera un mensaje amigable para el usuario"""
        if not recomendaciones:
            return "No se encontraron productos que coincidan con tu búsqueda."
        
        categoria = interpretacion.get('categoria', 'productos')
        filtros_precio = interpretacion.get('filtros', {}).get('precio', {})
        atributos = interpretacion.get('filtros', {}).get('atributos', [])
        
        mensaje = f"Mostrando {categoria}"
        
        # Agregar información de atributos
        if atributos:
            attrs_texto = []
            for attr in atributos:
                if isinstance(attr, dict):
                    attr_nombre = attr.get('atributo', '')
                    modificador = attr.get('modificador', '')
                    if modificador == 'sin':
                        attrs_texto.append(f"sin {attr_nombre}")
                    elif modificador == 'con':
                        attrs_texto.append(f"con {attr_nombre}")
                    else:
                        attrs_texto.append(attr_nombre)
                else:
                    attrs_texto.append(str(attr))
            
            if attrs_texto:
                mensaje += f" {' y '.join(attrs_texto)}"
        
        # Agregar información de precio
        if 'max' in filtros_precio:
            mensaje += f" económicos (menos de ${filtros_precio['max']})"
        elif 'min' in filtros_precio:
            mensaje += f" premium (más de ${filtros_precio['min']})"
        elif filtros_precio.get('tendency') == 'low':
            mensaje += " económicos"
        elif filtros_precio.get('tendency') == 'high':
            mensaje += " premium"
        
        return mensaje

    def calcular_score_producto_escalable(self, producto: Dict, interpretacion: Dict) -> float:
        """Calcula score para productos de la base escalable"""
        score = 0.0
        
        # Score por nombre
        producto_solicitado = interpretacion.get('producto', '')
        if producto_solicitado and producto_solicitado.lower() in producto['nombre'].lower():
            score += 0.4
        
        # Score por categoría  
        categoria_solicitada = interpretacion.get('categoria', '')
        if categoria_solicitada and categoria_solicitada.lower() in producto['categoria'].lower():
            score += 0.3
        
        # Score por atributos
        atributos = interpretacion.get('atributos', [])
        if atributos:
            # Simular que productos con nombre que contiene el atributo lo tienen
            for atributo in atributos:
                if atributo.lower() in producto['nombre'].lower():
                    score += 0.3
                    break
        
        return min(score, 1.0)
    
    def generar_razones_match_escalable(self, producto: Dict, interpretacion: Dict, score: float) -> List[str]:
        """Genera razones del match para productos escalables"""
        razones = []
        
        if score > 0.8:
            razones.append('alta_similitud')
        elif score > 0.6:
            razones.append('buena_similitud')
        
        # Verificar coincidencias específicas
        producto_solicitado = interpretacion.get('producto', '')
        if producto_solicitado and producto_solicitado.lower() in producto['nombre'].lower():
            razones.append('producto_exacto')
        
        categoria_solicitada = interpretacion.get('categoria', '')
        if categoria_solicitada and categoria_solicitada.lower() in producto['categoria'].lower():
            razones.append('categoria_correcta')
        
        atributos = interpretacion.get('atributos', [])
        for atributo in atributos:
            if atributo.lower() in producto['nombre'].lower():
                razones.append(f'atributo_{atributo}')
        
        if not razones:
            razones.append('producto_similar')
        
        return razones
