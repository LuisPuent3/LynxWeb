#!/usr/bin/env python3

import sistema_lcln_mejorado_limpio

sistema = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
resultado = sistema.analizar_consulta_lcln("coca cola")

print("=== CONTENIDO DE fase_4_interpretacion ===")
fase_4 = resultado['fase_4_interpretacion']
for key, value in fase_4.items():
    print(f"- {key}: {value}")

print("\n=== CONTENIDO DE fase_2_expansion_sinonimos ===")
fase_2 = resultado['fase_2_expansion_sinonimos']
for key, value in fase_2.items():
    print(f"- {key}: {value}")
    
print("\n=== CONTENIDO DE fase_3_tokenizacion ===")
fase_3 = resultado['fase_3_tokenizacion']
for key, value in fase_3.items():
    print(f"- {key}: {value}")
