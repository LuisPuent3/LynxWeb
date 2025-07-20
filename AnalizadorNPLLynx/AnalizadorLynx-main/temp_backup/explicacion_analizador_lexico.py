"""
Explicación detallada del Analizador Léxico LYNX
Este archivo contiene una versión simplificada y comentada del analizador léxico
para ilustrar el proceso de análisis paso a paso.
"""
from datetime import datetime
from graphviz import Digraph

class ExplicacionAnalizadorLexico:
    """Clase para explicar el funcionamiento del Analizador Léxico LYNX"""
    
    def __init__(self):
        """Inicializar la explicación"""
        self.consulta_ejemplo = "botana barata menor a 10"
        
    def generar_diagrama_flujo(self):
        """Genera un diagrama de flujo del proceso del analizador léxico"""
        dot = Digraph(comment='Flujo de Análisis Léxico LYNX', format='svg')
        
        # Estilo moderno para el diagrama
        dot.attr(rankdir='TB', size='11,14', bgcolor='#fafafa')
        dot.attr('graph', fontname='Arial', fontsize='16', fontcolor='#333333',
                splines='ortho', nodesep='0.8', ranksep='1.0')
        dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333',
                height='0.8', width='2.2', penwidth='1.5', margin='0.15')
        dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555',
                arrowsize='0.8', penwidth='1.5')
        
        # Colores para cada etapa
        color_entrada = "#AADDFF"    # Azul claro
        color_lexico = "#90EE90"     # Verde claro
        color_afds = "#FFD700"       # Dorado
        color_contexto = "#FFB6C1"   # Rosa claro
        color_semantico = "#D8BFD8"  # Cardo
        color_sql = "#98FB98"        # Verde menta
        
        # Nodos para cada etapa
        dot.node('entrada', 'Entrada de texto\\n"botana barata menor a 10"', shape='box', style='filled,rounded', fillcolor=color_entrada)
        
        # Etapa de análisis léxico
        with dot.subgraph(name='cluster_lexico') as c:
            c.attr(label='Análisis Léxico (Tokenización)', style='filled', fillcolor='#f0f0f0')
            c.node('preproc', 'Preprocesamiento\\n(minúsculas, espacios)', shape='box', style='filled,rounded', fillcolor=color_lexico)
            c.node('tokens', 'Reconocimiento de Tokens', shape='box', style='filled,rounded', fillcolor=color_lexico)
        
        # Subgrafo para los AFDs
        with dot.subgraph(name='cluster_afds') as c:
            c.attr(label='Autómatas Finitos Deterministas', style='filled', fillcolor='#f8f8f8')
            c.node('afd_multi', 'AFD Multipalabra\\n(Productos compuestos)', shape='ellipse', style='filled', fillcolor=color_afds)
            c.node('afd_op', 'AFD Operadores\\n("menor a" -> OP_MENOR)', shape='ellipse', style='filled', fillcolor=color_afds)
            c.node('afd_num', 'AFD Números\\n("10" -> NUMERO_ENTERO)', shape='ellipse', style='filled', fillcolor=color_afds)
            c.node('afd_uni', 'AFD Unidades\\n(kg, pesos, etc.)', shape='ellipse', style='filled', fillcolor=color_afds)
            c.node('afd_pal', 'AFD Palabras\\n("botana", "barata")', shape='ellipse', style='filled', fillcolor=color_afds)
        
        # Etapa de análisis contextual
        with dot.subgraph(name='cluster_contexto') as c:
            c.attr(label='Análisis Contextual', style='filled', fillcolor='#f0f0f0')
            c.node('contexto', 'Aplicación de reglas contextuales', shape='box', style='filled,rounded', fillcolor=color_contexto)
            c.node('lista_tokens', 'Lista de Tokens Procesados', shape='box', style='filled,rounded', fillcolor=color_contexto)
        
        # Etapa de interpretación semántica
        with dot.subgraph(name='cluster_semantico') as c:
            c.attr(label='Interpretación Semántica', style='filled', fillcolor='#f8f8f8')
            c.node('semantico', 'Interpretador Semántico', shape='box', style='filled,rounded', fillcolor=color_semantico)
            c.node('mapeo', 'Mapeo de términos\\n("botana" -> "snacks")', shape='box', style='filled,rounded', fillcolor=color_semantico)
            c.node('filtros', 'Procesamiento de filtros\\n("barata" -> precio < 50)', shape='box', style='filled,rounded', fillcolor=color_semantico)
        
        # Etapa de generación SQL
        dot.node('json', 'Generación JSON', shape='box', style='filled,rounded', fillcolor=color_sql)
        dot.node('sql', 'Generación SQL\\nSELECT * FROM productos WHERE\\ncategoria="snacks" AND precio<10', shape='box', style='filled,rounded', fillcolor=color_sql)
        
        # Conexiones
        dot.edge('entrada', 'preproc')
        dot.edge('preproc', 'tokens')
        
        # Conexiones a AFDs
        dot.edge('tokens', 'afd_multi')
        dot.edge('tokens', 'afd_op')
        dot.edge('tokens', 'afd_num')
        dot.edge('tokens', 'afd_uni')
        dot.edge('tokens', 'afd_pal')
        
        # Conexiones desde AFDs
        dot.edge('afd_multi', 'lista_tokens')
        dot.edge('afd_op', 'lista_tokens')
        dot.edge('afd_num', 'lista_tokens')
        dot.edge('afd_uni', 'lista_tokens')
        dot.edge('afd_pal', 'lista_tokens')
        
        # Conexiones de análisis contextual
        dot.edge('lista_tokens', 'contexto')
        dot.edge('contexto', 'semantico')
        
        # Conexiones de interpretación semántica
        dot.edge('semantico', 'mapeo')
        dot.edge('semantico', 'filtros')
        dot.edge('mapeo', 'json')
        dot.edge('filtros', 'json')
        
        # Conexión final
        dot.edge('json', 'sql')
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"explicacion_analizador_lexico_{timestamp}"
        
        # Renderizar diagrama
        dot.render(filename, cleanup=True)
        print(f"Diagrama generado: {filename}.svg")
        
        return filename + ".svg"
    
    def explicar_proceso_paso_a_paso(self):
        """Explicación detallada del proceso de análisis léxico"""
        return """
# Análisis Léxico en el Sistema LYNX - Proceso Detallado

## Fase 1: Inicialización y Preprocesamiento

Cuando el analizador léxico recibe la consulta "botana barata menor a 10", ocurre lo siguiente:

1. **Inicialización**:
   - Se reinicia el array `tokens_procesados = []`
   - Se convierte toda la consulta a minúsculas
   - Se establece la posición inicial en 0

2. **Eliminación de espacios iniciales**:
   - El analizador salta los espacios en blanco iniciales

## Fase 2: Reconocimiento de Tokens con AFDs

### Iteración 1: Posición 0, texto "botana barata menor a 10"

1. **AFD Multipalabra** (prioridad más alta):
   - Intenta reconocer un producto multipalabra
   - No encuentra coincidencia para "botana..." en la base de datos
   - Retorna `None`

2. **AFD Operadores**:
   - Intenta reconocer un operador
   - "botana" no coincide con ningún patrón de operador
   - Retorna `None`

3. **AFD Números**:
   - Intenta reconocer un número
   - "botana" no es un número
   - Retorna `None`

4. **AFD Unidades**:
   - Intenta reconocer una unidad de medida
   - "botana" no es una unidad
   - Retorna `None`

5. **AFD Palabras** (prioridad más baja):
   - Intenta reconocer una palabra genérica
   - Reconoce "botana" como PALABRA_GENERICA
   - Retorna token:
     ```
     {
       'tipo': 'PALABRA_GENERICA',
       'valor': 'botana',
       'posicion_inicial': 0,
       'posicion_final': 6,
       'longitud': 6
     }
     ```

6. **Actualización**:
   - Se añade el token a `tokens_procesados`
   - Se avanza la posición a 7 (después de "botana ")

### Iteración 2: Posición 7, texto "barata menor a 10"

1-4. **AFDs prioritarios**: Todos retornan `None`

5. **AFD Palabras**:
   - Reconoce "barata" como PALABRA_GENERICA
   - Retorna token para "barata"
   - Actualiza posición a 14 (después de "barata ")

### Iteración 3: Posición 14, texto "menor a 10"

1. **AFD Multipalabra**: No hay coincidencia, retorna `None`

2. **AFD Operadores**:
   - Reconoce "menor a" como OP_MENOR
   - Retorna token:
     ```
     {
       'tipo': 'OP_MENOR',
       'valor': 'menor a',
       'posicion_inicial': 14,
       'posicion_final': 21,
       'longitud': 7
     }
     ```
   - Actualiza posición a 22 (después de "menor a ")

### Iteración 4: Posición 22, texto "10"

1-3. **AFDs prioritarios**: Los dos primeros retornan `None`

4. **AFD Números**:
   - Reconoce "10" como NUMERO_ENTERO
   - Retorna token para "10"
   - Actualiza posición a 24 (fin de la cadena)

## Fase 3: Aplicación de Contexto

Una vez obtenidos los tokens básicos, el método `aplicar_contexto()` realiza:

1. **Para "botana" (PALABRA_GENERICA)**:
   - No hay reglas contextuales aplicables todavía

2. **Para "barata" (PALABRA_GENERICA)**:
   - No hay reglas contextuales aplicables todavía

3. **Para "menor a" (OP_MENOR)**:
   - Verifica si hay un número después (sí hay: "10")
   - Mantiene el tipo OP_MENOR

4. **Para "10" (NUMERO_ENTERO)**:
   - No hay unidades después, se mantiene como está

## Fase 4: Interpretación Semántica

El `InterpretadorSemantico` realiza:

1. **Para "botana" (PALABRA_GENERICA)**:
   - Busca en el diccionario de sinónimos/categorías
   - Encuentra que "botana" corresponde a "snacks"
   - Cambia el token a:
     ```
     {
       'tipo': 'CATEGORIA',
       'valor': 'snacks',
       'valor_original': 'botana',
       ...
     }
     ```

2. **Para "barata" (PALABRA_GENERICA)**:
   - Busca en el diccionario de atributos cualitativos de precio
   - Encuentra que "barata" significa precio bajo
   - Cambia el token a:
     ```
     {
       'tipo': 'FILTRO_PRECIO',
       'valor': 'barata',
       'interpretacion': { 'op': 'menor_a', 'valor': 50 },
       ...
     }
     ```

## Fase 5: Generación JSON y SQL

1. **Estructura JSON**:
   ```json
   {
     "consulta_original": "botana barata menor a 10",
     "tokens": [...],
     "interpretacion": {
       "productos": [],
       "categorias": ["snacks"],
       "filtros": {
         "precio": { "max": 10 },
         "atributos": []
       }
     },
     "sql_sugerido": "SELECT * FROM productos WHERE categoria = 'snacks' AND precio <= 10"
   }
   ```

2. **Lógica de priorización de filtros**:
   - El filtro numérico explícito ("menor a 10") tiene prioridad sobre el cualitativo ("barata")
   - Se usa 10 como valor máximo en lugar de 50

## Puntos importantes sobre el Analizador Léxico:

1. **Sistema de prioridades**: Los AFD se prueban en orden específico, permitiendo que los reconocedores más específicos tengan precedencia.

2. **Detección contextual**: El análisis se realiza en múltiples pasadas, permitiendo refinar la interpretación.

3. **Interpretación flexible**: El sistema puede mapear términos coloquiales a categorías formales y entender atributos cualitativos.

4. **Procesamiento secuencial**: El texto se procesa de izquierda a derecha, token por token, lo que permite manejar consultas complejas.
        """

if __name__ == "__main__":
    explicacion = ExplicacionAnalizadorLexico()
    ruta_diagrama = explicacion.generar_diagrama_flujo()
    print("Diagrama generado correctamente.")
    print("\nExplicación del proceso de análisis léxico:")
    print(explicacion.explicar_proceso_paso_a_paso())
