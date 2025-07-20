#!/usr/bin/env python3
# test_productos_picantes_baratos.py - Prueba para búsqueda con atributos combinados
import json
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

def test_productos_picantes_baratos():
    """Prueba específica para búsqueda 'productos picantes baratos'"""
    
    print("🧪 PRUEBA ESPECÍFICA: 'productos picantes baratos'")
    print("=" * 70)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema...")
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✅ Sistema inicializado")
    print()
    
    # Consulta a probar
    consulta = "productos picantes baratos"
    
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
            
            # Indicador visual si es barato y/o picante
            indicadores = []
            if precio < 10:
                indicadores.append("💰")
            if any(palabra in nombre.lower() for palabra in ['picante', 'adobada', 'chile', 'fuego', 'hot']):
                indicadores.append("🌶️")
            
            indicador_str = ''.join(indicadores) + ' ' if indicadores else ''
            
            print(f"{i}. {indicador_str}{nombre}")
            print(f"   💰 ${precio:.2f} | 📂 {categoria} | ⭐ {score*100:.0f}%")
            print(f"   🎯 Razones: {', '.join(razones[:3])}")
            print()
        
        # Análisis del resultado
        print("📊 ANÁLISIS:")
        
        # Verificar si detectó "picante"
        if 'picante' in interpretacion.get('atributos', []) or 'picante' in str(interpretacion):
            print("   ✅ Atributo 'picante' detectado correctamente")
        else:
            print("   ❌ Atributo 'picante' NO fue detectado")
        
        # Verificar si detectó "barato"
        if 'barato' in interpretacion.get('atributos', []) or 'barato' in str(interpretacion) or filtros.get('precio'):
            print("   ✅ Filtro 'barato' detectado correctamente")
        else:
            print("   ❌ Filtro 'barato' NO fue detectado")
        
        # Verificar si los productos encontrados son apropiados
        productos_picantes = 0
        productos_baratos = 0
        productos_ambos = 0
        
        for rec in recomendaciones:
            nombre = rec.get('name', '').lower()
            precio = rec.get('price', 0)
            
            es_picante = any(palabra in nombre for palabra in ['picante', 'adobada', 'chile', 'fuego', 'hot', 'jalapeño'])
            es_barato = precio < 10  # Consideramos barato menos de $10
            
            if es_picante:
                productos_picantes += 1
            if es_barato:
                productos_baratos += 1
            if es_picante and es_barato:
                productos_ambos += 1
        
        print(f"   🌶️  Productos picantes: {productos_picantes}/{len(recomendaciones)}")
        print(f"   💰 Productos baratos (<$10): {productos_baratos}/{len(recomendaciones)}")
        print(f"   🎯 Productos picantes Y baratos: {productos_ambos}/{len(recomendaciones)}")
        
        # Evaluación del comportamiento
        if productos_picantes > len(recomendaciones) * 0.6:
            print("   ✅ Buena detección de productos picantes")
        else:
            print("   ⚠️  Pocos productos picantes encontrados")
            
        if productos_baratos > len(recomendaciones) * 0.5:
            print("   ✅ Buena detección de productos baratos")
        else:
            print("   ⚠️  Pocos productos baratos encontrados")
            
        if productos_ambos > 0:
            print("   ✅ Encontrados productos que cumplen AMBOS criterios")
        else:
            print("   ❌ No se encontraron productos picantes Y baratos")
        
        # Verificar orden por precio (los más baratos primero)
        precios = [rec.get('price', 0) for rec in recomendaciones[:5]]
        if len(precios) > 1:
            ordenados_por_precio = all(precios[i] <= precios[i+1] for i in range(len(precios)-1))
            if ordenados_por_precio:
                print("   ✅ Productos ordenados correctamente por precio (baratos primero)")
            else:
                print("   ⚠️  Los productos no están ordenados por precio")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_productos_picantes_baratos()
