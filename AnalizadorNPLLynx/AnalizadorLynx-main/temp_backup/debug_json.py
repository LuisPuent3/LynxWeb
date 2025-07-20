# debug_json.py - Debug del JSON de respuesta
from analizador_lexico import AnalizadorLexicoLYNX
from utilidades import ConfiguracionLYNX
import json

print("=== DEBUG JSON RESPUESTA ===")

config = ConfiguracionLYNX()
analizador = AnalizadorLexicoLYNX(config)

consulta = "cheetos barata"
print(f"\nConsulta: '{consulta}'")

resultado_json = analizador.generar_json_resultado_completo(consulta)
resultado = json.loads(resultado_json)

print(f"\n=== ESTRUCTURA DEL JSON ===")
for key, value in resultado.items():
    if isinstance(value, list):
        print(f"{key}: [{len(value)} elementos]")
        if value:
            print(f"  Primer elemento: {value[0]}")
    elif isinstance(value, dict):
        print(f"{key}: [dict con {len(value)} keys]")
        print(f"  Keys: {list(value.keys())}")
    else:
        print(f"{key}: {value}")

print(f"\n=== RECOMENDACIONES ESPECÍFICAS ===")
recomendaciones = resultado.get('recommendations', [])
print(f"Número de recomendaciones: {len(recomendaciones)}")

for i, rec in enumerate(recomendaciones):
    print(f"\nRecomendación {i+1}:")
    for k, v in rec.items():
        print(f"  {k}: {v}")

print("\n=== FIN DEBUG ===")
