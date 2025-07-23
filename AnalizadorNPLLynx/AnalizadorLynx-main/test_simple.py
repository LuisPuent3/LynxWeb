#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_simple import SistemaLCLNSimplificado
from sistema_lcln_mejorado import sistema_lcln_mejorado

consulta = "papa picantes menor a 15 pesos"

print("="*80)
print("ANALISIS PASO A PASO: " + consulta)
print("="*80)

# PASO 1: Sistema Original
print("\n[PASO 1] SISTEMA ORIGINAL")
print("-"*50)
sistema_original = SistemaLCLNSimplificado()

try:
    resultado_original = sistema_original.buscar_productos_inteligente(consulta, 10)
    print("Productos encontrados:", resultado_original['products_found'])
    print("Estrategia:", resultado_original['interpretation']['estrategia_usada'])
    print("Mensaje:", resultado_original['user_message'])
    
    if resultado_original['products_found'] > 0:
        print("\nProductos del sistema original:")
        for i, prod in enumerate(resultado_original['recommendations'][:3], 1):
            print(f"  {i}. {prod['nombre']} - ${prod['precio']}")
except Exception as e:
    print("Error:", e)

# PASO 2: Sistema Formal
print("\n[PASO 2] SISTEMA FORMAL (AFD + BNF + RD1-4)")
print("-"*50)

try:
    resultado_formal = sistema_lcln_mejorado.obtener_analisis_completo_formal(consulta)
    
    print("Conformidad LCLN:", resultado_formal['resumen_ejecutivo']['conformidad_lcln'])
    print("Tokens formales:", resultado_formal['resumen_ejecutivo']['tokens_formales_count'])
    print("Productos encontrados:", resultado_formal['resumen_ejecutivo']['productos_encontrados'])
    
    # Mostrar tokens del AFD
    if resultado_formal.get('fase_afd_lexico'):
        print("\nTokens del AFD:")
        for token in resultado_formal['fase_afd_lexico']['tabla_tokens']:
            print(f"  {token['tipo']:15} | '{token['lexema']}' | Prioridad: {token['prioridad']}")
    
    # Mostrar análisis sintáctico
    if resultado_formal.get('fase_analisis_sintactico'):
        sintactico = resultado_formal['fase_analisis_sintactico']
        print(f"\nAnalisis sintactico:")
        print(f"  Estructura valida: {sintactico['valida']}")
        print(f"  Tipo gramatica: {sintactico.get('tipo_gramatica', 'N/A')}")
        if sintactico.get('reglas_aplicadas'):
            print(f"  Reglas aplicadas: {', '.join(sintactico['reglas_aplicadas'])}")
    
    # Mostrar validación
    if resultado_formal.get('validacion_gramatical'):
        validacion = resultado_formal['validacion_gramatical']
        print(f"\nValidacion gramatical:")
        print(f"  Cumple LCLN: {validacion['cumple_especificacion_lcln']}")
        print(f"  Nivel: {validacion['nivel_conformidad']}")

except Exception as e:
    print("Error en sistema formal:", e)
    import traceback
    traceback.print_exc()

# PASO 3: Resultado Combinado
print("\n[PASO 3] RESULTADO COMBINADO")
print("-"*50)
print("En el endpoint /search tu frontend recibe:")
print("1. Productos del sistema ORIGINAL (funcionamiento normal)")
print("2. Metadatos del sistema FORMAL (informacion adicional)")
print()
print("Estructura de respuesta:")
print("""
{
  "success": true,
  "products_found": [del sistema original],
  "recommendations": [productos del sistema original],
  "metadata": {
    "analisis_lexico_plus": {
      "conformidad_lcln": "ALTO/MEDIO/BAJO",
      "tokens_formales": 4,
      "precision_tokens": 0.75
    }
  }
}
""")

print("="*80)
print("RESUMEN:")
print("- Sistema ORIGINAL: Busca y devuelve productos reales")
print("- Sistema FORMAL: Analiza la consulta lexica y sintacticamente") 
print("- COMBINADO: Productos reales + calidad del analisis")
print("="*80)