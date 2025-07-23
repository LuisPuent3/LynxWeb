#!/usr/bin/env python3
"""
Test detallado del procesamiento: papa picantes menor a 15 pesos
"""

from sistema_lcln_simple import SistemaLCLNSimplificado
from sistema_lcln_mejorado import sistema_lcln_mejorado

def analizar_paso_a_paso():
    consulta = "papa picantes menor a 15 pesos"
    
    print("=" * 80)
    print("ANÁLISIS PASO A PASO - PROCESAMIENTO COMPLETO")
    print("=" * 80)
    print(f"CONSULTA: '{consulta}'")
    print("=" * 80)
    
    # ========================================
    # 1. SISTEMA ORIGINAL
    # ========================================
    print("\n[PASO 1] SISTEMA ORIGINAL (SistemaLCLNSimplificado)")
    print("-" * 60)
    
    sistema_original = SistemaLCLNSimplificado()
    
    try:
        resultado_original = sistema_original.buscar_productos_inteligente(consulta, 10)
        
        print("[OK] RESULTADO SISTEMA ORIGINAL:")
        print(f"   - Productos encontrados: {resultado_original['products_found']}")
        print(f"   - Estrategia usada: {resultado_original['interpretation']['estrategia_usada']}")
        print(f"   - Mensaje: {resultado_original['user_message']}")
        print(f"   - Tiempo procesamiento: {resultado_original['processing_time_ms']:.1f}ms")
        
        if resultado_original['products_found'] > 0:
            print("\n[PRODUCTOS] PRODUCTOS ENCONTRADOS (Sistema Original):")
            for i, prod in enumerate(resultado_original['recommendations'][:5], 1):
                print(f"   {i}. {prod['nombre']} - ${prod['precio']} (Stock: {prod['cantidad']})")
        
        print(f"\n[INTERPRETACION] INTERPRETACION (Sistema Original):")
        interp = resultado_original['interpretation']
        print(f"   - Tipo: {interp['tipo']}")
        print(f"   - Término búsqueda: {interp['termino_busqueda']}")
        print(f"   - Categoría: {interp['categoria']}")
        
    except Exception as e:
        print(f"[ERROR] Error en sistema original: {e}")
    
    # ========================================
    # 2. SISTEMA MEJORADO (FORMAL)
    # ========================================
    print("\n[PASO 2] SISTEMA MEJORADO (Analisis Formal LCLN)")
    print("-" * 60)
    
    try:
        resultado_formal = sistema_lcln_mejorado.obtener_analisis_completo_formal(consulta)
        
        print("✅ RESUMEN EJECUTIVO (Sistema Formal):")
        resumen = resultado_formal['resumen_ejecutivo']
        print(f"   - Modo análisis: {resumen['modo_analisis']}")
        print(f"   - Productos encontrados: {resumen['productos_encontrados']}")
        print(f"   - Estrategia usada: {resumen['estrategia_usada']}")
        print(f"   - Conformidad LCLN: {resumen['conformidad_lcln']}")
        print(f"   - Tokens formales: {resumen['tokens_formales_count']}")
        print(f"   - Validación gramatical: {resumen.get('validacion_gramatical', 'N/A')}")
        
        # Fase 1: Corrección ortográfica
        if resultado_formal.get('fase_1_correccion'):
            fase1 = resultado_formal['fase_1_correccion']
            print(f"\n📝 FASE 1 - CORRECCIÓN ORTOGRÁFICA:")
            print(f"   - Correcciones aplicadas: {fase1['correcciones_aplicadas']}")
            print(f"   - Texto corregido: '{fase1['texto_corregido']}'")
            if fase1['correcciones']:
                for corr in fase1['correcciones']:
                    print(f"     * '{corr['palabra_original']}' → '{corr['palabra_corregida']}' (confianza: {corr['confianza']:.2f})")
        
        # Fase AFD: Análisis léxico formal
        if resultado_formal.get('fase_afd_lexico'):
            afd = resultado_formal['fase_afd_lexico']
            print(f"\n🔤 ANÁLISIS LÉXICO FORMAL (AFD):")
            print(f"   - Total tokens: {afd['estadisticas']['total_tokens']}")
            print(f"   - Tokens reconocidos: {afd['estadisticas']['tokens_reconocidos']}")
            print(f"   - Precisión reconocimiento: {afd['estadisticas']['precision_reconocimiento']:.2%}")
            
            print("\n   📋 TABLA DE TOKENS:")
            for token in afd['tabla_tokens']:
                print(f"      {token['tipo']:20} | '{token['lexema']:15}' | Prioridad: {token['prioridad']} | Confianza: {token['confianza']:.2f}")
        
        # Análisis sintáctico
        if resultado_formal.get('fase_analisis_sintactico'):
            sintactico = resultado_formal['fase_analisis_sintactico']
            print(f"\n📝 ANÁLISIS SINTÁCTICO (BNF):")
            print(f"   - Estructura válida: {sintactico['valida']}")
            print(f"   - Tipo gramática: {sintactico.get('tipo_gramatica', 'N/A')}")
            
            if sintactico.get('entidad_prioritaria'):
                ent = sintactico['entidad_prioritaria']
                print(f"   - Entidad prioritaria: {ent['tipo']} = '{ent['valor']}'")
            
            if sintactico.get('modificadores'):
                print("   - Modificadores encontrados:")
                for mod in sintactico['modificadores']:
                    print(f"     * {mod['tipo']}: {mod}")
            
            if sintactico.get('reglas_aplicadas'):
                print(f"   - Reglas aplicadas: {', '.join(sintactico['reglas_aplicadas'])}")
        
        # Validación gramatical
        if resultado_formal.get('validacion_gramatical'):
            validacion = resultado_formal['validacion_gramatical']
            print(f"\n✅ VALIDACIÓN GRAMATICAL:")
            print(f"   - Cumple especificación LCLN: {validacion['cumple_especificacion_lcln']}")
            print(f"   - Nivel conformidad: {validacion['nivel_conformidad']}")
            
            if validacion['patrones_reconocidos']:
                print("   - Patrones reconocidos:")
                for patron in validacion['patrones_reconocidos']:
                    print(f"     * {patron}")
            
            if validacion['errores_gramaticales']:
                print("   - Errores gramaticales:")
                for error in validacion['errores_gramaticales']:
                    print(f"     * {error}")
        
        # Productos del sistema formal
        productos_formal = resultado_formal['fase_5_motor_recomendaciones']['productos_encontrados']
        if productos_formal:
            print(f"\n🛍️ PRODUCTOS ENCONTRADOS (Sistema Formal):")
            for i, prod in enumerate(productos_formal[:5], 1):
                print(f"   {i}. {prod['nombre']} - ${prod['precio']} (Stock: {prod['cantidad']})")
        
    except Exception as e:
        print(f"❌ Error en sistema formal: {e}")
        import traceback
        traceback.print_exc()
    
    # ========================================
    # 3. RESULTADO COMBINADO
    # ========================================
    print("\n" + "=" * 80)
    print("🔄 PASO 3: RESULTADO COMBINADO (como lo recibe tu frontend)")
    print("=" * 80)
    
    print("📡 ENDPOINT: POST /search")
    print("📨 ESTRUCTURA DE RESPUESTA:")
    print("""
    {
      "success": true,
      "products_found": [número de productos del sistema original],
      "recommendations": [productos del sistema original],
      "interpretation": {
        "estrategia_usada": "[estrategia del sistema original]"
      },
      "metadata": {
        "cache_timestamp": "[timestamp]",
        "analisis_lexico_plus": {
          "conformidad_lcln": "[ALTO/MEDIO/BAJO del sistema formal]",
          "tokens_formales": [número de tokens del análisis formal],
          "precision_tokens": [precisión del AFD]
        }
      }
    }
    """)
    
    print("\n✅ RESUMEN FINAL:")
    print("   - El sistema ORIGINAL procesa la consulta y devuelve productos")
    print("   - El sistema FORMAL analiza léxica y sintácticamente la consulta")
    print("   - Se combinan: productos del original + metadatos del formal")
    print("   - Tu frontend recibe productos reales + información de calidad del análisis")

if __name__ == "__main__":
    analizar_paso_a_paso()