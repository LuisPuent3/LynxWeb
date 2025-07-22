#!/usr/bin/env python3
"""
Pruebas avanzadas con los nuevos sinónimos
"""

from sistema_lcln_simple import sistema_lcln_simple

def pruebas_sinonimos_avanzadas():
    print("🚀 === PRUEBAS AVANZADAS CON 299 SINÓNIMOS ===\n")
    
    # Casos de prueba específicos para mostrar el poder de los sinónimos
    casos_avanzados = [
        # Sinónimos de errores ortográficos
        {
            'consulta': 'coka',
            'descripcion': 'Error ortográfico común: "coka" → Coca-Cola'
        },
        {
            'consulta': 'dorito',
            'descripción': 'Singular de marca: "dorito" → Doritos'
        },
        
        # Sinónimos de palabras en inglés
        {
            'consulta': 'apple',
            'descripcion': 'Inglés: "apple" → Manzana'
        },
        {
            'consulta': 'banana',
            'descripción': 'Sinónimo internacional: "banana" → Plátano Dominico'
        },
        
        # Sinónimos de categorías generales
        {
            'consulta': 'h2o',
            'descripcion': 'Químico: "h2o" → Agua'
        },
        {
            'consulta': 'energizante',
            'descripción': 'Categoría: "energizante" → Red Bull'
        },
        
        # Sinónimos regionales mexicanos
        {
            'consulta': 'agüita',
            'descripcion': 'Mexicanismo: "agüita" → Agua'
        },
        {
            'consulta': 'chamoy',
            'descripción': 'Dulce mexicano: "chamoy" → Pelon Pelo Rico'
        },
        
        # Sinónimos por características
        {
            'consulta': 'picante',
            'descripcion': 'Por característica: "picante" → Productos picantes'
        },
        {
            'consulta': 'tropical',
            'descripción': 'Por origen: "tropical" → Frutas tropicales'
        },
        
        # Sinónimos de marcas
        {
            'consulta': 'seven up',
            'descripcion': 'Marca competencia: "seven up" → Sprite'
        },
        {
            'consulta': 'cookies',
            'descripción': 'Inglés: "cookies" → Galletas/Oreo'
        },
        
        # Abreviaciones
        {
            'consulta': 'bm',
            'descripcion': 'Abreviación: "bm" → Boing Mango'
        }
    ]
    
    resultados_destacados = []
    
    for i, caso in enumerate(casos_avanzados, 1):
        consulta = caso['consulta']
        descripcion = caso.get('descripcion', caso.get('descripción', 'Prueba'))
        
        print(f"🔍 **CASO {i}: {descripcion}**")
        print(f"   Consulta: '{consulta}'")
        
        resultado = sistema_lcln_simple.buscar_productos_inteligente(consulta)
        
        print(f"   📊 Resultados:")
        print(f"      • Productos: {resultado['products_found']}")
        print(f"      • Estrategia: {resultado['interpretation']['estrategia_usada']}")
        print(f"      • Tiempo: {resultado['processing_time_ms']:.1f}ms")
        
        if resultado['products_found'] > 0:
            # Mostrar hasta 2 productos principales
            productos_top = resultado['recommendations'][:2]
            for j, prod in enumerate(productos_top, 1):
                print(f"      {j}. {prod['nombre']} - ${prod['precio']} ({prod['categoria']})")
            
            if resultado['products_found'] > 2:
                print(f"      ... y {resultado['products_found'] - 2} más")
                
            resultados_destacados.append({
                'consulta': consulta,
                'encontrados': resultado['products_found'],
                'primer_producto': productos_top[0]['nombre'],
                'tiempo': resultado['processing_time_ms']
            })
        else:
            print(f"      ❌ Sin resultados")
        
        print()
    
    print("🏆 === RESUMEN DE ÉXITOS ===")
    print(f"Casos probados: {len(casos_avanzados)}")
    casos_exitosos = [r for r in resultados_destacados if r['encontrados'] > 0]
    print(f"Casos exitosos: {len(casos_exitosos)}")
    print(f"Tasa de éxito: {(len(casos_exitosos)/len(casos_avanzados)*100):.1f}%")
    
    if casos_exitosos:
        tiempo_promedio = sum(r['tiempo'] for r in casos_exitosos) / len(casos_exitosos)
        print(f"Tiempo promedio: {tiempo_promedio:.1f}ms")
        
        print(f"\n🎯 **CASOS MÁS IMPRESIONANTES:**")
        # Ordenar por número de productos encontrados
        casos_exitosos.sort(key=lambda x: x['encontrados'], reverse=True)
        for caso in casos_exitosos[:5]:
            print(f"   • '{caso['consulta']}' → {caso['encontrados']} productos ({caso['primer_producto']}) - {caso['tiempo']:.1f}ms")

def probar_casos_complejos():
    print(f"\n🧠 === CASOS COMPLEJOS CON SINÓNIMOS ===")
    
    casos_complejos = [
        'chettos mix',  # Error ortográfico + palabra adicional
        'coca light',   # Sinónimo específico de variante
        'agua gasificada',  # Sinónimo técnico
        'dulces mexicanos',  # Categoría + origen
        'pluma negra',   # Sinónimo + color
        'refrescante citrico'  # Características combinadas
    ]
    
    for consulta in casos_complejos:
        print(f"\n🔍 Consulta compleja: '{consulta}'")
        resultado = sistema_lcln_simple.buscar_productos_inteligente(consulta)
        
        if resultado['products_found'] > 0:
            print(f"   ✅ {resultado['products_found']} productos encontrados")
            print(f"   🎯 Top result: {resultado['recommendations'][0]['nombre']} (${resultado['recommendations'][0]['precio']})")
            print(f"   ⚡ Estrategia: {resultado['interpretation']['estrategia_usada']}")
        else:
            print(f"   ❌ Sin resultados")

if __name__ == "__main__":
    pruebas_sinonimos_avanzadas()
    probar_casos_complejos()
