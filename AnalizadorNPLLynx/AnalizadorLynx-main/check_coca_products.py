#!/usr/bin/env python3

import sistema_lcln_mejorado_limpio

# Create instance and update cache
sistema = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
sistema._actualizar_cache_dinamico()

print("=== PRODUCTOS CON 'COCA' ===")
coca_products = [p for p in sistema._cache_productos.values() if 'coca' in p['nombre'].lower()]
print(f"Productos encontrados: {len(coca_products)}")
for p in coca_products:
    print(f"- {p['nombre']} (${p['precio']})")

print("\n=== PRODUCTOS CON 'COLA' ===")
cola_products = [p for p in sistema._cache_productos.values() if 'cola' in p['nombre'].lower()]
print(f"Productos encontrados: {len(cola_products)}")
for p in cola_products:
    print(f"- {p['nombre']} (${p['precio']})")

print("\n=== SINÓNIMOS DE 'COCA' ===")
coca_sinonimos = [k for k, v in sistema._cache_sinonimos.items() if 'coca' in k.lower()]
print(f"Sinónimos encontrados: {coca_sinonimos}")

print("\n=== TODOS LOS SINÓNIMOS DE PRODUCTOS ===")
sinonimos_productos = [(k, v) for k, v in sistema._cache_sinonimos.items() if isinstance(v, dict) and v.get('tipo') == 'producto']
print(f"Total sinónimos de productos: {len(sinonimos_productos)}")
for termino, data in sinonimos_productos[:10]:  # Solo los primeros 10
    print(f"- '{termino}' -> '{data['categoria']}'")
    
print("\n=== DETALLES DEL CACHE DE SINÓNIMOS ===")
print(f"Tipo de cache: {type(sistema._cache_sinonimos)}")
if sistema._cache_sinonimos:
    primer_item = list(sistema._cache_sinonimos.items())[0]
    print(f"Primer item: {primer_item}")
