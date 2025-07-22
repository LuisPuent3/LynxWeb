#!/usr/bin/env python3

import sys
from pathlib import Path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

import sistema_lcln_mejorado_limpio

# Test what phases are returned
sistema = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
resultado = sistema.analizar_consulta_lcln("coca cola")

print("=== FASES RETORNADAS POR EL SISTEMA LIMPIO ===")
for fase, contenido in resultado.items():
    print(f"- {fase}")
    if isinstance(contenido, dict):
        for key in contenido.keys():
            print(f"  - {key}")
    
print(f"\nTotal de fases: {len(resultado)}")

# Check if the specific phase exists
if 'fase_4_interpretacion_semantica' in resultado:
    print("\n✅ fase_4_interpretacion_semantica exists")
else:
    print("\n❌ fase_4_interpretacion_semantica NOT found")
    print("Available phases:")
    for fase in resultado.keys():
        print(f"  - {fase}")
