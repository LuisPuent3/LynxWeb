#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test simplificado de casos de uso críticos
"""

from sistema_lcln_simple import SistemaLCLNSimplificado
import time

def test_caso_critico(nombre, consulta):
    """Prueba un caso y muestra resultados básicos"""
    print(f"\n=== {nombre} ===")
    print(f"Consulta: '{consulta}'")
    
    sistema = SistemaLCLNSimplificado()
    inicio = time.time()
    resultado = sistema.buscar_productos_inteligente(consulta)
    tiempo_ms = (time.time() - inicio) * 1000
    
    productos = resultado.get('recommendations', [])
    print(f"Productos encontrados: {len(productos)}")
    print(f"Tiempo: {tiempo_ms:.1f}ms")
    
    # Mostrar productos
    for i, p in enumerate(productos[:5], 1):
        nombre_prod = p.get('nombre', 'N/A')
        precio = p.get('precio', 'N/A')
        categoria = p.get('categoria', 'N/A')
        print(f"  {i}. {nombre_prod} (${precio}) - {categoria}")
    
    return len(productos), tiempo_ms

def main():
    print("TEST DE CASOS DE USO CRITICOS")
    print("=" * 50)
    
    casos = [
        ("CASO 1.1: Producto específico", "coca cola 600ml"),
        ("CASO 1.2: Categoría directa", "bebidas"),
        ("CASO 1.3: Precio con filtro", "doritos menor a 25 pesos"),
        ("CASO 2.1: Error ortográfico", "koka kola"),
        ("CASO 5.1: Bebidas sin azúcar (CORREGIDO)", "bebidas sin azucar menor a 20 pesos"),
        ("CASO 7.1: Lenguaje natural", "que bebidas tienes por menos de 15 pesos"),
        ("CASO 10.2: Solo números", "20"),
    ]
    
    resultados = []
    
    for nombre, consulta in casos:
        try:
            productos_count, tiempo = test_caso_critico(nombre, consulta)
            resultados.append({
                'caso': nombre,
                'productos': productos_count,
                'tiempo': tiempo,
                'exito': productos_count > 0 and tiempo < 200
            })
        except Exception as e:
            print(f"ERROR en {nombre}: {e}")
            resultados.append({
                'caso': nombre,
                'productos': 0,
                'tiempo': 999,
                'exito': False
            })
    
    # Resumen final
    print("\n" + "=" * 50)
    print("RESUMEN FINAL")
    print("=" * 50)
    
    exitos = sum(1 for r in resultados if r['exito'])
    print(f"Tests ejecutados: {len(resultados)}")
    print(f"Exitosos: {exitos}")
    print(f"Fallidos: {len(resultados) - exitos}")
    print(f"Tasa de exito: {exitos/len(resultados)*100:.1f}%")
    
    print(f"\nTiempo promedio: {sum(r['tiempo'] for r in resultados)/len(resultados):.1f}ms")
    
    # Casos problemáticos
    problematicos = [r for r in resultados if not r['exito']]
    if problematicos:
        print(f"\nCasos problematicos:")
        for r in problematicos:
            print(f"  - {r['caso']}: {r['productos']} productos en {r['tiempo']:.1f}ms")
    
    return exitos == len(resultados)

if __name__ == "__main__":
    main()