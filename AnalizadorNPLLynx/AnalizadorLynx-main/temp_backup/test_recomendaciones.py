#!/usr/bin/env python3
"""
TEST DE RECOMENDACIONES - SISTEMA ESCALABLE

Prueba específica para verificar que las recomendaciones estén
funcionando correctamente con el nuevo sistema de atributos inteligentes.
"""

from adaptador_escalable import SimuladorBDLynxShopEscalable
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX
import json
import time

def test_busquedas_directas():
    """Probar búsquedas directas en el simulador escalable"""
    print("🧪 PROBANDO BÚSQUEDAS DIRECTAS EN SIMULADOR ESCALABLE")
    print("=" * 60)
    
    sim = SimuladorBDLynxShopEscalable()
    
    consultas_test = [
        "paleta dulce",
        "bebidas sin azucar",
        "productos picantes",
        "coca cola",
        "papitas sabritas",
        "chocolate",
        "dulce",
        "barato",
        "grande"
    ]
    
    for consulta in consultas_test:
        print(f"\n🔍 Consultando: '{consulta}'")
        resultados = sim.buscar_por_similitud(consulta)
        
        if resultados:
            print(f"   ✅ {len(resultados)} resultados encontrados:")
            for i, r in enumerate(resultados[:3], 1):
                print(f"      {i}. {r['nombre']} - ${r['precio']} (categoria: {r['categoria']})")
        else:
            print(f"   ❌ No se encontraron resultados")

def test_analizador_lexico():
    """Probar analizador léxico completo"""
    print(f"\n\n🧪 PROBANDO ANALIZADOR LÉXICO COMPLETO")
    print("=" * 60)
    
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    consultas_test = [
        "paleta dulce",
        "bebidas sin azucar",
        "productos picantes barato"
    ]
    
    for consulta in consultas_test:
        print(f"\n🔍 Analizando: '{consulta}'")
        
        try:
            # Usar el método completo del analizador
            resultado_json = analizador.generar_json_resultado_completo(consulta)
            resultado = json.loads(resultado_json)
            
            # Mostrar interpretación
            interpretacion = resultado.get('interpretation', {})
            print(f"   📂 Categoría detectada: {interpretacion.get('categoria', 'No detectada')}")
            
            # Mostrar recomendaciones
            recomendaciones = resultado.get('recommendations', [])
            print(f"   🛍️ Recomendaciones: {len(recomendaciones)}")
            
            for i, rec in enumerate(recomendaciones[:3], 1):
                print(f"      {i}. {rec.get('name', 'N/A')} - ${rec.get('price', 0)} (categoria: {rec.get('category', 'N/A')})")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_configuracion_escalable():
    """Probar configuración escalable directamente"""
    print(f"\n\n🧪 PROBANDO CONFIGURACIÓN ESCALABLE")
    print("=" * 60)
    
    try:
        from adaptador_escalable import ConfiguracionLYNXEscalable
        config_escalable = ConfiguracionLYNXEscalable()
        
        print(f"✅ Configuración escalable creada")
        print(f"   📦 Productos simples: {len(config_escalable.base_datos.get('productos_simples', []))}")
        print(f"   📦 Productos multi: {len(config_escalable.base_datos.get('productos_multi', []))}")
        print(f"   📂 Categorías: {config_escalable.base_datos.get('categorias', [])}")
        
        # Probar búsqueda escalable directa
        print(f"\n🔍 Probando búsqueda escalable directa:")
        
        consultas = ["dulce", "picante", "coca"]
        for consulta in consultas:
            resultados = config_escalable.simulador.config_escalable.buscar_productos_inteligente(consulta, limite=3)
            print(f"   '{consulta}': {len(resultados)} resultados")
            for r in resultados[:2]:
                print(f"      • {r['nombre']} - ${r['precio']}")
                
    except Exception as e:
        print(f"❌ Error con configuración escalable: {e}")
        import traceback
        traceback.print_exc()

def verificar_motor_recomendaciones():
    """Verificar que el motor de recomendaciones esté usando el sistema correcto"""
    print(f"\n\n🧪 VERIFICANDO MOTOR DE RECOMENDACIONES")
    print("=" * 60)
    
    configuracion = ConfiguracionLYNX()
    
    # Verificar tipo de simulador
    print(f"Tipo de simulador: {type(configuracion.simulador).__name__}")
    print(f"Usar escalable: {getattr(configuracion.simulador, 'usar_escalable', 'N/A')}")
    
    # Verificar estadísticas
    try:
        stats = configuracion.simulador.obtener_estadisticas()
        print(f"Tipo de arquitectura: {stats.get('tipo', 'N/A')}")
        print(f"Productos totales: {stats.get('productos', {}).get('total', 'N/A')}")
    except:
        print("No se pudieron obtener estadísticas")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE RECOMENDACIONES")
    print("=" * 80)
    
    # 1. Test búsquedas directas
    test_busquedas_directas()
    
    # 2. Test analizador léxico  
    test_analizador_lexico()
    
    # 3. Test configuración escalable
    test_configuracion_escalable()
    
    # 4. Verificar motor
    verificar_motor_recomendaciones()
    
    print(f"\n✅ TESTS COMPLETADOS")
