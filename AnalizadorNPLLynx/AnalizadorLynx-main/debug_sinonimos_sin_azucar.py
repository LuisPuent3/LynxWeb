#!/usr/bin/env python3

import sistema_lcln_mejorado_limpio

# Verificar sinónimos relacionados con "sin azucar"
sistema = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
sistema._actualizar_cache_dinamico()

print("=== VERIFICANDO SINÓNIMOS DE 'SIN AZÚCAR' ===")

# Buscar términos relacionados
terminos_buscar = ['sin', 'azucar', 'sin azucar', 'sin azúcar', 'light', 'zero', 'diet']

for termino in terminos_buscar:
    if termino.lower() in sistema._cache_sinonimos:
        print(f"\n'{termino}' encontrado en sinónimos:")
        sinonimos = sistema._cache_sinonimos[termino.lower()]
        for sin in sinonimos:
            print(f"  - {sin}")
    else:
        print(f"\n'{termino}' NO encontrado en sinónimos")

# Buscar cualquier sinónimo que contenga "sin" o "azucar"
print("\n=== TODOS LOS SINÓNIMOS RELACIONADOS ===")
relacionados = []
for termino, sinonimos_lista in sistema._cache_sinonimos.items():
    if 'sin' in termino.lower() or 'azucar' in termino.lower() or 'light' in termino.lower():
        relacionados.append((termino, sinonimos_lista))

print(f"Sinónimos relacionados encontrados: {len(relacionados)}")
for termino, sinonimos_lista in relacionados:
    print(f"\n'{termino}':")
    for sin in sinonimos_lista[:3]:  # Solo los primeros 3
        print(f"  - {sin}")
