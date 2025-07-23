#!/usr/bin/env python3

from sistema_lcln_simple import SistemaLCLNSimplificado
from sistema_lcln_mejorado import sistema_lcln_mejorado

consulta = "papas picantes menores a 40"

print("="*80)
print("ANALISIS PASO A PASO:", consulta)
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
        for i, prod in enumerate(resultado_original['recommendations'][:5], 1):
            print(f"  {i}. {prod['nombre']} - ${prod['precio']}")
    else:
        print("No se encontraron productos")
        
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

except Exception as e:
    print("Error en sistema formal:", e)

# PASO 3: Comparación con consulta anterior
print("\n[COMPARACION] CONSULTA ANTERIOR vs NUEVA")
print("-"*50)
print("ANTERIOR: 'papa picantes menor a 15 pesos'")
print("  - Filtro precio: <= $15")
print("  - Palabras: 6 tokens")
print("  - Productos: 4 encontrados")
print()
print("NUEVA: 'papas picantes menores a 40'")
print("  - Filtro precio: <= $40 (amplio)")
print("  - Palabras: 4 tokens")
print("  - Productos:", resultado_original.get('products_found', 0), "encontrados")
print()
print("DIFERENCIAS DETECTADAS:")
print("  - Sin 'pesos' explícito (debería detectar filtro numérico)")
print("  - Mayor rango de precio (40 vs 15)")
print("  - Plurales 'papas' y 'menores'")

print("\n" + "="*80)