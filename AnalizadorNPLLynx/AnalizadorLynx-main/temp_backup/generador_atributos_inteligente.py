#!/usr/bin/env python3
"""
GENERADOR DE ATRIBUTOS INTELIGENTE PARA LYNX

Mejora el sistema de sinónimos para manejar atributos descriptivos:
- Precio: barato, caro, económico
- Sabor: picante, dulce, salado, agrio
- Tamaño: grande, pequeño, familiar
- Características: light, diet, orgánico

Autor: GitHub Copilot
Fecha: 2025-01-19
"""

from typing import List, Dict, Set
from arquitectura_escalable import SinonimoRegistro
import re

class GeneradorAtributosInteligente:
    """Generador especializado para atributos descriptivos de productos"""
    
    def __init__(self):
        # Diccionario completo de atributos mexicanos
        self.atributos_descriptivos = {
            # PRECIO - Análisis automático por rangos
            'barato': {
                'sinonimos': ['económico', 'accesible', 'low cost', 'oferta', 'promoción', 'descuento'],
                'rangos_precio': {'bebidas': (0, 15), 'snacks': (0, 20), 'lacteos': (0, 25)},
                'confianza': 0.8
            },
            'caro': {
                'sinonimos': ['premium', 'gourmet', 'exclusivo', 'de lujo', 'costoso'],
                'rangos_precio': {'bebidas': (35, 100), 'snacks': (45, 100), 'lacteos': (60, 150)},
                'confianza': 0.8
            },
            
            # SABOR - Detección por palabras clave
            'picante': {
                'sinonimos': ['picoso', 'enchilado', 'con chile', 'spicy', 'hot', 'ardiente', 'chile', 'fuego', 'flaming hot', 'flammin', 'fire'],
                'palabras_clave': ['jalapeño', 'chile', 'habanero', 'chipotle', 'adobadas', 'flamin', 'hot', 'fuego', 'fire', 'flamming', 'flaming'],
                'confianza': 0.9
            },
            'dulce': {
                'sinonimos': ['azucarado', 'endulzado', 'sweet', 'con azúcar', 'meloso', 'caramelizado'],
                'palabras_clave': ['chocolate', 'fresa', 'vainilla', 'caramelo', 'miel', 'dulce', 'azúcar'],
                'confianza': 0.9
            },
            'salado': {
                'sinonimos': ['salted', 'con sal', 'salty', 'salino'],
                'palabras_clave': ['sal', 'saladas', 'original', 'clásicas', 'natural'],
                'confianza': 0.8
            },
            'agrio': {
                'sinonimos': ['ácido', 'cítrico', 'sour', 'limón', 'tamarindo'],
                'palabras_clave': ['limón', 'lima', 'tamarindo', 'naranja', 'toronja'],
                'confianza': 0.7
            },
            
            # TAMAÑO - Detección por presentación
            'grande': {
                'sinonimos': ['familiar', 'mega', 'extra', 'jumbo', 'big', 'xl', 'maxi'],
                'palabras_clave': ['2l', '3l', '1kg', '2kg', 'familiar', 'grande', 'mega', 'jumbo'],
                'confianza': 0.8
            },
            'pequeño': {
                'sinonimos': ['mini', 'individual', 'personal', 'small', 'pocket', 'chico'],
                'palabras_clave': ['250ml', '355ml', '25g', '35g', 'mini', 'individual', 'personal'],
                'confianza': 0.8
            },
            
            # CARACTERÍSTICAS NUTRICIONALES
            'light': {
                'sinonimos': ['diet', 'zero', 'sin azúcar', 'bajo en calorías', 'reducido', 'lite'],
                'palabras_clave': ['light', 'diet', 'zero', 'sin azúcar', 'descremada', 'bajo'],
                'confianza': 0.9
            },
            'orgánico': {
                'sinonimos': ['natural', 'bio', 'ecológico', 'sin químicos', 'verde'],
                'palabras_clave': ['orgánico', 'natural', 'bio', 'ecológico', 'verde'],
                'confianza': 0.7
            },
            
            # MARCAS COMO ATRIBUTOS
            'sabritas': {
                'sinonimos': ['papas', 'botanas', 'frituras', 'snacks'],
                'palabras_clave': ['sabritas'],
                'confianza': 0.9
            },
            'coca': {
                'sinonimos': ['cola', 'refresco', 'bebida'],
                'palabras_clave': ['coca-cola', 'coca'],
                'confianza': 0.9
            },
            
            # CATEGORÍAS COMO ATRIBUTOS
            'bebida': {
                'sinonimos': ['líquido', 'drink', 'refresco', 'jugo', 'agua'],
                'categorias': ['bebidas'],
                'confianza': 0.7
            },
            'comida': {
                'sinonimos': ['alimento', 'food', 'producto alimenticio'],
                'categorias': ['snacks', 'lacteos', 'carnes', 'frutas', 'verduras'],
                'confianza': 0.6
            }
        }
    
    def generar_sinonimos_con_atributos(self, productos: List[Dict]) -> List[SinonimoRegistro]:
        """Generar sinónimos inteligentes incluyendo atributos descriptivos"""
        sinonimos = []
        
        print("🧠 Generando sinónimos con atributos inteligentes...")
        
        for producto in productos:
            # Manejar tanto diccionarios como objetos ProductoCompleto
            if hasattr(producto, 'nombre'):  # Es un objeto ProductoCompleto
                nombre = producto.nombre.lower()
                categoria = producto.categoria
                producto_id = producto.id
                precio = producto.precio
            else:  # Es un diccionario
                nombre = producto['nombre'].lower()
                categoria = producto['categoria']
                producto_id = producto['id']
                precio = producto.get('precio', 0)
            
            # Analizar cada atributo
            for atributo, config in self.atributos_descriptivos.items():
                confianza_base = config['confianza']
                
                # 1. Verificar por precio
                if 'rangos_precio' in config:
                    if self._precio_coincide(precio, categoria, config['rangos_precio']):
                        sinonimos.extend(self._crear_sinonimos_atributo(
                            atributo, config, producto_id, categoria, confianza_base
                        ))
                
                # 2. Verificar por palabras clave
                if 'palabras_clave' in config:
                    if any(palabra in nombre for palabra in config['palabras_clave']):
                        sinonimos.extend(self._crear_sinonimos_atributo(
                            atributo, config, producto_id, categoria, confianza_base
                        ))
                
                # 3. Verificar por categoría
                if 'categorias' in config:
                    if categoria in config['categorias']:
                        sinonimos.extend(self._crear_sinonimos_atributo(
                            atributo, config, producto_id, categoria, confianza_base * 0.8
                        ))
        
        # Eliminar duplicados
        sinonimos_unicos = self._eliminar_duplicados(sinonimos)
        
        print(f"🎯 Sinónimos de atributos generados: {len(sinonimos_unicos)}")
        return sinonimos_unicos
    
    def _precio_coincide(self, precio: float, categoria: str, rangos: Dict) -> bool:
        """Verificar si el precio está en el rango del atributo"""
        if categoria in rangos:
            min_precio, max_precio = rangos[categoria]
            return min_precio <= precio <= max_precio
        return False
    
    def _crear_sinonimos_atributo(self, atributo: str, config: Dict, 
                                  producto_id: int, categoria: str, 
                                  confianza: float) -> List[SinonimoRegistro]:
        """Crear sinónimos para un atributo específico"""
        sinonimos = []
        
        # Sinónimo principal del atributo
        sinonimos.append(SinonimoRegistro(
            termino=atributo,
            termino_normalizado=self._normalizar(atributo),
            producto_id=producto_id,
            categoria=categoria,
            tipo='atributo_principal',
            confianza=confianza,
            frecuencia_uso=0
        ))
        
        # Sinónimos del atributo
        for sinonimo in config.get('sinonimos', []):
            sinonimos.append(SinonimoRegistro(
                termino=sinonimo,
                termino_normalizado=self._normalizar(sinonimo),
                producto_id=producto_id,
                categoria=categoria,
                tipo='atributo_sinonimo',
                confianza=confianza * 0.9,
                frecuencia_uso=0
            ))
        
        return sinonimos
    
    def _eliminar_duplicados(self, sinonimos: List[SinonimoRegistro]) -> List[SinonimoRegistro]:
        """Eliminar duplicados manteniendo el de mayor confianza"""
        sinonimos_unicos = {}
        for s in sinonimos:
            key = (s.termino_normalizado, s.producto_id)
            if key not in sinonimos_unicos or s.confianza > sinonimos_unicos[key].confianza:
                sinonimos_unicos[key] = s
        return list(sinonimos_unicos.values())
    
    def _normalizar(self, texto: str) -> str:
        """Normalización básica de texto"""
        import unicodedata
        texto = texto.lower().strip()
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join(c for c in texto if not unicodedata.combining(c))
        return ' '.join(texto.split())
    
    def generar_reporte_atributos(self, productos: List[Dict]) -> str:
        """Generar reporte de atributos detectados"""
        reporte = "📊 REPORTE DE ATRIBUTOS DETECTADOS\n"
        reporte += "=" * 50 + "\n\n"
        
        atributos_conteo = {}
        
        for producto in productos:
            # Manejar tanto diccionarios como objetos ProductoCompleto
            if hasattr(producto, 'nombre'):  # Es un objeto ProductoCompleto
                nombre = producto.nombre.lower()
                precio = producto.precio
                categoria = producto.categoria
            else:  # Es un diccionario
                nombre = producto['nombre'].lower()
                precio = producto.get('precio', 0)
                categoria = producto['categoria']
            
            # Contar atributos detectados
            for atributo, config in self.atributos_descriptivos.items():
                detectado = False
                
                # Verificar detección
                if 'rangos_precio' in config and self._precio_coincide(precio, categoria, config['rangos_precio']):
                    detectado = True
                elif 'palabras_clave' in config and any(palabra in nombre for palabra in config['palabras_clave']):
                    detectado = True
                elif 'categorias' in config and categoria in config['categorias']:
                    detectado = True
                
                if detectado:
                    atributos_conteo[atributo] = atributos_conteo.get(atributo, 0) + 1
        
        # Ordenar por frecuencia
        atributos_ordenados = sorted(atributos_conteo.items(), key=lambda x: x[1], reverse=True)
        
        for atributo, conteo in atributos_ordenados:
            porcentaje = (conteo / len(productos)) * 100
            reporte += f"🏷️ {atributo.upper():<15}: {conteo:>4} productos ({porcentaje:>5.1f}%)\n"
        
        reporte += f"\n📈 Total productos analizados: {len(productos)}"
        reporte += f"\n🎯 Atributos únicos detectados: {len(atributos_conteo)}"
        
        return reporte


def mejorar_sinonimos_existentes():
    """Función para mejorar los sinónimos existentes con atributos inteligentes"""
    print("🚀 MEJORANDO SINÓNIMOS CON ATRIBUTOS INTELIGENTES")
    print("=" * 60)
    
    # 1. Cargar productos existentes
    from arquitectura_escalable import ConfiguracionEscalableLYNX
    config = ConfiguracionEscalableLYNX()
    productos = config.bd_escalable.obtener_todos_productos()
    
    print(f"📦 Productos cargados: {len(productos)}")
    
    # 2. Generar atributos inteligentes
    generador_atributos = GeneradorAtributosInteligente()
    sinonimos_atributos = generador_atributos.generar_sinonimos_con_atributos(productos)
    
    # 3. Agregar a la base de datos
    config.bd_escalable.gestor_sinonimos.agregar_sinonimos_masivos(sinonimos_atributos)
    
    # 4. Mostrar reporte
    reporte = generador_atributos.generar_reporte_atributos(productos)
    print(f"\n{reporte}")
    
    # 5. Pruebas específicas de atributos
    print(f"\n🔍 PRUEBAS DE ATRIBUTOS:")
    consultas_atributos = ["barato", "picante", "dulce", "grande", "light", "coca"]
    
    for consulta in consultas_atributos:
        resultados = config.buscar_productos_inteligente(consulta, limite=3)
        print(f"   '{consulta}': {len(resultados)} resultados")
        for i, r in enumerate(resultados[:2], 1):
            print(f"     {i}. {r['nombre'][:50]} - ${r['precio']} ({r['match_type']})")
    
    print(f"\n🎉 MEJORA DE SINÓNIMOS COMPLETADA")
    return config


if __name__ == "__main__":
    config = mejorar_sinonimos_existentes()
