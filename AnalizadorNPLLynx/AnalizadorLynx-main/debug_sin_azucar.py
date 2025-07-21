#!/usr/bin/env python3

import sistema_lcln_mejorado_limpio

# Test específico para "bebidas sin azucar"
sistema = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
resultado = sistema.analizar_consulta_lcln("bebidas sin azucar")

print("=== ANÁLISIS DETALLADO: 'bebidas sin azucar' ===")
print(f"Consulta original: {resultado['consulta_original']}")

print("\n--- FASE 2: EXPANSIÓN DE SINÓNIMOS ---")
fase_2 = resultado['fase_2_expansion_sinonimos']
print(f"Términos expandidos: {len(fase_2['terminos_expandidos'])}")
print(f"Categorías detectadas: {fase_2['categorias_detectadas']}")
print(f"Atributos detectados: {fase_2['atributos_detectados']}")

print("\n--- FASE 4: INTERPRETACIÓN ---")
fase_4 = resultado['fase_4_interpretacion']
print(f"Tipo de búsqueda: {fase_4['tipo_busqueda']}")
print(f"Categoría principal: {fase_4['categoria_principal']}")
print(f"Atributos detectados: {fase_4['atributos']}")
print(f"Filtros precio: {fase_4['filtros_precio']}")

print("\n--- FASE 5: PRODUCTOS ENCONTRADOS ---")
fase_5 = resultado['fase_5_motor_recomendaciones']
print(f"Estrategia usada: {fase_5['estrategia_usada']}")
print(f"Total productos: {fase_5['total_encontrados']}")

print("\n--- PRIMEROS 5 PRODUCTOS ---")
for i, producto in enumerate(fase_5['productos_encontrados'][:5], 1):
    print(f"{i}. {producto['nombre']} - ${producto['precio']}")
    print(f"   ¿Tiene 'sin azúcar' en nombre? {'SÍ' if 'sin' in producto['nombre'].lower() or 'light' in producto['nombre'].lower() or 'zero' in producto['nombre'].lower() else 'NO'}")

print("\n--- VERIFICANDO PRODUCTOS 'SIN AZÚCAR' REALES ---")
# Buscar productos que SÍ tienen "sin azúcar" en el nombre
productos_sin_azucar = [p for p in fase_5['productos_encontrados'] 
                       if any(keyword in p['nombre'].lower() for keyword in ['sin azúcar', 'light', 'zero', 'diet'])]
print(f"Productos que SÍ son sin azúcar: {len(productos_sin_azucar)}")
for producto in productos_sin_azucar:
    print(f"  - {producto['nombre']} - ${producto['precio']}")
