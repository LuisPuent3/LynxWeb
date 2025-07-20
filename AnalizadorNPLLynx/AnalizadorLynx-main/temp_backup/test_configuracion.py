#!/usr/bin/env python3
# test_configuracion.py - Prueba de la nueva configuración dinámica

from utilidades import ConfiguracionLYNX

def test_configuracion():
    """Prueba la nueva configuración dinámica"""
    print("🧪 Probando nueva configuración dinámica LYNX...")
    
    try:
        config = ConfiguracionLYNX()
        print(config.generar_reporte_configuracion())
        
        # Mostrar algunos productos de ejemplo
        if hasattr(config, 'simulador'):
            print("\n📦 PRODUCTOS DE EJEMPLO:")
            productos_ejemplo = config.simulador.productos[:10]
            for prod in productos_ejemplo:
                print(f"   • {prod['nombre']} - ${prod['precio']} ({prod['categoria']})")
        
        print("\n✅ Configuración cargada exitosamente")
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_configuracion()
