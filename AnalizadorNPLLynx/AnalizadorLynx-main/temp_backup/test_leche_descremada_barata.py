#!/usr/bin/env python3
# test_leche_descremada_barata.py - Prueba para consulta compleja multi-criterio
import json
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

def test_leche_descremada_barata():
    """Prueba específica para búsqueda 'leche descremada barata'"""
    
    print("🧪 PRUEBA ESPECÍFICA: 'leche descremada barata'")
    print("=" * 70)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema...")
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✅ Sistema inicializado")
    print()
    
    # Consulta a probar
    consulta = "leche descremada barata"
    
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
            if 'leche' in nombre.lower():
                indicadores.append("🥛")
            if any(palabra in nombre.lower() for palabra in ['descremada', 'light', 'deslactosada', 'baja grasa']):
                indicadores.append("💪")  # Saludable
            if precio < 15:
                indicadores.append("💰")  # Barata
            if 'lacteo' in categoria.lower():
                indicadores.append("🧀")  # Lácteo
                
            indicador_str = ''.join(indicadores) + ' ' if indicadores else ''
            
            print(f"{i}. {indicador_str}{nombre}")
            print(f"   💰 ${precio:.2f} | 📂 {categoria} | ⭐ {score*100:.0f}%")
            print(f"   🎯 Razones: {', '.join(razones[:3])}")
            print()
        
        # Análisis del resultado
        print("📊 ANÁLISIS:")
        
        # Verificar si detectó "leche"
        if 'leche' in str(interpretacion).lower():
            print("   ✅ Producto 'leche' detectado correctamente")
        else:
            print("   ❌ Producto 'leche' NO fue detectado")
        
        # Verificar si detectó "descremada"
        if 'descremada' in interpretacion.get('atributos', []) or 'descremada' in str(interpretacion).lower():
            print("   ✅ Atributo 'descremada' detectado correctamente")
        else:
            print("   ❌ Atributo 'descremada' NO fue detectado")
        
        # Verificar si detectó "barata" (filtro de precio)
        if 'barata' in str(interpretacion).lower() or filtros.get('precio'):
            print("   ✅ Filtro 'barata' detectado correctamente")
        else:
            print("   ❌ Filtro 'barata' NO fue detectado")
        
        # Verificar si la categoría es lácteos
        if 'lacteo' in interpretacion.get('categoria', '').lower():
            print("   ✅ Categoría 'lácteos' detectada correctamente")
        else:
            print("   ⚠️  Categoría 'lácteos' no detectada explícitamente")
        
        # Verificar si los productos encontrados son apropiados
        productos_leche = 0
        productos_descremada = 0
        productos_baratos = 0
        productos_lacteos = 0
        productos_completos = 0  # Leche + descremada + barata
        
        for rec in recomendaciones:
            nombre = rec.get('name', '').lower()
            categoria = rec.get('category', '').lower()
            precio = rec.get('price', 0)
            
            es_leche = 'leche' in nombre
            es_descremada = any(palabra in nombre for palabra in ['descremada', 'light', 'deslactosada', 'baja grasa'])
            es_barata = precio < 20  # Consideramos barata menos de $20 para leche
            es_lacteo = 'lacteo' in categoria
            es_completo = es_leche and es_descremada and es_barata
            
            if es_leche:
                productos_leche += 1
            if es_descremada:
                productos_descremada += 1
            if es_barata:
                productos_baratos += 1
            if es_lacteo:
                productos_lacteos += 1
            if es_completo:
                productos_completos += 1
        
        print(f"   🥛 Productos de leche: {productos_leche}/{len(recomendaciones)}")
        print(f"   💪 Productos descremados: {productos_descremada}/{len(recomendaciones)}")
        print(f"   💰 Productos baratos (<$20): {productos_baratos}/{len(recomendaciones)}")
        print(f"   🧀 Productos lácteos: {productos_lacteos}/{len(recomendaciones)}")
        print(f"   🎯 Leche descremada barata (todo): {productos_completos}/{len(recomendaciones)}")
        
        # Evaluación del comportamiento
        if productos_leche > len(recomendaciones) * 0.7:
            print("   ✅ Buena detección de productos de leche")
        else:
            print("   ⚠️  Pocos productos de leche encontrados")
            
        if productos_descremada > 0:
            print("   ✅ Encontrados productos descremados/light")
        else:
            print("   ❌ No se encontraron productos descremados")
            
        if productos_baratos > len(recomendaciones) * 0.5:
            print("   ✅ Buena aplicación del filtro 'barata'")
        else:
            print("   ⚠️  Pocos productos baratos encontrados")
            
        if productos_lacteos > len(recomendaciones) * 0.8:
            print("   ✅ Excelente categorización en lácteos")
        else:
            print("   ⚠️  Algunos productos no son lácteos")
        
        if productos_completos > 0:
            print("   ✅ Encontrados productos que cumplen TODOS los criterios")
            if productos_completos >= 3:
                print("   ✅ Múltiples opciones disponibles")
        else:
            print("   ❌ No se encontraron productos que cumplan todos los criterios")
        
        # Verificar orden por precio (más baratos primero)
        precios = [rec.get('price', 0) for rec in recomendaciones[:5]]
        if len(precios) > 1:
            ordenados_por_precio = all(precios[i] <= precios[i+1] for i in range(len(precios)-1))
            if ordenados_por_precio:
                print("   ✅ Productos ordenados por precio (baratos primero)")
            else:
                print("   ⚠️  Los productos no están ordenados por precio")
        
        # Verificar scoring inteligente
        productos_exactos_top = sum(1 for rec in recomendaciones[:3] if 'leche' in rec.get('name', '').lower() and any(palabra in rec.get('name', '').lower() for palabra in ['descremada', 'light']))
        if productos_exactos_top >= 2:
            print("   ✅ Los productos más específicos aparecen primero")
        else:
            print("   ⚠️  Los productos más específicos no priorizan correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_leche_descremada_barata()
