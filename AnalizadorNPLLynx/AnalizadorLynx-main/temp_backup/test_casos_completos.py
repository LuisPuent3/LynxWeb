#!/usr/bin/env python3
# test_casos_completos.py - Casos completos de prueba para el sistema escalable
import json
import time
from datetime import datetime
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def mostrar_resultado_detallado(consulta, resultado_json):
    """Muestra el resultado detallado de una consulta"""
    print(f"🔍 {Colors.BOLD}CONSULTA:{Colors.ENDC} {Colors.CYAN}'{consulta}'{Colors.ENDC}")
    print("=" * 70)
    
    try:
        resultado = json.loads(resultado_json)
        
        # Correcciones aplicadas
        correcciones = resultado.get('corrections', {})
        if correcciones.get('applied'):
            print(f"{Colors.WARNING}🔧 CORRECCIÓN APLICADA:{Colors.ENDC}")
            consulta_corregida = correcciones.get('corrected_query', consulta)
            print(f"   Original: '{consulta}' → Corregida: '{consulta_corregida}'")
            print()
        
        # Interpretación del sistema
        interpretacion = resultado.get('interpretation', {})
        print(f"{Colors.HEADER}🧠 INTERPRETACIÓN:{Colors.ENDC}")
        
        if interpretacion.get('producto'):
            print(f"   🔍 Producto: {Colors.GREEN}{interpretacion['producto']}{Colors.ENDC}")
        
        if interpretacion.get('categoria'):
            print(f"   📂 Categoría: {Colors.GREEN}{interpretacion['categoria']}{Colors.ENDC}")
            
        if interpretacion.get('atributos'):
            atributos = ', '.join(interpretacion['atributos'])
            print(f"   🏷️  Atributos: {Colors.BLUE}{atributos}{Colors.ENDC}")
        
        # Filtros
        filtros = interpretacion.get('filtros', {})
        if filtros.get('precio'):
            precio_info = filtros['precio']
            print(f"   💰 Filtros precio: {Colors.CYAN}{precio_info}{Colors.ENDC}")
        
        print()
        
        # Resultados
        recomendaciones = resultado.get('recommendations', [])
        print(f"{Colors.GREEN}🛍️  PRODUCTOS ENCONTRADOS: {len(recomendaciones)}{Colors.ENDC}")
        
        for i, rec in enumerate(recomendaciones[:5], 1):  # Solo mostrar primeros 5
            nombre = rec.get('name', 'Sin nombre')
            precio = rec.get('price', 0)
            categoria = rec.get('category', 'Sin categoría')
            score = rec.get('match_score', 0)
            razones = rec.get('match_reasons', [])
            
            print(f"   {i}. {Colors.CYAN}{nombre}{Colors.ENDC}")
            print(f"      💰 ${precio:.2f} | 📂 {categoria} | ⭐ {score*100:.0f}%")
            print(f"      🎯 {', '.join(razones[:3])}")
        
        print()
        
    except json.JSONDecodeError as e:
        print(f"{Colors.FAIL}❌ Error al parsear JSON: {e}{Colors.ENDC}")
        print(resultado_json[:200] + "...")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error inesperado: {e}{Colors.ENDC}")

def evaluar_resultado(consulta, resultado_json, expectativa):
    """Evalúa si el resultado cumple con la expectativa"""
    try:
        resultado = json.loads(resultado_json)
        interpretacion = resultado.get('interpretation', {})
        recomendaciones = resultado.get('recommendations', [])
        
        # Verificar expectativas
        evaluacion = {
            'producto_detectado': False,
            'categoria_detectada': False,
            'atributos_detectados': False,
            'filtros_aplicados': False,
            'resultados_apropiados': False
        }
        
        # Evaluar detección de producto
        if expectativa.get('producto_esperado'):
            if interpretacion.get('producto') == expectativa['producto_esperado']:
                evaluacion['producto_detectado'] = True
        
        # Evaluar detección de categoría
        if expectativa.get('categoria_esperada'):
            if interpretacion.get('categoria') == expectativa['categoria_esperada']:
                evaluacion['categoria_detectada'] = True
        
        # Evaluar atributos
        if expectativa.get('atributos_esperados'):
            atributos_encontrados = interpretacion.get('atributos', [])
            if all(attr in atributos_encontrados for attr in expectativa['atributos_esperados']):
                evaluacion['atributos_detectados'] = True
        
        # Evaluar filtros de precio
        if expectativa.get('filtro_precio'):
            filtros = interpretacion.get('filtros', {}).get('precio', {})
            filtro_esperado = expectativa['filtro_precio']
            
            if filtro_esperado.get('min') and filtros.get('min') == filtro_esperado['min']:
                evaluacion['filtros_aplicados'] = True
            elif filtro_esperado.get('max') and filtros.get('max') == filtro_esperado['max']:
                evaluacion['filtros_aplicados'] = True
        
        # Evaluar si hay resultados
        if len(recomendaciones) > 0:
            evaluacion['resultados_apropiados'] = True
        
        # Mostrar evaluación
        total_criterios = len([k for k in evaluacion.keys() if expectativa.get(k.replace('_detectado', '_esperado').replace('_detectados', '_esperados').replace('_aplicados', '_precio').replace('_apropiados', '')) is not None])
        criterios_cumplidos = sum(evaluacion.values())
        
        if total_criterios > 0:
            porcentaje = (criterios_cumplidos / total_criterios) * 100
            color = Colors.GREEN if porcentaje >= 80 else Colors.WARNING if porcentaje >= 60 else Colors.FAIL
            print(f"{color}📊 EVALUACIÓN: {criterios_cumplidos}/{total_criterios} criterios ({porcentaje:.0f}%){Colors.ENDC}")
        
        return evaluacion
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error evaluando resultado: {e}{Colors.ENDC}")
        return {}

def main():
    """Pruebas completas del sistema escalable"""
    
    print(Colors.HEADER + Colors.BOLD + """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                   🧪 TEST CASOS COMPLETOS LYNX 3.0              ║
    ║                     Sistema Escalable - 1000+ Productos         ║
    ╚══════════════════════════════════════════════════════════════════╝
    """ + Colors.ENDC)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema escalable...")
    try:
        configuracion = ConfiguracionLYNX()
        analizador = AnalizadorLexicoLYNX(configuracion)
        print("✅ Sistema inicializado correctamente")
        print()
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")
        return
    
    # Casos de prueba completos
    casos_prueba = [
        {
            'consulta': 'papitas sin picante',
            'descripcion': 'Búsqueda de papitas excluyendo sabor picante',
            'expectativa': {
                'producto_esperado': 'papitas',
                'atributos_esperados': ['sin_picante'],
                'resultados': True
            }
        },
        {
            'consulta': 'botana mayor a 50',
            'descripcion': 'Búsqueda de botanas con precio superior a $50',
            'expectativa': {
                'categoria_esperada': 'snacks',
                'filtro_precio': {'min': 50.0},
                'resultados': True
            }
        },
        {
            'consulta': 'bebidas sin azucar',
            'descripcion': 'Búsqueda de bebidas dietéticas (atributo compuesto)',
            'expectativa': {
                'categoria_esperada': 'bebidas',
                'atributos_esperados': ['sin_azucar'],
                'resultados': True
            }
        },
        {
            'consulta': 'productos picantes barato',
            'descripcion': 'Búsqueda con múltiples atributos (sabor + precio)',
            'expectativa': {
                'atributos_esperados': ['picante'],
                'filtro_precio': {'max': 50.0},
                'resultados': True
            }
        },
        {
            'consulta': 'chocolate',
            'descripcion': 'Búsqueda por nombre de producto específico',
            'expectativa': {
                'producto_esperado': 'chocolate',
                'categoria_esperada': 'Galletas y Dulces',
                'resultados': True
            }
        },
        {
            'consulta': 'coca cola',
            'descripcion': 'Búsqueda de marca específica',
            'expectativa': {
                'producto_esperado': 'coca',
                'categoria_esperada': 'Bebidas',
                'resultados': True
            }
        },
        {
            'consulta': 'paleta dulce',
            'descripcion': 'Búsqueda con atributo de sabor dulce',
            'expectativa': {
                'categoria_esperada': 'Galletas y Dulces',
                'atributos_esperados': ['dulce'],
                'resultados': True
            }
        },
        {
            'consulta': 'leche sin lactosa',
            'descripcion': 'Búsqueda con atributo compuesto de salud',
            'expectativa': {
                'producto_esperado': 'leche',
                'atributos_esperados': ['sin_lactosa'],
                'resultados': True
            }
        },
        {
            'consulta': 'refresco grande barato',
            'descripcion': 'Búsqueda con múltiples filtros (tamaño + precio)',
            'expectativa': {
                'categoria_esperada': 'bebidas',
                'atributos_esperados': ['grande', 'barato'],
                'resultados': True
            }
        },
        {
            'consulta': 'frituras saladas',
            'descripcion': 'Búsqueda por categoría con atributo de sabor',
            'expectativa': {
                'categoria_esperada': 'snacks',
                'atributos_esperados': ['salado'],
                'resultados': True
            }
        },
        {
            'consulta': 'yogurt deslactosado',
            'descripcion': 'Búsqueda de producto lácteo sin lactosa',
            'expectativa': {
                'producto_esperado': 'yogurt',
                'atributos_esperados': ['deslactosado'],
                'resultados': True
            }
        },
        {
            'consulta': 'agua sin gas',
            'descripcion': 'Búsqueda con negación de atributo',
            'expectativa': {
                'producto_esperado': 'agua',
                'atributos_esperados': ['sin_gas'],
                'resultados': True
            }
        },
        # Casos con corrección ortográfica
        {
            'consulta': 'votana picabte varata',
            'descripcion': 'Caso con múltiples errores ortográficos',
            'expectativa': {
                'categoria_esperada': 'snacks',
                'atributos_esperados': ['picante', 'barato'],
                'correcciones': True
            }
        },
        {
            'consulta': 'koka kola sin asucar',
            'descripcion': 'Marca con errores + atributo con error',
            'expectativa': {
                'producto_esperado': 'coca',
                'atributos_esperados': ['sin_azucar'],
                'correcciones': True
            }
        },
        # Casos complejos
        {
            'consulta': 'productos para diabeticos',
            'descripcion': 'Búsqueda por contexto de salud',
            'expectativa': {
                'atributos_esperados': ['sin_azucar'],
                'resultados': True
            }
        },
        {
            'consulta': 'botana para fiesta barata',
            'descripcion': 'Búsqueda contextual con filtro de precio',
            'expectativa': {
                'categoria_esperada': 'snacks',
                'atributos_esperados': ['barato'],
                'resultados': True
            }
        }
    ]
    
    # Estadísticas generales
    total_casos = len(casos_prueba)
    casos_exitosos = 0
    tiempo_total = 0
    
    print(f"🎯 Ejecutando {total_casos} casos de prueba...")
    print("=" * 70)
    print()
    
    # Ejecutar cada caso
    for i, caso in enumerate(casos_prueba, 1):
        print(f"{Colors.BOLD}CASO {i}/{total_casos}:{Colors.ENDC} {caso['descripcion']}")
        
        start_time = time.time()
        
        try:
            resultado_json = analizador.generar_json_resultado_completo(caso['consulta'])
            end_time = time.time()
            tiempo_caso = (end_time - start_time) * 1000
            tiempo_total += tiempo_caso
            
            # Mostrar resultado
            mostrar_resultado_detallado(caso['consulta'], resultado_json)
            
            # Evaluar
            evaluacion = evaluar_resultado(caso['consulta'], resultado_json, caso['expectativa'])
            
            # Contar como exitoso si cumple la mayoría de criterios
            criterios_cumplidos = sum(evaluacion.values())
            total_criterios = len([k for k in evaluacion.keys() if caso['expectativa'].get(k.replace('_detectado', '_esperado').replace('_detectados', '_esperados').replace('_aplicados', '_precio').replace('_apropiados', '')) is not None])
            
            if total_criterios > 0 and (criterios_cumplidos / total_criterios) >= 0.6:
                casos_exitosos += 1
            
            print(f"⏱️  Tiempo: {tiempo_caso:.1f}ms")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error ejecutando caso: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
        
        print()
        print("─" * 70)
        print()
        
        # Pequeña pausa entre casos
        time.sleep(0.5)
    
    # Estadísticas finales
    print(Colors.HEADER + Colors.BOLD + "📊 RESUMEN GENERAL DE PRUEBAS:" + Colors.ENDC)
    print(f"   📋 Total casos ejecutados: {total_casos}")
    print(f"   ✅ Casos exitosos: {casos_exitosos}")
    print(f"   ❌ Casos con problemas: {total_casos - casos_exitosos}")
    
    porcentaje_exito = (casos_exitosos / total_casos) * 100
    color_resultado = Colors.GREEN if porcentaje_exito >= 80 else Colors.WARNING if porcentaje_exito >= 60 else Colors.FAIL
    print(f"   {color_resultado}🎯 Tasa de éxito: {porcentaje_exito:.1f}%{Colors.ENDC}")
    
    tiempo_promedio = tiempo_total / total_casos
    print(f"   ⏱️  Tiempo promedio: {tiempo_promedio:.1f}ms")
    print(f"   🚀 Tiempo total: {tiempo_total:.1f}ms")
    
    print()
    
    # Recomendaciones
    if porcentaje_exito >= 90:
        print(f"{Colors.GREEN}🎉 ¡Excelente! El sistema está funcionando muy bien{Colors.ENDC}")
    elif porcentaje_exito >= 70:
        print(f"{Colors.WARNING}⚠️  El sistema funciona bien, pero hay margen de mejora{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}🔧 El sistema necesita ajustes importantes{Colors.ENDC}")
    
    print()
    print(Colors.BLUE + "💡 Para mejorar resultados:" + Colors.ENDC)
    print("   • Verificar sincronización con base de datos escalable")
    print("   • Actualizar mapeo de atributos complejos")
    print("   • Revisar productos específicos en interpretador semántico")

if __name__ == "__main__":
    main()
