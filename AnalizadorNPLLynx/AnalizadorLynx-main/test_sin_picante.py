#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_simple import SistemaLCLNSimplificado

sistema = SistemaLCLNSimplificado()

query = 'papas sin picante'
print(f"Query: {query}")
result = sistema.buscar_productos_inteligente(query)
print(f"Estrategia: {result['interpretation']['estrategia_usada']}")
print(f"Productos encontrados: {len(result['recommendations'])}")
for i, p in enumerate(result['recommendations'][:5]):
    print(f"{i+1}. {p['nombre']} - ${p['precio']}")