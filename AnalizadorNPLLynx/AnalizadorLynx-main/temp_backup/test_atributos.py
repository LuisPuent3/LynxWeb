#!/usr/bin/env python3
"""
Prueba del sistema de atributos inteligentes
"""
from adaptador_escalable import SimuladorBDLynxShopEscalable

print("🧪 PROBANDO SISTEMA DE ATRIBUTOS INTELIGENTES")
print("=" * 60)

# Crear simulador
sim = SimuladorBDLynxShopEscalable()

# Lista de atributos a probar
atributos = [
    ("🌶️ PICANTE", "picante"),
    ("💰 BARATO", "barato"),
    ("🧂 SALADO", "salado"),
    ("🍭 DULCE", "dulce"),
    ("📏 GRANDE", "grande"),
    ("🥤 COCA", "coca"),
    ("🍟 PAPITAS", "papitas")
]

for emoji_nombre, atributo in atributos:
    print(f"\n{emoji_nombre}:")
    resultados = sim.buscar_por_similitud(atributo)
    
    if resultados:
        for i, r in enumerate(resultados[:3], 1):
            print(f"   {i}. {r['nombre']} - ${r['precio']}")
    else:
        print("   ❌ Sin resultados")

print(f"\n✅ Prueba completada")
