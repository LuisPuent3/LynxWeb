#!/usr/bin/env python3
# test_bebidas_sin_azucar.py - Prueba específica para búsqueda de bebidas sin azúcar
import json
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

def test_bebidas_sin_azucar():
    """Prueba específica para búsqueda 'bebidas sin azucar'"""
    
    print("🧪 PRUEBA ESPECÍFICA: 'bebidas sin azucar'")
    print("=" * 60)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema...")
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✅ Sistema inicializado")
    print()
    
    # Consulta a probar
    consulta = "bebidas sin azucar"
    
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
            
            print(f"{i}. {nombre}")
            print(f"   💰 ${precio:.2f} | 📂 {categoria} | ⭐ {score*100:.0f}%")
            print(f"   🎯 Razones: {', '.join(razones[:3])}")
            print()
        
        # Análisis del resultado
        print("📊 ANÁLISIS:")
        
        # Verificar si detectó el modificador "sin"
        if 'sin_azucar' in interpretacion.get('atributos', []) or 'sin azucar' in str(interpretacion):
            print("   ✅ Atributo 'sin azucar' detectado correctamente")
        else:
            print("   ❌ Atributo 'sin azucar' NO fue detectado")
        
        # Verificar si detectó bebidas
        if 'bebidas' in interpretacion.get('categoria', '').lower():
            print("   ✅ Categoría 'bebidas' detectada correctamente")
        else:
            print("   ❌ Categoría 'bebidas' NO fue detectada")
        
        # Verificar si los productos encontrados son apropiados
        productos_bebidas = 0
        productos_sin_azucar = 0
        
        for rec in recomendaciones:
            nombre = rec.get('name', '').lower()
            categoria = rec.get('category', '').lower()
            
            if 'bebida' in categoria or any(palabra in nombre for palabra in ['agua', 'cola', 'jugo', 'refresco', 'té', 'café']):
                productos_bebidas += 1
            
            # Verificar que sean sin azúcar o bajos en azúcar
            if any(palabra in nombre for palabra in ['light', 'diet', 'sin azucar', 'zero', 'natural', 'agua']):
                productos_sin_azucar += 1
        
        print(f"   🥤 Productos de bebidas: {productos_bebidas}/{len(recomendaciones)}")
        print(f"   🚫 Productos sin azúcar: {productos_sin_azucar}/{len(recomendaciones)}")
        
        if productos_bebidas >= len(recomendaciones) * 0.7:
            print("   ✅ Categoría 'bebidas' bien representada")
        else:
            print("   ⚠️  Pocos productos de bebidas encontrados")
        
        if productos_sin_azucar > 0:
            print("   ✅ Algunos productos 'sin azúcar' encontrados")
        else:
            print("   ⚠️  No se encontraron productos sin azúcar específicos")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bebidas_sin_azucar()
