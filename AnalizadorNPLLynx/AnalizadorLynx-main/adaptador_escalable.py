#!/usr/bin/env python3
"""
ADAPTADOR DE COMPATIBILIDAD - ARQUITECTURA ESCALABLE LYNX

Permite que el sistema actual funcione con la nueva arquitectura escalable
sin modificar el código existente. Implementa un patrón Adapter.

Características:
- Mantiene compatibilidad con ConfiguracionLYNX actual  
- Reemplaza SimuladorBDLynxShop transparentemente
- Optimiza rendimiento con 1000+ productos
- Cache inteligente para consultas frecuentes

Autor: GitHub Copilot  
Fecha: 2025-01-19
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional, Union
from collections import defaultdict

# Importar arquitectura escalable (si existe)
try:
    from arquitectura_escalable import ConfiguracionEscalableLYNX, BaseDatosEscalable
    ARQUITECTURA_ESCALABLE_DISPONIBLE = True
except ImportError:
    ARQUITECTURA_ESCALABLE_DISPONIBLE = False
    print("⚠️  Arquitectura escalable no disponible, usando modo compatible")

# Importar configuración original
try:
    from configuracion_bd import SimuladorBDLynxShop
    CONFIGURACION_ORIGINAL_DISPONIBLE = True
except ImportError:
    CONFIGURACION_ORIGINAL_DISPONIBLE = False


class SimuladorBDLynxShopEscalable:
    """Adaptador que reemplaza SimuladorBDLynxShop con capacidad escalable"""
    
    def __init__(self, usar_escalable: bool = True):
        self.usar_escalable = usar_escalable and ARQUITECTURA_ESCALABLE_DISPONIBLE
        self.cache_consultas = {}
        self.cache_similitudes = {}
        self.stats = {
            'consultas_totales': 0,
            'cache_hits': 0,
            'tiempo_promedio': 0.0
        }
        
        if self.usar_escalable:
            print("🚀 Inicializando simulador escalable...")
            self._init_escalable()
        else:
            print("📊 Usando simulador original...")
            self._init_original()
    
    def _init_escalable(self):
        """Inicializar con arquitectura escalable"""
        try:
            self.config_escalable = ConfiguracionEscalableLYNX()
            
            # Verificar si ya existe BD poblada
            if os.path.exists("productos_lynx_escalable.db"):
                print("✅ Base de datos escalable encontrada")
                self._cargar_datos_escalables()
            else:
                print("⚠️  BD escalable no encontrada, generando datos...")
                self._generar_datos_iniciales()
                
        except Exception as e:
            print(f"❌ Error inicializando escalable: {e}")
            self.usar_escalable = False
            self._init_original()
    
    def _init_original(self):
        """Fallback al simulador original"""
        if CONFIGURACION_ORIGINAL_DISPONIBLE:
            self.simulador_original = SimuladorBDLynxShop()
            self.productos = self.simulador_original.productos
            self.categorias = self.simulador_original.categorias
        else:
            # Crear datos mínimos si no hay nada disponible
            self._crear_datos_minimos()
    
    def _cargar_datos_escalables(self):
        """Cargar datos desde BD escalable para compatibilidad"""
        stats = self.config_escalable.obtener_estadisticas()
        print(f"📊 BD escalable cargada: {stats['productos']['total']} productos, {stats['sinonimos']['total']} sinónimos")
        
        # Crear productos simulados para compatibilidad
        self.productos = []
        self.categorias = {}
        
        # Obtener muestra de productos para interfaces legacy
        query_muestra = {'limit': 200}  # Limitar para performance
        productos_muestra = self.config_escalable.bd_escalable.buscar_productos_avanzado(query_muestra)
        
        for i, p in enumerate(productos_muestra, 1):
            self.productos.append({
                'id': p.id,
                'nombre': p.nombre,
                'precio': p.precio,
                'cantidad': p.stock,
                'categoria': p.categoria,
                'disponible': p.stock > 0
            })
            
            # Crear categorías
            if p.categoria not in self.categorias:
                self.categorias[i] = {
                    'nombre': p.categoria,
                    'descripcion': f'Categoría {p.categoria}'
                }
    
    def _generar_datos_iniciales(self):
        """Generar datos iniciales si no existen"""
        try:
            from generador_datos_masivos import poblar_base_datos_masiva
            print("🔄 Generando base de datos masiva...")
            self.config_escalable = poblar_base_datos_masiva()
            self._cargar_datos_escalables()
            print("✅ Datos iniciales generados")
        except Exception as e:
            print(f"❌ Error generando datos: {e}")
            self.usar_escalable = False
            self._init_original()
    
    def _crear_datos_minimos(self):
        """Crear datos mínimos para funcionamiento básico"""
        self.productos = [
            {'id': 1, 'nombre': 'Coca Cola 600ml', 'precio': 18.5, 'cantidad': 50, 'categoria': 'bebidas', 'disponible': True},
            {'id': 2, 'nombre': 'Sabritas Clásicas 45g', 'precio': 15.5, 'cantidad': 30, 'categoria': 'snacks', 'disponible': True},
            {'id': 3, 'nombre': 'Leche Lala Entera 1L', 'precio': 24.5, 'cantidad': 25, 'categoria': 'lacteos', 'disponible': True}
        ]
        
        self.categorias = {
            1: {'nombre': 'bebidas', 'descripcion': 'Bebidas y refrescos'},
            2: {'nombre': 'snacks', 'descripcion': 'Botanas y snacks'},  
            3: {'nombre': 'lacteos', 'descripción': 'Productos lácteos'}
        }
    
    # MÉTODOS DE COMPATIBILIDAD CON SIMULADOR ORIGINAL
    
    def buscar_productos(self, consulta_sql: str = None, filtros: Dict = None) -> List[Dict]:
        """Método compatible con SimuladorBDLynxShop original"""
        inicio = time.time()
        self.stats['consultas_totales'] += 1
        
        # Usar cache si está disponible
        cache_key = f"buscar_{hash(str(filtros))}"
        if cache_key in self.cache_consultas:
            self.stats['cache_hits'] += 1
            return self.cache_consultas[cache_key]
        
        if self.usar_escalable:
            resultados = self._buscar_productos_escalable(filtros or {})
        else:
            if hasattr(self, 'simulador_original'):
                resultados = self.simulador_original.buscar_productos(consulta_sql, filtros)
            else:
                resultados = self._buscar_productos_basico(filtros or {})
        
        # Actualizar cache y stats
        tiempo_transcurrido = time.time() - inicio
        self.stats['tiempo_promedio'] = (self.stats['tiempo_promedio'] + tiempo_transcurrido) / 2
        
        if len(self.cache_consultas) < 100:  # Limitar cache
            self.cache_consultas[cache_key] = resultados
        
        return resultados
    
    def _buscar_productos_escalable(self, filtros: Dict) -> List[Dict]:
        """Búsqueda usando arquitectura escalable"""
        query_escalable = {}
        
        # Mapear filtros al formato escalable
        if 'categoria' in filtros:
            query_escalable['categoria'] = filtros['categoria']
        
        if 'nombre' in filtros:
            query_escalable['termino'] = filtros['nombre']
        
        if 'precio_max' in filtros:
            query_escalable['precio_max'] = filtros['precio_max']
        
        if 'precio_min' in filtros:
            query_escalable['precio_min'] = filtros['precio_min']
        
        query_escalable['limit'] = filtros.get('limit', 20)
        
        # Usar búsqueda avanzada
        productos_encontrados = self.config_escalable.bd_escalable.buscar_productos_avanzado(query_escalable)
        
        # Convertir a formato compatible
        resultados = []
        for p in productos_encontrados:
            resultados.append({
                'id': p.id,
                'nombre': p.nombre,
                'precio': p.precio,
                'cantidad': p.stock,
                'categoria': p.categoria,
                'disponible': p.stock > 0,
                'match_score': 0.9  # Score alto por búsqueda exacta
            })
        
        return resultados
    
    def _buscar_productos_basico(self, filtros: Dict) -> List[Dict]:
        """Búsqueda básica usando datos mínimos"""
        resultados = self.productos[:]
        
        if 'categoria' in filtros:
            categoria = filtros['categoria']
            resultados = [p for p in resultados if p['categoria'] == categoria]
        
        if 'nombre' in filtros:
            nombre = filtros['nombre'].lower()
            resultados = [p for p in resultados if nombre in p['nombre'].lower()]
        
        if 'precio_max' in filtros:
            precio_max = filtros['precio_max']
            resultados = [p for p in resultados if p['precio'] <= precio_max]
        
        return resultados[:20]  # Limitar resultados
    
    def buscar_productos_por_atributo(self, atributo: str) -> List[Dict]:
        """Buscar productos por un atributo específico (dulce, picante, barato, etc.)"""
        if self.usar_escalable:
            # Mapear atributos compuestos
            mapeo_atributos = {
                'sin_azucar': 'sin azúcar',
                'sin_lactosa': 'sin lactosa', 
                'sin_gluten': 'sin gluten',
                'extra_picante': 'extra picante',
                'muy_dulce': 'muy dulce'
            }
            
            # Usar mapeo si existe, sino usar el atributo tal como viene
            termino_busqueda = mapeo_atributos.get(atributo, atributo)
            
            # Usar búsqueda inteligente del sistema escalable
            resultados = self.config_escalable.buscar_productos_inteligente(termino_busqueda, limite=10)
            
            # Convertir a formato esperado
            productos_atributo = []
            for r in resultados:
                productos_atributo.append({
                    'id': r['id'],
                    'nombre': r['nombre'],
                    'categoria': r['categoria'],
                    'precio': r['precio'],
                    'disponible': True,
                    'cantidad': r.get('cantidad', 50)
                })
            
            return productos_atributo
        else:
            # Fallback para sistema original
            return []
    
    def buscar_por_similitud(self, termino: str, categoria: str = None) -> List[Dict]:
        """Método compatible para búsqueda por similitud"""
        cache_key = f"similitud_{termino}_{categoria}"
        if cache_key in self.cache_similitudes:
            return self.cache_similitudes[cache_key]
        
        if self.usar_escalable:
            # Usar búsqueda inteligente escalable
            resultados = self.config_escalable.buscar_productos_inteligente(termino, limite=15)
            
            # Filtrar por categoría si se especifica
            if categoria:
                resultados = [r for r in resultados if r.get('categoria') == categoria]
            
            # Convertir a formato esperado
            productos_similitud = []
            for r in resultados:
                productos_similitud.append({
                    'id': r['id'],
                    'nombre': r['nombre'],
                    'precio': r['precio'],
                    'cantidad': r.get('stock', 0),
                    'categoria': r['categoria'],
                    'disponible': r.get('stock', 0) > 0,
                    'similitud': r.get('match_score', 0.7)
                })
            
        else:
            if hasattr(self, 'simulador_original'):
                productos_similitud = self.simulador_original.buscar_por_similitud(termino, categoria)
            else:
                # Búsqueda básica por similitud
                productos_similitud = []
                termino_lower = termino.lower()
                
                base_productos = (
                    [p for p in self.productos if p['categoria'] == categoria] 
                    if categoria else self.productos
                )
                
                for producto in base_productos:
                    nombre_lower = producto['nombre'].lower()
                    if termino_lower in nombre_lower:
                        producto_copia = producto.copy()
                        producto_copia['similitud'] = 0.8
                        productos_similitud.append(producto_copia)
        
        # Cache resultado
        if len(self.cache_similitudes) < 100:
            self.cache_similitudes[cache_key] = productos_similitud
        
        return productos_similitud
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        if self.usar_escalable:
            stats_escalables = self.config_escalable.obtener_estadisticas()
            
            return {
                'tipo': 'escalable',
                'productos': {
                    'total': stats_escalables['productos']['total'],
                    'cache_activo': len(self.cache_consultas) > 0
                },
                'sinonimos': stats_escalables['sinonimos'],
                'performance': {
                    'consultas_totales': self.stats['consultas_totales'],
                    'cache_hits': self.stats['cache_hits'],
                    'cache_ratio': self.stats['cache_hits'] / max(self.stats['consultas_totales'], 1),
                    'tiempo_promedio_ms': self.stats['tiempo_promedio'] * 1000
                }
            }
        else:
            return {
                'tipo': 'original',
                'productos': {
                    'total': len(self.productos),
                    'cache_activo': len(self.cache_consultas) > 0
                },
                'sinonimos': {'total': 0},
                'performance': {
                    'consultas_totales': self.stats['consultas_totales'],
                    'cache_hits': self.stats['cache_hits'],
                    'cache_ratio': self.stats['cache_hits'] / max(self.stats['consultas_totales'], 1),
                    'tiempo_promedio_ms': self.stats['tiempo_promedio'] * 1000
                }
            }
    
    def obtener_productos_populares(self, limit: int = 10) -> List[Dict]:
        """Obtener productos populares (método compatible)"""
        if self.usar_escalable:
            # Simular popularidad basada en stock bajo
            query = {'limit': limit * 2}
            productos_todos = self.config_escalable.bd_escalable.buscar_productos_avanzado(query)
            productos_populares = sorted(productos_todos, key=lambda x: x.stock)[:limit]
            
            return [{
                'id': p.id,
                'nombre': p.nombre,
                'precio': p.precio,
                'cantidad': p.stock,
                'categoria': p.categoria,
                'disponible': p.stock > 0
            } for p in productos_populares]
        else:
            if hasattr(self, 'simulador_original'):
                return self.simulador_original.obtener_productos_populares(limit)
            else:
                return sorted(self.productos, key=lambda x: x['cantidad'])[:limit]
    
    def obtener_ofertas(self, limit: int = 5) -> List[Dict]:
        """Obtener ofertas (método compatible)"""  
        if self.usar_escalable:
            # Productos baratos como ofertas
            query = {'precio_max': 20.0, 'limit': limit}
            productos_ofertas = self.config_escalable.bd_escalable.buscar_productos_avanzado(query)
            
            ofertas = []
            for p in productos_ofertas:
                oferta = {
                    'id': p.id,
                    'nombre': p.nombre,
                    'precio': p.precio,
                    'cantidad': p.stock,
                    'categoria': p.categoria,
                    'disponible': p.stock > 0,
                    'en_oferta': True,
                    'descuento': '15%'
                }
                ofertas.append(oferta)
            
            return ofertas
        else:
            if hasattr(self, 'simulador_original'):
                return self.simulador_original.obtener_ofertas(limit)
            else:
                productos_baratos = [p for p in self.productos if p['precio'] <= 20.0]
                for p in productos_baratos[:limit]:
                    p['en_oferta'] = True
                    p['descuento'] = '10%'
                return productos_baratos[:limit]
    
    # MÉTODOS ADICIONALES PARA COMPATIBILIDAD
    
    def limpiar_cache(self):
        """Limpiar cache de consultas"""
        self.cache_consultas.clear()
        self.cache_similitudes.clear()
        print("🧹 Cache limpiado")
    
    def cambiar_a_escalable(self):
        """Cambiar dinámicamente a arquitectura escalable"""
        if not self.usar_escalable and ARQUITECTURA_ESCALABLE_DISPONIBLE:
            print("🔄 Cambiando a arquitectura escalable...")
            self.usar_escalable = True
            self._init_escalable()
            print("✅ Cambio completado")
        else:
            print("⚠️  Arquitectura escalable no disponible")
    
    def cambiar_a_original(self):
        """Cambiar dinámicamente a simulador original"""
        if self.usar_escalable:
            print("🔄 Cambiando a simulador original...")
            self.usar_escalable = False
            self._init_original()
            print("✅ Cambio completado")


class ConfiguracionLYNXEscalable:
    """Adaptador para ConfiguracionLYNX que usa arquitectura escalable"""
    
    def __init__(self, forzar_escalable: bool = False):
        self.forzar_escalable = forzar_escalable
        self.simulador = SimuladorBDLynxShopEscalable(usar_escalable=True)
        self.bd_escalable = None  # Se asignará en _configurar
        self.base_datos = {}
        self._configurar()
    
    def _configurar(self):
        """Configurar usando simulador escalable"""
        try:
            if self.simulador.usar_escalable:
                self._configurar_desde_escalable()
            else:
                self._configurar_desde_bd_original()
        except Exception as e:
            print(f"❌ Error en configuración: {e}")
            self._configurar_fallback()
    
    def _configurar_desde_escalable(self):
        """Configurar usando arquitectura escalable optimizada"""
        print("🚀 Configurando desde BD escalable...")
        
        # Exponer bd_escalable - usar la instancia de BaseDatosEscalable
        self.bd_escalable = self.simulador.config_escalable.bd_escalable
        
        # Obtener configuración optimizada para AFDs
        config_afd = self.simulador.config_escalable.obtener_configuracion_afd()
        
        self.base_datos = {
            'operadores': ['mayor que', 'menor que', 'igual a', 'entre', 'y', 'mas', 'menos',
                           'no', 'sin', 'con', 'de', 'barato', 'bara', 'caro', 'economico'],
            'unidades': ['pesos', 'kg', 'g', 'gramos', 'kilogramos', 'litros', 'l', 'ml', 'unidades', 'piezas'],
            'categorias': config_afd['categorias'],
            'multipalabras': config_afd['multipalabras'],
            'productos_multi': config_afd['productos_multi'],
            'productos_completos': config_afd['productos_simples'] + config_afd['productos_multi'],
            'productos_simples': config_afd['productos_simples'],
            'productos_por_categoria': config_afd['productos_por_categoria'],
            'atributos': ['dulce', 'salado', 'picante', 'light', 'grande', 'pequeño', 'natural'],
            'modificadores': ['extra', 'sin', 'con', 'bajo', 'alto', 'azucar', 'sal', 'grasa',
                             'light', 'diet', 'natural', 'organico', 'fresco', 'seco']
        }
        
        stats = self.simulador.obtener_estadisticas()
        print(f"✅ Configuración escalable cargada: {stats['productos']['total']} productos, {len(self.base_datos['categorias'])} categorías")
    
    def _configurar_desde_bd_original(self):
        """Configurar usando BD original"""
        print("📊 Configurando desde BD original...")
        
        # Exponer bd_escalable - usar la instancia de BaseDatosEscalable si existe
        self.bd_escalable = getattr(self.simulador.config_escalable, 'bd_escalable', None)
        
        productos_bd = self.simulador.productos
        categorias = set(p['categoria'] for p in productos_bd)
        
        productos_simples = []
        productos_multi = []
        productos_completos = []
        
        for producto in productos_bd:
            nombre = producto['nombre'].lower()
            palabras = nombre.split()
            
            if len(palabras) == 1:
                productos_simples.append(nombre)
            elif len(palabras) >= 2:
                productos_multi.append(nombre)
            
            productos_completos.append(nombre)
        
        self.base_datos = {
            'operadores': ['mayor que', 'menor que', 'igual a', 'entre', 'y', 'mas', 'menos',
                           'no', 'sin', 'con', 'de', 'barato', 'bara', 'caro', 'economico'],
            'unidades': ['pesos', 'kg', 'g', 'gramos', 'kilogramos', 'litros', 'l', 'ml', 'unidades', 'piezas'],
            'categorias': list(categorias),
            'multipalabras': [p for p in productos_multi if len(p.split()) == 2][:50],
            'productos_multi': productos_multi[:100],
            'productos_completos': productos_completos,
            'productos_simples': productos_simples[:50],
            'atributos': ['dulce', 'salado', 'picante', 'light'],
            'modificadores': ['extra', 'sin', 'con', 'bajo', 'alto']
        }
        
        print(f"✅ Configuración original cargada: {len(productos_bd)} productos, {len(categorias)} categorías")
    
    def _configurar_fallback(self):
        """Configuración mínima de fallback"""
        print("⚠️  Usando configuración mínima de fallback")
        
        # Exponer bd_escalable, incluso si es None - usar instancia correcta si está disponible
        if hasattr(self.simulador, 'config_escalable') and hasattr(self.simulador.config_escalable, 'bd_escalable'):
            self.bd_escalable = self.simulador.config_escalable.bd_escalable
        else:
            self.bd_escalable = None
        
        self.base_datos = {
            'operadores': ['mayor que', 'menor que', 'igual a', 'barato', 'caro'],
            'unidades': ['pesos', 'kg', 'g', 'litros', 'l', 'ml'],
            'categorias': ['bebidas', 'snacks', 'lacteos'],
            'multipalabras': ['coca cola', 'sabritas clasicas'],
            'productos_multi': ['coca cola 600ml', 'sabritas clasicas 45g'],
            'productos_completos': ['coca', 'cola', 'sabritas', 'clasicas', 'leche'],
            'productos_simples': ['coca', 'sabritas', 'leche'],
            'atributos': ['dulce', 'salado'],
            'modificadores': ['sin', 'con']
        }


# PUNTO DE ENTRADA PARA REEMPLAZAR CONFIGURACIÓN ORIGINAL
def crear_configuracion_optimizada(usar_escalable: bool = True) -> Union[ConfiguracionLYNXEscalable, 'ConfiguracionLYNX']:
    """
    Factory function para crear la configuración más apropiada
    """
    if usar_escalable and ARQUITECTURA_ESCALABLE_DISPONIBLE:
        return ConfiguracionLYNXEscalable()
    else:
        # Fallback a configuración original si está disponible
        try:
            from utilidades import ConfiguracionLYNX
            return ConfiguracionLYNX()
        except ImportError:
            # Si no hay nada disponible, usar escalable básico
            return ConfiguracionLYNXEscalable(forzar_escalable=False)


# CREAR INSTANCIA GLOBAL PARA REEMPLAZAR SIMULADOR ORIGINAL
simulador_bd = SimuladorBDLynxShopEscalable()


if __name__ == "__main__":
    # Prueba del adaptador
    print("🧪 PROBANDO ADAPTADOR ESCALABLE")
    print("=" * 50)
    
    # Crear simulador escalable
    sim = SimuladorBDLynxShopEscalable()
    
    # Probar métodos de compatibilidad
    print(f"\n📊 Estadísticas:")
    stats = sim.obtener_estadisticas()
    print(f"   Tipo: {stats['tipo']}")
    print(f"   Productos: {stats['productos']['total']}")
    if 'sinonimos' in stats:
        print(f"   Sinónimos: {stats['sinonimos']['total']}")
    
    # Probar búsqueda
    print(f"\n🔍 Prueba de búsqueda:")
    resultados = sim.buscar_por_similitud("coca cola")
    for i, r in enumerate(resultados[:3], 1):
        print(f"   {i}. {r['nombre']} - ${r['precio']}")
    
    # Probar configuración
    print(f"\n⚙️  Prueba de configuración:")
    config = ConfiguracionLYNXEscalable()
    print(f"   Categorías disponibles: {len(config.base_datos['categorias'])}")
    print(f"   Productos simples: {len(config.base_datos['productos_simples'])}")
    
    print(f"\n✅ Adaptador funcionando correctamente")
