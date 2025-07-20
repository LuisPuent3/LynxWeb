#!/usr/bin/env python3
# test_snacks_sin_sal.py - Prueba para modificador negativo específico
import json
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

def test_snacks_sin_sal():
    """Prueba específica para búsqueda 'snacks sin sal'"""
    
    print("🧪 PRUEBA ESPECÍFICA: 'snacks sin sal'")
    print("=" * 60)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema...")
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✅ Sistema inicializado")
    print()
    
    # Consulta a probar
    consulta = "snacks sin sal"
    
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
            if 'snack' in categoria.lower():
                indicadores.append("🍿")
            if any(palabra in nombre.lower() for palabra in ['natural', 'sin sal', 'clasica', 'original']):
                indicadores.append("🚫🧂")
            if any(palabra in nombre.lower() for palabra in ['salad', 'adobad', 'chile']):
                indicadores.append("⚠️")
                
            indicador_str = ''.join(indicadores) + ' ' if indicadores else ''
            
            print(f"{i}. {indicador_str}{nombre}")
            print(f"   💰 ${precio:.2f} | 📂 {categoria} | ⭐ {score*100:.0f}%")
            print(f"   🎯 Razones: {', '.join(razones[:3])}")
            print()
        
        # Análisis del resultado
        print("📊 ANÁLISIS:")
        
        # Verificar si detectó "sin sal"
        if 'sin_sal' in interpretacion.get('atributos', []) or 'sin sal' in str(interpretacion):
            print("   ✅ Atributo 'sin sal' detectado correctamente")
        else:
            print("   ❌ Atributo 'sin sal' NO fue detectado")
        
        # Verificar si detectó "snacks"
        if 'snack' in interpretacion.get('categoria', '').lower() or 'snack' in str(interpretacion).lower():
            print("   ✅ Categoría 'snacks' detectada correctamente")
        else:
            print("   ❌ Categoría 'snacks' NO fue detectada")
        
        # Verificar si los productos encontrados son apropiados
        productos_snacks = 0
        productos_sin_sal = 0
        productos_con_sal = 0
        productos_ambos = 0
        
        for rec in recomendaciones:
            nombre = rec.get('name', '').lower()
            categoria = rec.get('category', '').lower()
            
            es_snack = 'snack' in categoria or any(palabra in nombre for palabra in ['papitas', 'chips', 'fritas', 'sabritas', 'doritos'])
            es_sin_sal = any(palabra in nombre for palabra in ['natural', 'sin sal', 'clasica', 'original']) and not any(palabra in nombre for palabra in ['salad', 'adobad'])
            es_con_sal = any(palabra in nombre for palabra in ['salad', 'adobad', 'chile', 'picante'])
            
            if es_snack:
                productos_snacks += 1
            if es_sin_sal:
                productos_sin_sal += 1
            if es_con_sal:
                productos_con_sal += 1
            if es_snack and es_sin_sal:
                productos_ambos += 1
        
        print(f"   🍿 Productos snacks: {productos_snacks}/{len(recomendaciones)}")
        print(f"   🚫 Productos sin sal: {productos_sin_sal}/{len(recomendaciones)}")
        print(f"   ⚠️  Productos CON sal: {productos_con_sal}/{len(recomendaciones)}")
        print(f"   🎯 Snacks sin sal ideales: {productos_ambos}/{len(recomendaciones)}")
        
        # Evaluación del comportamiento
        if productos_snacks > len(recomendaciones) * 0.7:
            print("   ✅ Buena categorización de snacks")
        else:
            print("   ⚠️  Pocos productos de snacks encontrados")
            
        if productos_sin_sal > productos_con_sal:
            print("   ✅ Prioriza productos sin sal correctamente")
        else:
            print("   ❌ No está priorizando productos sin sal")
            
        if productos_ambos > 0:
            print("   ✅ Encontrados snacks que cumplen criterio 'sin sal'")
        else:
            print("   ❌ No se encontraron snacks específicamente sin sal")
        
        # Verificar que no hay demasiados productos con sal
        if productos_con_sal < len(recomendaciones) * 0.3:
            print("   ✅ Filtro 'sin sal' funciona bien (pocos productos salados)")
        else:
            print("   ⚠️  Muchos productos salados - filtro 'sin sal' necesita mejoras")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_snacks_sin_sal()
