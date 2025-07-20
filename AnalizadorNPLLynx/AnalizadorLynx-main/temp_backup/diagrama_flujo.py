#!/usr/bin/env python
# -*- coding: utf-8 -*-
# diagrama_flujo.py - Generador de diagrama de flujo para el sistema LYNX

from graphviz import Digraph
import os
from datetime import datetime

def generar_diagrama_flujo_procesamiento():
    """
    Genera un diagrama de flujo que ilustra el procesamiento de una consulta
    como 'botana barata menor a 10' en el sistema LYNX.
    """
    # Crear directorio si no existe
    if not os.path.exists('diagramas_explicativos'):
        os.makedirs('diagramas_explicativos')
    
    # Crear un nuevo objeto Digraph
    dot = Digraph(comment='Flujo de procesamiento LYNX')
    
    # Configuraciones de estilo
    dot.attr(rankdir='TB', size='12,18')
    dot.attr('graph', fontname='Arial', fontsize='16', fontcolor='#333333',
            splines='ortho', nodesep='0.8', ranksep='1.0')
    dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333',
            height='0.8', width='2.0', penwidth='1.5', margin='0.15')
    dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555',
            arrowsize='0.8', penwidth='1.3')
            
    # Colores
    color_entrada = "#E1F5FE"      # Azul muy claro
    color_afd = "#FFF9C4"          # Amarillo claro
    color_tokens = "#E8F5E9"       # Verde claro
    color_interpretacion = "#F3E5F5"  # Morado claro
    color_sql = "#FBE9E7"          # Naranja claro
    
    # Nodos principales del flujo
    dot.node('entrada', 'Entrada de Texto\\n"botana barata menor a 10"', 
            shape='box', style='filled,rounded', fillcolor=color_entrada)
    
    dot.node('analisis_lexico', 'Análisis Léxico', 
            shape='box', style='filled,rounded', fillcolor=color_afd)
    
    # Cluster para los AFDs
    with dot.subgraph(name='cluster_afds') as c:
        c.attr(label='Autómatas Finitos Deterministas', style='filled', fillcolor='#F8F8F8')
        
        c.node('afd_multi', 'AFD\\nMultipalabra', shape='ellipse', style='filled', fillcolor=color_afd)
        c.node('afd_op', 'AFD\\nOperadores', shape='ellipse', style='filled', fillcolor=color_afd)
        c.node('afd_num', 'AFD\\nNúmeros', shape='ellipse', style='filled', fillcolor=color_afd)
        c.node('afd_palabras', 'AFD\\nPalabras', shape='ellipse', style='filled', fillcolor=color_afd)
    
    # Cluster para los tokens generados
    with dot.subgraph(name='cluster_tokens') as c:
        c.attr(label='Tokens Generados', style='filled', fillcolor='#F8F8F8')
        
        c.node('token_botana', 'PALABRA_GENERICA\\n"botana"', shape='box', style='filled', fillcolor=color_tokens)
        c.node('token_barata', 'PALABRA_GENERICA\\n"barata"', shape='box', style='filled', fillcolor=color_tokens)
        c.node('token_menor', 'OP_MENOR\\n"menor a"', shape='box', style='filled', fillcolor=color_tokens)
        c.node('token_10', 'NUMERO_ENTERO\\n"10"', shape='box', style='filled', fillcolor=color_tokens)
    
    dot.node('analisis_contextual', 'Análisis Contextual', 
            shape='box', style='filled,rounded', fillcolor=color_interpretacion)
            
    # Cluster para tokens interpretados
    with dot.subgraph(name='cluster_interpretacion') as c:
        c.attr(label='Interpretación Semántica', style='filled', fillcolor='#F8F8F8')
        
        c.node('token_categoria', 'CATEGORIA\\n"snacks"\\n(mapeo de "botana")', 
                shape='box', style='filled', fillcolor=color_interpretacion)
        c.node('token_precio', 'FILTRO_PRECIO\\n"barata"\\n{op: menor_a, valor: 50}', 
                shape='box', style='filled', fillcolor=color_interpretacion)
        c.node('token_filtro', 'Filtro de Precio\\n"menor a 10"', 
                shape='box', style='filled', fillcolor=color_interpretacion)
    
    dot.node('generacion_sql', 'Generación de SQL', 
            shape='box', style='filled,rounded', fillcolor=color_sql)
            
    dot.node('sql_final', 'SQL: SELECT * FROM productos\\nWHERE categoria = \'snacks\'\\nAND precio < 10', 
            shape='box', style='filled,rounded', fillcolor=color_sql)
    
    # Conexiones principales
    dot.edge('entrada', 'analisis_lexico')
    dot.edge('analisis_lexico', 'afd_multi')
    dot.edge('analisis_lexico', 'afd_op')
    dot.edge('analisis_lexico', 'afd_num')
    dot.edge('analisis_lexico', 'afd_palabras')
    
    # De AFDs a Tokens
    dot.edge('afd_palabras', 'token_botana')
    dot.edge('afd_palabras', 'token_barata')
    dot.edge('afd_op', 'token_menor')
    dot.edge('afd_num', 'token_10')
    
    # Unificar tokens
    dot.edge('token_botana', 'analisis_contextual')
    dot.edge('token_barata', 'analisis_contextual')
    dot.edge('token_menor', 'analisis_contextual')
    dot.edge('token_10', 'analisis_contextual')
    
    # Interpretación
    dot.edge('analisis_contextual', 'token_categoria')
    dot.edge('analisis_contextual', 'token_precio')
    dot.edge('analisis_contextual', 'token_filtro')
    
    # SQL
    dot.edge('token_categoria', 'generacion_sql')
    dot.edge('token_precio', 'generacion_sql')
    dot.edge('token_filtro', 'generacion_sql')
    
    dot.edge('generacion_sql', 'sql_final')
    
    # Título y configuraciones finales
    dot.attr(label='Flujo de Procesamiento de Consulta en LYNX')
    dot.attr(labelloc='t')
    dot.attr(labelfontsize='20')
    dot.attr(labelfontcolor='#333333')
    
    # Generar diagrama
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"diagramas_explicativos/flujo_procesamiento_{timestamp}"
    
    # Renderizar en diferentes formatos
    formatos = ['png', 'svg', 'pdf']
    for formato in formatos:
        try:
            dot.render(filename, format=formato, cleanup=True)
            print(f"Diagrama de flujo guardado como: {filename}.{formato}")
        except Exception as e:
            print(f"Error al generar el formato {formato}: {e}")
    
    return f"{filename}.svg"

if __name__ == "__main__":
    ruta_diagrama = generar_diagrama_flujo_procesamiento()
    print(f"\nDiagrama generado en: {ruta_diagrama}")
    print("Este diagrama muestra el flujo de procesamiento de la consulta 'botana barata menor a 10' en el sistema LYNX.")
    print("Incluye la transformación semántica de 'botana' a 'snacks' y la interpretación del término cualitativo 'barata'.")
