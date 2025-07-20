# test_motor.py - Prueba del motor de recomendaciones
from configuracion_bd import simulador_bd
from motor_recomendaciones import MotorRecomendaciones
from utilidades import ConfiguracionLYNX
import json

print("=== PRUEBA MOTOR DE RECOMENDACIONES ===")

config = ConfiguracionLYNX()
motor = MotorRecomendaciones(config)

# Test 1: Búsqueda por producto específico
print("\n1. Búsqueda: 'cheetos'")
interpretacion1 = {
    'producto': 'cheetos',
    'categoria': None, 
    'filtros': {}
}

recomendaciones1 = motor.generar_recomendaciones(interpretacion1, 3)
print(f"Resultados: {len(recomendaciones1)}")
for i, rec in enumerate(recomendaciones1):
    print(f"  {i+1}. {rec['name']} (${rec['price']}) - Score: {rec['match_score']}")

# Test 2: Búsqueda por categoría
print("\n2. Búsqueda por categoría: 'snacks'")
interpretacion2 = {
    'producto': None,
    'categoria': 'snacks', 
    'filtros': {}
}

recomendaciones2 = motor.generar_recomendaciones(interpretacion2, 5)
print(f"Resultados: {len(recomendaciones2)}")
for i, rec in enumerate(recomendaciones2):
    print(f"  {i+1}. {rec['name']} (${rec['price']}) - Score: {rec['match_score']}")

# Test 3: Búsqueda con filtros de precio
print("\n3. Búsqueda: snacks baratos")
interpretacion3 = {
    'producto': None,
    'categoria': 'snacks', 
    'filtros': {
        'precio': {'max': 20}
    }
}

recomendaciones3 = motor.generar_recomendaciones(interpretacion3, 5)
print(f"Resultados: {len(recomendaciones3)}")
for i, rec in enumerate(recomendaciones3):
    print(f"  {i+1}. {rec['name']} (${rec['price']}) - Score: {rec['match_score']}")
    if 'precio_en_rango' in rec.get('match_reasons', []):
        print(f"      ✅ Cumple filtro de precio")

print("\n=== FIN PRUEBAS ===")
