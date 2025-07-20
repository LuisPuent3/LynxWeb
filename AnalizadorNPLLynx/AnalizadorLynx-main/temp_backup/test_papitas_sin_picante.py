#!/usr/bin/env python3
# test_papitas_sin_picante.py - Prueba específica para búsqueda de papitas sin picante
import json
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

def test_papitas_sin_picante():
    """Prueba específica para búsqueda 'papitas sin picante'"""
    
    print("🧪 PRUEBA ESPECÍFICA: 'papitas sin picante'")
    print("=" * 60)
    
    # Inicializar sistema
    print("🚀 Inicializando sistema...")
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✅ Sistema inicializado")
    print()
    
    # Consulta a probar
    consulta = "papitas sin picante"
    
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
        if 'sin_picante' in interpretacion.get('atributos', []) or 'sin picante' in str(interpretacion):
            print("   ✅ Atributo 'sin picante' detectado correctamente")
        else:
            print("   ❌ Atributo 'sin picante' NO fue detectado")
        
        # Verificar si detectó papitas
        if interpretacion.get('producto') == 'papitas' or 'papitas' in str(interpretacion).lower():
            print("   ✅ Producto 'papitas' detectado correctamente")
        else:
            print("   ❌ Producto 'papitas' NO fue detectado")
        
        # Verificar si los productos encontrados son apropiados
        productos_sin_picante = 0
        productos_con_papitas = 0
        
        for rec in recomendaciones:
            nombre = rec.get('name', '').lower()
            if 'papita' in nombre or 'papa' in nombre or 'frita' in nombre:
                productos_con_papitas += 1
            
            # Verificar que no contengan términos picantes
            if not any(palabra in nombre for palabra in ['picante', 'adobada', 'chile', 'jalapeño']):
                productos_sin_picante += 1
        
        print(f"   🥔 Productos con papitas: {productos_con_papitas}/{len(recomendaciones)}")
        print(f"   🚫 Productos sin picante: {productos_sin_picante}/{len(recomendaciones)}")
        
        if productos_sin_picante > productos_con_papitas:
            print("   ✅ Filtro 'sin picante' parece funcionar correctamente")
        else:
            print("   ⚠️  El filtro 'sin picante' podría necesitar mejoras")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_papitas_sin_picante()
