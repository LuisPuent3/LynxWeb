#!/usr/bin/env python3
"""
Prueba directa del sistema LCLN mejorado
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

from sistema_lcln_simple import sistema_lcln_simple

def probar_mejoras():
    print("🧪 PROBANDO MEJORAS DEL SISTEMA LCLN")
    print("=" * 50)
    
    consultas_test = [
        "bebidas sin azucar",
        "limon", 
        "snacks dulces barato"
    ]
    
    for consulta in consultas_test:
        print(f"\n🔍 CONSULTA: '{consulta}'")
        print("-" * 30)
        
        try:
            result = sistema_lcln_simple.buscar_productos_inteligente(consulta)
            
            print(f"✅ Estrategia: {result['interpretation']['estrategia_usada']}")
            print(f"📦 Productos encontrados: {len(result['recommendations'])}")
            print(f"💬 Mensaje: {result['user_message']}")
            
            print("📋 Productos:")
            for i, prod in enumerate(result['recommendations'][:5], 1):
                print(f"  {i}. {prod['nombre']} - ${prod['precio']} ({prod['categoria']})")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    probar_mejoras()
