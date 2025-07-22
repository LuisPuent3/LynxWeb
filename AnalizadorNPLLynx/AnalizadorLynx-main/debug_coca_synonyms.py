#!/usr/bin/env python3

import sistema_lcln_mejorado_limpio

# Create instance and update cache
sistema = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
sistema._actualizar_cache_dinamico()

print("=== SINÓNIMOS RELACIONADOS CON COCA ===")
for termino, sinonimos_list in sistema._cache_sinonimos.items():
    if 'coca' in termino.lower():
        print(f"\nTérmino: '{termino}'")
        for sinonimo in sinonimos_list:
            print(f"  - {sinonimo}")

print("\n=== BUSCANDO SINÓNIMOS DE TIPO PRODUCTO ===")
productos_sinonimos = []
for termino, sinonimos_list in sistema._cache_sinonimos.items():
    for sinonimo in sinonimos_list:
        if sinonimo.get('tipo') == 'producto':
            productos_sinonimos.append((termino, sinonimo))

print(f"Total sinónimos de productos: {len(productos_sinonimos)}")
for termino, sinonimo in productos_sinonimos:
    print(f"- '{termino}' -> '{sinonimo['categoria']}'")

print("\n=== PROBANDO DETECCIÓN DE PRODUCTOS ESPECÍFICOS ===")
# Simular fase 2
consulta = "coca cola"
resultado = sistema.analizar_consulta_lcln(consulta)
expansion = resultado['fase_2_expansion_sinonimos']
print(f"Productos detectados en fase 2: {expansion['productos_detectados']}")
