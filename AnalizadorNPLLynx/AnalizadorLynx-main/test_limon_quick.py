#!/usr/bin/env python3

from sistema_lcln_simple import sistema_lcln_simple

resultado = sistema_lcln_simple.buscar_productos_inteligente('limon')
print('=== RESULTADO LIMÓN MEJORADO ===')
print(f'Productos encontrados: {resultado["products_found"]}')
print(f'Estrategia: {resultado["interpretation"]["estrategia_usada"]}')
print(f'Mensaje: {resultado["user_message"]}')
print('Productos:')
for i, prod in enumerate(resultado['recommendations'], 1):
    print(f'  {i}. {prod["nombre"]} - ${prod["precio"]} ({prod["categoria"]})')
