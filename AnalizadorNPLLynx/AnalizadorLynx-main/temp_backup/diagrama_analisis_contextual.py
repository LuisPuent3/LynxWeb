"""
Diagrama explicativo detallado del Análisis Contextual en el Analizador Léxico LYNX.
Este script genera diagramas que muestran el funcionamiento del análisis contextual,
explicando cómo se refinan los tokens identificados inicialmente.
"""
from datetime import datetime
from graphviz import Digraph
import os

def crear_directorio(directorio):
    """Crea un directorio si no existe"""
    if not os.path.exists(directorio):
        os.makedirs(directorio)

def generar_diagrama_analisis_contextual():
    """Genera un diagrama detallado del análisis contextual"""
    # Crear directorio de salida
    directorio_salida = "diagramas"
    crear_directorio(directorio_salida)
    
    # Crear el diagrama
    dot = Digraph(comment='Análisis Contextual LYNX', format='svg')
    
    # Configuración básica
    dot.attr(rankdir='TB', size='14,16')
    dot.attr('graph', fontname='Arial', fontsize='18', fontcolor='#333333')
    dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333')
    dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555')
    
    # Título
    dot.attr(label='ANÁLISIS CONTEXTUAL EN ANALIZADOR LÉXICO LYNX')
    dot.attr(labelloc='t')
    dot.attr(labelfontsize='22')
    dot.attr(labelfontcolor='#333333')
    
    # Paleta de colores
    color_tokens = "#FFB6C1"      # Rosa claro
    color_reglas = "#E6E6FA"      # Lavanda
    color_proceso = "#AADDFF"     # Azul claro
    color_resultado = "#90EE90"   # Verde claro
    
    # SECCIÓN 1: ENTRADA DE TOKENS INICIALES
    with dot.subgraph(name='cluster_entrada') as c:
        c.attr(label='1. TOKENS ANTES DEL ANÁLISIS CONTEXTUAL', style='filled', fillcolor='#f0f0f0')
        
        # Tokens iniciales ejemplo 1
        c.node('tokens_iniciales1', 'Ejemplo 1: "comprar categoría bebidas"', shape='box', style='filled,rounded', fillcolor=color_tokens)
        c.node('tokens_lista1', '1. PALABRA_GENERICA: "comprar"\n2. CATEGORIA_KEYWORD: "categoría"\n3. PALABRA_GENERICA: "bebidas"', shape='box', style='filled', fillcolor=color_tokens)
        
        # Tokens iniciales ejemplo 2
        c.node('tokens_iniciales2', 'Ejemplo 2: "botana sin chile 20 pesos"', shape='box', style='filled,rounded', fillcolor=color_tokens)
        c.node('tokens_lista2', '1. PALABRA_GENERICA: "botana"\n2. MODIFICADOR: "sin"\n3. PALABRA_GENERICA: "chile"\n4. NUMERO_ENTERO: "20"\n5. PALABRA_GENERICA: "pesos"', shape='box', style='filled', fillcolor=color_tokens)
    
    # SECCIÓN 2: REGLAS CONTEXTUALES
    with dot.subgraph(name='cluster_reglas') as c:
        c.attr(label='2. REGLAS DE ANÁLISIS CONTEXTUAL', style='filled', fillcolor='#f8f8f8')
        
        # Regla 1
        c.node('regla1', 'REGLA 1: CATEGORIA_KEYWORD + PALABRA_GENERICA = CATEGORIA', shape='box', style='filled,rounded', fillcolor=color_reglas)
        c.node('regla1_exp', 'Si un token es CATEGORIA_KEYWORD y el siguiente\nes PALABRA_GENERICA, este último se convierte en CATEGORIA\n\nEjemplo: "categoría bebidas" → "bebidas" se clasifica como CATEGORIA', shape='box', style='filled', fillcolor=color_reglas)
        
        # Regla 2
        c.node('regla2', 'REGLA 2: MODIFICADOR + PALABRA_GENERICA = ATRIBUTO', shape='box', style='filled,rounded', fillcolor=color_reglas)
        c.node('regla2_exp', 'Si un token es MODIFICADOR y el siguiente\nes PALABRA_GENERICA o MODIFICADOR, este se convierte en ATRIBUTO\n\nEjemplo: "sin chile" → "chile" se clasifica como ATRIBUTO', shape='box', style='filled', fillcolor=color_reglas)
        
        # Regla 3
        c.node('regla3', 'REGLA 3: NUMERO + PALABRA_GENERICA(si es unidad) = UNIDAD', shape='box', style='filled,rounded', fillcolor=color_reglas)
        c.node('regla3_exp', 'Si un token es NUMERO y el siguiente\nes una palabra que está en la lista de unidades,\nse clasifica como UNIDAD_MEDIDA o UNIDAD_MONEDA\n\nEjemplo: "20 pesos" → "pesos" se clasifica como UNIDAD_MONEDA', shape='box', style='filled', fillcolor=color_reglas)
    
    # SECCIÓN 3: PROCESO DE APLICACIÓN
    with dot.subgraph(name='cluster_proceso') as c:
        c.attr(label='3. PROCESO DE APLICACIÓN DE REGLAS', style='filled', fillcolor='#f0f0f0')
        
        # Diagrama de flujo
        c.node('inicio', 'INICIO\nRecibir lista de tokens iniciales', shape='box', style='filled,rounded', fillcolor=color_proceso)
        c.node('iteracion', 'ITERACIÓN\nRecorrer cada token en la lista', shape='box', style='filled,rounded', fillcolor=color_proceso)
        c.node('verificacion1', 'VERIFICACIÓN REGLA 1\n¿Es CATEGORIA_KEYWORD y el siguiente es PALABRA_GENERICA?', shape='diamond', style='filled', fillcolor=color_proceso)
        c.node('aplicacion1', 'APLICAR REGLA 1\nCambiar siguiente token a tipo CATEGORIA', shape='box', style='filled', fillcolor=color_proceso)
        c.node('verificacion2', 'VERIFICACIÓN REGLA 2\n¿Es MODIFICADOR y el siguiente es PALABRA_GENERICA?', shape='diamond', style='filled', fillcolor=color_proceso)
        c.node('aplicacion2', 'APLICAR REGLA 2\nCambiar siguiente token a tipo ATRIBUTO', shape='box', style='filled', fillcolor=color_proceso)
        c.node('verificacion3', 'VERIFICACIÓN REGLA 3\n¿Es NUMERO y el siguiente es una unidad?', shape='diamond', style='filled', fillcolor=color_proceso)
        c.node('aplicacion3', 'APLICAR REGLA 3\nCambiar siguiente token a tipo UNIDAD_X', shape='box', style='filled', fillcolor=color_proceso)
        c.node('continuar', 'CONTINUAR\nPasar al siguiente token', shape='box', style='filled,rounded', fillcolor=color_proceso)
        c.node('fin', 'FIN\nDevolver lista de tokens refinada', shape='box', style='filled,rounded', fillcolor=color_proceso)
    
    # SECCIÓN 4: RESULTADOS
    with dot.subgraph(name='cluster_resultado') as c:
        c.attr(label='4. TOKENS DESPUÉS DEL ANÁLISIS CONTEXTUAL', style='filled', fillcolor='#f8f8f8')
        
        # Resultados ejemplo 1
        c.node('resultado1', 'Resultado Ejemplo 1', shape='box', style='filled,rounded', fillcolor=color_resultado)
        c.node('resultado_lista1', '1. PALABRA_GENERICA: "comprar"\n2. CATEGORIA_KEYWORD: "categoría"\n3. CATEGORIA: "bebidas" ← REGLA 1 aplicada', shape='box', style='filled', fillcolor=color_resultado)
        
        # Resultados ejemplo 2
        c.node('resultado2', 'Resultado Ejemplo 2', shape='box', style='filled,rounded', fillcolor=color_resultado)
        c.node('resultado_lista2', '1. PALABRA_GENERICA: "botana"\n2. MODIFICADOR: "sin"\n3. ATRIBUTO: "chile" ← REGLA 2 aplicada\n4. NUMERO_ENTERO: "20"\n5. UNIDAD_MONEDA: "pesos" ← REGLA 3 aplicada', shape='box', style='filled', fillcolor=color_resultado)
    
    # CONEXIONES
    # Conexiones de entrada
    dot.edge('tokens_iniciales1', 'tokens_lista1', style='dotted')
    dot.edge('tokens_iniciales2', 'tokens_lista2', style='dotted')
    
    # Conexiones de reglas
    dot.edge('regla1', 'regla1_exp', style='dotted')
    dot.edge('regla2', 'regla2_exp', style='dotted')
    dot.edge('regla3', 'regla3_exp', style='dotted')
    
    # Conexiones de proceso
    dot.edge('inicio', 'iteracion')
    dot.edge('iteracion', 'verificacion1')
    dot.edge('verificacion1', 'aplicacion1', label='Sí')
    dot.edge('verificacion1', 'verificacion2', label='No')
    dot.edge('aplicacion1', 'verificacion2')
    dot.edge('verificacion2', 'aplicacion2', label='Sí')
    dot.edge('verificacion2', 'verificacion3', label='No')
    dot.edge('aplicacion2', 'verificacion3')
    dot.edge('verificacion3', 'aplicacion3', label='Sí')
    dot.edge('verificacion3', 'continuar', label='No')
    dot.edge('aplicacion3', 'continuar')
    dot.edge('continuar', 'iteracion', label='¿Quedan tokens?')
    dot.edge('continuar', 'fin', label='No quedan tokens')
    
    # Conexiones de resultados
    dot.edge('resultado1', 'resultado_lista1', style='dotted')
    dot.edge('resultado2', 'resultado_lista2', style='dotted')
    
    # Conexiones entre secciones
    dot.edge('tokens_lista1', 'regla1', style='invis')
    dot.edge('regla3_exp', 'inicio', style='invis')
    dot.edge('fin', 'resultado1', style='invis')
    
    # Guardar diagrama
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directorio_salida}/analisis_contextual_{timestamp}"
    
    # Renderizar diagrama
    dot.render(filename, cleanup=True)
    print(f"Diagrama de análisis contextual generado: {filename}.svg")
    
    return filename + ".svg"

def generar_diagrama_ejemplo_contextual():
    """Genera un diagrama con un ejemplo detallado de análisis contextual"""
    # Crear directorio de salida
    directorio_salida = "diagramas"
    crear_directorio(directorio_salida)
    
    # Crear el diagrama
    dot = Digraph(comment='Ejemplo de Análisis Contextual', format='svg')
    
    # Configuración básica
    dot.attr(rankdir='LR', size='14,12')
    dot.attr('graph', fontname='Arial', fontsize='16', fontcolor='#333333')
    dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333')
    dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555')
    
    # Título
    dot.attr(label='EJEMPLO DE ANÁLISIS CONTEXTUAL: "categoría bebidas económicas"')
    dot.attr(labelloc='t')
    dot.attr(labelfontsize='20')
    dot.attr(labelfontcolor='#333333')
    
    # Paleta de colores
    color_tokens = "#FFB6C1"      # Rosa claro
    color_estado = "#E6E6FA"      # Lavanda
    color_resultado = "#90EE90"   # Verde claro
    color_nota = "#FFF8DC"        # Blanco maíz
    
    # Estado inicial
    dot.node('estado_inicial', 'Tokens Iniciales', shape='box', style='filled,rounded', fillcolor=color_estado)
    dot.node('tokens_iniciales', '1. CATEGORIA_KEYWORD: "categoría"\n2. PALABRA_GENERICA: "bebidas"\n3. PALABRA_GENERICA: "económicas"', shape='box', style='filled', fillcolor=color_tokens)
    
    # Paso 1: Aplicación de regla 1
    dot.node('paso1', 'Paso 1: Aplicación de Regla 1', shape='box', style='filled,rounded', fillcolor=color_estado)
    dot.node('regla1', 'REGLA 1:\nCATEGORIA_KEYWORD + PALABRA_GENERICA = CATEGORIA', shape='note', style='filled', fillcolor=color_nota)
    dot.node('resultado_paso1', '1. CATEGORIA_KEYWORD: "categoría"\n2. CATEGORIA: "bebidas" ← Cambio aplicado\n3. PALABRA_GENERICA: "económicas"', shape='box', style='filled', fillcolor=color_tokens)
    
    # Paso 2: No hay más reglas aplicables
    dot.node('paso2', 'Paso 2: No hay más reglas aplicables', shape='box', style='filled,rounded', fillcolor=color_estado)
    dot.node('resultado_paso2', '1. CATEGORIA_KEYWORD: "categoría"\n2. CATEGORIA: "bebidas"\n3. PALABRA_GENERICA: "económicas"', shape='box', style='filled', fillcolor=color_tokens)
    
    # Resultado final (interpretación semántica posterior)
    dot.node('paso_semantico', 'Interpretación Semántica\n(Paso siguiente)', shape='box', style='filled,rounded', fillcolor=color_resultado)
    dot.node('nota_semantica', 'Nota: "económicas" será interpretado\npor el módulo semántico como\nFILTRO_PRECIO con valor < 50', shape='note', style='filled', fillcolor=color_nota)
    dot.node('resultado_final', '1. CATEGORIA_KEYWORD: "categoría"\n2. CATEGORIA: "bebidas"\n3. FILTRO_PRECIO: "económicas"\n   interpretacion: {op: "menor_a", valor: 50}', shape='box', style='filled', fillcolor=color_resultado)
    
    # Conexiones
    dot.edge('estado_inicial', 'tokens_iniciales')
    dot.edge('estado_inicial', 'paso1')
    dot.edge('paso1', 'regla1', style='dotted')
    dot.edge('paso1', 'resultado_paso1')
    dot.edge('paso1', 'paso2')
    dot.edge('paso2', 'resultado_paso2')
    dot.edge('paso2', 'paso_semantico')
    dot.edge('paso_semantico', 'nota_semantica', style='dotted')
    dot.edge('paso_semantico', 'resultado_final')
    
    # Guardar diagrama
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directorio_salida}/ejemplo_contextual_{timestamp}"
    
    # Renderizar diagrama
    dot.render(filename, cleanup=True)
    print(f"Diagrama de ejemplo contextual generado: {filename}.svg")
    
    return filename + ".svg"

def generar_diagrama_papel_contextual():
    """Genera un diagrama que explica el papel del análisis contextual en el pipeline completo"""
    # Crear directorio de salida
    directorio_salida = "diagramas"
    crear_directorio(directorio_salida)
    
    # Crear el diagrama
    dot = Digraph(comment='Papel del Análisis Contextual', format='svg')
    
    # Configuración básica
    dot.attr(rankdir='TB', size='14,12')
    dot.attr('graph', fontname='Arial', fontsize='16', fontcolor='#333333')
    dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333')
    dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555')
    
    # Título
    dot.attr(label='PAPEL DEL ANÁLISIS CONTEXTUAL EN EL PIPELINE COMPLETO')
    dot.attr(labelloc='t')
    dot.attr(labelfontsize='20')
    dot.attr(labelfontcolor='#333333')
    
    # Paleta de colores
    color_lexico = "#AADDFF"      # Azul claro
    color_contextual = "#FFB6C1"  # Rosa claro
    color_semantico = "#D8BFD8"   # Cardo
    color_sql = "#90EE90"         # Verde claro
    color_nota = "#FFF8DC"        # Blanco maíz
    
    # Nodos para cada fase
    dot.node('texto', 'TEXTO DE ENTRADA\n"categoría bebidas económicas"', shape='box', style='filled,rounded', fillcolor='#FFFFFF')
    
    # Análisis léxico
    with dot.subgraph(name='cluster_lexico') as c:
        c.attr(label='1. ANÁLISIS LÉXICO BÁSICO', style='filled', fillcolor='#f0f0f0')
        c.node('lexico', 'Analizador Léxico\nIdentificación de tokens', shape='box', style='filled,rounded', fillcolor=color_lexico)
        c.node('tokens_iniciales', 'Tokens sin contexto\n1. CATEGORIA_KEYWORD: "categoría"\n2. PALABRA_GENERICA: "bebidas"\n3. PALABRA_GENERICA: "económicas"', shape='box', style='filled', fillcolor=color_lexico)
    
    # Análisis contextual
    with dot.subgraph(name='cluster_contextual') as c:
        c.attr(label='2. ANÁLISIS CONTEXTUAL', style='filled', fillcolor='#f8f8f8')
        c.node('contextual', 'Analizador Contextual\nRefinamiento de tokens', shape='box', style='filled,rounded', fillcolor=color_contextual)
        c.node('tokens_contextual', 'Tokens con contexto\n1. CATEGORIA_KEYWORD: "categoría"\n2. CATEGORIA: "bebidas"\n3. PALABRA_GENERICA: "económicas"', shape='box', style='filled', fillcolor=color_contextual)
        c.node('nota_contextual', 'El análisis contextual aprovecha\nlas relaciones entre tokens adyacentes\npara refinar su clasificación\nbasado en reglas establecidas', shape='note', style='filled', fillcolor=color_nota)
    
    # Análisis semántico
    with dot.subgraph(name='cluster_semantico') as c:
        c.attr(label='3. INTERPRETACIÓN SEMÁNTICA', style='filled', fillcolor='#f0f0f0')
        c.node('semantico', 'Interpretador Semántico\nEntendimiento del significado', shape='box', style='filled,rounded', fillcolor=color_semantico)
        c.node('tokens_semantico', 'Tokens con significado\n1. CATEGORIA_KEYWORD: "categoría"\n2. CATEGORIA: "bebidas"\n3. FILTRO_PRECIO: "económicas"', shape='box', style='filled', fillcolor=color_semantico)
    
    # Generación SQL
    with dot.subgraph(name='cluster_sql') as c:
        c.attr(label='4. GENERACIÓN SQL', style='filled', fillcolor='#f8f8f8')
        c.node('generador', 'Generador SQL\nCreación de consulta', shape='box', style='filled,rounded', fillcolor=color_sql)
        c.node('sql', 'SELECT * FROM productos\nWHERE categoria = "bebidas"\nAND precio <= 50', shape='box', style='filled', fillcolor=color_sql)
    
    # Conexiones
    dot.edge('texto', 'lexico')
    dot.edge('lexico', 'tokens_iniciales')
    dot.edge('tokens_iniciales', 'contextual')
    dot.edge('contextual', 'tokens_contextual')
    dot.edge('contextual', 'nota_contextual', style='dotted')
    dot.edge('tokens_contextual', 'semantico')
    dot.edge('semantico', 'tokens_semantico')
    dot.edge('tokens_semantico', 'generador')
    dot.edge('generador', 'sql')
    
    # Guardar diagrama
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{directorio_salida}/papel_contextual_{timestamp}"
    
    # Renderizar diagrama
    dot.render(filename, cleanup=True)
    print(f"Diagrama del papel del análisis contextual generado: {filename}.svg")
    
    return filename + ".svg"

if __name__ == "__main__":
    print("Generando diagramas explicativos del Análisis Contextual en LYNX...")
    
    try:
        ruta1 = generar_diagrama_analisis_contextual()
        ruta2 = generar_diagrama_ejemplo_contextual()
        ruta3 = generar_diagrama_papel_contextual()
        
        print("\nDiagramas generados con éxito:")
        print(f"1. Análisis Contextual: {ruta1}")
        print(f"2. Ejemplo de Análisis Contextual: {ruta2}")
        print(f"3. Papel del Análisis Contextual: {ruta3}")
        
    except Exception as e:
        print(f"Error al generar diagramas: {str(e)}")
        import traceback
        traceback.print_exc()
