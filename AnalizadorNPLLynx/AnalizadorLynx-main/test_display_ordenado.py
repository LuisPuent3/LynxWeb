#!/usr/bin/env python3
"""
Test para mostrar resultados ordenados y clasificados
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def clasificar_relevancia(producto, consulta):
    """Clasifica la relevancia del producto según la consulta"""
    nombre = producto.get('nombre', '').lower()
    consulta = consulta.lower()
    categoria = producto.get('categoria', '').lower()
    
    # Relevancia PERFECTA: nombre contiene términos clave de la consulta
    if any(term in nombre for term in ['fuego', 'dinamita', 'flama'] if 'picante' in consulta):
        return 'perfecta', 'producto picante específico'
    
    if 'negro' in consulta and 'negro' in nombre:
        return 'perfecta', 'color específico solicitado'
        
    if 'dulce' in consulta and categoria == 'golosinas':
        return 'perfecta', 'golosina dulce'
        
    if 'fruta' in consulta and categoria == 'frutas':
        return 'perfecta', 'fruta solicitada'
    
    # Relevancia ALTA: categoría coincide
    if 'papeleria' in consulta and categoria == 'papeleria':
        return 'alta', 'categoría papelería'
        
    if 'snack' in consulta and categoria == 'snacks':
        return 'alta', 'categoría snacks'
    
    # Relevancia MEDIA: sinónimo válido pero no exacto
    if 'picante' in consulta and any(term in nombre for term in ['pelo', 'rockaleta']):
        return 'media', 'dulce picante (sinónimo)'
    
    # Relevancia BAJA: no muy relacionado
    return 'baja', 'resultado genérico'

def mostrar_resultados_ordenados(consulta, limite=10):
    """Muestra resultados clasificados y ordenados"""
    sistema = SistemaLCLNSimplificado()
    resultado = sistema.buscar_productos_inteligente(consulta, limite)
    
    print('=' * 70)
    print(f'CONSULTA: "{consulta}"')
    print('=' * 70)
    
    productos_count = resultado.get('products_found', 0)
    print(f'Productos encontrados: {productos_count}')
    print(f'Estrategia: {resultado["interpretation"]["estrategia_usada"]}')
    
    if productos_count == 0:
        print('\n❌ NO se encontraron productos')
        return
    
    # Clasificar productos
    productos_clasificados = {
        'perfecta': [],
        'alta': [],
        'media': [],
        'baja': []
    }
    
    for prod in resultado['recommendations']:
        relevancia, razon = clasificar_relevancia(prod, consulta)
        productos_clasificados[relevancia].append((prod, razon))
    
    # Mostrar resultados ordenados
    print(f'\nProductos devueltos ({productos_count} total):')
    
    contador = 1
    iconos = {'perfecta': '[PERFECTO]', 'alta': '[ALTA]', 'media': '[MEDIA]', 'baja': '[BAJA]'}
    
    for relevancia in ['perfecta', 'alta', 'media', 'baja']:
        for prod, razon in productos_clasificados[relevancia]:
            nombre = prod.get('nombre', 'N/A')
            precio = prod.get('precio', 0)
            categoria = prod.get('categoria', 'N/A')
            icono = iconos[relevancia]
            
            print(f'  {contador}. {icono} {nombre} - ${precio} [{categoria}] - {razon}')
            contador += 1
    
    # Resumen
    print(f'\nRESUMEN DE RELEVANCIA:')
    for relevancia, productos in productos_clasificados.items():
        if productos:
            icono = iconos[relevancia]
            print(f'  {icono} {relevancia.upper()}: {len(productos)} productos')

if __name__ == "__main__":
    # Probar diferentes consultas
    consultas = [
        "papas picantes menores a 40",
        "bolígrafos negros menor a 10", 
        "frutas dulces menores a 10 pesos",
        "golosinas dulces menor a 15 pesos"
    ]
    
    for consulta in consultas:
        mostrar_resultados_ordenados(consulta)
        print('\n')