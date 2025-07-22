#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback

print("🔄 Iniciando prueba del sistema LCLN...")

try:
    print("📦 Importando módulo LCLN...")
    import sistema_lcln_mejorado_limpio
    print("✅ Módulo LCLN importado correctamente")
    
    print("🔧 Creando instancia del sistema...")
    sistema_lcln_mejorado = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
    print("✅ Instancia creada correctamente")
    
    print("🔍 Probando consulta: 'snacks picantes'...")
    resultado = sistema_lcln_mejorado.analizar_consulta_lcln("snacks picantes")
    print("✅ Consulta procesada")
    
    print("📋 Resultado obtenido:")
    print(f"Fases completadas: {len(resultado)} fases")
    
    # Verificar fase 5
    if 'fase_5_motor_recomendaciones' in resultado:
        motor = resultado['fase_5_motor_recomendaciones']
        print(f"🎯 Estrategia usada: {motor['estrategia_usada']}")
        print(f"📦 Productos encontrados: {motor['total_encontrados']}")
        
        if motor['productos_encontrados']:
            print("🛍️ Primeros 3 productos:")
            for i, producto in enumerate(motor['productos_encontrados'][:3], 1):
                print(f"   {i}. {producto['nombre']} - ${producto['precio']}")
                print(f"      Stock: {producto['cantidad']}, Imagen: {producto['imagen']}")
        else:
            print("❌ No se encontraron productos")
    else:
        print("❌ No se encontró la fase 5 en el resultado")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("📋 Traceback completo:")
    traceback.print_exc()

print("\n🏁 Prueba completada")
