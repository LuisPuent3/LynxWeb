#!/usr/bin/env python3
"""
TEST DIRECTO DE SINÓNIMOS EN BD

Verifica directamente los sinónimos en la base de datos
"""

from arquitectura_escalable import ConfiguracionEscalableLYNX

def test_directo_sinonimos():
    print("🔥 TEST DIRECTO DE SINÓNIMOS EN BD")
    print("=" * 50)
    
    config = ConfiguracionEscalableLYNX()
    
    # Test directo de sinónimos
    terminos_test = ['fuego', 'flaming', 'hot', 'picante', 'adobadas']
    
    for termino in terminos_test:
        print(f"\n🔍 Buscando sinónimos para: '{termino}'")
        sinonimos = config.bd_escalable.gestor_sinonimos.buscar_sinónimo(termino)
        
        if sinonimos:
            print(f"✅ Encontrados {len(sinonimos)} sinónimos:")
            for i, sin in enumerate(sinonimos[:5], 1):  # Mostrar primeros 5
                print(f"   {i}. '{sin.termino}' → Producto ID: {sin.producto_id}")
                print(f"      Categoría: {sin.categoria} | Confianza: {sin.confianza}")
                
                # Buscar el producto específico
                productos = config.bd_escalable.buscar_productos_avanzado({
                    'termino': '',  # Búsqueda por ID específico
                    'limit': 1
                })
                
                # Buscar producto por ID usando query SQL directa
                import sqlite3
                conn = sqlite3.connect(config.bd_escalable.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, precio, categoria FROM productos WHERE id = ?", (sin.producto_id,))
                resultado = cursor.fetchone()
                conn.close()
                
                if resultado:
                    print(f"      Producto: {resultado[0]} | ${resultado[1]} | {resultado[2]}")
                print()
        else:
            print("❌ No se encontraron sinónimos")

if __name__ == "__main__":
    test_directo_sinonimos()
