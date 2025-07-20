# test_interpretador.py - Prueba directa del interpretador semántico
from interpretador_semantico import InterpretadorSemantico
import json

print("=== PRUEBA INTERPRETADOR SEMÁNTICO ===")

interpretador = InterpretadorSemantico()

# Simular tokens que deberían llegar del analizador léxico
tokens_test = [
    {'tipo': 'PALABRA_GENERICA', 'valor': 'cheetos', 'posicion': 0},
    {'tipo': 'PALABRA_GENERICA', 'valor': 'barata', 'posicion': 8}
]

print("Tokens de entrada:")
for token in tokens_test:
    print(f"  {token}")

# Procesar tokens
tokens_interpretados = interpretador.interpretar_tokens(tokens_test)

print(f"\nTokens interpretados:")
for token in tokens_interpretados:
    print(f"  {token}")

# Prueba de interpretación completa
print("\n--- Interpretación completa ---")
interpretacion = interpretador.interpretar_consulta_completa(tokens_test, "cheetos barata")
print(f"Producto detectado: {interpretacion['interpretacion_semantica'].get('producto')}")
print(f"Categoría detectada: {interpretacion['interpretacion_semantica'].get('categoria')}")
print(f"Filtros: {interpretacion['interpretacion_semantica'].get('filtros_precio')}")

print("\n=== FIN PRUEBA ===")
