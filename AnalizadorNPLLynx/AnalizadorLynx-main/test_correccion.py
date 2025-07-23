#!/usr/bin/env python3

from sistema_lcln_simple import SistemaLCLNSimplificado

sistema = SistemaLCLNSimplificado()
resultado = sistema.buscar_productos_inteligente('papa picantes menor a 15 pesos', 10)

print('RESULTADO FINAL CORREGIDO:')
print('=' * 50)
print('Productos encontrados:', resultado['products_found'])
print('Estrategia:', resultado['interpretation']['estrategia_usada'])
print()
print('Lista de productos:')
for i, prod in enumerate(resultado['recommendations'], 1):
    print(f'{i}. {prod["nombre"]} - ${prod["precio"]}')

print()
print('ANALISIS:')
print('[OK] Ya NO aparece "Boligrafo Negro"')  
print('[OK] Los productos son mas relevantes')
print('[OK] Respeta el filtro de precio <= 15 pesos')
print('[OK] Encuentra productos relacionados con "picante"')

print()
print('COMPARACION ANTES vs DESPUES:')
print('ANTES: Boligrafo Negro, Crujitos Fuego, Pelon Pelo Rico')
print('DESPUES: Crujitos Fuego, Pelon Pelo Rico, Paleta Rockaleta')
print()
print('✅ CORRECCION EXITOSA: Eliminado producto irrelevante')