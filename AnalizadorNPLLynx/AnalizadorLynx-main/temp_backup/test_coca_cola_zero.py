#!/usr/bin/env python3
# test_coca_cola_zero.py - Prueba para búsqueda de marca y variante específica
import json
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

def test_coca_cola_zero():
    """Prueba específica para búsqueda 'coca cola zero'"""
    
    print("🧪 PRUEBA ESPECÍFICA: 'coca cola zero'")
    print("=" * 60)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema...")
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✅ Sistema inicializado")
    print()
    
    # Consulta a probar
    consulta = "coca cola zero"
    
    print(f"🔍 Consultando: '{consulta}'")
    print()
    
    try:
        # Generar resultado completo
        resultado_json = analizador.generar_json_resultado_completo(consulta)
        resultado = json.loads(resultado_json)
        
        # Mostrar interpretación
        interpretacion = resultado.get('interpretation', {})
        print("🧠 INTERPRETACIÓN DEL SISTEMA:")
        print(f"   • Producto: {interpretacion.get('producto', 'No detectado')}")
        print(f"   • Categoría: {interpretacion.get('categoria', 'No detectada')}")
        print(f"   • Atributos: {interpretacion.get('atributos', [])}")
        
        filtros = interpretacion.get('filtros', {})
        if filtros.get('precio'):
            print(f"   • Filtros precio: {filtros['precio']}")
        
        print()
        
        # Mostrar recomendaciones
        recomendaciones = resultado.get('recommendations', [])
        print(f"🛍️  PRODUCTOS ENCONTRADOS: {len(recomendaciones)}")
        print()
        
        for i, rec in enumerate(recomendaciones, 1):
            nombre = rec.get('name', 'Sin nombre')
            precio = rec.get('price', 0)
            categoria = rec.get('category', 'Sin categoría')
            score = rec.get('match_score', 0)
            razones = rec.get('match_reasons', [])
            
            # Indicadores visuales
            indicadores = []
            if 'coca' in nombre.lower() and 'cola' in nombre.lower():
                indicadores.append("🥤")
            if 'zero' in nombre.lower() or 'light' in nombre.lower():
                indicadores.append("🚫🍯")  # Sin azúcar
            if any(palabra in nombre.lower() for palabra in ['500ml', '1l', '2l', '355ml']):
                indicadores.append("📏")  # Tamaño específico
                
            indicador_str = ''.join(indicadores) + ' ' if indicadores else ''
            
            print(f"{i}. {indicador_str}{nombre}")
            print(f"   💰 ${precio:.2f} | 📂 {categoria} | ⭐ {score*100:.0f}%")
            print(f"   🎯 Razones: {', '.join(razones[:3])}")
            print()
        
        # Análisis del resultado
        print("📊 ANÁLISIS:")
        
        # Verificar si detectó "coca cola"
        if 'coca cola' in str(interpretacion).lower() or ('coca' in str(interpretacion) and 'cola' in str(interpretacion)):
            print("   ✅ Marca 'Coca Cola' detectada correctamente")
        else:
            print("   ❌ Marca 'Coca Cola' NO fue detectada")
        
        # Verificar si detectó "zero"
        if 'zero' in interpretacion.get('atributos', []) or 'zero' in str(interpretacion).lower():
            print("   ✅ Variante 'Zero' detectada correctamente")
        else:
            print("   ❌ Variante 'Zero' NO fue detectada")
        
        # Verificar si la categoría es bebidas
        if 'bebida' in interpretacion.get('categoria', '').lower():
            print("   ✅ Categoría 'bebidas' detectada correctamente")
        else:
            print("   ⚠️  Categoría 'bebidas' no detectada explícitamente")
        
        # Verificar si los productos encontrados son apropiados
        productos_coca_cola = 0
        productos_zero = 0
        productos_bebidas = 0
        productos_exactos = 0
        
        for rec in recomendaciones:
            nombre = rec.get('name', '').lower()
            categoria = rec.get('category', '').lower()
            
            es_coca_cola = 'coca' in nombre and 'cola' in nombre
            es_zero = 'zero' in nombre
            es_bebida = 'bebida' in categoria
            es_exacto = es_coca_cola and es_zero
            
            if es_coca_cola:
                productos_coca_cola += 1
            if es_zero:
                productos_zero += 1
            if es_bebida:
                productos_bebidas += 1
            if es_exacto:
                productos_exactos += 1
        
        print(f"   🥤 Productos Coca Cola: {productos_coca_cola}/{len(recomendaciones)}")
        print(f"   🚫 Productos Zero: {productos_zero}/{len(recomendaciones)}")
        print(f"   🍺 Productos bebidas: {productos_bebidas}/{len(recomendaciones)}")
        print(f"   🎯 Coca Cola Zero exactos: {productos_exactos}/{len(recomendaciones)}")
        
        # Evaluación del comportamiento
        if productos_exactos > 0:
            print("   ✅ Encontrados productos Coca Cola Zero exactos")
            if productos_exactos >= 3:
                print("   ✅ Múltiples opciones de Coca Cola Zero disponibles")
        else:
            print("   ❌ No se encontraron productos Coca Cola Zero exactos")
            
        if productos_coca_cola > productos_exactos:
            print("   ✅ También muestra otras variantes de Coca Cola (buena expansión)")
        elif productos_coca_cola == productos_exactos and productos_exactos > 0:
            print("   ✅ Resultados muy específicos para Coca Cola Zero")
        else:
            print("   ⚠️  Pocos productos de Coca Cola encontrados")
            
        if productos_bebidas > len(recomendaciones) * 0.7:
            print("   ✅ Bien categorizado como bebidas")
        else:
            print("   ⚠️  Algunos resultados no son bebidas")
        
        # Verificar si están ordenados por relevancia (productos exactos primero)
        primeros_3 = recomendaciones[:3]
        exactos_en_top3 = sum(1 for rec in primeros_3 if 'coca' in rec.get('name', '').lower() and 'cola' in rec.get('name', '').lower() and 'zero' in rec.get('name', '').lower())
        
        if exactos_en_top3 >= 1:
            print("   ✅ Productos más específicos aparecen primero")
        else:
            print("   ⚠️  Los resultados más específicos no aparecen primero")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coca_cola_zero()
