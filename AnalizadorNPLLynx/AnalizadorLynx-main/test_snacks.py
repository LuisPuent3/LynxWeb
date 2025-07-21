#!/usr/bin/env python3
from configurador_hibrido import ConfiguradorHibridoLYNX

config = ConfiguradorHibridoLYNX()

# Probar búsqueda por categoría
print("🔍 Probando búsqueda por categoría 'Snacks':")
productos = config.buscar_productos_mysql(categoria='Snacks')
print(f"   Productos encontrados: {len(productos)}")
for p in productos[:5]:
    print(f"     - {p['nombre']} (ID:{p['id_producto']}) ${p['precio']}")

print("\n🔍 Probando búsqueda por consulta 'snacks':")
productos2 = config.buscar_productos_mysql(consulta='snacks')
print(f"   Productos encontrados: {len(productos2)}")
for p in productos2[:5]:
    print(f"     - {p['nombre']} (ID:{p['id_producto']}) ${p['precio']}")

print("\n🔍 Verificando sinónimos para 'snacks':")
sinonimos = config.obtener_sinonimos_sqlite('snacks')
print(f"   Sinónimos encontrados: {len(sinonimos)}")
for s in sinonimos:
    print(f"     - {s['termino']} → {s['categoria']} ({s['tipo']}, confianza:{s['confianza']})")

print("\n🔍 Probando análisis NLP completo:")
analisis = config.analizar_consulta_nlp('snacks')
print(f"   Análisis: {analisis}")

print("\n🔍 Probando búsqueda híbrida completa:")
resultado = config.buscar_productos_hibrido('snacks')
print(f"   Productos híbridos encontrados: {resultado['products_found']}")
for p in resultado['products'][:5]:
    print(f"     - {p['nombre']} (ID:{p['id_producto']}) ${p['precio']}")
