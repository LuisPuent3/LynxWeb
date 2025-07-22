#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_simple import SistemaLCLNSimplificado

sistema = SistemaLCLNSimplificado()

query = 'bebidas con azucar'
print(f"=== QUERY: {query} ===")
result = sistema.buscar_productos_inteligente(query)
print(f"Productos encontrados: {len(result['recommendations'])}")
for i, p in enumerate(result['recommendations'][:5]):
    print(f"{i+1}. {p['nombre']} - ${p['precio']}")

# Test papas sin picante  
query2 = 'papas sin picante'
print(f"\n=== QUERY: {query2} ===")
result2 = sistema.buscar_productos_inteligente(query2)
print(f"Productos encontrados: {len(result2['recommendations'])}")
for i, p in enumerate(result2['recommendations'][:5]):
    print(f"{i+1}. {p['nombre']} - ${p['precio']}")