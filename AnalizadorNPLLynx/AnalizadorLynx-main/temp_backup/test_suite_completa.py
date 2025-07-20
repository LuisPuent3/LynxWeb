#!/usr/bin/env python3
# test_suite_completa.py - Suite completa de pruebas para el buscador LYNX
import json
import time
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

class EvaluadorBuscador:
    """Evaluador completo del comportamiento del buscador LYNX"""
    
    def __init__(self):
        print("🚀 Inicializando suite de pruebas del buscador LYNX...")
        self.configuracion = ConfiguracionLYNX()
        self.analizador = AnalizadorLexicoLYNX(self.configuracion)
        self.resultados_pruebas = []
        print("✅ Sistema inicializado para pruebas")
        print()
    
    def ejecutar_prueba(self, nombre, consulta, criterios_evaluacion):
        """Ejecuta una prueba individual y evalúa los resultados"""
        print(f"🧪 PRUEBA: {nombre}")
        print("=" * 60)
        print(f"🔍 Consulta: '{consulta}'")
        
        tiempo_inicio = time.time()
        
        try:
            # Ejecutar consulta
            resultado_json = self.analizador.generar_json_resultado_completo(consulta)
            resultado = json.loads(resultado_json)
            
            tiempo_ejecucion = (time.time() - tiempo_inicio) * 1000
            
            # Extraer datos
            interpretacion = resultado.get('interpretation', {})
            recomendaciones = resultado.get('recommendations', [])
            
            # Evaluar criterios
            puntuacion_total = 0
            criterios_pasados = 0
            evaluaciones = []
            
            for criterio in criterios_evaluacion:
                nombre_criterio = criterio['nombre']
                funcion_evaluacion = criterio['evaluacion']
                peso = criterio.get('peso', 1)
                
                resultado_criterio = funcion_evaluacion(interpretacion, recomendaciones)
                if resultado_criterio:
                    puntuacion_total += peso
                    criterios_pasados += 1
                    evaluaciones.append(f"   ✅ {nombre_criterio}")
                else:
                    evaluaciones.append(f"   ❌ {nombre_criterio}")
            
            # Calcular puntuación
            puntuacion_porcentaje = (puntuacion_total / sum(c.get('peso', 1) for c in criterios_evaluacion)) * 100
            
            # Mostrar resultados
            print(f"📊 RESULTADOS ({len(recomendaciones)} productos, {tiempo_ejecucion:.1f}ms):")
            for evaluacion in evaluaciones:
                print(evaluacion)
            
            print(f"\n🎯 PUNTUACIÓN: {puntuacion_porcentaje:.1f}% ({criterios_pasados}/{len(criterios_evaluacion)} criterios)")
            
            # Guardar resultado
            self.resultados_pruebas.append({
                'nombre': nombre,
                'consulta': consulta,
                'puntuacion': puntuacion_porcentaje,
                'criterios_pasados': criterios_pasados,
                'total_criterios': len(criterios_evaluacion),
                'tiempo_ms': tiempo_ejecucion,
                'productos_encontrados': len(recomendaciones)
            })
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
            self.resultados_pruebas.append({
                'nombre': nombre,
                'consulta': consulta,
                'puntuacion': 0,
                'error': str(e)
            })
            print()
            return False
    
    def ejecutar_suite_completa(self):
        """Ejecuta todas las pruebas del buscador"""
        
        # Prueba 1: Bebidas sin azúcar
        self.ejecutar_prueba(
            "Bebidas Sin Azúcar",
            "bebidas sin azucar",
            [
                {
                    'nombre': 'Detecta atributo "sin azúcar"',
                    'evaluacion': lambda i, r: 'sin_azucar' in i.get('atributos', []),
                    'peso': 2
                },
                {
                    'nombre': 'Detecta categoría bebidas',
                    'evaluacion': lambda i, r: 'bebida' in i.get('categoria', '').lower(),
                    'peso': 2
                },
                {
                    'nombre': 'Productos son bebidas',
                    'evaluacion': lambda i, r: sum(1 for rec in r if 'bebida' in rec.get('category', '').lower()) > len(r) * 0.7,
                    'peso': 2
                },
                {
                    'nombre': 'Incluye productos light/zero',
                    'evaluacion': lambda i, r: sum(1 for rec in r if any(palabra in rec.get('name', '').lower() for palabra in ['light', 'zero'])) > 0,
                    'peso': 3
                }
            ]
        )
        
        # Prueba 2: Productos picantes baratos
        self.ejecutar_prueba(
            "Productos Picantes Baratos",
            "productos picantes baratos",
            [
                {
                    'nombre': 'Detecta atributo picante',
                    'evaluacion': lambda i, r: 'picante' in i.get('atributos', []),
                    'peso': 2
                },
                {
                    'nombre': 'Detecta filtro barato',
                    'evaluacion': lambda i, r: i.get('filtros', {}).get('precio') is not None,
                    'peso': 2
                },
                {
                    'nombre': 'Productos son picantes',
                    'evaluacion': lambda i, r: sum(1 for rec in r if any(palabra in rec.get('name', '').lower() for palabra in ['picante', 'adobada', 'chile'])) > len(r) * 0.7,
                    'peso': 2
                },
                {
                    'nombre': 'Productos son baratos',
                    'evaluacion': lambda i, r: sum(1 for rec in r if rec.get('price', 999) < 10) > len(r) * 0.5,
                    'peso': 2
                }
            ]
        )
        
        # Prueba 3: Coca Cola Zero
        self.ejecutar_prueba(
            "Coca Cola Zero",
            "coca cola zero",
            [
                {
                    'nombre': 'Detecta producto Coca Cola',
                    'evaluacion': lambda i, r: 'coca' in str(i).lower(),
                    'peso': 2
                },
                {
                    'nombre': 'Productos contienen Coca Cola',
                    'evaluacion': lambda i, r: sum(1 for rec in r if 'coca' in rec.get('name', '').lower() and 'cola' in rec.get('name', '').lower()) > 0,
                    'peso': 3
                },
                {
                    'nombre': 'Incluye variantes Zero',
                    'evaluacion': lambda i, r: sum(1 for rec in r if 'zero' in rec.get('name', '').lower()) > 0,
                    'peso': 3
                },
                {
                    'nombre': 'Son bebidas',
                    'evaluacion': lambda i, r: sum(1 for rec in r if 'bebida' in rec.get('category', '').lower()) > len(r) * 0.8,
                    'peso': 1
                }
            ]
        )
        
        # Prueba 4: Leche descremada barata
        self.ejecutar_prueba(
            "Leche Descremada Barata",
            "leche descremada barata",
            [
                {
                    'nombre': 'Detecta producto leche',
                    'evaluacion': lambda i, r: 'leche' in str(i).lower(),
                    'peso': 2
                },
                {
                    'nombre': 'Detecta filtro barato',
                    'evaluacion': lambda i, r: i.get('filtros', {}).get('precio') is not None,
                    'peso': 2
                },
                {
                    'nombre': 'Son productos lácteos',
                    'evaluacion': lambda i, r: sum(1 for rec in r if 'lacteo' in rec.get('category', '').lower()) > len(r) * 0.8,
                    'peso': 2
                },
                {
                    'nombre': 'Incluye productos descremados',
                    'evaluacion': lambda i, r: sum(1 for rec in r if 'descremada' in rec.get('name', '').lower()) > 0,
                    'peso': 3
                }
            ]
        )
        
        # Prueba 5: Papitas sin picante
        self.ejecutar_prueba(
            "Papitas Sin Picante",
            "papitas sin picante",
            [
                {
                    'nombre': 'Detecta producto papitas',
                    'evaluacion': lambda i, r: 'papitas' in str(i).lower(),
                    'peso': 2
                },
                {
                    'nombre': 'Detecta atributo sin picante',
                    'evaluacion': lambda i, r: 'sin_picante' in i.get('atributos', []),
                    'peso': 2
                },
                {
                    'nombre': 'Son snacks',
                    'evaluacion': lambda i, r: sum(1 for rec in r if 'snack' in rec.get('category', '').lower()) > len(r) * 0.7,
                    'peso': 2
                },
                {
                    'nombre': 'Prioriza productos no picantes',
                    'evaluacion': lambda i, r: sum(1 for rec in r if not any(palabra in rec.get('name', '').lower() for palabra in ['adobada', 'picante', 'chile'])) > len(r) * 0.3,
                    'peso': 1
                }
            ]
        )
    
    def mostrar_resumen_final(self):
        """Muestra el resumen final de todas las pruebas"""
        print("🏆 RESUMEN FINAL DEL BUSCADOR LYNX")
        print("=" * 70)
        print()
        
        if not self.resultados_pruebas:
            print("❌ No se ejecutaron pruebas")
            return
        
        # Estadísticas generales
        pruebas_exitosas = [p for p in self.resultados_pruebas if 'error' not in p]
        pruebas_fallidas = [p for p in self.resultados_pruebas if 'error' in p]
        
        if pruebas_exitosas:
            puntuacion_promedio = sum(p['puntuacion'] for p in pruebas_exitosas) / len(pruebas_exitosas)
            tiempo_promedio = sum(p['tiempo_ms'] for p in pruebas_exitosas) / len(pruebas_exitosas)
            productos_promedio = sum(p['productos_encontrados'] for p in pruebas_exitosas) / len(pruebas_exitosas)
        else:
            puntuacion_promedio = tiempo_promedio = productos_promedio = 0
        
        print(f"📊 ESTADÍSTICAS GENERALES:")
        print(f"   • Pruebas ejecutadas: {len(self.resultados_pruebas)}")
        print(f"   • Pruebas exitosas: {len(pruebas_exitosas)}")
        print(f"   • Pruebas fallidas: {len(pruebas_fallidas)}")
        print(f"   • Puntuación promedio: {puntuacion_promedio:.1f}%")
        print(f"   • Tiempo promedio: {tiempo_promedio:.1f}ms")
        print(f"   • Productos promedio: {productos_promedio:.1f}")
        print()
        
        # Detalle por prueba
        print(f"📋 DETALLE POR PRUEBA:")
        for i, prueba in enumerate(self.resultados_pruebas, 1):
            if 'error' in prueba:
                print(f"   {i}. ❌ {prueba['nombre']}: ERROR - {prueba['error']}")
            else:
                puntuacion = prueba['puntuacion']
                criterios = f"{prueba['criterios_pasados']}/{prueba['total_criterios']}"
                tiempo = prueba['tiempo_ms']
                productos = prueba['productos_encontrados']
                
                # Emoji según puntuación
                if puntuacion >= 80:
                    emoji = "🟢"
                elif puntuacion >= 60:
                    emoji = "🟡"
                else:
                    emoji = "🔴"
                
                print(f"   {i}. {emoji} {prueba['nombre']}: {puntuacion:.1f}% ({criterios}) - {productos} productos, {tiempo:.1f}ms")
        
        print()
        
        # Evaluación final
        if puntuacion_promedio >= 80:
            evaluacion = "🏆 EXCELENTE - Funciona como buscador real"
        elif puntuacion_promedio >= 60:
            evaluacion = "✅ BUENO - Comportamiento adecuado con mejoras"
        elif puntuacion_promedio >= 40:
            evaluacion = "⚠️  REGULAR - Necesita optimización"
        else:
            evaluacion = "❌ DEFICIENTE - Requiere revisión importante"
        
        print(f"🎯 EVALUACIÓN FINAL: {evaluacion}")
        print()
        
        # Recomendaciones
        print("💡 FORTALEZAS IDENTIFICADAS:")
        if any(p.get('puntuacion', 0) >= 80 for p in pruebas_exitosas):
            print("   • Detección de categorías funciona bien")
            print("   • Búsqueda por atributos operativa")
            print("   • Tiempo de respuesta aceptable")
        
        print()
        print("🔧 ÁREAS DE MEJORA:")
        if any(p.get('puntuacion', 0) < 60 for p in pruebas_exitosas):
            print("   • Mejorar filtros negativos (sin azúcar, sin sal)")
            print("   • Optimizar detección de productos específicos")
            print("   • Refinar scoring por relevancia")
        
        print()
        print(f"📈 PROGRESO: El buscador LYNX muestra un comportamiento {puntuacion_promedio:.0f}% similar a buscadores reales")

def main():
    """Función principal que ejecuta todas las pruebas"""
    evaluador = EvaluadorBuscador()
    evaluador.ejecutar_suite_completa()
    evaluador.mostrar_resumen_final()

if __name__ == "__main__":
    main()
