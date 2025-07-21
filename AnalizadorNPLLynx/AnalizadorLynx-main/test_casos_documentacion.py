#!/usr/bin/env python3

import sys
from pathlib import Path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

import sistema_lcln_mejorado_limpio

def test_casos_documentacion():
    """Probar casos específicos de la documentación LCLN"""
    sistema = sistema_lcln_mejorado_limpio.SistemaLCLNMejorado()
    
    print("🧪 PROBANDO CASOS DE LA DOCUMENTACIÓN LCLN")
    print("=" * 60)
    
    # Casos adicionales de la documentación
    casos_prueba = [
        # Casos nuevos que el usuario mencionó
        {
            "query": "botana sin picante", 
            "descripcion": "Debería mostrar snacks dulces/no picantes",
            "esperado": ["dulce", "suave", "no picante"]
        },
        {
            "query": "dulces", 
            "descripcion": "Debería mostrar golosinas/panditas",
            "esperado": ["golosinas", "panditas", "dulces"]
        },
        {
            "query": "panditas", 
            "descripcion": "Debería encontrar gomitas/dulces específicos",
            "esperado": ["panditas", "gomas", "dulces"]
        },
        # Casos de la documentación
        {
            "query": "coca cola sin azucar menor a 20 pesos", 
            "descripcion": "Producto específico + filtro precio",
            "esperado": ["coca", "sin azucar", "precio"]
        },
        {
            "query": "bebidas baratas", 
            "descripcion": "Categoría + filtro precio",
            "esperado": ["bebidas", "baratas", "economicas"]
        },
        {
            "query": "snacks picantes entre 10 y 30 pesos", 
            "descripcion": "Operadores de rango complejo", 
            "esperado": ["snacks", "picantes", "rango"]
        },
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        query = caso["query"]
        descripcion = caso["descripcion"]
        esperado = caso["esperado"]
        
        print(f"\n{i}. 🔍 Consulta: '{query}'")
        print(f"   📋 Descripción: {descripcion}")
        
        try:
            resultado = sistema.analizar_consulta_lcln(query)
            
            # Analizar resultado
            fase_2 = resultado['fase_2_expansion_sinonimos']
            fase_4 = resultado['fase_4_interpretacion'] 
            fase_5 = resultado['fase_5_motor_recomendaciones']
            
            print(f"   📊 Estrategia: {fase_5['estrategia_usada']}")
            print(f"   📦 Productos encontrados: {fase_5['total_encontrados']}")
            
            # Mostrar categorías y atributos detectados
            if fase_2['categorias_detectadas']:
                print(f"   📂 Categorías: {fase_2['categorias_detectadas']}")
            if fase_4['atributos']:
                print(f"   🏷️  Atributos: {fase_4['atributos']}")
            if fase_4['productos_especificos']:
                print(f"   🎯 Productos específicos: {fase_4['productos_especificos']}")
                
            # Mostrar primeros productos
            if fase_5['productos_encontrados']:
                print(f"   🛍️  Primeros productos:")
                for j, producto in enumerate(fase_5['productos_encontrados'][:3], 1):
                    nombre = producto['nombre']
                    precio = producto['precio']
                    print(f"      {j}. {nombre} - ${precio}")
                    
                print(f"   {'✅' if fase_5['total_encontrados'] > 0 else '❌'} Resultado")
            else:
                print(f"   ❌ No se encontraron productos")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print("🏁 Pruebas de casos de documentación completadas")

if __name__ == "__main__":
    test_casos_documentacion()
