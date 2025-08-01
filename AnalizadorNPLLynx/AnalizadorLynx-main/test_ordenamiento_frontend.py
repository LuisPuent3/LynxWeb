#!/usr/bin/env python3
"""
Test para verificar que el ordenamiento funciona en el endpoint del frontend
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def test_ordenamiento_frontend():
    """Probar el ordenamiento en las búsquedas como las recibe el frontend"""
    sistema = SistemaLCLNSimplificado()
    
    consultas_test = [
        "papas picantes menores a 40",
        "productos escolares menores a 10 pesos", 
        "frutas dulces menores a 10 pesos",
        "bolígrafos negros menor a 8"
    ]
    
    for consulta in consultas_test:
        print("=" * 80)
        print(f"CONSULTA: '{consulta}'")
        print("=" * 80)
        
        # Simular llamada del frontend
        resultado = sistema.buscar_productos_inteligente(consulta, 10)
        
        print(f"Productos encontrados: {resultado['products_found']}")
        print(f"Estrategia: {resultado['interpretation']['estrategia_usada']}")
        print(f"Success: {resultado['success']}")
        
        if resultado['products_found'] > 0:
            print(f"\nProductos (ordenados por relevancia):")
            for i, prod in enumerate(resultado['recommendations'], 1):
                nombre = prod.get('nombre', 'N/A')
                precio = prod.get('precio', 0)
                categoria = prod.get('categoria', 'N/A')
                relevancia = prod.get('_relevancia', 'sin clasificar')
                razon = prod.get('_razon_relevancia', 'sin razón')
                
                # Iconos de relevancia
                iconos = {
                    'perfecta': '[PERFECTO]',
                    'alta': '[ALTA]', 
                    'media': '[MEDIA]',
                    'baja': '[BAJA]',
                    'sin clasificar': '[?]'
                }
                icono = iconos.get(relevancia, '[?]')
                
                print(f"  {i}. {icono} {nombre} - ${precio} [{categoria}] - {razon}")
        
        print("\n")

if __name__ == "__main__":
    test_ordenamiento_frontend()