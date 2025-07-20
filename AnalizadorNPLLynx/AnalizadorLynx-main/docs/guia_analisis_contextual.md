# Guía Detallada del Análisis Contextual en el Analizador LYNX

## Introducción al Análisis Contextual

El análisis contextual es una etapa crucial en el proceso de análisis léxico del sistema LYNX. Mientras que el análisis léxico básico identifica tokens individuales sin considerar su contexto, el análisis contextual examina las relaciones entre tokens adyacentes para refinar su clasificación y mejorar la interpretación general de la consulta.

## Propósito del Análisis Contextual

En el lenguaje natural, el significado de una palabra a menudo depende de las palabras que la rodean. El análisis contextual en LYNX sirve para:

1. **Refinar la clasificación de tokens** basándose en su contexto sintáctico
2. **Identificar patrones específicos** en secuencias de tokens
3. **Preparar los datos** para la interpretación semántica posterior
4. **Reducir ambigüedades** en palabras con múltiples posibles clasificaciones

## Reglas del Análisis Contextual

El analizador contextual de LYNX aplica tres reglas fundamentales:

### Regla 1: CATEGORIA_KEYWORD + PALABRA_GENERICA = CATEGORIA

**Definición:** Si un token es de tipo `CATEGORIA_KEYWORD` (palabras como "categoría", "categorías") y el siguiente token es de tipo `PALABRA_GENERICA`, entonces este segundo token se reclasifica como `CATEGORIA`.

**Ejemplo:**
```
"categoría bebidas" → "bebidas" se reclasifica como CATEGORIA
```

**Justificación:** Esta regla identifica cuando el usuario está especificando explícitamente una categoría de productos. La palabra "categoría" actúa como una señal explícita de que la palabra siguiente representa una categoría de productos.

### Regla 2: MODIFICADOR + PALABRA_GENERICA = ATRIBUTO

**Definición:** Si un token es de tipo `MODIFICADOR` (palabras como "con", "sin", "extra") y el siguiente token es de tipo `PALABRA_GENERICA` o `MODIFICADOR`, entonces este segundo token se reclasifica como `ATRIBUTO`.

**Ejemplo:**
```
"sin chile" → "chile" se reclasifica como ATRIBUTO
"con mucho picante" → "picante" se reclasifica como ATRIBUTO
```

**Justificación:** Esta regla identifica atributos o características de los productos que el usuario está especificando. Los modificadores indican que la palabra siguiente es una característica que el producto debe tener o no tener.

### Regla 3: NUMERO + PALABRA_GENERICA (si es unidad) = UNIDAD

**Definición:** Si un token es de tipo `NUMERO_ENTERO` o `NUMERO_DECIMAL` y el siguiente token es una palabra que aparece en la lista de unidades conocidas, entonces este segundo token se reclasifica como `UNIDAD_MEDIDA` o `UNIDAD_MONEDA`, según corresponda.

**Ejemplo:**
```
"20 pesos" → "pesos" se reclasifica como UNIDAD_MONEDA
"500 gramos" → "gramos" se reclasifica como UNIDAD_MEDIDA
```

**Justificación:** Esta regla identifica expresiones de cantidad, ayudando a distinguir si un número se refiere a un precio, peso, volumen u otra medida.

## Proceso de Aplicación de Reglas

El análisis contextual sigue estos pasos:

1. **Recibir la lista de tokens** generada por el analizador léxico básico
2. **Iterar** a través de cada token en la lista
3. **Verificar cada regla** en orden (Regla 1, Regla 2, Regla 3)
4. **Aplicar la primera regla** que coincida con el patrón actual
5. **Continuar** con el siguiente token hasta procesar toda la lista
6. **Devolver** la lista de tokens con las clasificaciones refinadas

## Ejemplos Detallados de Análisis Contextual

### Ejemplo 1: "categoría bebidas económicas"

**Tokens iniciales:**
1. `CATEGORIA_KEYWORD`: "categoría"
2. `PALABRA_GENERICA`: "bebidas"
3. `PALABRA_GENERICA`: "económicas"

**Análisis paso a paso:**
1. Verificar token "categoría" (índice 0):
   - Es `CATEGORIA_KEYWORD` y el siguiente es `PALABRA_GENERICA`
   - Aplicar Regla 1: Cambiar "bebidas" a `CATEGORIA`
   
2. Verificar token "bebidas" (índice 1):
   - No coincide con ninguna regla
   
3. Verificar token "económicas" (índice 2):
   - Es el último token, no hay siguiente para aplicar reglas

**Tokens después del análisis contextual:**
1. `CATEGORIA_KEYWORD`: "categoría"
2. `CATEGORIA`: "bebidas"
3. `PALABRA_GENERICA`: "económicas"

Nota: "económicas" será posteriormente interpretado por el módulo semántico como un `FILTRO_PRECIO` con interpretación `{op: "menor_a", valor: 50}`.

### Ejemplo 2: "botana sin chile 20 pesos"

**Tokens iniciales:**
1. `PALABRA_GENERICA`: "botana"
2. `MODIFICADOR`: "sin"
3. `PALABRA_GENERICA`: "chile"
4. `NUMERO_ENTERO`: "20"
5. `PALABRA_GENERICA`: "pesos"

**Análisis paso a paso:**
1. Verificar token "botana" (índice 0):
   - No coincide con ninguna regla
   
2. Verificar token "sin" (índice 1):
   - Es `MODIFICADOR` y el siguiente es `PALABRA_GENERICA`
   - Aplicar Regla 2: Cambiar "chile" a `ATRIBUTO`
   
3. Verificar token "chile" (índice 2):
   - No coincide con ninguna regla
   
4. Verificar token "20" (índice 3):
   - Es `NUMERO_ENTERO` y el siguiente es "pesos" (una unidad conocida)
   - Aplicar Regla 3: Cambiar "pesos" a `UNIDAD_MONEDA`
   
5. Verificar token "pesos" (índice 4):
   - Es el último token, no hay siguiente para aplicar reglas

**Tokens después del análisis contextual:**
1. `PALABRA_GENERICA`: "botana"
2. `MODIFICADOR`: "sin"
3. `ATRIBUTO`: "chile"
4. `NUMERO_ENTERO`: "20"
5. `UNIDAD_MONEDA`: "pesos"

Nota: "botana" será posteriormente interpretado por el módulo semántico como `CATEGORIA` "snacks" si existe un mapeo para esa palabra en el diccionario de categorías.

## Papel del Análisis Contextual en el Pipeline Completo

El análisis contextual es el segundo paso en el proceso de análisis completo:

1. **Análisis Léxico Básico**: Identifica tokens individuales sin considerar su contexto
2. **Análisis Contextual**: Refina la clasificación de tokens basándose en las relaciones entre tokens adyacentes
3. **Interpretación Semántica**: Asigna significado a los tokens y realiza mapeos a términos conocidos
4. **Generación SQL**: Traduce la interpretación a una consulta SQL ejecutable

## Importancia del Análisis Contextual

El análisis contextual es esencial porque:

- **Mejora la precisión**: Refina la clasificación de tokens para reducir errores en la interpretación
- **Captura intenciones implícitas**: Identifica patrones lingüísticos que implican ciertos significados
- **Facilita la interpretación semántica**: Proporciona tokens mejor clasificados al módulo semántico
- **Maneja expresiones complejas**: Permite entender construcciones como "categoría bebidas sin azúcar"

## Implementación en el Código

En el código del analizador LYNX, el análisis contextual se implementa en el método `aplicar_contexto()` de la clase `AnalizadorLexicoLYNX`:

```python
def aplicar_contexto(self):
    """Aplica reglas de contexto para mejorar la clasificación"""
    for i in range(len(self.tokens_procesados)):
        token_actual = self.tokens_procesados[i]
        
        # Regla 1: CATEGORIA_KEYWORD + PALABRA_GENERICA = CATEGORIA
        if (token_actual['tipo'] == 'CATEGORIA_KEYWORD' and 
            i + 1 < len(self.tokens_procesados) and
            self.tokens_procesados[i + 1]['tipo'] == 'PALABRA_GENERICA'):
            self.tokens_procesados[i + 1]['tipo'] = 'CATEGORIA'
        
        # Regla 2: MODIFICADOR + PALABRA_GENERICA = ATRIBUTO
        if (token_actual['tipo'] == 'MODIFICADOR' and 
            i + 1 < len(self.tokens_procesados) and
            self.tokens_procesados[i + 1]['tipo'] in ['PALABRA_GENERICA', 'MODIFICADOR']):
            self.tokens_procesados[i + 1]['tipo'] = 'ATRIBUTO'
        
        # Regla 3: NUMERO + PALABRA_GENERICA (si es unidad) = UNIDAD
        if (token_actual['tipo'] in ['NUMERO_ENTERO', 'NUMERO_DECIMAL'] and 
            i + 1 < len(self.tokens_procesados)):
            siguiente = self.tokens_procesados[i + 1]
            if siguiente['valor'] in self.base_datos['unidades']:
                if siguiente['valor'] in ['pesos', 'peso']:
                    siguiente['tipo'] = 'UNIDAD_MONEDA'
                else:
                    siguiente['tipo'] = 'UNIDAD_MEDIDA'
```

## Conclusión

El análisis contextual es una capa fundamental que conecta el análisis léxico básico con la interpretación semántica más compleja. Sin este paso, muchas consultas en lenguaje natural no podrían interpretarse correctamente, ya que el significado de muchas palabras depende de su contexto.

Al aplicar reglas específicas para refinar la clasificación de tokens basándose en su contexto, el analizador LYNX logra una mejor comprensión de las consultas de los usuarios y puede generar consultas SQL más precisas.
