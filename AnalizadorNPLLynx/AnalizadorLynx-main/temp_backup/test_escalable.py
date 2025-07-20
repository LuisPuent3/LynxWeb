#!/usr/bin/env python3
"""
Test rápido del sistema escalable
"""

try:
    from arquitectura_escalable import ConfiguracionEscalableLYNX
    
    print("🔍 Probando sistema escalable...")
    config = ConfiguracionEscalableLYNX()
    
    # Obtener estadísticas
    stats = config.obtener_estadisticas()
    print(f"✅ Estadísticas obtenidas:")
    print(f"   • Productos: {stats['productos']['total']}")
    print(f"   • Sinónimos: {stats['sinonimos']['total']}")
    print(f"   • Categorías: {stats['categorias']['total']}")
    
    # Probar búsqueda
    print(f"\n🔍 Probando búsqueda:")
    resultados = config.buscar_productos_inteligente("coca", limite=3)
    print(f"   Resultados para 'coca': {len(resultados)}")
    for r in resultados[:2]:
        print(f"   • {r['nombre']} - ${r['precio']}")
    
    print(f"\n✅ Sistema funcionando correctamente")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
