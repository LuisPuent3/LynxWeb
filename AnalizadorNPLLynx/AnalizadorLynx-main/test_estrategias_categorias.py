#!/usr/bin/env python3
"""
Test para estrategias de búsqueda por categorías
Querys sugeridos para probar diferentes categorías de productos
"""

from sistema_lcln_simple import SistemaLCLNSimplificado

def clasificar_relevancia_completa(producto, consulta):
    """Clasificación de relevancia mejorada para todas las categorías"""
    nombre = producto.get('nombre', '').lower()
    consulta = consulta.lower()
    categoria = producto.get('categoria', '').lower()
    
    # FRUTAS - Relevancia PERFECTA
    if 'fruta' in consulta and categoria == 'frutas':
        return 'perfecta', 'fruta natural solicitada'
    
    if any(term in consulta for term in ['dulce', 'dulces']) and categoria == 'frutas':
        return 'perfecta', 'fruta dulce natural'
        
    if any(term in consulta for term in ['ácida', 'ácidas', 'agria']) and categoria == 'frutas':
        return 'perfecta', 'fruta ácida natural'
    
    # GOLOSINAS - Relevancia PERFECTA 
    if any(term in consulta for term in ['golosina', 'golosinas', 'dulce', 'dulces', 'caramelo', 'chocolate']) and categoria == 'golosinas':
        return 'perfecta', 'golosina dulce'
        
    if 'picante' in consulta and categoria == 'golosinas' and any(term in nombre for term in ['pelo', 'rockaleta', 'tamarindo']):
        return 'perfecta', 'golosina picante específica'
    
    # PAPELERÍA - Relevancia PERFECTA
    if any(term in consulta for term in ['papeleria', 'papelería', 'escolar', 'escolares', 'cosas escolares', 'productos escolares']) and categoria == 'papeleria':
        return 'perfecta', 'artículo de papelería'
        
    if any(term in consulta for term in ['boligrafo', 'bolígrafo', 'pluma', 'lápiz']) and categoria == 'papeleria':
        return 'perfecta', 'utensilio de escritura'
        
    if any(term in consulta for term in ['cuaderno', 'libreta', 'marcador', 'marcatexto']) and categoria == 'papeleria':
        return 'perfecta', 'material escolar específico'
    
    # Color específico en papelería
    if any(color in consulta for color in ['negro', 'rojo', 'azul', 'verde']) and categoria == 'papeleria':
        color_encontrado = next(color for color in ['negro', 'rojo', 'azul', 'verde'] if color in consulta)
        if color_encontrado in nombre:
            return 'perfecta', f'color {color_encontrado} específico'
    
    # SNACKS PICANTES (ya implementado)
    if 'picante' in consulta and categoria == 'snacks' and any(term in nombre for term in ['fuego', 'dinamita', 'flama', 'takis']):
        return 'perfecta', 'snack picante específico'
    
    # BEBIDAS - Relevancia PERFECTA
    if any(term in consulta for term in ['bebida', 'bebidas', 'refresco', 'jugo']) and categoria == 'bebidas':
        return 'perfecta', 'bebida solicitada'
        
    if 'sin azúcar' in consulta and 'sin azúcar' in nombre:
        return 'perfecta', 'bebida sin azúcar específica'
    
    # Relevancia ALTA - Categoría coincide
    if categoria in consulta:
        return 'alta', f'categoría {categoria}'
    
    # Relevancia MEDIA - Sinónimo válido
    if 'picante' in consulta and categoria == 'golosinas':
        return 'media', 'dulce picante (sinónimo)'
    
    # Relevancia BAJA - No muy relacionado
    return 'baja', 'resultado genérico'

def mostrar_resultados_con_estrategia(consulta, limite=10):
    """Muestra resultados con estrategia mejorada"""
    sistema = SistemaLCLNSimplificado()
    resultado = sistema.buscar_productos_inteligente(consulta, limite)
    
    print('=' * 80)
    print(f'CONSULTA: "{consulta}"')
    print('=' * 80)
    
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
        relevancia, razon = clasificar_relevancia_completa(prod, consulta)
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
    
    print()

if __name__ == "__main__":
    print("=" * 80)
    print("ESTRATEGIAS DE BÚSQUEDA POR CATEGORÍAS")
    print("=" * 80)
    
    # ============================================
    # CATEGORÍA: FRUTAS
    # ============================================
    print("\n[FRUTAS] CATEGORÍA: FRUTAS")
    print("-" * 50)
    
    consultas_frutas = [
        "frutas dulces menores a 10 pesos",
        "frutas ácidas menor a 8 pesos", 
        "manzana roja menor a 12",
        "frutas tropicales menores a 15",
        "fruta dulce barata",
        "mango maduro menor a 10"
    ]
    
    print("ESTRATEGIAS SUGERIDAS PARA FRUTAS:")
    for i, consulta in enumerate(consultas_frutas, 1):
        print(f"  {i}. {consulta}")
    
    print("\nEJEMPLO DE BÚSQUEDA:")
    mostrar_resultados_con_estrategia("frutas dulces menores a 8 pesos")
    
    # ============================================
    # CATEGORÍA: GOLOSINAS
    # ============================================
    print("\n[GOLOSINAS] CATEGORÍA: GOLOSINAS")
    print("-" * 50)
    
    consultas_golosinas = [
        "golosinas dulces menor a 15 pesos",
        "dulces picantes menores a 12",
        "chocolates baratos menor a 20", 
        "caramelos duros menor a 8",
        "golosinas ácidas menores a 10",
        "dulces mexicanos menor a 15",
        "mazapán menor a 10 pesos"
    ]
    
    print("ESTRATEGIAS SUGERIDAS PARA GOLOSINAS:")
    for i, consulta in enumerate(consultas_golosinas, 1):
        print(f"  {i}. {consulta}")
    
    print("\nEJEMPLO DE BÚSQUEDA:")
    mostrar_resultados_con_estrategia("dulces picantes menores a 12 pesos")
    
    # ============================================
    # CATEGORÍA: PAPELERÍA
    # ============================================
    print("\n[PAPELERÍA] CATEGORÍA: PAPELERÍA")
    print("-" * 50)
    
    consultas_papeleria = [
        "productos escolares menores a 10 pesos",
        "bolígrafos negros menor a 8",
        "cosas escolares baratas menor a 15",
        "cuadernos rayados menor a 20",
        "marcadores de colores menor a 25", 
        "papelería básica menor a 12",
        "útiles escolares menores a 30",
        "plumas rojas menor a 10"
    ]
    
    print("ESTRATEGIAS SUGERIDAS PARA PAPELERÍA:")
    for i, consulta in enumerate(consultas_papeleria, 1):
        print(f"  {i}. {consulta}")
    
    print("\nEJEMPLO DE BÚSQUEDA:")
    mostrar_resultados_con_estrategia("productos escolares menores a 10 pesos")
    
    # ============================================
    # CATEGORÍAS COMBINADAS
    # ============================================
    print("\n[COMBINADAS] BÚSQUEDAS COMBINADAS")
    print("-" * 50)
    
    consultas_combinadas = [
        "productos dulces menores a 15",  # Frutas + Golosinas
        "cosas baratas menor a 8 pesos",  # Todas las categorías  
        "productos picantes menor a 20",  # Snacks + Golosinas
        "artículos escolares y frutas menor a 25"  # Papelería + Frutas
    ]
    
    print("ESTRATEGIAS PARA BÚSQUEDAS COMBINADAS:")
    for i, consulta in enumerate(consultas_combinadas, 1):
        print(f"  {i}. {consulta}")
    
    print("\nEJEMPLO DE BÚSQUEDA COMBINADA:")
    mostrar_resultados_con_estrategia("productos dulces menores a 15")
    
    print("\n" + "=" * 80)
    print("RESUMEN DE ESTRATEGIAS POR CATEGORÍA")
    print("=" * 80)
    
    print("""
[FRUTAS] FRUTAS:
   - Términos clave: 'frutas', 'dulces', 'ácidas', 'tropicales'
   - Nombres específicos: 'manzana', 'mango', 'pera', etc.
   - Filtros efectivos: precio, dulzura, acidez

[GOLOSINAS] GOLOSINAS:
   - Términos clave: 'golosinas', 'dulces', 'caramelos', 'chocolates'
   - Variantes: 'picantes', 'ácidas', 'mexicanas'
   - Productos específicos: 'mazapán', 'pelon pelo rico'

[PAPELERÍA] PAPELERÍA:
   - Términos clave: 'papelería', 'escolares', 'útiles', 'cosas escolares'
   - Productos: 'bolígrafos', 'cuadernos', 'marcadores', 'plumas'
   - Colores: 'negro', 'rojo', 'azul', 'verde'

[COMBINADAS] COMBINADAS:
   - Términos generales: 'productos', 'cosas', 'artículos'
   - Características: 'dulces', 'baratos', 'picantes'
   - Múltiples categorías en una búsqueda
""")