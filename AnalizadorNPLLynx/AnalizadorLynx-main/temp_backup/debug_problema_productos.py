#!/usr/bin/env python3
"""
Script de debug para identificar el problema del flujo de productos específicos
"""

from analizador_lexico import AnalizadorLexicoLYNX
from interpretador_semantico import InterpretadorSemantico  
from motor_recomendaciones import MotorRecomendaciones
from configuracion_bd import simulador_bd
from utilidades import ConfiguracionLYNX
import json

def debug_flujo_completo():
    print("🔍 DEBUG: Problema de flujo de productos específicos")
    print("=" * 60)
    
    # Inicializar componentes
    config = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(config)
    interpretador = InterpretadorSemantico()
    motor = MotorRecomendaciones(config)
    
    # Casos de prueba problemáticos (EXPANDIDOS - 10 casos)
    casos_test = [
        "papitas picantes",          # Caso original
        "papitas picosas",           # Sinónimo de picantes
        "snacks picosos",            # Categoría + sabor
        "bebida barata sin azucar",  # Complejo: bebida + precio + característica
        "yogurt de fresa barato",    # Lácteo + sabor + precio
        "botana dulce familiar",     # Snack + sabor + tamaño
        "refresco zero grande",      # Bebida + característica + tamaño
        "galletas chocolate económicas", # Dulce + sabor + precio
        "agua mineral pequeña",      # Bebida + tipo + tamaño
        "cheetos mega picosos"       # Producto + tamaño + sabor
    ]
    
    for i, consulta in enumerate(casos_test, 1):
        print(f"\n🧪 CASO {i}: '{consulta}'")
        print("-" * 40)
        
        # PASO 1: Análisis léxico
        print("📝 PASO 1 - Análisis Léxico:")
        tokens = analizador.analizar(consulta)
        tokens_reconocidos = [t for t in tokens if t['tipo'] != 'PALABRA_NO_RECONOCIDA']
        print(f"   Tokens reconocidos: {len(tokens_reconocidos)}")
        for token in tokens_reconocidos:
            print(f"   • {token['valor']} → {token['tipo']}")
        
        # PASO 2: Interpretación semántica
        print("\n🧠 PASO 2 - Interpretación Semántica:")
        interpretacion_completa = interpretador.interpretar_consulta_completa(tokens, consulta)
        interpretacion = interpretacion_completa.get('interpretacion_semantica', {})
        
        print(f"   Tipo: {interpretacion_completa.get('tipo', 'consulta_productos')}")
        print(f"   Producto: {interpretacion.get('producto', 'None')}")
        print(f"   Categoría: {interpretacion.get('categoria', 'None')}")
        print(f"   Confianza: {interpretacion_completa.get('confianza', 0):.2f}")
        
        # Usar la interpretación completa para el motor
        interpretacion = interpretacion_completa
        
        # PASO 3: Verificar en BD simulada
        print("\n💾 PASO 3 - Verificación en BD:")
        productos_bd = simulador_bd.buscar_por_similitud(consulta.split()[0])
        print(f"   Productos encontrados en BD: {len(productos_bd)}")
        for producto in productos_bd[:3]:
            print(f"   • {producto['nombre']} (${producto['precio']})")
        
        # PASO 4: Recomendaciones  
        print("\n💡 PASO 4 - Motor de Recomendaciones:")
        recomendaciones = []
        try:
            # Revisar qué datos tenemos para el motor
            datos_para_motor = interpretacion.get('interpretacion_semantica', {})
            print(f"   Datos enviados al motor: {datos_para_motor}")
            
            # Buscar el método correcto del motor de recomendaciones
            if hasattr(motor, 'procesar_consulta_completa'):
                recomendaciones = motor.procesar_consulta_completa(interpretacion)
            elif hasattr(motor, 'generar_recomendaciones'):
                # Pasar la interpretación semántica, no la completa
                recomendaciones = motor.generar_recomendaciones(datos_para_motor)
            elif hasattr(motor, 'obtener_productos_similares'):
                recomendaciones = motor.obtener_productos_similares(consulta, max_resultados=5)
            else:
                print(f"   ⚠️ Métodos disponibles: {[m for m in dir(motor) if not m.startswith('_')]}")
                recomendaciones = []
            
            print(f"   Recomendaciones generadas: {len(recomendaciones)}")
            for i, rec in enumerate(recomendaciones[:3]):
                if isinstance(rec, dict):
                    nombre = rec.get('name', rec.get('nombre', 'N/A'))
                    score = rec.get('match_score', rec.get('score', 0))
                    print(f"   {i+1}. {nombre} (score: {score:.2f})")
                else:
                    print(f"   {i+1}. {rec}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            recomendaciones = []
        
        # DIAGNÓSTICO
        print("\n🩺 DIAGNÓSTICO:")
        problemas = []
        
        if not any(t['tipo'] == 'PRODUCTO_SIMPLE' for t in tokens_reconocidos):
            problemas.append("AFD no detecta producto específico")
        
        if interpretacion.get('interpretacion_semantica', {}).get('producto') is None:
            problemas.append("Interpretador no identifica producto")
        
        if len(productos_bd) > 0 and len(recomendaciones) == 0:
            problemas.append("Motor no conecta BD con interpretación")
        
        if problemas:
            print("   ❌ PROBLEMAS DETECTADOS:")
            for problema in problemas:
                print(f"     - {problema}")
        else:
            print("   ✅ Flujo funcionando correctamente")

if __name__ == "__main__":
    debug_flujo_completo()
