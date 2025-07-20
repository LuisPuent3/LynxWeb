# Guía Detallada: Analizador Léxico LYNX

## Introducción

El Analizador Léxico es el componente central del sistema LYNX que se encarga de procesar consultas en lenguaje natural y convertirlas en una estructura que pueda ser interpretada por el sistema para generar consultas SQL. Este documento explica detalladamente el funcionamiento interno del analizador.

## Arquitectura del Analizador Léxico

El Analizador Léxico LYNX está compuesto por varias capas de procesamiento que trabajan de forma secuencial:

1. **Tokenización** - Conversión del texto en tokens elementales
2. **Análisis Contextual** - Refinamiento de tokens según su contexto
3. **Interpretación Semántica** - Asignación de significado y mapeo a conceptos conocidos
4. **Generación de Consultas** - Transformación a formato estructurado (JSON) y SQL

![Diagrama de Flujo del Analizador Léxico](explicacion_analizador_lexico_20250714_075808.svg)

## Proceso Detallado

### Fase 1: Inicialización y Preprocesamiento

Cuando el analizador léxico recibe una consulta como "botana barata menor a 10", realiza:

1. **Inicialización**:
   - Reinicia el array `tokens_procesados = []`
   - Convierte toda la consulta a minúsculas
   - Establece la posición inicial en 0

2. **Eliminación de espacios iniciales**:
   - El analizador salta los espacios en blanco iniciales

### Fase 2: Reconocimiento de Tokens con AFDs

El sistema utiliza cinco Autómatas Finitos Deterministas (AFDs) especializados, que se prueban en orden de prioridad:

#### AFDMultipalabra
- **Propósito**: Reconocer productos compuestos por múltiples palabras
- **Ejemplos**: "coca cola sin azucar", "frutas y verduras frescas"
- **Prioridad**: Máxima - se evalúa primero para capturar frases compuestas

#### AFDOperadores
- **Propósito**: Reconocer operadores de comparación y lógicos
- **Ejemplos**: "menor a", "mayor que", "igual a", "entre", "y"
- **Técnica**: Utiliza un árbol de prefijos para reconocimiento eficiente

#### AFDNumeros
- **Propósito**: Reconocer valores numéricos (enteros y decimales)
- **Ejemplos**: "10", "2.5", "1,000"
- **Características**: Maneja notación decimal y miles según diferentes estándares

#### AFDUnidades
- **Propósito**: Reconocer unidades de medida
- **Ejemplos**: "kg", "litros", "pesos"
- **Clasificación**: Distingue entre unidades monetarias y unidades físicas

#### AFDPalabras
- **Propósito**: Reconocer palabras genéricas que no encajan en otras categorías
- **Ejemplos**: "barata", "botana", "rojo"
- **Prioridad**: Mínima - se evalúa último como "catch-all"

### Fase 3: Aplicación de Contexto

Una vez obtenidos los tokens básicos, el método `aplicar_contexto()` aplica reglas para refinar la interpretación:

1. **Regla 1: CATEGORIA_KEYWORD + PALABRA_GENERICA → CATEGORIA**
   ```python
   if (token_actual['tipo'] == 'CATEGORIA_KEYWORD' and 
       i + 1 < len(self.tokens_procesados) and
       self.tokens_procesados[i + 1]['tipo'] == 'PALABRA_GENERICA'):
       self.tokens_procesados[i + 1]['tipo'] = 'CATEGORIA'
   ```

2. **Regla 2: MODIFICADOR + PALABRA_GENERICA → ATRIBUTO**
   ```python
   if (token_actual['tipo'] == 'MODIFICADOR' and 
       i + 1 < len(self.tokens_procesados) and
       self.tokens_procesados[i + 1]['tipo'] in ['PALABRA_GENERICA', 'MODIFICADOR']):
       self.tokens_procesados[i + 1]['tipo'] = 'ATRIBUTO'
   ```

3. **Regla 3: NUMERO + PALABRA_GENERICA (si es unidad) → UNIDAD**
   ```python
   if (token_actual['tipo'] in ['NUMERO_ENTERO', 'NUMERO_DECIMAL'] and 
       i + 1 < len(self.tokens_procesados)):
       siguiente = self.tokens_procesados[i + 1]
       if siguiente['valor'] in self.base_datos['unidades']:
           if siguiente['valor'] in ['pesos', 'peso']:
               siguiente['tipo'] = 'UNIDAD_MONEDA'
           else:
               siguiente['tipo'] = 'UNIDAD_MEDIDA'
   ```

### Fase 4: Interpretación Semántica

El `InterpretadorSemantico` realiza transformaciones avanzadas:

1. **Mapeo de categorías**:
   - Traduce términos coloquiales a categorías formales
   - Ejemplo: "botana" → "snacks", "refresco" → "bebidas"

2. **Interpretación de términos cualitativos**:
   - Mapea adjetivos a rangos numéricos
   - Ejemplos:
     - "barata" → precio < 50
     - "cara" → precio > 100
     - "grande" → tamaño > valor_promedio * 1.5

3. **Resolución de sinónimos**:
   - Unifica diferentes formas de referirse al mismo concepto
   - Ejemplo: "gaseosa", "soda", "refresco" → "bebidas"

4. **Normalización de unidades**:
   - Convierte unidades a una forma estándar
   - Ejemplo: "grande" → "tamaño: grande" → "volumen > X"

### Fase 5: Generación de JSON y SQL

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

2. **Generación SQL**:
   - Construye dinámicamente cláusulas WHERE
   - Prioriza filtros explícitos sobre implícitos
   - Maneja filtros de rango, categorías y atributos

## Casos Especiales

### 1. Resolución de Categorías Inexactas

Cuando una categoría exacta no existe (como "botana"), el sistema:
1. Busca en el diccionario de sinónimos/mapeos
2. Si encuentra una correspondencia (como "snacks"), la utiliza
3. Si no encuentra coincidencia, mantiene la categoría original

### 2. Conflicto entre Filtros Cualitativos y Explícitos

Cuando hay conflictos entre un filtro cualitativo ("barata") y un filtro explícito ("menor a 10"):
1. El filtro explícito tiene prioridad
2. Se utiliza el valor numérico específico (10) en lugar del implícito (50)

### 3. Resolución de Ambigüedades

Para resolver ambigüedades en tokens, el sistema:
1. Aplica el principio de "coincidencia más larga"
2. Prefiere tokens específicos sobre genéricos
3. Utiliza el contexto para desambiguar

## Mejoras Posibles

1. **Fuzzy Matching**: Implementar reconocimiento aproximado para manejar errores ortográficos
   ```python
   def buscar_categoria_similar_fuzzy(categoria, umbral=0.8):
       """Busca categoría similar usando distancia Levenshtein"""
       mejor_match = None
       mejor_score = 0
       
       for cat in self.categorias_conocidas:
           score = calcular_similitud(categoria, cat)
           if score > umbral and score > mejor_score:
               mejor_score = score
               mejor_match = cat
               
       return mejor_match
   ```

2. **Modelos de Lenguaje**: Integrar embeddings para capturar mejor las relaciones semánticas

3. **Expansión de Diccionarios**: Ampliar los mapeos para cubrir más términos regionales y coloquiales

4. **Aprendizaje Continuo**: Implementar retroalimentación del usuario para mejorar los mapeos

## Conclusiones

El Analizador Léxico LYNX es un sistema sofisticado que combina técnicas de procesamiento de lenguaje natural con autómatas finitos para interpretar consultas en lenguaje natural. Su arquitectura en capas permite un procesamiento flexible y extensible, capaz de manejar consultas complejas y términos coloquiales.
