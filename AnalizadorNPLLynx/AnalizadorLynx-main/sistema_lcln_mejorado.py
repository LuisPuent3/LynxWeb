#!/usr/bin/env python3
"""
Sistema LCLN Mejorado - Módulo principal
Integra todos los componentes del analizador léxico LYNX
"""

from analizador_lexico import AnalizadorLexico
from interpretador_semantico import InterpretadorSemantico
from motor_recomendaciones import MotorRecomendaciones

def sistema_lcln_mejorado(texto_busqueda, productos_db=None):
    """
    Función principal del sistema LCLN mejorado
    
    Args:
        texto_busqueda (str): Texto a analizar
        productos_db (list): Lista de productos de la base de datos
    
    Returns:
        dict: Resultado del análisis con tokens, interpretación y recomendaciones
    """
    try:
        # Inicializar componentes
        analizador = AnalizadorLexico()
        interpretador = InterpretadorSemantico()
        motor = MotorRecomendaciones()
        
        # Análisis léxico
        tokens = analizador.analizar(texto_busqueda)
        
        # Interpretación semántica
        interpretacion = interpretador.interpretar(tokens)
        
        # Generar recomendaciones si hay productos
        recomendaciones = []
        if productos_db:
            recomendaciones = motor.generar_recomendaciones(interpretacion, productos_db)
        
        return {
            "texto_original": texto_busqueda,
            "tokens": tokens,
            "interpretacion": interpretacion,
            "recomendaciones": recomendaciones,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "texto_original": texto_busqueda,
            "tokens": [],
            "interpretacion": {},
            "recomendaciones": [],
            "error": str(e),
            "status": "error"
        }
