#!/usr/bin/env python3
"""
TEST SIMPLIFICADO PARA SINÓNIMOS DE FUEGO Y FLAMING HOT

Verifica que los nuevos sinónimos de picante funcionen correctamente.

Autor: GitHub Copilot
Fecha: 2025-01-19
"""

from arquitectura_escalable import ConfiguracionEscalableLYNX
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
    """Test simplificado de sinónimos de fuego/picante"""
    
    print(colorear("🔥 TEST DE SINÓNIMOS: FUEGO Y FLAMING HOT", 'amarillo'))
    print("=" * 60)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema escalable...")
    config = ConfiguracionEscalableLYNX()
    
    # Casos de prueba específicos para fuego/picante
    casos_test = [
        'papitas fuego',
        'botana flaming hot',
        'snacks con fuego',
        'productos hot',
        'papas fuego',
        'frituras hot'
    ]
    
    resultados_exitosos = 0
    tiempo_total = 0
    
    for i, caso in enumerate(casos_test, 1):
        print(f"\n{colorear(f'CASO {i}/6: {caso}', 'cyan')}")
        print("-" * 50)
        
        inicio = time.time()
        
        # Buscar productos usando método inteligente
        resultados = config.buscar_productos_inteligente(caso)
        
        tiempo_caso = (time.time() - inicio) * 1000
        tiempo_total += tiempo_caso
        
        # Verificar resultados
        success = False
        if resultados and len(resultados) > 0:
            # Buscar productos que contengan términos relacionados con picante
            productos_picantes = []
            for resultado in resultados:
                nombre_lower = resultado['nombre'].lower()
                if any(term in nombre_lower for term in ['adobadas', 'chile', 'picante', 'jalapeño', 'chipotle']):
                    productos_picantes.append(resultado)
            
            if productos_picantes:
                success = True
                resultados_exitosos += 1
                print(f"{colorear('✅ ÉXITO', 'verde')}: Encontró productos picantes correctamente")
            else:
                print(f"{colorear('⚠️  PARCIAL', 'amarillo')}: Encontró productos pero no específicamente picantes")
        else:
            print(f"{colorear('❌ FALLO', 'rojo')}: No encontró productos")
        
        # Mostrar productos encontrados
        print(f"🛍️  PRODUCTOS ENCONTRADOS: {len(resultados)}")
        for j, producto in enumerate(resultados[:3], 1):
            nombre = producto['nombre']
            precio = producto.get('precio', 0)
            categoria = producto.get('categoria', 'N/A')
            match_type = producto.get('match_type', 'N/A')
            print(f"   {j}. {nombre}")
            print(f"      💰 ${precio:.2f} | 📂 {categoria} | 🎯 {match_type}")
        
        if not success and len(resultados) > 0:
            print(f"{colorear('⚠️  INFO', 'amarillo')}: Se encontraron productos pero no parecen específicamente picantes")
        
        print(f"⏱️  Tiempo: {tiempo_caso:.1f}ms")
    
    # Resumen final
    print(f"\n{colorear('📊 RESUMEN FINAL', 'morado')}")
    print("=" * 60)
    print(f"📋 Total casos: 6")
    print(f"✅ Casos exitosos: {resultados_exitosos}")
    print(f"❌ Casos fallidos: {6 - resultados_exitosos}")
    print(f"🎯 Tasa de éxito: {(resultados_exitosos/6)*100:.1f}%")
    print(f"⏱️  Tiempo promedio: {tiempo_total/6:.1f}ms")
    
    # Test específico de sinónimos en la BD
    print(f"\n{colorear('🔍 TEST DE SINÓNIMOS EN BASE DE DATOS', 'cyan')}")
    print("-" * 50)
    
    terminos_fuego = ['fuego', 'flaming', 'hot']
    sinonimos_encontrados = 0
    
    for termino in terminos_fuego:
        sinonimos = config.bd_escalable.gestor_sinonimos.buscar_sinónimo(termino)
        if sinonimos:
            sinonimos_encontrados += 1
            print(f"✅ '{termino}': {len(sinonimos)} sinónimos encontrados")
            for sin in sinonimos[:2]:  # Mostrar solo primeros 2
                print(f"   • {sin.termino} → Producto ID: {sin.producto_id} (confianza: {sin.confianza})")
        else:
            print(f"❌ '{termino}': No se encontraron sinónimos")
    
    # Conclusiones
    if resultados_exitosos >= 4 and sinonimos_encontrados >= 2:
        print(f"\n{colorear('🎉 EXCELENTE!', 'verde')} Los sinónimos de fuego/picante funcionan correctamente")
        return True
    elif resultados_exitosos >= 2 or sinonimos_encontrados >= 1:
        print(f"\n{colorear('👍 BIEN', 'amarillo')} Los sinónimos funcionan parcialmente")
        return False
    else:
        print(f"\n{colorear('🔧 NECESITA MEJORAS', 'rojo')} Los sinónimos requieren ajustes")
        return False

if __name__ == "__main__":
    print("🔥 INICIANDO TEST DE SINÓNIMOS FUEGO/PICANTE")
    print("🕐", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    exito = test_sinonimos_fuego()
    
    print(f"\n🏁 Test completado: {colorear('✅ ÉXITO', 'verde') if exito else colorear('❌ NECESITA MEJORAS', 'rojo')}")
