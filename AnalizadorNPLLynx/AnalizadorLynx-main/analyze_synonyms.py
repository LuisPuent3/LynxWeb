#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analizar el uso actual de sinónimos en el sistema
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def analyze_synonyms():
    print("=== ANÁLISIS DE SINÓNIMOS EN EL SISTEMA ===")
    print("=" * 60)
    
    sistema = SistemaLCLNSimplificado()
    
    # Forzar actualización del cache para ver sinónimos
    sistema._actualizar_cache_dinamico()
    
    print(f"Total sinónimos en cache: {len(sistema._cache_sinonimos)}")
    print(f"Total productos en cache: {len(sistema._cache_productos)}")
    
    print(f"\n=== PRIMEROS 10 SINÓNIMOS ===")
    for i, (sinonimo, productos) in enumerate(list(sistema._cache_sinonimos.items())[:10]):
        print(f"{i+1}. '{sinonimo}' -> {len(productos)} productos:")
        for prod in productos[:3]:  # Mostrar solo 3 productos por sinónimo
            print(f"   - {prod['producto_nombre']} (ID: {prod['producto_id']})")
        if len(productos) > 3:
            print(f"   ... y {len(productos) - 3} más")
    
    # Analizar tipos de sinónimos
    print(f"\n=== ANÁLISIS POR CATEGORÍAS DE SINÓNIMOS ===")
    
    sinonimos_bebidas = []
    sinonimos_snacks = []
    sinonimos_picantes = []
    sinonimos_sabores = []
    
    for sinonimo, productos in sistema._cache_sinonimos.items():
        sin_lower = sinonimo.lower()
        
        # Clasificar sinónimos
        if any(palabra in sin_lower for palabra in ['coca', 'pepsi', 'agua', 'jugo', 'refresco', 'bebida']):
            sinonimos_bebidas.append((sinonimo, productos))
        elif any(palabra in sin_lower for palabra in ['papa', 'chip', 'doritos', 'cheetos', 'snack']):
            sinonimos_snacks.append((sinonimo, productos))
        elif any(palabra in sin_lower for palabra in ['picante', 'flama', 'fuego', 'chile', 'hot']):
            sinonimos_picantes.append((sinonimo, productos))
        elif any(palabra in sin_lower for palabra in ['dulce', 'salado', 'limón', 'naranja', 'sabor']):
            sinonimos_sabores.append((sinonimo, productos))
    
    print(f"Sinónimos de bebidas: {len(sinonimos_bebidas)}")
    for sin, prods in sinonimos_bebidas[:5]:
        print(f"  - '{sin}' ({len(prods)} productos)")
        
    print(f"\nSinónimos de snacks: {len(sinonimos_snacks)}")
    for sin, prods in sinonimos_snacks[:5]:
        print(f"  - '{sin}' ({len(prods)} productos)")
        
    print(f"\nSinónimos picantes: {len(sinonimos_picantes)}")
    for sin, prods in sinonimos_picantes[:5]:
        print(f"  - '{sin}' ({len(prods)} productos)")
        
    print(f"\nSinónimos de sabores: {len(sinonimos_sabores)}")
    for sin, prods in sinonimos_sabores[:5]:
        print(f"  - '{sin}' ({len(prods)} productos)")
    
    # Probar algunas búsquedas para ver el uso actual de sinónimos
    print(f"\n=== PRUEBA DE BÚSQUEDAS CON SINÓNIMOS ===")
    
    test_queries = [
        "coca",           # Sinónimo común
        "refresco",       # Sinónimo de categoría
        "chesco",         # Jerga/sinónimo informal
        "papitas",        # Sinónimo de papas
    ]
    
    for query in test_queries:
        print(f"\nBúsqueda: '{query}'")
        result = sistema.buscar_productos_inteligente(query)
        
        print(f"  Estrategia: {result['interpretation']['estrategia_usada']}")
        print(f"  Productos: {len(result['recommendations'])}")
        
        # Verificar si encontró productos por sinónimo
        if result['recommendations']:
            for i, p in enumerate(result['recommendations'][:3]):
                print(f"    {i+1}. {p['nombre']} (${p['precio']})")
        
        # Verificar si hay sinónimos que no se están aprovechando
        sinonimos_disponibles = []
        for sinonimo in sistema._cache_sinonimos.keys():
            if query.lower() in sinonimo.lower() or sinonimo.lower() in query.lower():
                sinonimos_disponibles.append(sinonimo)
        
        if sinonimos_disponibles:
            print(f"  Sinónimos disponibles: {sinonimos_disponibles[:3]}")
        else:
            print(f"  Sin sinónimos directos encontrados")

if __name__ == "__main__":
    analyze_synonyms()