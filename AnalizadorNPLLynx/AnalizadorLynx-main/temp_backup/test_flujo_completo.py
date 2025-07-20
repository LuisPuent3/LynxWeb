# test_flujo_completo.py - Prueba del flujo completo
from analizador_lexico import AnalizadorLexicoLYNX
from utilidades import ConfiguracionLYNX
import json

print("=== PRUEBA FLUJO COMPLETO ===")

config = ConfiguracionLYNX()
analizador = AnalizadorLexicoLYNX(config)

# Test con "cheetos barata"
consulta = "cheetos barata"
print(f"\nConsulta: '{consulta}'")

try:
    resultado_json = analizador.generar_json_resultado_completo(consulta)
    resultado = json.loads(resultado_json)
    
    print(f"✅ Análisis completado")
    print(f"Correcciones aplicadas: {resultado.get('corrections', {}).get('applied', False)}")
    
    # Mostrar interpretación
    interpretacion = resultado.get('interpretation', {})
    print(f"Interpretación - Producto: {interpretacion.get('producto')}")
    print(f"Interpretación - Categoría: {interpretacion.get('categoria')}")
    print(f"Interpretación - Filtros: {interpretacion.get('filtros')}")
    
    # Mostrar recomendaciones
    recomendaciones = resultado.get('recommendations', [])
    print(f"Recomendaciones encontradas: {len(recomendaciones)}")
    
    for i, rec in enumerate(recomendaciones):
        print(f"  {i+1}. {rec.get('name', 'Sin nombre')} (${rec.get('price', 0)}) - Score: {rec.get('match_score', 0)}")
        print(f"      Razones: {rec.get('match_reasons', [])}")
    
    if not recomendaciones:
        print("❌ No se generaron recomendaciones")
        print("SQL generado:", resultado.get('sql_query'))
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN PRUEBA ===")
