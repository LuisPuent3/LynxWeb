#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test completo de todos los casos de uso definidos en casosuso.md
"""

from sistema_lcln_simple import SistemaLCLNSimplificado
import time

class TestCasosUso:
    def __init__(self):
        print("Inicializando sistema LCLN para tests...")
        self.sistema = SistemaLCLNSimplificado()
        self.resultados = []
        
    def ejecutar_test(self, nombre_caso, consulta, criterios_exito):
        """Ejecuta un test y valida los criterios de éxito"""
        print(f"\n--- {nombre_caso} ---")
        print(f"Consulta: '{consulta}'")
        
        # Medir tiempo de respuesta
        inicio = time.time()
        resultado = self.sistema.buscar_productos_inteligente(consulta)
        tiempo_ms = (time.time() - inicio) * 1000
        
        productos = resultado.get('recommendations', [])
        interpretacion = resultado.get('interpretation', {})
        
        print(f"Productos encontrados: {len(productos)}")
        print(f"Tiempo de respuesta: {tiempo_ms:.1f}ms")
        
        # Mostrar primeros productos
        for i, p in enumerate(productos[:3], 1):
            print(f"  {i}. {p.get('nombre', 'N/A')} (${p.get('precio', 'N/A')})")
        
        # Validar criterios
        exito = True
        for criterio, validacion in criterios_exito.items():
            if criterio == 'tiempo_max_ms':
                if tiempo_ms > validacion:
                    print(f"  [ERROR] Tiempo {tiempo_ms:.1f}ms > {validacion}ms")
                    exito = False
                else:
                    print(f"  [OK] Tiempo dentro del límite")
                    
            elif criterio == 'min_productos':
                if len(productos) < validacion:
                    print(f"  [ERROR] Solo {len(productos)} productos, esperaba >= {validacion}")
                    exito = False
                else:
                    print(f"  [OK] Cantidad suficiente de productos")
                    
            elif criterio == 'max_productos':
                if len(productos) > validacion:
                    print(f"  [ERROR] Demasiados productos {len(productos)}, esperaba <= {validacion}")
                    exito = False
                else:
                    print(f"  [OK] Cantidad controlada de productos")
                    
            elif criterio == 'debe_contener_producto':
                productos_nombres = [p.get('nombre', '').lower() for p in productos]
                if not any(validacion.lower() in nombre for nombre in productos_nombres):
                    print(f"  [ERROR] No encontró producto que contenga '{validacion}'")
                    exito = False
                else:
                    print(f"  [OK] Encontró producto con '{validacion}'")
                    
            elif criterio == 'categoria_esperada':
                if productos:
                    categoria_encontrada = productos[0].get('categoria', '').lower()
                    if validacion.lower() not in categoria_encontrada:
                        print(f"  [ERROR] Categoría '{categoria_encontrada}' != '{validacion}'")
                        exito = False
                    else:
                        print(f"  [OK] Categoría correcta: {validacion}")
                        
            elif criterio == 'precio_max':
                precios_altos = [p for p in productos if p.get('precio', 0) > validacion]
                if precios_altos:
                    print(f"  [ERROR] {len(precios_altos)} productos sobre ${validacion}")
                    exito = False
                else:
                    print(f"  [OK] Todos los precios <= ${validacion}")
                    
            elif criterio == 'no_debe_contener':
                productos_nombres = [p.get('nombre', '').lower() for p in productos]
                if any(validacion.lower() in nombre for nombre in productos_nombres):
                    print(f"  [ERROR] Encontró producto prohibido con '{validacion}'")
                    exito = False
                else:
                    print(f"  [OK] No hay productos prohibidos con '{validacion}'")
        
        self.resultados.append({
            'caso': nombre_caso,
            'consulta': consulta,
            'exito': exito,
            'tiempo_ms': tiempo_ms,
            'productos_count': len(productos)
        })
        
        print(f"Resultado: {'EXITO' if exito else 'FALLO'}")
        return exito
    
    def test_casos_basicos(self):
        """Casos básicos de búsqueda exacta"""
        print("\n=== CASOS BÁSICOS ===")
        
        # CASO 1.1: Producto específico
        self.ejecutar_test(
            "CASO 1.1: Producto específico existe",
            "coca cola 600ml",
            {
                'tiempo_max_ms': 50,
                'min_productos': 1,
                'debe_contener_producto': 'coca-cola',
                'categoria_esperada': 'bebidas'
            }
        )
        
        # CASO 1.2: Categoría directa
        self.ejecutar_test(
            "CASO 1.2: Categoría directa",
            "bebidas",
            {
                'tiempo_max_ms': 50,
                'min_productos': 3,
                'categoria_esperada': 'bebidas'
            }
        )
        
        # CASO 1.3: Búsqueda con precio
        self.ejecutar_test(
            "CASO 1.3: Búsqueda con precio",
            "doritos menor a 25 pesos",
            {
                'tiempo_max_ms': 50,
                'min_productos': 1,
                'debe_contener_producto': 'doritos',
                'precio_max': 25
            }
        )
    
    def test_errores_ortograficos(self):
        """Casos con errores ortográficos"""
        print("\n=== CASOS CON ERRORES ORTOGRÁFICOS ===")
        
        # CASO 2.1: Error simple
        self.ejecutar_test(
            "CASO 2.1: Error simple",
            "koka kola",
            {
                'tiempo_max_ms': 100,
                'min_productos': 1,
                'debe_contener_producto': 'coca',
                'categoria_esperada': 'bebidas'
            }
        )
        
        # CASO 2.2: Múltiples errores
        self.ejecutar_test(
            "CASO 2.2: Múltiples errores",
            "dortios nachos baratos",
            {
                'tiempo_max_ms': 100,
                'min_productos': 1,
                'debe_contener_producto': 'doritos'
            }
        )
    
    def test_sinonimos(self):
        """Casos con sinónimos"""
        print("\n=== CASOS CON SINÓNIMOS ===")
        
        # CASO 3.2: Término genérico
        self.ejecutar_test(
            "CASO 3.2: Término genérico",
            "botana para la tarde",
            {
                'tiempo_max_ms': 100,
                'min_productos': 2
            }
        )
        
        # CASO 3.3: Atributo sinónimo
        self.ejecutar_test(
            "CASO 3.3: Atributo sinónimo",
            "papitas baratas",
            {
                'tiempo_max_ms': 100,
                'min_productos': 1
            }
        )
    
    def test_casos_complejos(self):
        """Casos complejos con múltiples filtros"""
        print("\n=== CASOS COMPLEJOS ===")
        
        # CASO 5.1: Categoría + precio + atributo (YA CORREGIDO)
        self.ejecutar_test(
            "CASO 5.1: Bebidas sin azúcar menor a 20 pesos",
            "bebidas sin azucar menor a 20 pesos",
            {
                'tiempo_max_ms': 150,
                'min_productos': 2,
                'max_productos': 6,
                'categoria_esperada': 'bebidas',
                'precio_max': 20,
                'no_debe_contener': 'bolígrafo',  # No debe incluir papelería
                'no_debe_contener': 'té negro'    # No debe incluir tés con azúcar
            }
        )
        
        # CASO 5.2: Rango de precios
        self.ejecutar_test(
            "CASO 5.2: Rango de precios",
            "snacks entre 15 y 25 pesos",
            {
                'tiempo_max_ms': 100,
                'min_productos': 1,
                'precio_max': 25
            }
        )
    
    def test_lenguaje_natural(self):
        """Casos de queries en lenguaje natural"""
        print("\n=== LENGUAJE NATURAL ===")
        
        # CASO 7.1: Pregunta completa
        self.ejecutar_test(
            "CASO 7.1: Pregunta completa",
            "qué bebidas tienes por menos de 15 pesos",
            {
                'tiempo_max_ms': 100,
                'min_productos': 1,
                'categoria_esperada': 'bebidas',
                'precio_max': 15
            }
        )
        
        # CASO 7.2: Jerga estudiantil
        self.ejecutar_test(
            "CASO 7.2: Jerga estudiantil", 
            "algo para la sed bien helado",
            {
                'tiempo_max_ms': 100,
                'min_productos': 2,
                'categoria_esperada': 'bebidas'
            }
        )
    
    def test_casos_edge(self):
        """Casos límite"""
        print("\n=== CASOS LÍMITE ===")
        
        # CASO 10.2: Solo números
        self.ejecutar_test(
            "CASO 10.2: Solo números",
            "20",
            {
                'tiempo_max_ms': 100,
                'min_productos': 1
            }
        )
        
        # CASO 10.3: Caracteres especiales
        self.ejecutar_test(
            "CASO 10.3: Caracteres especiales",
            "coca-cola!!!",
            {
                'tiempo_max_ms': 100,
                'min_productos': 1,
                'debe_contener_producto': 'coca'
            }
        )
    
    def ejecutar_todos_los_tests(self):
        """Ejecuta todos los tests y genera reporte"""
        print("INICIANDO TESTS COMPLETOS DE CASOS DE USO")
        print("=" * 50)
        
        self.test_casos_basicos()
        self.test_errores_ortograficos()
        self.test_sinonimos()
        self.test_casos_complejos()
        self.test_lenguaje_natural()
        self.test_casos_edge()
        
        # Generar reporte final
        print("\n" + "=" * 50)
        print("REPORTE FINAL")
        print("=" * 50)
        
        exitos = len([r for r in self.resultados if r['exito']])
        fallos = len([r for r in self.resultados if not r['exito']])
        
        print(f"Tests ejecutados: {len(self.resultados)}")
        print(f"Éxitos: {exitos}")
        print(f"Fallos: {fallos}")
        print(f"Tasa de éxito: {exitos/len(self.resultados)*100:.1f}%")
        
        if fallos > 0:
            print(f"\nCASOS FALLIDOS:")
            for r in self.resultados:
                if not r['exito']:
                    print(f"  - {r['caso']}: '{r['consulta']}' ({r['tiempo_ms']:.1f}ms, {r['productos_count']} productos)")
        
        print(f"\nTiempo promedio: {sum(r['tiempo_ms'] for r in self.resultados)/len(self.resultados):.1f}ms")
        
        return exitos == len(self.resultados)

if __name__ == "__main__":
    tester = TestCasosUso()
    tester.ejecutar_todos_los_tests()