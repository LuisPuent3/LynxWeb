"""
Diagrama Explicativo Detallado del Analizador Léxico LYNX
Este archivo genera un diagrama completo que explica el funcionamiento interno del analizador,
incluyendo el reconocimiento de tokens, la lista de tokens, y el flujo de procesamiento.
"""
from datetime import datetime
from graphviz import Digraph
import os

class DiagramaDetalladoLYNX:
    """Clase para generar un diagrama detallado del Analizador Léxico LYNX"""
    
    def __init__(self):
        """Inicializar la explicación"""
        self.consulta_ejemplo = "botana barata menor a 10"
        self.directorio_salida = "diagramas"
        self._crear_directorio()
        
    def _crear_directorio(self):
        """Crea el directorio de salida si no existe"""
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
            
    def generar_diagrama_arquitectura_completa(self):
        """Genera un diagrama completo de la arquitectura del analizador léxico"""
        dot = Digraph(comment='Arquitectura Completa del Analizador Léxico LYNX', format='svg')
        
        # Estilo moderno para el diagrama
        dot.attr(rankdir='TB', size='14,20', bgcolor='#fafafa')
        dot.attr('graph', fontname='Arial', fontsize='18', fontcolor='#333333',
                splines='polyline', nodesep='0.8', ranksep='1.2')
        dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333',
                height='0.8', width='2.0', penwidth='1.5', margin='0.15')
        dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555',
                arrowsize='0.8', penwidth='1.5')
                
        # Título del diagrama
        dot.attr(label='Sistema Completo de Análisis Léxico LYNX')
        dot.attr(labelloc='t')
        dot.attr(labelfontsize='24')
        dot.attr(labelfontcolor='#333333')
        
        # Paleta de colores
        color_entrada = "#AADDFF"    # Azul claro
        color_lexico = "#90EE90"     # Verde claro
        color_afds = "#FFD700"       # Dorado
        color_token = "#FFB6C1"      # Rosa claro
        color_contexto = "#E6E6FA"   # Lavanda
        color_semantico = "#D8BFD8"  # Cardo
        color_sql = "#98FB98"        # Verde menta
        color_nota = "#FFF8DC"       # Blanco maíz
        
        # SECCIÓN 1: ENTRADA Y PREPROCESAMIENTO
        with dot.subgraph(name='cluster_entrada') as c:
            c.attr(label='1. ENTRADA Y PREPROCESAMIENTO', style='filled', fillcolor='#f0f0f0', fontsize='16')
            c.node('entrada', 'Texto de Entrada\n"botana barata menor a 10"', shape='box', style='filled,rounded', fillcolor=color_entrada)
            c.node('preproc', 'Preprocesamiento\n- Conversión a minúsculas\n- Eliminación espacios iniciales', shape='box', style='filled,rounded', fillcolor=color_entrada)
            c.edge('entrada', 'preproc')
        
        # SECCIÓN 2: SISTEMA DE RECONOCIMIENTO DE TOKENS
        with dot.subgraph(name='cluster_reconocimiento') as c:
            c.attr(label='2. SISTEMA DE RECONOCIMIENTO DE TOKENS', style='filled', fillcolor='#f8f8f8', fontsize='16')
            
            # Motor principal del analizador
            c.node('motor_afds', 'Motor de Análisis Léxico\nIteración por posición en el texto', shape='box', style='filled,rounded', fillcolor=color_lexico)
            
            # Subgrafo para los AFDs
            with c.subgraph(name='cluster_afds') as afd:
                afd.attr(label='Autómatas Finitos Deterministas (Por Prioridad)', style='filled', fillcolor='#f0f0f0')
                
                # Añadir nodos detallados para cada AFD
                afd.node('afd_multi', 'AFD Multipalabra\n- Reconoce frases multipalabra\n- Estados: q0, q_multi, q_final\n- Verifica en diccionario', shape='box', style='filled', fillcolor=color_afds)
                
                afd.node('afd_op', 'AFD Operadores\n- Reconoce operadores: mayor, menor, igual\n- Patrones: "menor a", "mayor que", etc.\n- Genera tokens tipo OP_X', shape='box', style='filled', fillcolor=color_afds)
                
                afd.node('afd_num', 'AFD Números\n- Reconoce enteros y decimales\n- Estados: q0, q_entero, q_punto, q_decimal\n- Genera tokens NUMERO_X', shape='box', style='filled', fillcolor=color_afds)
                
                afd.node('afd_uni', 'AFD Unidades\n- Reconoce unidades de medida\n- kg, g, ml, l, pesos, etc.\n- Genera tokens UNIDAD_X', shape='box', style='filled', fillcolor=color_afds)
                
                afd.node('afd_pal', 'AFD Palabras\n- Reconoce palabras genéricas\n- Clasifica por diccionarios\n- Tipos: CATEGORIA, MODIFICADOR, etc.', shape='box', style='filled', fillcolor=color_afds)
                
                # Conexiones internas entre AFDs
                afd.edge('afd_multi', 'afd_op', style='invis')
                afd.edge('afd_op', 'afd_num', style='invis')
                afd.edge('afd_num', 'afd_uni', style='invis')
                afd.edge('afd_uni', 'afd_pal', style='invis')
            
            # Nodo para el token reconocido
            c.node('token_reconocido', 'Token Reconocido', shape='box', style='filled,rounded', fillcolor=color_token)
            # Añadir un nodo con información simplificada
            c.node('token_info', 'tipo: PALABRA_GENERICA\\nvalor: "botana"\\nposición: 0-6', shape='box', style='filled', fillcolor=color_token)
            c.edge('token_reconocido', 'token_info', style='dotted')
        
        # SECCIÓN 3: LISTA DE TOKENS Y ANÁLISIS CONTEXTUAL
        with dot.subgraph(name='cluster_tokens') as c:
            c.attr(label='3. LISTA DE TOKENS Y ANÁLISIS CONTEXTUAL', style='filled', fillcolor='#f0f0f0', fontsize='16')
            
            # Lista de tokens
            c.node('lista_tokens', 'Lista de Tokens Reconocidos', shape='box', style='filled,rounded', fillcolor=color_token)
            # Añadir una tabla con tokens
            c.node('tokens_tabla', 'Token 1: CATEGORIA "botana"\\nToken 2: FILTRO_PRECIO "barata"\\nToken 3: OP_MENOR "menor a"\\nToken 4: NUMERO_ENTERO "10"', shape='box', style='filled', fillcolor=color_token)
            c.edge('lista_tokens', 'tokens_tabla', style='dotted')
            
            # Análisis contextual
            c.node('analisis_contextual', 'Análisis Contextual\n- Regla 1: CATEGORIA_KEYWORD + PALABRA_GENERICA = CATEGORIA\n- Regla 2: MODIFICADOR + PALABRA_GENERICA = ATRIBUTO\n- Regla 3: NUMERO + PALABRA_GENERICA (si es unidad) = UNIDAD', shape='box', style='filled,rounded', fillcolor=color_contexto)
        
        # SECCIÓN 4: INTERPRETACIÓN SEMÁNTICA
        with dot.subgraph(name='cluster_semantico') as c:
            c.attr(label='4. INTERPRETACIÓN SEMÁNTICA', style='filled', fillcolor='#f8f8f8', fontsize='16')
            
            # Interpretador semántico
            c.node('interpretador', 'Interpretador Semántico', shape='box', style='filled,rounded', fillcolor=color_semantico)
            
            # Mapeos semánticos
            with c.subgraph(name='cluster_mapeos') as m:
                m.attr(label='Diccionarios de Mapeos Semánticos', style='filled', fillcolor='#f0f0f0')
                m.node('mapeo_categorias', 'Mapeo de Categorías\n- "botana" → "snacks"\n- "refresco" → "bebidas"\n- "galletas" → "panificados"', shape='box', style='filled', fillcolor=color_semantico)
                
                m.node('mapeo_precios', 'Mapeo de Precios\n- "barato" → precio < 50\n- "caro" → precio > 100\n- "moderado" → 40 < precio < 80', shape='box', style='filled', fillcolor=color_semantico)
                
                m.node('mapeo_tamanos', 'Mapeo de Tamaños\n- "grande" → contenido > 1000ml\n- "chico" → contenido < 500ml\n- "familiar" → contenido > 1500ml', shape='box', style='filled', fillcolor=color_semantico)
            
            # Resultado de interpretación
            c.node('tokens_interpretados', 'Tokens Interpretados', shape='box', style='filled,rounded', fillcolor=color_token)
            # Añadir una tabla con tokens interpretados
            c.node('tokens_interp_tabla', 'Token 1: CATEGORIA "snacks" (original: "botana")\\nToken 2: FILTRO_PRECIO "barata" (precio < 50)\\nToken 3: OP_MENOR "menor a"\\nToken 4: NUMERO_ENTERO "10"', shape='box', style='filled', fillcolor=color_token)
            c.edge('tokens_interpretados', 'tokens_interp_tabla', style='dotted')
        
        # SECCIÓN 5: GENERACIÓN DE CONSULTAS
        with dot.subgraph(name='cluster_generacion') as c:
            c.attr(label='5. GENERACIÓN DE CONSULTAS', style='filled', fillcolor='#f0f0f0', fontsize='16')
            
            # Estructura interpretación
            c.node('estructura_json', 'Estructura JSON Intermedia', shape='box', style='filled,rounded', fillcolor=color_sql)
            # Añadir una representación simplificada
            c.node('json_content', 'consulta_original: "botana barata menor a 10"\\ncategorias: ["snacks"]\\nproductos: []\\nfiltros.precio.max: 10\\nfiltros.atributos: []', shape='box', style='filled', fillcolor=color_sql)
            c.edge('estructura_json', 'json_content', style='dotted')
            
            # Consulta SQL final
            c.node('sql_final', 'Consulta SQL Final', shape='box', style='filled,rounded', fillcolor=color_sql)
            c.node('sql_query', 'SELECT * FROM productos\\nWHERE categoria = "snacks"\\nAND precio <= 10', shape='box', style='filled', fillcolor=color_sql)
            c.edge('sql_final', 'sql_query', style='dotted')
        
        # SECCIÓN 6: DETALLES DE FUNCIONAMIENTO
        with dot.subgraph(name='cluster_detalles') as c:
            c.attr(label='6. DETALLES DE FUNCIONAMIENTO', style='filled', fillcolor='#f8f8f8', fontsize='16')
            
            # Explicación de iteraciones
            c.node('iteracion1', 'Iteración 1: "botana"\n- Posición inicial: 0\n- AFD elegido: AFD Palabras\n- Token: PALABRA_GENERICA\n- Nueva posición: 7', shape='note', style='filled', fillcolor=color_nota)
            
            c.node('iteracion2', 'Iteración 2: "barata"\n- Posición inicial: 7\n- AFD elegido: AFD Palabras\n- Token: PALABRA_GENERICA\n- Nueva posición: 14', shape='note', style='filled', fillcolor=color_nota)
            
            c.node('iteracion3', 'Iteración 3: "menor a"\n- Posición inicial: 14\n- AFD elegido: AFD Operadores\n- Token: OP_MENOR\n- Nueva posición: 22', shape='note', style='filled', fillcolor=color_nota)
            
            c.node('iteracion4', 'Iteración 4: "10"\n- Posición inicial: 22\n- AFD elegido: AFD Números\n- Token: NUMERO_ENTERO\n- Nueva posición: 24 (fin)', shape='note', style='filled', fillcolor=color_nota)
        
        # Conexiones entre secciones principales
        dot.edge('preproc', 'motor_afds')
        dot.edge('motor_afds', 'afd_multi')
        dot.edge('motor_afds', 'afd_op')
        dot.edge('motor_afds', 'afd_num')
        dot.edge('motor_afds', 'afd_uni')
        dot.edge('motor_afds', 'afd_pal')
        
        # Cambiar a splines=curved para las conexiones con etiquetas para evitar problemas con ortho
        dot.edge('afd_multi', 'token_reconocido', style='dashed', xlabel='si reconoce')
        dot.edge('afd_op', 'token_reconocido', style='dashed', xlabel='si reconoce')
        dot.edge('afd_num', 'token_reconocido', style='dashed', xlabel='si reconoce')
        dot.edge('afd_uni', 'token_reconocido', style='dashed', xlabel='si reconoce')
        dot.edge('afd_pal', 'token_reconocido', style='dashed', xlabel='si reconoce')
        
        dot.edge('token_reconocido', 'lista_tokens')
        dot.edge('lista_tokens', 'analisis_contextual')
        dot.edge('analisis_contextual', 'interpretador')
        
        dot.edge('interpretador', 'mapeo_categorias')
        dot.edge('interpretador', 'mapeo_precios')
        dot.edge('interpretador', 'mapeo_tamanos')
        
        dot.edge('mapeo_categorias', 'tokens_interpretados', style='dashed')
        dot.edge('mapeo_precios', 'tokens_interpretados', style='dashed')
        dot.edge('mapeo_tamanos', 'tokens_interpretados', style='dashed')
        
        dot.edge('tokens_interpretados', 'estructura_json')
        dot.edge('estructura_json', 'sql_final')
        
        dot.edge('motor_afds', 'iteracion1', style='dotted')
        dot.edge('motor_afds', 'iteracion2', style='dotted')
        dot.edge('motor_afds', 'iteracion3', style='dotted')
        dot.edge('motor_afds', 'iteracion4', style='dotted')
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.directorio_salida}/diagrama_completo_analizador_{timestamp}"
        
        # Renderizar diagrama
        dot.render(filename, cleanup=True)
        print(f"Diagrama completo generado: {filename}.svg")
        
        return filename + ".svg"
    
    def generar_diagrama_reconocimiento_tokens(self):
        """Genera un diagrama detallado del proceso de reconocimiento de tokens"""
        dot = Digraph(comment='Proceso de Reconocimiento de Tokens', format='svg')
        
        # Estilo moderno para el diagrama
        dot.attr(rankdir='TB', size='12,14', bgcolor='#fafafa')
        dot.attr('graph', fontname='Arial', fontsize='16', fontcolor='#333333',
                splines='ortho', nodesep='0.8', ranksep='1.0')
        dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333',
                height='0.8', width='2.0', penwidth='1.5', margin='0.15')
        dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555',
                arrowsize='0.8', penwidth='1.5')
                
        # Título del diagrama
        dot.attr(label='Proceso Detallado de Reconocimiento de Tokens')
        dot.attr(labelloc='t')
        dot.attr(labelfontsize='20')
        dot.attr(labelfontcolor='#333333')
        
        # Paleta de colores
        color_estado = "#ADD8E6"     # Azul claro
        color_transicion = "#90EE90" # Verde claro
        color_aceptacion = "#FFD700" # Dorado
        color_token = "#FFB6C1"      # Rosa claro
        color_nota = "#FFF8DC"       # Blanco maíz
        
        # Ejemplo con el AFD de números
        with dot.subgraph(name='cluster_afd_numeros') as c:
            c.attr(label='Ejemplo: AFD de Números', style='filled', fillcolor='#f0f0f0')
            
            # Estados
            c.node('q0', 'Estado Inicial\nq0', shape='circle', style='filled', fillcolor=color_estado)
            c.node('q_entero', 'Estado de\nAceptación\nq_entero', shape='doublecircle', style='filled', fillcolor=color_aceptacion)
            c.node('q_punto', 'Estado\nIntermedio\nq_punto', shape='circle', style='filled', fillcolor=color_estado)
            c.node('q_decimal', 'Estado de\nAceptación\nq_decimal', shape='doublecircle', style='filled', fillcolor=color_aceptacion)
            
            # Transiciones
            c.edge('q0', 'q_entero', label='dígito [0-9]')
            c.edge('q_entero', 'q_entero', label='dígito [0-9]')
            c.edge('q_entero', 'q_punto', label='.')
            c.edge('q_punto', 'q_decimal', label='dígito [0-9]')
            c.edge('q_decimal', 'q_decimal', label='dígito [0-9]')
            
            # Proceso para "10"
            c.node('ejemplo1', '"10"', shape='box', style='filled', fillcolor=color_nota)
            c.node('paso1', 'Paso 1:\nCarácter "1"\nq0 → q_entero', shape='note', style='filled', fillcolor=color_nota)
            c.node('paso2', 'Paso 2:\nCarácter "0"\nq_entero → q_entero', shape='note', style='filled', fillcolor=color_nota)
            c.node('paso3', 'Paso 3:\nFin de entrada\nq_entero es estado final\nToken reconocido', shape='note', style='filled', fillcolor=color_nota)
            
            # Conexiones de ejemplo
            c.edge('ejemplo1', 'paso1', style='dotted')
            c.edge('paso1', 'paso2', style='dotted')
            c.edge('paso2', 'paso3', style='dotted')
        
        # Estructura de un token
        with dot.subgraph(name='cluster_token') as c:
            c.attr(label='Estructura de un Token', style='filled', fillcolor='#f8f8f8')
            
            c.node('token_estructura', 'Token', shape='box', style='filled,rounded', fillcolor=color_token)
            c.node('token_struct_info', 'tipo: "NUMERO_ENTERO"\\nvalor: "10"\\nposicion_inicial: 22\\nposicion_final: 24\\nlongitud: 2', shape='box', style='filled', fillcolor=color_token)
            c.edge('token_estructura', 'token_struct_info', style='dotted')
            
            # Notas sobre los tipos de token
            c.node('tipos_token', 'Tipos de Tokens\n- PALABRA_GENERICA\n- CATEGORIA\n- PRODUCTO_SIMPLE\n- PRODUCTO_COMPLETO\n- MODIFICADOR\n- ATRIBUTO\n- OP_MENOR, OP_MAYOR, OP_IGUAL\n- NUMERO_ENTERO, NUMERO_DECIMAL\n- UNIDAD_MEDIDA, UNIDAD_MONEDA\n- FILTRO_PRECIO, FILTRO_TAMANO', shape='note', style='filled', fillcolor=color_nota)
            
            # Conexión
            c.edge('token_estructura', 'tipos_token', style='invis')
        
        # Lista de tokens completa
        dot.node('lista_tokens_completa', 'Lista de Tokens Reconocidos', shape='box', style='filled,rounded', fillcolor=color_token)
        dot.node('tokens_lista_detalle', 'Token 1: CATEGORIA "botana" (pos: 0-6)\\nToken 2: FILTRO_PRECIO "barata" (pos: 7-13)\\nToken 3: OP_MENOR "menor a" (pos: 14-21)\\nToken 4: NUMERO_ENTERO "10" (pos: 22-24)', shape='box', style='filled', fillcolor=color_token)
        dot.edge('lista_tokens_completa', 'tokens_lista_detalle', style='dotted')
        
        # Algoritmo de reconocimiento de tokens
        with dot.subgraph(name='cluster_algoritmo') as c:
            c.attr(label='Algoritmo de Reconocimiento de Tokens', style='filled', fillcolor='#f0f0f0')
            
            c.node('algoritmo', 'Pseudocódigo del Analizador Léxico\n\nfunción analizar(texto):\n    tokens = []\n    posición = 0\n    \n    mientras posición < longitud(texto):\n        # Saltar espacios\n        si texto[posición] es espacio:\n            posición += 1\n            continuar\n            \n        # Probar AFDs en orden de prioridad\n        token_encontrado = falso\n        para cada afd en afds_prioritarios:\n            resultado = afd.procesar_cadena(texto, posición)\n            si resultado no es nulo:\n                tokens.append(resultado)\n                posición = resultado.posición_final\n                token_encontrado = verdadero\n                romper ciclo\n                \n        # Si ningún AFD reconoció un token\n        si no token_encontrado:\n            posición += 1\n    \n    # Aplicar contexto e interpretación\n    aplicar_contexto(tokens)\n    interpretar_semanticamente(tokens)\n    \n    retornar tokens', shape='box', style='filled', fillcolor='#E6E6FA', fontname='Courier')
        
        # Conexión principal entre secciones
        dot.edge('cluster_afd_numeros', 'token_estructura', style='invis')
        dot.edge('token_estructura', 'lista_tokens_completa')
        dot.edge('lista_tokens_completa', 'algoritmo')
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.directorio_salida}/reconocimiento_tokens_{timestamp}"
        
        # Renderizar diagrama
        dot.render(filename, cleanup=True)
        print(f"Diagrama de reconocimiento generado: {filename}.svg")
        
        return filename + ".svg"
    
    def generar_diagrama_flujo_procesamiento(self):
        """Genera un diagrama de flujo del procesamiento de una consulta"""
        dot = Digraph(comment='Flujo de Procesamiento de Consulta', format='svg')
        
        # Estilo moderno para el diagrama
        dot.attr(rankdir='TB', size='12,16', bgcolor='#fafafa')
        dot.attr('graph', fontname='Arial', fontsize='16', fontcolor='#333333',
                splines='ortho', nodesep='0.8', ranksep='1.0')
        dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333',
                height='0.8', width='2.0', penwidth='1.5', margin='0.15')
        dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555',
                arrowsize='0.8', penwidth='1.5')
                
        # Título del diagrama
        dot.attr(label='Flujo de Procesamiento: "botana barata menor a 10"')
        dot.attr(labelloc='t')
        dot.attr(labelfontsize='20')
        dot.attr(labelfontcolor='#333333')
        
        # Paleta de colores
        color_entrada = "#AADDFF"    # Azul claro
        color_token = "#FFB6C1"      # Rosa claro
        color_contexto = "#E6E6FA"   # Lavanda
        color_semantico = "#D8BFD8"  # Cardo
        color_sql = "#98FB98"        # Verde menta
        
        # Entrada de texto
        dot.node('entrada', 'Consulta Original\n"botana barata menor a 10"', shape='box', style='filled,rounded', fillcolor=color_entrada)
        
        # Tokenización inicial
        dot.node('tokens_iniciales', 'Tokens Iniciales', shape='box', style='filled,rounded', fillcolor=color_token)
        dot.node('tokens_iniciales_lista', 'Token 1: PALABRA_GENERICA "botana"\\nToken 2: PALABRA_GENERICA "barata"\\nToken 3: OP_MENOR "menor a"\\nToken 4: NUMERO_ENTERO "10"', shape='box', style='filled', fillcolor=color_token)
        dot.edge('tokens_iniciales', 'tokens_iniciales_lista', style='dotted')
        
        # Análisis contextual
        dot.node('contexto', 'Análisis Contextual\nNo se aplican reglas en este caso', shape='box', style='filled,rounded', fillcolor=color_contexto)
        
        # Interpretación semántica
        dot.node('semantico', 'Interpretación Semántica\n- "botana" → Buscar en diccionario de categorías\n- "barata" → Buscar en diccionario de precios\n- No hay cambios para "menor a" y "10"', shape='box', style='filled,rounded', fillcolor=color_semantico)
        
        # Tokens interpretados
        dot.node('tokens_interpretados', 'Tokens Interpretados', shape='box', style='filled,rounded', fillcolor=color_token)
        dot.node('tokens_interpretados_lista', 'Token 1: CATEGORIA "snacks" (original: "botana")\\nToken 2: FILTRO_PRECIO "barata" (precio < 50)\\nToken 3: OP_MENOR "menor a"\\nToken 4: NUMERO_ENTERO "10"', shape='box', style='filled', fillcolor=color_token)
        dot.edge('tokens_interpretados', 'tokens_interpretados_lista', style='dotted')
        
        # Estructura intermedia
        dot.node('estructura', 'Estructura Semántica', shape='box', style='filled,rounded', fillcolor=color_semantico)
        dot.node('estructura_detalle', 'categorias: ["snacks"]\\nproductos: []\\nfiltros.precio.max: 10\\nfiltros.atributos: []', shape='box', style='filled', fillcolor=color_semantico)
        dot.edge('estructura', 'estructura_detalle', style='dotted')
        
        # Priorización de filtros (explicación)
        dot.node('priorizacion', 'Priorización de Filtros\n- El filtro numérico explícito ("menor a 10")\n  tiene prioridad sobre el cualitativo ("barata")\n- Se usa 10 como valor máximo en lugar de 50', shape='note', style='filled', fillcolor='#FFF8DC')
        
        # SQL final
        dot.node('sql', 'Consulta SQL Final', shape='box', style='filled,rounded', fillcolor=color_sql)
        dot.node('sql_texto', 'SELECT * FROM productos\\nWHERE categoria = "snacks"\\nAND precio <= 10', shape='box', style='filled', fillcolor=color_sql)
        dot.edge('sql', 'sql_texto', style='dotted')
        
        # Conexiones usando xlabel en lugar de label para evitar problemas con splines=ortho
        dot.edge('entrada', 'tokens_iniciales', xlabel='Analizador léxico')
        dot.edge('tokens_iniciales', 'contexto', xlabel='aplicar_contexto()')
        dot.edge('contexto', 'semantico', xlabel='interpretador_semantico.interpretar()')
        dot.edge('semantico', 'tokens_interpretados')
        dot.edge('tokens_interpretados', 'estructura', xlabel='_interpretar_tokens()')
        dot.edge('estructura', 'priorizacion', style='dashed')
        dot.edge('estructura', 'sql', xlabel='_generar_sql()')
        dot.edge('priorizacion', 'sql', style='dashed')
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.directorio_salida}/flujo_procesamiento_{timestamp}"
        
        # Renderizar diagrama
        dot.render(filename, cleanup=True)
        print(f"Diagrama de flujo generado: {filename}.svg")
        
        return filename + ".svg"
        
    def generar_diagramas_completos(self):
        """Genera todos los diagramas explicativos"""
        ruta_arquitectura = self.generar_diagrama_arquitectura_completa()
        ruta_reconocimiento = self.generar_diagrama_reconocimiento_tokens()
        ruta_flujo = self.generar_diagrama_flujo_procesamiento()
        
        print("\nTodos los diagramas explicativos han sido generados:")
        print(f"1. Arquitectura completa: {ruta_arquitectura}")
        print(f"2. Reconocimiento de tokens: {ruta_reconocimiento}")
        print(f"3. Flujo de procesamiento: {ruta_flujo}")
        
        return [ruta_arquitectura, ruta_reconocimiento, ruta_flujo]

if __name__ == "__main__":
    diagrama = DiagramaDetalladoLYNX()
    rutas = diagrama.generar_diagramas_completos()
    
    print("\nDiagramas generados con éxito!")
    print("Estos diagramas explican detalladamente el funcionamiento del Analizador Léxico LYNX.")
