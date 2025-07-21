"""
SISTEMA LCLN CON PRIORIDADES INTELIGENTES
Implementación del motor de búsqueda mejorado con sistema de prioridades para resultados
Basado en la estrategia definida en ESTRATEGIA_SISTEMA_LCLN_MEJORADO.md

Autor: Sistema LCLN v2.0
Fecha: Julio 2025
"""

import mysql.connector
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import re
from corrector_ortografico import CorrectorOrtografico


class SistemaLCLNConPrioridades:
    """
    Sistema LCLN mejorado con prioridades inteligentes para presentación de resultados
    
    Orden de prioridades:
    🥇 Productos específicos por sinónimo directo en BD
    🥈 Productos por atributos exactos (sin picante, sin azúcar)
    🥉 Productos por categoría relacionada
    🏃 Fallback con corrección ortográfica
    """
    
    def __init__(self):
        # Configuración MySQL
        self.mysql_config = {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': '12345678',
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        # Corrector ortográfico
        self.corrector = CorrectorOrtografico()
        
        # Sistema de pesos para prioridades
        self.pesos_prioridad = {
            'producto_especifico_sinonimo': 1.0,    # Máxima prioridad
            'atributos_exactos': 0.85,              # Alta prioridad
            'categoria_relacionada': 0.7,           # Prioridad media
            'popularidad_boost': 0.2,               # Boost adicional
            'fallback_correccion': 0.4              # Baja prioridad
        }
        
        # Cache de conexiones y resultados
        self._cache_productos = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)
        
        # Analizador de negaciones mejorado
        self.analizador_negaciones = AnalizadorNegacionesAvanzado()

    def buscar_con_prioridades(self, consulta: str, limit: int = 20, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Método principal de búsqueda con sistema de prioridades inteligentes
        
        Args:
            consulta: Consulta del usuario (ej: "chettos sin picante baratos")
            limit: Número máximo de resultados
            user_id: ID del usuario para métricas (opcional)
            
        Returns:
            Diccionario con resultados ordenados por prioridades
        """
        inicio = datetime.now()
        consulta_original = consulta.strip()
        
        if not consulta_original:
            return self._respuesta_vacia("Consulta vacía")
        
        # PASO 1: Análisis completo de la consulta (mantiene flujo LCLN)
        analisis = self._analizar_consulta_completa(consulta_original)
        
        # PASO 2: Búsqueda por sistema de prioridades
        resultados_priorizados = []
        estrategias_usadas = []
        correcciones_aplicadas = False
        
        try:
            # 🥇 PRIORIDAD 1: Productos específicos por sinónimo directo
            productos_especificos = self._buscar_productos_especificos(analisis['terminos'])
            if productos_especificos:
                for producto in productos_especificos:
                    producto['priority_score'] = self.pesos_prioridad['producto_especifico_sinonimo']
                    producto['priority_type'] = 'producto_especifico'
                    producto['priority_order'] = 1
                resultados_priorizados.extend(productos_especificos)
                estrategias_usadas.append("productos_especificos")
            
            # 🥈 PRIORIDAD 2: Productos por atributos exactos
            if len(resultados_priorizados) < limit:
                productos_atributos = self._buscar_por_atributos_exactos(
                    analisis['negaciones'], 
                    analisis['atributos_positivos'],
                    analisis['filtros_precio'],
                    limit - len(resultados_priorizados)
                )
                if productos_atributos:
                    for producto in productos_atributos:
                        producto['priority_score'] = self.pesos_prioridad['atributos_exactos']
                        producto['priority_type'] = 'atributos_exactos'
                        producto['priority_order'] = 2
                    resultados_priorizados.extend(productos_atributos)
                    estrategias_usadas.append("atributos_exactos")
            
            # 🥉 PRIORIDAD 3: Productos por categoría
            if len(resultados_priorizados) < limit:
                productos_categoria = self._buscar_por_categoria(
                    analisis['categoria_inferida'],
                    analisis['filtros_precio'],
                    limit - len(resultados_priorizados)
                )
                if productos_categoria:
                    for producto in productos_categoria:
                        producto['priority_score'] = self.pesos_prioridad['categoria_relacionada']
                        producto['priority_type'] = 'categoria_relacionada'
                        producto['priority_order'] = 3
                    resultados_priorizados.extend(productos_categoria)
                    estrategias_usadas.append("categoria_relacionada")
            
            # 🏃 PRIORIDAD 4: Fallback con corrección ortográfica
            if len(resultados_priorizados) < max(3, limit // 3):
                resultado_correcciones = self.corrector.corregir_consulta(consulta_original)
                if resultado_correcciones.get('applied', False):
                    correcciones_aplicadas = True
                    consulta_corregida = resultado_correcciones.get('corrected_query', consulta_original)
                    
                    productos_fallback = self._buscar_fallback_completo(
                        consulta_corregida,
                        limit - len(resultados_priorizados)
                    )
                    if productos_fallback:
                        for producto in productos_fallback:
                            producto['priority_score'] = self.pesos_prioridad['fallback_correccion']
                            producto['priority_type'] = 'fallback_correccion'
                            producto['priority_order'] = 4
                        resultados_priorizados.extend(productos_fallback)
                        estrategias_usadas.append("fallback_correccion")
            
            # PASO 3: Aplicar ranking final y eliminar duplicados
            resultados_finales = self._aplicar_ranking_final(resultados_priorizados, analisis)
            
            # PASO 4: Registrar métricas para aprendizaje automático
            if user_id and resultados_finales:
                self._registrar_metricas_busqueda(consulta_original, resultados_finales[:5], user_id)
            
            tiempo_total = (datetime.now() - inicio).total_seconds() * 1000
            
            return {
                'success': True,
                'processing_time_ms': round(tiempo_total, 2),
                'original_query': consulta_original,
                'corrections': {
                    'applied': correcciones_aplicadas,
                    'details': resultado_correcciones if correcciones_aplicadas else {}
                },
                'interpretation': {
                    'terminos_detectados': analisis['terminos'],
                    'negaciones': analisis['negaciones'],
                    'atributos_positivos': analisis['atributos_positivos'],
                    'categoria_inferida': analisis['categoria_inferida'],
                    'filtros_precio': analisis['filtros_precio']
                },
                'recommendations': resultados_finales[:limit],
                'products_found': len(resultados_finales),
                'priority_breakdown': self._generar_breakdown_prioridades(resultados_finales[:limit]),
                'strategies_used': estrategias_usadas,
                'user_message': self._generar_mensaje_inteligente(analisis, estrategias_usadas, len(resultados_finales)),
                'metadata': {
                    'search_type': 'lcln_with_priorities',
                    'has_specific_products': 'productos_especificos' in estrategias_usadas,
                    'has_attribute_filters': len(analisis['negaciones']) > 0 or len(analisis['atributos_positivos']) > 0,
                    'has_corrections': correcciones_aplicadas,
                    'priority_levels_used': len(set(r.get('priority_order', 0) for r in resultados_finales))
                }
            }
            
        except Exception as e:
            print(f"Error en búsqueda con prioridades: {e}")
            return self._respuesta_error(str(e), consulta_original)

    def _buscar_productos_especificos(self, terminos: List[str]) -> List[Dict[str, Any]]:
        """
        🥇 PRIORIDAD 1: Buscar productos específicos usando sinónimos directos en BD
        """
        if not terminos:
            return []
        
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            # Búsqueda por sinónimos específicos
            placeholders = ','.join(['%s'] * len(terminos))
            query = f"""
            SELECT DISTINCT 
                p.id_producto as id,
                p.nombre,
                p.precio,
                p.descripcion,
                p.imagen,
                p.cantidad,
                p.activo,
                c.nombre as categoria,
                ps.sinonimo as sinonimo_usado,
                ps.popularidad,
                ps.precision_score
            FROM productos p
            INNER JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE ps.sinonimo IN ({placeholders}) 
              AND ps.activo = 1 
              AND p.activo = 1
              AND p.cantidad > 0
            ORDER BY ps.popularidad DESC, ps.precision_score DESC, p.precio ASC
            LIMIT 10
            """
            
            cursor.execute(query, terminos)
            resultados = cursor.fetchall()
            
            productos_encontrados = []
            for row in resultados:
                producto = {
                    'id': row['id'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'categoria': row['categoria'],
                    'descripcion': row['descripcion'] or '',
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.95 + (float(row['precision_score']) * 0.05),
                    'match_type': 'producto_especifico_sinonimo',
                    'match_details': {
                        'sinonimo_usado': row['sinonimo_usado'],
                        'popularidad': row['popularidad'],
                        'precision_score': float(row['precision_score']),
                        'source': 'mysql_producto_sinonimos'
                    },
                    'confidence': min(0.95 + (row['popularidad'] * 0.001), 1.0)
                }
                productos_encontrados.append(producto)
            
            return productos_encontrados
            
        except Exception as e:
            print(f"Error en búsqueda específica: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _buscar_por_atributos_exactos(self, negaciones: List[Dict], 
                                      atributos_positivos: List[str],
                                      filtros_precio: Dict,
                                      limit: int) -> List[Dict[str, Any]]:
        """
        🥈 PRIORIDAD 2: Buscar productos por atributos exactos (sin picante, sin azúcar, etc.)
        """
        if not negaciones and not atributos_positivos and not filtros_precio:
            return []
        
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            # Query base optimizada
            query_base = """
            SELECT DISTINCT 
                p.id_producto as id,
                p.nombre,
                p.precio,
                p.descripcion,
                p.imagen,
                p.cantidad,
                c.nombre as categoria,
                GROUP_CONCAT(
                    CONCAT(pa.atributo, ':', pa.valor, ':', pa.intensidad) 
                    SEPARATOR ';'
                ) as atributos_detalle
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            LEFT JOIN producto_atributos pa ON p.id_producto = pa.producto_id
            WHERE p.activo = 1 AND p.cantidad > 0
            """
            
            condiciones = []
            parametros = []
            
            # Manejar negaciones (sin picante, sin azúcar)
            if negaciones:
                for negacion in negaciones:
                    atributo = negacion.get('atributo', '').lower()
                    if atributo:
                        condiciones.append(f"""
                            p.id_producto IN (
                                SELECT pa2.producto_id 
                                FROM producto_atributos pa2 
                                WHERE pa2.atributo = %s AND pa2.valor = FALSE
                                UNION
                                SELECT p2.id_producto 
                                FROM productos p2 
                                WHERE p2.id_producto NOT IN (
                                    SELECT pa3.producto_id 
                                    FROM producto_atributos pa3 
                                    WHERE pa3.atributo = %s
                                )
                            )
                        """)
                        parametros.extend([atributo, atributo])
            
            # Manejar atributos positivos (picante, dulce)
            if atributos_positivos:
                for atributo in atributos_positivos:
                    condiciones.append("""
                        p.id_producto IN (
                            SELECT pa4.producto_id 
                            FROM producto_atributos pa4 
                            WHERE pa4.atributo = %s AND pa4.valor = TRUE
                        )
                    """)
                    parametros.append(atributo.lower())
            
            # Filtros de precio
            if filtros_precio:
                if filtros_precio.get('max'):
                    condiciones.append("p.precio <= %s")
                    parametros.append(filtros_precio['max'])
                if filtros_precio.get('min'):
                    condiciones.append("p.precio >= %s")
                    parametros.append(filtros_precio['min'])
                if filtros_precio.get('tendency') == 'low':
                    # Precio menor al promedio
                    condiciones.append("""
                        p.precio < (SELECT AVG(precio) FROM productos WHERE activo = 1)
                    """)
            
            # Construir query final
            if condiciones:
                query_final = query_base + " AND (" + " AND ".join(condiciones) + ")"
            else:
                return []  # No hay filtros de atributos
            
            query_final += " GROUP BY p.id_producto ORDER BY p.precio ASC LIMIT %s"
            parametros.append(limit)
            
            cursor.execute(query_final, parametros)
            resultados = cursor.fetchall()
            
            productos_encontrados = []
            for row in resultados:
                producto = {
                    'id': row['id'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'categoria': row['categoria'],
                    'descripcion': row['descripcion'] or '',
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.8,
                    'match_type': 'atributos_exactos',
                    'match_details': {
                        'negaciones_aplicadas': [n.get('atributo', '') for n in negaciones],
                        'atributos_positivos': atributos_positivos,
                        'filtros_precio': filtros_precio,
                        'atributos_producto': row['atributos_detalle'] or ''
                    },
                    'confidence': 0.85
                }
                productos_encontrados.append(producto)
            
            return productos_encontrados
            
        except Exception as e:
            print(f"Error en búsqueda por atributos: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _buscar_por_categoria(self, categoria_inferida: Optional[str], 
                              filtros_precio: Dict,
                              limit: int) -> List[Dict[str, Any]]:
        """
        🥉 PRIORIDAD 3: Buscar productos por categoría relacionada
        """
        if not categoria_inferida:
            return []
        
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            # Query por categoría
            query = """
            SELECT DISTINCT 
                p.id_producto as id,
                p.nombre,
                p.precio,
                p.descripcion,
                p.imagen,
                p.cantidad,
                c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.activo = 1 
              AND p.cantidad > 0
              AND (LOWER(c.nombre) = %s OR LOWER(c.nombre) LIKE %s)
            """
            
            parametros = [categoria_inferida.lower(), f"%{categoria_inferida.lower()}%"]
            
            # Agregar filtros de precio si existen
            if filtros_precio:
                if filtros_precio.get('max'):
                    query += " AND p.precio <= %s"
                    parametros.append(filtros_precio['max'])
                if filtros_precio.get('min'):
                    query += " AND p.precio >= %s"
                    parametros.append(filtros_precio['min'])
                if filtros_precio.get('tendency') == 'low':
                    query += " AND p.precio < (SELECT AVG(precio) FROM productos WHERE activo = 1)"
            
            query += " ORDER BY p.precio ASC LIMIT %s"
            parametros.append(limit)
            
            cursor.execute(query, parametros)
            resultados = cursor.fetchall()
            
            productos_encontrados = []
            for row in resultados:
                producto = {
                    'id': row['id'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'categoria': row['categoria'],
                    'descripcion': row['descripcion'] or '',
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.7,
                    'match_type': 'categoria_relacionada',
                    'match_details': {
                        'categoria_buscada': categoria_inferida,
                        'categoria_encontrada': row['categoria'],
                        'filtros_precio': filtros_precio
                    },
                    'confidence': 0.7
                }
                productos_encontrados.append(producto)
            
            return productos_encontrados
            
        except Exception as e:
            print(f"Error en búsqueda por categoría: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _buscar_fallback_completo(self, consulta_corregida: str, limit: int) -> List[Dict[str, Any]]:
        """
        🏃 PRIORIDAD 4: Búsqueda de fallback con corrección ortográfica
        """
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            # Búsqueda por texto en nombre y descripción
            terminos = consulta_corregida.lower().split()
            
            if not terminos:
                return []
            
            # Construir condiciones LIKE para cada término
            condiciones_like = []
            parametros = []
            
            for termino in terminos:
                if len(termino) > 2:  # Solo términos significativos
                    condiciones_like.append("(LOWER(p.nombre) LIKE %s OR LOWER(p.descripcion) LIKE %s)")
                    parametros.extend([f"%{termino}%", f"%{termino}%"])
            
            if not condiciones_like:
                return []
            
            query = f"""
            SELECT DISTINCT 
                p.id_producto as id,
                p.nombre,
                p.precio,
                p.descripcion,
                p.imagen,
                p.cantidad,
                c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.activo = 1 
              AND p.cantidad > 0
              AND ({' OR '.join(condiciones_like)})
            ORDER BY p.precio ASC
            LIMIT %s
            """
            
            parametros.append(limit)
            
            cursor.execute(query, parametros)
            resultados = cursor.fetchall()
            
            productos_encontrados = []
            for row in resultados:
                producto = {
                    'id': row['id'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'categoria': row['categoria'],
                    'descripcion': row['descripcion'] or '',
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.4,
                    'match_type': 'fallback_correccion',
                    'match_details': {
                        'consulta_corregida': consulta_corregida,
                        'terminos_buscados': terminos
                    },
                    'confidence': 0.4
                }
                productos_encontrados.append(producto)
            
            return productos_encontrados
            
        except Exception as e:
            print(f"Error en búsqueda fallback: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _analizar_consulta_completa(self, consulta: str) -> Dict[str, Any]:
        """
        Análisis completo de la consulta (mantiene flujo LCLN original)
        """
        terminos = [t.strip().lower() for t in consulta.split() if t.strip()]
        
        analisis = {
            'terminos': terminos,
            'negaciones': [],
            'atributos_positivos': [],
            'filtros_precio': {},
            'categoria_inferida': None
        }
        
        # Detectar negaciones usando analizador avanzado
        negaciones_detectadas = self.analizador_negaciones.detectar_negaciones(consulta)
        analisis['negaciones'] = negaciones_detectadas
        
        # Detectar filtros de precio
        filtros_precio = self._detectar_filtros_precio(consulta)
        if filtros_precio:
            analisis['filtros_precio'] = filtros_precio
        
        # Detectar atributos positivos
        atributos_conocidos = ['picante', 'dulce', 'salado', 'grande', 'pequeño', 'natural']
        for termino in terminos:
            if termino in atributos_conocidos and not any(neg.get('atributo') == termino for neg in negaciones_detectadas):
                analisis['atributos_positivos'].append(termino)
        
        # Inferir categoría
        categoria = self._inferir_categoria(terminos)
        if categoria:
            analisis['categoria_inferida'] = categoria
        
        return analisis

    def _detectar_filtros_precio(self, consulta: str) -> Dict[str, Any]:
        """
        Detectar filtros de precio en la consulta
        """
        filtros = {}
        consulta_lower = consulta.lower()
        
        # Patrones mejorados para detectar precios
        patron_menor = r'(?:menor|menos|bajo)\s+(?:de|a|que)?\s*\$?(\d+)'
        patron_mayor = r'(?:mayor|mas|más|alto)\s+(?:de|a|que)?\s*\$?(\d+)'
        patron_entre = r'entre\s+\$?(\d+)\s+y\s+\$?(\d+)'
        patron_exacto = r'\$(\d+)'
        patron_barato = r'\b(?:barato|barata|económico|económica|bara)\b'
        patron_caro = r'\b(?:caro|cara|costoso|costosa|premium)\b'
        
        # Menor que
        match_menor = re.search(patron_menor, consulta_lower)
        if match_menor:
            filtros['max'] = int(match_menor.group(1))
        
        # Mayor que  
        match_mayor = re.search(patron_mayor, consulta_lower)
        if match_mayor:
            filtros['min'] = int(match_mayor.group(1))
        
        # Entre rango
        match_entre = re.search(patron_entre, consulta_lower)
        if match_entre:
            filtros['min'] = int(match_entre.group(1))
            filtros['max'] = int(match_entre.group(2))
        
        # Precio exacto
        match_exacto = re.search(patron_exacto, consulta)
        if match_exacto and not filtros:  # Solo si no hay otros filtros
            precio_exacto = int(match_exacto.group(1))
            filtros['min'] = precio_exacto - 5
            filtros['max'] = precio_exacto + 5
        
        # Términos de precio bajo/alto
        if re.search(patron_barato, consulta_lower):
            filtros['tendency'] = 'low'
        elif re.search(patron_caro, consulta_lower):
            filtros['tendency'] = 'high'
        
        return filtros

    def _inferir_categoria(self, terminos: List[str]) -> Optional[str]:
        """
        Inferir categoría basada en términos de la consulta
        """
        mapeo_categorias = {
            # Snacks/Botanas
            'botana': 'snacks', 'snack': 'snacks', 'papas': 'snacks',
            'doritos': 'snacks', 'cheetos': 'snacks', 'crujitos': 'snacks',
            'galleta': 'snacks', 'galletas': 'snacks',
            
            # Bebidas
            'bebida': 'bebidas', 'bebidas': 'bebidas',
            'refresco': 'bebidas', 'refrescos': 'bebidas',
            'coca': 'bebidas', 'agua': 'bebidas',
            'jugo': 'bebidas', 'jugos': 'bebidas',
            
            # Panadería
            'pan': 'panaderia', 'panes': 'panaderia',
            'pastel': 'panaderia', 'pasteles': 'panaderia',
            
            # Frutas
            'fruta': 'frutas', 'frutas': 'frutas',
            'manzana': 'frutas', 'naranja': 'frutas',
            'platano': 'frutas', 'banana': 'frutas'
        }
        
        for termino in terminos:
            if termino in mapeo_categorias:
                return mapeo_categorias[termino]
        
        return None

    def _aplicar_ranking_final(self, productos: List[Dict[str, Any]], analisis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aplicar ranking final considerando prioridades y boost de popularidad
        """
        # Eliminar duplicados por ID
        productos_unicos = {}
        for producto in productos:
            producto_id = producto.get('id')
            if producto_id not in productos_unicos:
                productos_unicos[producto_id] = producto
            else:
                # Mantener el de mayor prioridad
                if producto.get('priority_order', 5) < productos_unicos[producto_id].get('priority_order', 5):
                    productos_unicos[producto_id] = producto
        
        productos_finales = list(productos_unicos.values())
        
        # Aplicar boost por popularidad y scoring final
        for producto in productos_finales:
            score_base = producto.get('priority_score', 0.5)
            
            # Boost por disponibilidad
            if producto.get('available', False):
                score_base += 0.05
            
            # Boost por precio en consultas de "barato"
            if analisis.get('filtros_precio', {}).get('tendency') == 'low':
                precio = producto.get('precio', 999)
                if precio < 25:  # Considerado barato
                    score_base += 0.1
            
            # Penalización por precio alto en consultas de "barato"
            elif analisis.get('filtros_precio', {}).get('tendency') == 'low':
                precio = producto.get('precio', 0)
                if precio > 50:  # Considerado caro
                    score_base -= 0.1
            
            producto['final_score'] = min(max(score_base, 0.0), 1.0)
        
        # Ordenar por: priority_order ASC, final_score DESC, precio ASC
        return sorted(productos_finales, key=lambda x: (
            x.get('priority_order', 5),  # Prioridad principal
            -x.get('final_score', 0),    # Score descendente
            x.get('precio', 999)         # Precio ascendente
        ))

    def _generar_breakdown_prioridades(self, productos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generar breakdown de cómo se distribuyeron los resultados por prioridad
        """
        breakdown = {
            'total_products': len(productos),
            'by_priority': {},
            'by_type': {}
        }
        
        for producto in productos:
            priority_order = producto.get('priority_order', 0)
            priority_type = producto.get('priority_type', 'unknown')
            
            if priority_order not in breakdown['by_priority']:
                breakdown['by_priority'][priority_order] = 0
            breakdown['by_priority'][priority_order] += 1
            
            if priority_type not in breakdown['by_type']:
                breakdown['by_type'][priority_type] = 0
            breakdown['by_type'][priority_type] += 1
        
        return breakdown

    def _generar_mensaje_inteligente(self, analisis: Dict[str, Any], 
                                   estrategias: List[str], 
                                   total_resultados: int) -> str:
        """
        Generar mensaje descriptivo inteligente para el usuario
        """
        mensajes = []
        
        # Mensaje base
        if total_resultados == 0:
            return "No se encontraron productos que coincidan con tu búsqueda"
        
        mensaje_base = f"Encontrados {total_resultados} productos"
        
        # Agregar detalles según estrategias usadas
        if 'productos_especificos' in estrategias:
            mensajes.append("productos específicos encontrados")
        
        if analisis.get('negaciones'):
            negaciones_texto = ', '.join([f"sin {neg.get('atributo', '')}" for neg in analisis['negaciones']])
            mensajes.append(f"con filtros: {negaciones_texto}")
        
        if analisis.get('atributos_positivos'):
            atributos_texto = ', '.join(analisis['atributos_positivos'])
            mensajes.append(f"con características: {atributos_texto}")
        
        if analisis.get('filtros_precio'):
            filtro = analisis['filtros_precio']
            if filtro.get('max'):
                mensajes.append(f"precio menor a ${filtro['max']}")
            elif filtro.get('tendency') == 'low':
                mensajes.append("productos económicos")
            elif filtro.get('tendency') == 'high':
                mensajes.append("productos premium")
        
        if 'fallback_correccion' in estrategias:
            mensajes.append("(con corrección ortográfica aplicada)")
        
        if mensajes:
            mensaje_base += f" - {', '.join(mensajes)}"
        
        return mensaje_base

    def _registrar_metricas_busqueda(self, consulta: str, productos: List[Dict[str, Any]], user_id: int):
        """
        Registrar métricas de búsqueda para aprendizaje automático futuro
        """
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor()
            
            session_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
            # Registrar cada producto en los primeros resultados
            for i, producto in enumerate(productos[:5]):
                cursor.execute("""
                    INSERT INTO busqueda_metricas 
                    (termino_busqueda, producto_id, session_id, fecha_busqueda)
                    VALUES (%s, %s, %s, %s)
                """, [
                    consulta.lower()[:255],  # Truncar si es muy largo
                    producto.get('id'), 
                    session_id,
                    datetime.now()
                ])
            
            conn.commit()
            
        except Exception as e:
            print(f"Error registrando métricas: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _respuesta_vacia(self, razon: str) -> Dict[str, Any]:
        """Respuesta para consultas vacías"""
        return {
            'success': False,
            'processing_time_ms': 0,
            'original_query': '',
            'error': razon,
            'recommendations': [],
            'products_found': 0,
            'user_message': f'Error: {razon}'
        }

    def _respuesta_error(self, error: str, consulta: str) -> Dict[str, Any]:
        """Respuesta para errores en búsqueda"""
        return {
            'success': False,
            'processing_time_ms': 0,
            'original_query': consulta,
            'error': error,
            'recommendations': [],
            'products_found': 0,
            'user_message': 'Error en la búsqueda. Inténtalo de nuevo.'
        }


class AnalizadorNegacionesAvanzado:
    """
    Clase especializada en detectar y manejar negaciones de forma avanzada
    """
    
    def __init__(self):
        # Palabras que indican negación
        self.palabras_negacion = [
            'sin', 'no', 'libre', 'zero', 'ningún', 'ninguna', 'nada', 'nunca'
        ]
        
        # Atributos comunes que pueden ser negados
        self.atributos_comunes = [
            'picante', 'azucar', 'azúcar', 'gluten', 'lactosa', 
            'sal', 'grasa', 'conservantes', 'artificiales', 'quimicos',
            'colorantes', 'endulzantes', 'sodio'
        ]
        
        # Patrones especiales
        self.patrones_especiales = {
            r'\bsin azucar\b': 'azucar',
            r'\bsin azúcar\b': 'azucar', 
            r'\bzero azucar\b': 'azucar',
            r'\blibre de gluten\b': 'gluten',
            r'\bsin gluten\b': 'gluten',
            r'\bsin picante\b': 'picante',
            r'\bno picante\b': 'picante',
            r'\bsin sal\b': 'sal',
            r'\blibre de lactosa\b': 'lactosa'
        }
    
    def detectar_negaciones(self, consulta: str) -> List[Dict[str, Any]]:
        """
        Detectar patrones de negación en la consulta de forma avanzada
        """
        negaciones_encontradas = []
        consulta_lower = consulta.lower()
        
        # 1. Buscar patrones especiales primero
        for patron, atributo in self.patrones_especiales.items():
            if re.search(patron, consulta_lower):
                negaciones_encontradas.append({
                    'palabra_negacion': 'sin',
                    'atributo': atributo,
                    'patron_usado': patron,
                    'confianza': 0.95,
                    'tipo': 'patron_especial'
                })
        
        # 2. Buscar patrones palabra por palabra
        tokens = consulta_lower.split()
        
        for i, token in enumerate(tokens):
            if token in self.palabras_negacion:
                # Buscar el siguiente token que sea un atributo conocido
                for j in range(i + 1, min(i + 4, len(tokens))):  # Buscar hasta 3 tokens adelante
                    token_candidato = tokens[j]
                    
                    # Verificar coincidencia exacta
                    if token_candidato in self.atributos_comunes:
                        # Evitar duplicados
                        if not any(neg.get('atributo') == token_candidato for neg in negaciones_encontradas):
                            negaciones_encontradas.append({
                                'palabra_negacion': token,
                                'atributo': token_candidato,
                                'posicion': i,
                                'confianza': 0.9,
                                'tipo': 'palabra_directa'
                            })
                        break
                    
                    # Verificar coincidencia parcial
                    elif any(attr.startswith(token_candidato) or token_candidato.startswith(attr) 
                            for attr in self.atributos_comunes):
                        attr_encontrado = next(attr for attr in self.atributos_comunes 
                                             if attr.startswith(token_candidato) or token_candidato.startswith(attr))
                        
                        if not any(neg.get('atributo') == attr_encontrado for neg in negaciones_encontradas):
                            negaciones_encontradas.append({
                                'palabra_negacion': token,
                                'atributo': attr_encontrado,
                                'posicion': i,
                                'confianza': 0.75,
                                'tipo': 'palabra_parcial'
                            })
                        break
        
        return negaciones_encontradas


# Instancia global del sistema mejorado
sistema_lcln_con_prioridades = SistemaLCLNConPrioridades()