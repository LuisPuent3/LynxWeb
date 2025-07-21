#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_mejorado_limpio import sistema_lcln_mejorado
import json

def test_botana_sin_picante():
    """Test the 'botana sin picante' query specifically"""
    query = "botana sin picante"
    print(f"Testing query: '{query}'")
    print("="*60)
      # Crear instancia del sistema LCLN
    sistema = sistema_lcln_mejorado
      # Procesar la consulta
    resultado = sistema.analizar_consulta_lcln(query)
    
    # Mostrar todas las fases
    print("PHASE RESULTS:")
    for fase, contenido in resultado.items():
        if fase == 'productos' and contenido:
            print(f"{fase}: {len(contenido)} products found")
            for i, producto in enumerate(contenido[:3]):
                print(f"  {i+1}. {producto['nombre']} - ${producto['precio']}")
        else:
            print(f"{fase}: {contenido}")
        print("-" * 40)
    
    return resultado

if __name__ == "__main__":
    test_botana_sin_picante()
