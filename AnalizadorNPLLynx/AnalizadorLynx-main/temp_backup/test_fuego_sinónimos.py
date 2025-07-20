#!/usr/bin/env python3
"""
TEST ESPECÍFICO PARA SINÓNIMOS DE FUEGO Y FLAMING HOT

Verifica que los nuevos sinónimos de picante funcionen correctamente:
- fuego
- flaming hot
- flamming hot
- sabor fuego
- con fuego

Autor: GitHub Copilot
Fecha: 2025-01-19
"""

from analizador_lexico import AnalizadorLexicoLYNX
from adaptador_escalable import ConfiguracionLYNXEscalable
import time

def colorear(texto: str, color: str) -> str:
    """Colorear texto para la consola"""
    colores = {
        'verde': '\033[92m',
        'rojo': '\033[91m',
        'amarillo': '\033[93m',
        'azul': '\033[94m',
        'morado': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    return f"{colores.get(color, '')}{texto}{colores['reset']}"

def test_sinonimos_fuego():
    """Test completo de sinónimos de fuego/picante"""
    
    print(colorear("🔥 TEST DE SINÓNIMOS: FUEGO Y FLAMING HOT", 'amarillo'))
    print("=" * 60)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema escalable...")
    adaptador = ConfiguracionLYNXEscalable()
    analizador = AnalizadorLexicoLYNX(adaptador)
    
    # Casos de prueba específicos para fuego/picante
    casos_test = [
        {
            'query': 'papitas fuego',
            'esperado': 'Debe encontrar productos picantes',
            'categoria_esperada': 'snacks'
        },
        {
            'query': 'botana flaming hot',
            'esperado': 'Debe encontrar productos picantes tipo flaming hot',
            'categoria_esperada': 'snacks'
        },
        {
            'query': 'snacks con fuego',
            'esperado': 'Debe encontrar snacks picantes',
            'categoria_esperada': 'snacks'
        },
        {
            'query': 'papas sabor fuego',
            'esperado': 'Debe encontrar papas picantes',
            'categoria_esperada': 'snacks'
        },
        {
            'query': 'flamming hot cheetos',
            'esperado': 'Debe interpretar flaming hot como picante',
            'categoria_esperada': 'snacks'
        },
        {
            'query': 'producto hot',
            'esperado': 'Debe encontrar productos picantes',
            'categoria_esperada': None
        }
    ]
    
    resultados_exitosos = 0
    tiempo_total = 0
    
    for i, caso in enumerate(casos_test, 1):
        print(f"\n{colorear(f'CASO {i}/6: {caso['query']}', 'cyan')}")
        print("-" * 50)
        
        inicio = time.time()
        
        # Análisis léxico
        tokens = analizador.analizar(caso['query'])
        interpretacion = analizador.interpretar_para_motor_recomendaciones(
            tokens, caso['query']
        )
        
        # Motor de recomendaciones
        resultados = adaptador.buscar_productos_inteligente(caso['query'])
        
        tiempo_caso = (time.time() - inicio) * 1000
        tiempo_total += tiempo_caso
        
        # Mostrar interpretación
        print(f"🧠 INTERPRETACIÓN:")
        if interpretacion.get('producto'):
            print(f"   🔍 Producto: {interpretacion['producto']}")
        if interpretacion.get('categoria'):
            print(f"   📂 Categoría: {interpretacion['categoria']}")
        if interpretacion.get('atributos'):
            print(f"   🏷️  Atributos: {', '.join(interpretacion['atributos'])}")
        
        # Verificar resultados
        success = False
        if resultados and len(resultados) > 0:
            # Verificar si hay atributo picante detectado
            tiene_picante = 'picante' in interpretacion.get('atributos', [])
            
            # Verificar si encontró productos relacionados con picante
            productos_picantes = [r for r in resultados if 'adobadas' in r['nombre'].lower() or 'picante' in r['nombre'].lower()]
            
            if tiene_picante or productos_picantes:
                success = True
                resultados_exitosos += 1
                print(f"{colorear('✅ ÉXITO', 'verde')}: Sinónimo de fuego/picante detectado correctamente")
            else:
                print(f"{colorear('⚠️  PARCIAL', 'amarillo')}: Encontró productos pero sin mapeo de picante")
        
        # Mostrar productos encontrados
        print(f"🛍️  PRODUCTOS ENCONTRADOS: {len(resultados)}")
        for j, producto in enumerate(resultados[:3], 1):
            nombre = producto['nombre']
            precio = producto.get('precio', 0)
            categoria = producto.get('categoria', 'N/A')
            print(f"   {j}. {nombre}")
            print(f"      💰 ${precio:.2f} | 📂 {categoria}")
        
        if not success:
            print(f"{colorear('❌ FALLO', 'rojo')}: No detectó correctamente el sinónimo")
        
        print(f"⏱️  Tiempo: {tiempo_caso:.1f}ms")
    
    # Resumen final
    print(f"\n{colorear('📊 RESUMEN FINAL', 'morado')}")
    print("=" * 60)
    print(f"📋 Total casos: 6")
    print(f"✅ Casos exitosos: {resultados_exitosos}")
    print(f"❌ Casos fallidos: {6 - resultados_exitosos}")
    print(f"🎯 Tasa de éxito: {(resultados_exitosos/6)*100:.1f}%")
    print(f"⏱️  Tiempo promedio: {tiempo_total/6:.1f}ms")
    
    # Conclusiones
    if resultados_exitosos >= 5:
        print(f"\n{colorear('🎉 EXCELENTE!', 'verde')} Los sinónimos de fuego/picante funcionan correctamente")
    elif resultados_exitosos >= 3:
        print(f"\n{colorear('👍 BIEN', 'amarillo')} Los sinónimos funcionan parcialmente, revisar mapeo")
    else:
        print(f"\n{colorear('🔧 NECESITA MEJORAS', 'rojo')} Los sinónimos requieren ajustes")
    
    return resultados_exitosos >= 4

if __name__ == "__main__":
    print("🔥 INICIANDO TEST DE SINÓNIMOS FUEGO/PICANTE")
    print("🕐", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    exito = test_sinonimos_fuego()
    
    print(f"\n🏁 Test completado: {'✅ ÉXITO' if exito else '❌ NECESITA MEJORAS'}")
