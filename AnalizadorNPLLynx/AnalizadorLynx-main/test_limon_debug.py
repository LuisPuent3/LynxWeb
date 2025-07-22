#!/usr/bin/env python3
"""
Test específico para debuggear el problema con "limón"
"""

from sistema_lcln_simple import sistema_lcln_simple

def test_limon_detallado():
    print("🔍 === ANÁLISIS DETALLADO DE BÚSQUEDA 'LIMÓN' ===")
    
    # Probar búsqueda de limón
    resultado = sistema_lcln_simple.buscar_productos_inteligente('limon')
    
    print(f"\n📊 RESULTADOS:")
    print(f"  - Productos encontrados: {resultado['products_found']}")
    print(f"  - Estrategia usada: {resultado['interpretation']['estrategia_usada']}")
    print(f"  - Mensaje usuario: {resultado['user_message']}")
    print(f"  - Tiempo proceso: {resultado['processing_time_ms']:.2f}ms")
    
    print(f"\n🏷️ PRODUCTOS DEVUELTOS:")
    for i, prod in enumerate(resultado['recommendations'], 1):
        print(f"  {i}. {prod['nombre']} - ${prod['precio']} ({prod['categoria']})")
    
    print(f"\n🔍 VERIFICANDO CACHE DE PRODUCTOS CON 'LIMÓN':")
    # Verificar qué productos tienen "limón" en el cache
    productos_con_limon = []
    for nombre, datos in sistema_lcln_simple._cache_productos.items():
        if 'limon' in nombre.lower() or 'limón' in nombre.lower():
            productos_con_limon.append({
                'nombre': datos['nombre'],
                'precio': datos['precio'],
                'categoria': datos['categoria']
            })
    
    print(f"  Productos en cache con 'limón': {len(productos_con_limon)}")
    for prod in productos_con_limon:
        print(f"    - {prod['nombre']} - ${prod['precio']} ({prod['categoria']})")
    
    print(f"\n🔍 VERIFICANDO SINÓNIMOS CON 'LIMÓN':")
    # Verificar sinónimos
    sinonimos_con_limon = []
    for sinonimo, productos in sistema_lcln_simple._cache_sinonimos.items():
        if 'limon' in sinonimo.lower() or 'limón' in sinonimo.lower():
            sinonimos_con_limon.append({
                'sinonimo': sinonimo,
                'productos': productos
            })
    
    print(f"  Sinónimos en cache con 'limón': {len(sinonimos_con_limon)}")
    for sin in sinonimos_con_limon:
        print(f"    - '{sin['sinonimo']}' → {[p['producto_nombre'] for p in sin['productos']]}")
    
    print(f"\n📈 ANÁLISIS DEL PROBLEMA:")
    print(f"  - Cache productos con limón: {len(productos_con_limon)}")
    print(f"  - Cache sinónimos con limón: {len(sinonimos_con_limon)}")
    print(f"  - Productos devueltos: {len(resultado['recommendations'])}")
    
    if len(productos_con_limon) > len(resultado['recommendations']):
        print(f"  ❌ PROBLEMA: El cache tiene {len(productos_con_limon)} productos con limón, pero solo devuelve {len(resultado['recommendations'])}")
        print(f"      Esto sugiere que la lógica de búsqueda está siendo muy restrictiva")

def verificar_productos_completos():
    print(f"\n🧠 === ANÁLISIS AFD - PRODUCTOS COMPLETOS ===")
    
    # Forzar actualización de cache
    sistema_lcln_simple._actualizar_cache_dinamico()
    
    print(f"📊 ESTADÍSTICAS DE CACHE:")
    print(f"  - Total productos en cache: {len(sistema_lcln_simple._cache_productos)}")
    print(f"  - Total categorías en cache: {len(sistema_lcln_simple._cache_categorias)}")
    print(f"  - Total sinónimos en cache: {len(sistema_lcln_simple._cache_sinonimos)}")
    
    print(f"\n🔍 TODOS LOS PRODUCTOS EN CACHE:")
    for i, (nombre, datos) in enumerate(sistema_lcln_simple._cache_productos.items(), 1):
        print(f"  {i:2d}. {datos['nombre']} - ${datos['precio']} ({datos['categoria']})")
    
    # Ver qué productos se están considerando "completos" para AFD
    productos_completos = []
    productos_multi = []
    
    for nombre in sistema_lcln_simple._cache_productos.keys():
        palabras = nombre.split()
        if len(palabras) >= 3:
            productos_completos.append(nombre)
        elif len(palabras) >= 2:
            productos_multi.append(nombre)
    
    print(f"\n🧠 CLASIFICACIÓN PARA AFD:")
    print(f"  - Productos completos (≥3 palabras): {len(productos_completos)}")
    for prod in productos_completos:
        print(f"    • {prod}")
    
    print(f"  - Productos multi-palabra (2 palabras): {len(productos_multi)}")
    for prod in productos_multi:
        print(f"    • {prod}")
    
    print(f"  - Productos simples (1 palabra): {len(sistema_lcln_simple._cache_productos) - len(productos_completos) - len(productos_multi)}")

if __name__ == "__main__":
    test_limon_detallado()
    verificar_productos_completos()
