#!/usr/bin/env python3
"""
Test simple del sistema LYNX para verificar que "papas" funciona
"""

from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

print("🧪 TEST SIMPLE LYNX - Probando 'papas'")

# Cargar configuración
print("📋 Cargando configuración...")
config = ConfiguracionLYNX()

# Crear analizador
print("🔍 Creando analizador...")
analizador = AnalizadorLexicoLYNX(config)

# Probar "papas"
print("🥔 Probando consulta: 'papas'")
try:
    resultado = analizador.procesar_consulta("papas")
    print("✅ RESULTADO:")
    print(f"   • Interpretación: {resultado.get('interpretacion', {})}")
    print(f"   • Recomendaciones: {len(resultado.get('recomendaciones', []))}")
    
    # Mostrar primeras 3 recomendaciones
    recomendaciones = resultado.get('recomendaciones', [])
    for i, rec in enumerate(recomendaciones[:3], 1):
        print(f"   {i}. {rec.get('name', 'N/A')} - ${rec.get('price', 0)}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Test completado")
