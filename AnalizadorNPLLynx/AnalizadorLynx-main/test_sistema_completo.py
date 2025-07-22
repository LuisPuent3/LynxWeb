#!/usr/bin/env python3
"""
Pruebas completas del Sistema LCLN mejorado
"""

from sistema_lcln_simple import sistema_lcln_simple

def probar_casos_mejorados():
    print("🧪 === PRUEBAS SISTEMA LCLN MEJORADO ===\n")
    
    casos_prueba = [
        # Caso 1: Búsqueda de limón (mejorado)
        {
            'consulta': 'limon',
            'descripcion': 'Búsqueda múltiple de limón (antes: 1, ahora: 4)'
        },
        # Caso 2: Búsqueda semántica mejorada
        {
            'consulta': 'bebidas sin azucar',
            'descripcion': 'Búsqueda semántica: bebidas + atributo (debe encontrar 2 productos)'
        },
        # Caso 3: Búsqueda con filtro precio
        {
            'consulta': 'snacks dulces barato',
            'descripcion': 'Búsqueda con filtro semántico de precio'
        },
        # Caso 4: Prueba AFD vs Fallback
        {
            'consulta': 'coca cola',
            'descripcion': 'Producto común (AFD vs Fallback)'
        },
        # Caso 5: Búsqueda por palabra clave semántica
        {
            'consulta': 'chocolate',
            'descripcion': 'Búsqueda semántica por ingrediente'
        },
        # Caso 6: Categoría + atributo
        {
            'consulta': 'snacks picantes',
            'descripcion': 'Categoría + atributo específico'
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"🔍 **CASO {i}: {caso['descripcion']}**")
        print(f"   Consulta: '{caso['consulta']}'")
        
        resultado = sistema_lcln_simple.buscar_productos_inteligente(caso['consulta'])
        
        print(f"   📊 Resultados:")
        print(f"      • Productos encontrados: {resultado['products_found']}")
        print(f"      • Estrategia: {resultado['interpretation']['estrategia_usada']}")
        print(f"      • Tiempo: {resultado['processing_time_ms']:.1f}ms")
        print(f"      • Mensaje: {resultado['user_message']}")
        
        if resultado['products_found'] > 0:
            print(f"   🏷️  Productos:")
            for j, prod in enumerate(resultado['recommendations'][:3], 1):  # Mostrar top 3
                print(f"      {j}. {prod['nombre']} - ${prod['precio']} ({prod['categoria']})")
            if resultado['products_found'] > 3:
                print(f"      ... y {resultado['products_found'] - 3} más")
        else:
            print(f"   ❌ No se encontraron productos")
        
        print()  # Línea en blanco
    
    print("✅ **RESUMEN DE MEJORAS IMPLEMENTADAS:**")
    print("   1. 🎯 Búsqueda múltiple para palabras simples (ej: 'limón' → 4 productos)")
    print("   2. 🧠 Búsqueda semántica mejorada (categoría + atributo)")
    print("   3. 💰 Filtros de precio más inteligentes")
    print("   4. 🔍 Coincidencias por sinónimos más flexibles")
    print("   5. 📊 Mejor información de debug del AFD")
    print("   6. 💬 Mensajes de usuario más descriptivos")

def estadisticas_sistema():
    print("\n📈 === ESTADÍSTICAS DEL SISTEMA ===")
    
    # Forzar actualización de cache
    sistema_lcln_simple._actualizar_cache_dinamico()
    
    print(f"🗂️  **Base de Datos MySQL:**")
    print(f"   • Total productos: {len(sistema_lcln_simple._cache_productos)}")
    print(f"   • Total categorías: {len(sistema_lcln_simple._cache_categorias)}")
    print(f"   • Total sinónimos: {len(sistema_lcln_simple._cache_sinonimos)}")
    
    print(f"\n🧠 **Analizador Léxico (AFD):**")
    productos_completos = sum(1 for nombre in sistema_lcln_simple._cache_productos.keys() if len(nombre.split()) >= 3)
    productos_multi = sum(1 for nombre in sistema_lcln_simple._cache_productos.keys() if len(nombre.split()) == 2)
    productos_simples = len(sistema_lcln_simple._cache_productos) - productos_completos - productos_multi
    
    print(f"   • Productos complejos (≥3 palabras): {productos_completos}")
    print(f"   • Productos multi-palabra (2 palabras): {productos_multi}")
    print(f"   • Productos simples (1 palabra): {productos_simples}")
    
    # Análisis de categorías
    categorias_conteo = {}
    for prod in sistema_lcln_simple._cache_productos.values():
        cat = prod['categoria']
        categorias_conteo[cat] = categorias_conteo.get(cat, 0) + 1
    
    print(f"\n📦 **Distribución por Categorías:**")
    for categoria, count in sorted(categorias_conteo.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {categoria}: {count} productos")

if __name__ == "__main__":
    estadisticas_sistema()
    probar_casos_mejorados()
