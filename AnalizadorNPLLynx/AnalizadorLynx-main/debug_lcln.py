#!/usr/bin/env python3
"""
Direct test of LCLN system with debugging
"""
import sys
sys.path.append('.')
from sistema_lcln_simple import SistemaLCLNSimplificado

print("🔍 Testing LCLN system directly with debugging...")

sistema = SistemaLCLNSimplificado()

# Test the exact query
consulta = "votana barata picabte menor a 20"
print(f"\n📝 Original query: '{consulta}'")

# Test corrector directly first
print("\n🧪 Testing corrector directly:")
resultado_corrector = sistema.corrector.corregir_consulta(consulta)
print(f"  Applied: {resultado_corrector['applied']}")
print(f"  Changes: {resultado_corrector['changes']}")
print(f"  Corrected: '{resultado_corrector['corrected_query']}'")

print("\n🔍 Testing full LCLN system:")
resultado = sistema.buscar_productos_inteligente(consulta)
print(f"  Applied: {resultado['corrections']['applied']}")
print(f"  Original: '{resultado['corrections']['original_query']}'")
print(f"  Corrected: '{resultado['corrections']['corrected_query']}'")
print(f"  Details: {resultado['corrections']['corrections_details']}")
