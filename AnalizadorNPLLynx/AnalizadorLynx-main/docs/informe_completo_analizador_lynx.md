# Analizador Léxico LYNX

![Logo LYNX](https://via.placeholder.com/600x100/90EE90/000000?text=ANALIZADOR+L%C3%89XICO+LYNX)

## Portada

**Universidad [Nombre de la Universidad]**

**Facultad [Nombre de la Facultad]**

**Asignatura: Lenguajes y Autómatas I**

**Proyecto: Analizador Léxico LYNX**

**Integrantes del equipo:**
* [Tu nombre completo]
* [Nombres de tus compañeros si aplica]

**Profesor:**
* [Nombre del profesor]

**Fecha de entrega:** 14 de julio de 2025

---

## Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Especificación del Lenguaje a Procesar](#especificación-del-lenguaje-a-procesar)
3. [Tabla de Componentes Léxicos](#tabla-de-componentes-léxicos)
4. [Autómatas Finitos Deterministas](#autómatas-finitos-deterministas)
   1. [AFD General](#afd-general)
   2. [AFD Palabras](#afd-palabras)
   3. [AFD Números](#afd-números)
   4. [AFD Multipalabra](#afd-multipalabra)
   5. [AFD Operadores](#afd-operadores)
   6. [AFD Unidades](#afd-unidades)
   7. [Análisis Contextual](#análisis-contextual)
5. [Conclusiones](#conclusiones)
6. [Referencias](#referencias)

---

## Descripción del Proyecto

El proyecto Analizador Léxico LYNX consiste en un sistema de procesamiento de lenguaje natural que permite interpretar consultas en español coloquial y transformarlas en consultas SQL estructuradas. El sistema está diseñado principalmente para el contexto de una tienda o comercio, permitiendo a los usuarios buscar productos usando un lenguaje cotidiano.

### Objetivo General

Desarrollar un analizador léxico capaz de procesar consultas en lenguaje natural, identificar sus componentes léxicos (tokens) y transformarlos en una estructura que pueda ser interpretada semánticamente para generar consultas SQL funcionales.

### Objetivos Específicos

1. Implementar autómatas finitos deterministas (AFD) para el reconocimiento de diferentes tipos de tokens.
2. Desarrollar un sistema de análisis contextual que refine la clasificación de tokens basándose en su contexto.
3. Crear un interpretador semántico que asigne significado a expresiones coloquiales.
4. Generar consultas SQL válidas a partir de la interpretación de las consultas en lenguaje natural.

### Alcance

El analizador léxico LYNX puede procesar consultas que incluyen:
- Nombres de productos y categorías
- Modificadores de atributos (con, sin, extra)
- Expresiones de precio (barato, caro, menor a, mayor que)
- Expresiones numéricas y unidades de medida
- Términos cualitativos (económico, grande, pequeño)

### Tecnologías Utilizadas

- **Lenguaje de Programación**: Python 3.x
- **Visualización de Autómatas**: Graphviz
- **Gestión de Base de Datos**: SQL (interfaz genérica)

---

## Especificación del Lenguaje a Procesar

El lenguaje procesado por el analizador LYNX es un subconjunto del español coloquial orientado a consultas de productos en una tienda. Se caracteriza por:

### Características Sintácticas

1. **Estructura flexible**: Las consultas no requieren seguir una estructura gramatical estricta.
2. **Orden variable**: Los elementos pueden aparecer en diferentes órdenes manteniendo la semántica.
3. **Elementos opcionales**: Algunos componentes de la consulta pueden estar implícitos.

### Componentes Principales

1. **Productos**: Nombres de productos individuales o compuestos (ej. "coca cola", "galletas").
2. **Categorías**: Clasificaciones de productos (ej. "bebidas", "botanas").
3. **Atributos**: Características de los productos (ej. "sin azúcar", "con chile").
4. **Operadores**: Expresiones que indican relaciones (ej. "menor a", "igual a").
5. **Valores numéricos**: Cantidades y precios (ej. "10", "5.50").
6. **Unidades**: Monedas o medidas (ej. "pesos", "gramos", "litros").

### Ejemplos de Consultas Válidas

- "botana barata menor a 10"
- "categoría bebidas económicas"
- "coca cola sin azúcar"
- "galletas con chocolate menos de 30 pesos"
- "productos entre 10 y 50 pesos"

### Reglas Implícitas

1. El sistema interpreta términos coloquiales como "barato" o "caro" como filtros de precio.
2. Las palabras como "categoría" seguidas de una palabra genérica indican una clasificación.
3. Los modificadores como "sin" o "con" seguidos de una palabra generan atributos.
4. Los números seguidos de unidades se interpretan como cantidades o precios.

---

## Tabla de Componentes Léxicos

A continuación, se presenta la tabla de componentes léxicos (tokens) que el analizador LYNX identifica en las consultas:

| Tipo de Token | Descripción | Ejemplos | Patrón |
|---------------|-------------|----------|--------|
| PRODUCTO_SIMPLE | Producto individual | "galletas", "refresco" | Palabra en diccionario de productos |
| PRODUCTO_COMPLETO | Producto compuesto | "coca cola", "papas fritas" | Frase en diccionario de productos |
| CATEGORIA | Categoría de productos | "bebidas", "botanas" | Palabra en diccionario de categorías |
| CATEGORIA_KEYWORD | Palabra clave de categoría | "categoría", "tipo" | Palabra reservada específica |
| MODIFICADOR | Modificador de atributo | "con", "sin", "extra" | Palabra en lista de modificadores |
| ATRIBUTO | Característica de producto | "azúcar", "chile", "chocolate" | Palabra después de un MODIFICADOR |
| PALABRA_GENERICA | Palabra no clasificada | Cualquier palabra no reconocida | Secuencia de letras |
| OP_MENOR | Operador "menor que" | "menor a", "menos de" | Patrón de operador específico |
| OP_MAYOR | Operador "mayor que" | "mayor a", "más de" | Patrón de operador específico |
| OP_IGUAL | Operador "igual a" | "igual a", "exactamente" | Patrón de operador específico |
| OP_ENTRE | Operador "entre" | "entre", "desde...hasta" | Patrón de operador específico |
| NUMERO_ENTERO | Número sin decimales | "10", "5", "100" | Secuencia de dígitos |
| NUMERO_DECIMAL | Número con decimales | "10.5", "3.99" | Dígitos.Dígitos |
| UNIDAD_MEDIDA | Unidad de medida | "gramos", "litros", "ml" | Palabra en lista de unidades |
| UNIDAD_MONEDA | Unidad monetaria | "pesos", "peso" | Palabra específica |
| FILTRO_PRECIO | Filtro cualitativo de precio | "barato", "económico", "caro" | Palabra en diccionario de precios |
| FILTRO_TAMANO | Filtro cualitativo de tamaño | "grande", "pequeño", "familiar" | Palabra en diccionario de tamaños |

Esta tabla muestra los diversos tipos de tokens que el sistema reconoce, junto con su descripción, ejemplos y el patrón general que sigue cada tipo.

---

## Autómatas Finitos Deterministas

### AFD General

El sistema completo del Analizador Léxico LYNX está compuesto por múltiples autómatas que trabajan en conjunto. El siguiente diagrama muestra la arquitectura general del sistema:

*[AQUÍ INSERTAR IMAGEN: Incluir la imagen generada por generar_diagrama_simple.py - diagrama_analizador_XXXXXXXX.svg]*

Este diagrama muestra:
1. El flujo de procesamiento desde la entrada de texto hasta la generación SQL
2. Los diferentes AFDs que componen el sistema
3. Las fases de procesamiento: análisis léxico, contextual, interpretación semántica y generación SQL

### Flujo de Procesamiento

El siguiente diagrama muestra el flujo detallado de procesamiento para un ejemplo:

*[AQUÍ INSERTAR IMAGEN: Incluir la imagen generada por generar_diagrama_simple.py - proceso_analisis_XXXXXXXX.svg]*

Este diagrama ilustra paso a paso cómo se procesa la entrada "botana barata menor a 10" a través del analizador léxico.

### AFD Palabras

El AFD de Palabras reconoce tokens de tipo PALABRA_GENERICA, PRODUCTO_SIMPLE, CATEGORIA y otros tipos basados en diccionarios:

*[AQUÍ INSERTAR IMAGEN: Si tienes una imagen del AFD de palabras generada, inclúyela aquí]*

### AFD Números

El AFD de Números reconoce valores numéricos, tanto enteros como decimales:

*[AQUÍ INSERTAR IMAGEN: Si tienes una imagen del AFD de números generada, inclúyela aquí]*

Este autómata permite identificar tokens de tipo NUMERO_ENTERO y NUMERO_DECIMAL, los cuales son fundamentales para filtros de precio y cantidades.

### AFD Multipalabra

El AFD de Multipalabra reconoce productos compuestos por más de una palabra:

*[AQUÍ INSERTAR IMAGEN: Si tienes una imagen del AFD de multipalabra generada, inclúyela aquí]*

### AFD Operadores

El AFD de Operadores reconoce expresiones que indican relaciones como "menor a", "mayor que", etc.:

*[AQUÍ INSERTAR IMAGEN: Si tienes una imagen del AFD de operadores generada, inclúyela aquí]*

### AFD Unidades

El AFD de Unidades reconoce unidades de medida y moneda:

*[AQUÍ INSERTAR IMAGEN: Si tienes una imagen del AFD de unidades generada, inclúyela aquí]*

### Análisis Contextual

El análisis contextual es una parte crucial que refina la clasificación de tokens basándose en su contexto:

*[AQUÍ INSERTAR IMAGEN: Incluir la imagen generada por diagrama_analisis_contextual.py - analisis_contextual_XXXXXXXX.svg]*

#### Reglas de Contexto

*[AQUÍ INSERTAR IMAGEN: Incluir la imagen generada por diagrama_analisis_contextual.py - papel_contextual_XXXXXXXX.svg]*

#### Ejemplo de Análisis Contextual

*[AQUÍ INSERTAR IMAGEN: Incluir la imagen generada por diagrama_analisis_contextual.py - ejemplo_contextual_XXXXXXXX.svg]*

---

## Conclusiones

El desarrollo del Analizador Léxico LYNX ha permitido crear un sistema capaz de procesar consultas en lenguaje natural y transformarlas en consultas SQL estructuradas. A través de la implementación de múltiples autómatas finitos deterministas especializados, el sistema puede reconocer diversos tipos de tokens y aplicar reglas contextuales para refinar su clasificación.

### Logros

1. **Identificación precisa de tokens**: Los AFDs especializados permiten reconocer con precisión diferentes tipos de elementos léxicos.
2. **Análisis contextual efectivo**: El sistema puede refinar la clasificación de tokens basándose en su contexto, mejorando significativamente la interpretación.
3. **Interpretación semántica**: Se logró la traducción de términos cualitativos (como "barato" o "grande") a valores concretos utilizables en consultas SQL.
4. **Flexibilidad en las consultas**: El sistema puede manejar consultas con estructura variable y términos coloquiales.

### Limitaciones

1. **Dependencia del diccionario**: El sistema depende en gran medida de los diccionarios de términos preestablecidos.
2. **Ambigüedades no resueltas**: Algunas expresiones ambiguas requieren contexto adicional para ser interpretadas correctamente.
3. **Complejidad gramatical limitada**: El sistema no realiza un análisis sintáctico completo, lo que limita la complejidad de las consultas que puede procesar.

### Trabajo futuro

1. **Incorporación de análisis sintáctico**: Agregar un analizador sintáctico para manejar consultas más complejas.
2. **Mejora de la interpretación semántica**: Implementar técnicas más avanzadas de procesamiento de lenguaje natural.
3. **Ampliación de diccionarios**: Expandir los diccionarios para incluir más términos y categorías.
4. **Implementación de aprendizaje automático**: Incorporar técnicas de machine learning para mejorar la interpretación y adaptarse a nuevas expresiones.

La creación de este analizador léxico demuestra la complejidad y potencial del procesamiento de lenguaje natural en contextos específicos, y representa un paso importante hacia interfaces más naturales para sistemas de consulta de información.

---

## Referencias

American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). https://doi.org/10.1037/0000165-000

Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison Wesley.

Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson Education.

Graphviz. (2023). *Graph Visualization Software*. https://graphviz.org/

Python Software Foundation. (2023). *Python Language Reference, version 3.11*. https://docs.python.org/3/reference/

Russell, S. J., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.

Jurafsky, D., & Martin, J. H. (2021). *Speech and Language Processing* (3rd ed. draft). https://web.stanford.edu/~jurafsky/slp3/

Manning, C. D., & Schütze, H. (1999). *Foundations of Statistical Natural Language Processing*. MIT Press.

Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.
