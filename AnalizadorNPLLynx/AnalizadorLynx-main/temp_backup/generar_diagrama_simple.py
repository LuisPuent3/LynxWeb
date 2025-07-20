"""
Script simple para generar un diagrama básico explicativo del analizador léxico LYNX.
Este script evita los problemas de formato y se enfoca en generar un diagrama más sencillo
pero efectivo para explicar el proceso de análisis.
"""
from datetime import datetime
from graphviz import Digraph
import os

def crear_directorio(directorio):
    """Crea un directorio si no existe"""
    if not os.path.exists(directorio):
        os.makedirs(directorio)

def generar_diagrama_completo():
    """Genera un diagrama completo del analizador léxico LYNX"""
    # Crear directorio de salida
    directorio_salida = "diagramas"
    crear_directorio(directorio_salida)
    
    # Crear el diagrama
    dot = Digraph(comment='Analizador Léxico LYNX - Diagrama Completo', format='svg')
    
    # Configuración básica
    dot.attr(rankdir='TB', size='14,16')
    
    # Paleta de colores
    color_entrada = "#AADDFF"    # Azul claro
    color_afds = "#FFD700"       # Dorado
    color_lexico = "#90EE90"     # Verde claro
    color_tokens = "#FFB6C1"     # Rosa claro
    color_semantico = "#D8BFD8"  # Cardo
    color_sql = "#98FB98"        # Verde menta
    
    # SECCIÓN 1: ENTRADA DE TEXTO
    dot.node('entrada', 'ENTRADA DE TEXTO\n"botana barata menor a 10"', shape='box', style='filled,rounded', fillcolor=color_entrada)
    
    # SECCIÓN 2: ANÁLISIS LÉXICO
    with dot.subgraph(name='cluster_lexico') as c:
        c.attr(label='ANÁLISIS LÉXICO', style='filled', fillcolor='#f0f0f0')
        
        # Preprocesamiento
        c.node('preproc', 'Preprocesamiento\nConversión a minúsculas', shape='box', style='filled,rounded', fillcolor=color_lexico)
        
        # AFDs
        c.node('afd_multi', 'AFD Multipalabra\nReconoce frases completas', shape='ellipse', style='filled', fillcolor=color_afds)
        c.node('afd_op', 'AFD Operadores\nReconoce "menor a", "mayor que", etc.', shape='ellipse', style='filled', fillcolor=color_afds)
        c.node('afd_num', 'AFD Números\nReconoce enteros y decimales', shape='ellipse', style='filled', fillcolor=color_afds)
        c.node('afd_uni', 'AFD Unidades\nReconoce "kg", "pesos", etc.', shape='ellipse', style='filled', fillcolor=color_afds)
        c.node('afd_pal', 'AFD Palabras\nReconoce palabras genéricas', shape='ellipse', style='filled', fillcolor=color_afds)
        
        # Tokens iniciales
        c.node('tokens', 'TOKENS INICIALES', shape='box', style='filled,rounded', fillcolor=color_tokens)
        c.node('tokens_lista', 'PALABRA_GENERICA "botana"\nPALABRA_GENERICA "barata"\nOP_MENOR "menor a"\nNUMERO_ENTERO "10"', shape='box', style='filled', fillcolor=color_tokens)
    
    # SECCIÓN 3: ANÁLISIS CONTEXTUAL
    with dot.subgraph(name='cluster_contextual') as c:
        c.attr(label='ANÁLISIS CONTEXTUAL E INTERPRETACIÓN', style='filled', fillcolor='#f0f0f0')
        
        c.node('contexto', 'Análisis Contextual\nAplicación de reglas', shape='box', style='filled,rounded', fillcolor=color_semantico)
        c.node('interpretador', 'Interpretador Semántico\nMapeo de términos', shape='box', style='filled,rounded', fillcolor=color_semantico)
        
        # Tokens interpretados
        c.node('tokens_finales', 'TOKENS INTERPRETADOS', shape='box', style='filled,rounded', fillcolor=color_tokens)
        c.node('tokens_lista_final', 'CATEGORIA "snacks" (era "botana")\nFILTRO_PRECIO "barata" (precio < 50)\nOP_MENOR "menor a"\nNUMERO_ENTERO "10"', shape='box', style='filled', fillcolor=color_tokens)
    
    # SECCIÓN 4: GENERACIÓN DE CONSULTA
    with dot.subgraph(name='cluster_sql') as c:
        c.attr(label='GENERACIÓN DE CONSULTA', style='filled', fillcolor='#f0f0f0')
        
        c.node('json', 'Estructura JSON Intermedia', shape='box', style='filled,rounded', fillcolor=color_sql)
        c.node('sql', 'CONSULTA SQL FINAL', shape='box', style='filled,rounded', fillcolor=color_sql)
        c.node('sql_texto', 'SELECT * FROM productos\nWHERE categoria = "snacks"\nAND precio <= 10', shape='box', style='filled', fillcolor=color_sql)
    
    # Conexiones
    dot.edge('entrada', 'preproc')
    
    # Conexiones del análisis léxico
    dot.edge('preproc', 'afd_multi')
    dot.edge('preproc', 'afd_op')
    dot.edge('preproc', 'afd_num')
    dot.edge('preproc', 'afd_uni')
    dot.edge('preproc', 'afd_pal')
    
    dot.edge('afd_multi', 'tokens', style='dashed')
    dot.edge('afd_op', 'tokens')
    dot.edge('afd_num', 'tokens')
    dot.edge('afd_uni', 'tokens', style='dashed')
    dot.edge('afd_pal', 'tokens')
    
    dot.edge('tokens', 'tokens_lista', style='dotted')
    
    # Conexiones del análisis contextual
    dot.edge('tokens', 'contexto')
    dot.edge('contexto', 'interpretador')
    dot.edge('interpretador', 'tokens_finales')
    dot.edge('tokens_finales', 'tokens_lista_final', style='dotted')
    
    # Conexiones de la generación de consulta
    dot.edge('tokens_finales', 'json')
    dot.edge('json', 'sql')
    dot.edge('sql', 'sql_texto', style='dotted')
    
    # Guardar diagrama
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directorio_salida}/diagrama_analizador_{timestamp}"
    
    # Renderizar diagrama
    dot.render(filename, cleanup=True)
    print(f"Diagrama generado: {filename}.svg")
    
    return filename + ".svg"

def generar_diagrama_proceso():
    """Genera un diagrama del proceso de análisis paso a paso"""
    # Crear directorio de salida
    directorio_salida = "diagramas"
    crear_directorio(directorio_salida)
    
    # Crear el diagrama
    dot = Digraph(comment='Proceso de Análisis Léxico - Paso a Paso', format='svg')
    
    # Configuración básica
    dot.attr(rankdir='LR', size='14,10')
    
    # Paleta de colores
    color_paso = "#E6E6FA"      # Lavanda
    color_token = "#FFB6C1"     # Rosa claro
    
    # Título
    dot.attr(label='PROCESO DE ANÁLISIS LÉXICO - PASO A PASO')
    dot.attr(labelloc='t')
    dot.attr(labelfontsize='20')
    
    # Entrada de texto
    dot.node('entrada', 'CONSULTA ORIGINAL\n"botana barata menor a 10"', shape='box', style='filled,rounded', fillcolor='#AADDFF')
    
    # Paso 1
    dot.node('paso1', 'PASO 1\nPosición: 0\nPalabra: "botana"', shape='box', style='filled,rounded', fillcolor=color_paso)
    dot.node('token1', 'Token: PALABRA_GENERICA\nValor: "botana"\nPosición: 0-6', shape='box', style='filled', fillcolor=color_token)
    
    # Paso 2
    dot.node('paso2', 'PASO 2\nPosición: 7\nPalabra: "barata"', shape='box', style='filled,rounded', fillcolor=color_paso)
    dot.node('token2', 'Token: PALABRA_GENERICA\nValor: "barata"\nPosición: 7-13', shape='box', style='filled', fillcolor=color_token)
    
    # Paso 3
    dot.node('paso3', 'PASO 3\nPosición: 14\nFrase: "menor a"', shape='box', style='filled,rounded', fillcolor=color_paso)
    dot.node('token3', 'Token: OP_MENOR\nValor: "menor a"\nPosición: 14-21', shape='box', style='filled', fillcolor=color_token)
    
    # Paso 4
    dot.node('paso4', 'PASO 4\nPosición: 22\nNúmero: "10"', shape='box', style='filled,rounded', fillcolor=color_paso)
    dot.node('token4', 'Token: NUMERO_ENTERO\nValor: "10"\nPosición: 22-24', shape='box', style='filled', fillcolor=color_token)
    
    # Resultado final
    dot.node('final', 'ANÁLISIS CONTEXTUAL\nY SEMÁNTICO', shape='box', style='filled,rounded', fillcolor='#D8BFD8')
    dot.node('resultado', 'TOKENS FINALES\nCATEGORIA "snacks"\nFILTRO_PRECIO "barata"\nOP_MENOR "menor a"\nNUMERO_ENTERO "10"', shape='box', style='filled', fillcolor=color_token)
    dot.node('sql', 'SELECT * FROM productos\nWHERE categoria = "snacks"\nAND precio <= 10', shape='box', style='filled', fillcolor='#98FB98')
    
    # Conexiones
    dot.edge('entrada', 'paso1')
    dot.edge('paso1', 'token1')
    dot.edge('paso1', 'paso2')
    dot.edge('paso2', 'token2')
    dot.edge('paso2', 'paso3')
    dot.edge('paso3', 'token3')
    dot.edge('paso3', 'paso4')
    dot.edge('paso4', 'token4')
    dot.edge('paso4', 'final')
    dot.edge('final', 'resultado')
    dot.edge('final', 'sql')
    
    # Guardar diagrama
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directorio_salida}/proceso_analisis_{timestamp}"
    
    # Renderizar diagrama
    dot.render(filename, cleanup=True)
    print(f"Diagrama de proceso generado: {filename}.svg")
    
    return filename + ".svg"

if __name__ == "__main__":
    print("Generando diagramas explicativos del Analizador Léxico LYNX...")
    
    try:
        ruta1 = generar_diagrama_completo()
        ruta2 = generar_diagrama_proceso()
        
        print("\nDiagramas generados con éxito:")
        print(f"1. Diagrama completo: {ruta1}")
        print(f"2. Diagrama de proceso: {ruta2}")
        
    except Exception as e:
        print(f"Error al generar diagramas: {str(e)}")
