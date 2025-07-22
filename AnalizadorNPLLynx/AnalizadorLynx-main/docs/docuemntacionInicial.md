# Proyecto: Analizador Léxico LCLN para Sistema LYNX
**Materia:** Lenguajes y Autómatas  
**Sistema:** LYNX - Gestión de Inventarios y Pedidos

## 1. Descripción del Proyecto

### 1.1 Objetivo
Desarrollar un analizador léxico como microservicio para el sistema LYNX que procese consultas en lenguaje natural sobre productos, transformándolas en estructuras JSON para consultas a la base de datos, resolviendo ambigüedades mediante un sistema de prioridades y análisis contextual.

### 1.2 Problemática
El sistema LYNX cuenta con productos y categorías que pueden generar ambigüedades al procesar lenguaje natural:
- Productos con nombres multi-palabra ("Coca Cola")
- Categorías que coinciden con nombres genéricos ("Frutas" vs "frutas")
- Atributos que pueden ser parte del nombre o filtros ("sin azúcar")
- Operadores que requieren contexto ("a", "de", "entre")

### 1.3 Estrategia de Resolución
Implementaremos un **Analizador Léxico Multi-Fase con Desambiguación Contextual**:

1. **Fase 1 - Tokenización Inicial**: Identificación básica de tokens
2. **Fase 2 - Reconocimiento de Entidades**: Detección de productos y categorías conocidas
3. **Fase 3 - Análisis Contextual**: Resolución de ambigüedades mediante ventanas deslizantes
4. **Fase 4 - Validación Sintáctica**: Verificación de estructuras válidas

## 2. Especificación del Lenguaje a Procesar

### 2.1 Definición Formal
```
L(LCLN) = {w ∈ Σ* | w representa una consulta válida sobre productos}

Donde Σ = {a-z, A-Z, 0-9, á, é, í, ó, ú, ñ, espacios}
```

### 2.2 Gramática Formal con Prioridades
```bnf
<consulta> ::= <entidad_prioritaria> <modificadores_opcionales>
           | <busqueda_general> <filtros>

<entidad_prioritaria> ::= <producto_conocido_completo> 
                       | <producto_conocido> <variante>
                       | <categoria_explicita>

<producto_conocido_completo> ::= "coca cola sin azucar" 
                               | "manzana verde" 
                               | "arroz integral"

<producto_conocido> ::= "coca cola" | "doritos" | "arroz" | "manzana" | "lechuga"

<categoria_explicita> ::= "categoria" <nombre_categoria>
                       | <nombre_categoria> {lookahead: no hay producto después}

<nombre_categoria> ::= "bebidas" | "snacks" | "abarrotes" | "frutas" | "verduras"

<modificadores_opcionales> ::= <modificador> <modificadores_opcionales> | ε

<modificador> ::= <filtro_atributo> | <filtro_precio> | <filtro_cantidad>

<filtro_atributo> ::= ("sin" | "con") <atributo>
<filtro_precio> ::= <operador_precio> <numero> "pesos"
<filtro_cantidad> ::= "de" <numero> <unidad_medida>

<operador_precio> ::= "menor a" | "mayor a" | "entre" <numero> "y"
<unidad_medida> ::= "litros" | "gramos" | "mililitros" | "unidades"
```

### 2.3 Reglas de Desambiguación

**RD1**: Los productos conocidos multi-palabra tienen prioridad sobre interpretaciones separadas  
**RD2**: Las categorías explícitas (con palabra clave "categoria") tienen prioridad  
**RD3**: Los modificadores se asocian al elemento más cercano a la izquierda  
**RD4**: En caso de ambigüedad persistente, se aplica scoring basado en frecuencia de uso

## 3. Tabla de Componentes Léxicos Extendida

| Token | Lexema | Patrón RegEx | Prioridad | Contexto |
|-------|---------|--------------|-----------|----------|
| **PRODUCTO_COMPLETO** | coca cola sin azucar | `\b(coca\s+cola\s+sin\s+azucar)\b` | 1 | Global |
| **PRODUCTO_MULTIPALABRA** | coca cola | `\b(coca\s+cola)\b` | 2 | No seguido de "sin azucar" |
| **CATEGORIA_KEYWORD** | categoria, categoría | `\b(categor[ií]a)\b` | 3 | Inicio de frase |
| **CATEGORIA** | bebidas, frutas | `\b(bebidas|snacks|abarrotes|frutas|verduras)\b` | 4 | Sin producto cerca |
| **PRODUCTO_SIMPLE** | manzana, arroz | `\b(coca-cola|doritos|arroz|manzana|lechuga)\b` | 5 | General |
| **NEGACION** | sin, no | `\b(sin|no)\b` | 6 | Antes de atributo |
| **INCLUSION** | con | `\b(con)\b` | 6 | Antes de atributo |
| **ATRIBUTO** | azúcar, verde | `\b[a-záéíóúñ]{3,}\b` | 7 | Después de sin/con |
| **OP_MENOR** | menor a | `\b(menor\s+a)\b` | 8 | Antes de número |
| **OP_MAYOR** | mayor a | `\b(mayor\s+a)\b` | 8 | Antes de número |
| **OP_ENTRE** | entre | `\b(entre)\b` | 8 | Antes de número |
| **NUMERO** | 10, 20.5 | `\b\d+(\.\d+)?\b` | 9 | General |
| **UNIDAD_MONEDA** | pesos, peso | `\b(pesos?)\b` | 10 | Después de número |
| **UNIDAD_MEDIDA** | litros, gramos | `\b(litros?|gramos?|ml|kg)\b` | 10 | Después de número |
| **CONECTOR_Y** | y | `\b(y)\b` | 11 | Entre elementos |
| **PREPOSICION** | de, a | `\b(de|a)\b` | 12 | Contexto variable |
| **PALABRA_GENERICA** | - | `\b[a-záéíóúñ]+\b` | 13 | No reconocida |

## 4. Autómata Finito Determinista (AFD)

### 4.1 Definición Formal del AFD
```
M = (Q, Σ, δ, q0, F)

Donde:
- Q = {q0, q1, q2, ..., q20} // Estados
- Σ = Alfabeto de entrada (caracteres válidos)
- δ = Función de transición
- q0 = Estado inicial
- F = {q3, q5, q7, q9, q11, q13, q15, q17, q19} // Estados finales
```

### 4.2 Diagrama del AFD Principal

```
Estados y Transiciones Principales:

[q0] --'c'--> [q1] --'o'--> [q2] --'c'--> [q_coca]
                                     |
                                     v
                              --'a'--> [q_cola] --espacio--> [q_prod_multi]
                                                    |
                                                    v
                                            --'s'--> [q_sin] --> [q_prod_completo]

[q0] --'b'--> [q_b] --'e'--> [q_be] --'b'--> [q_beb] --'i'--> [q_bebi] 
                                                          |
                                                          v
                                                   --'d'--> [q_bebid] --'a'--> [q_bebida] --'s'--> [q_bebidas] ✓

[q0] --'s'--> [q_s] --'i'--> [q_si] --'n'--> [q_sin] ✓
         |
         └--'n'--> [q_sn] --'a'--> [q_sna] --'c'--> [q_snac] --'k'--> [q_snack] --'s'--> [q_snacks] ✓

[q0] --dígito--> [q_num] --dígito*--> [q_numero] ✓
                              |
                              └--'.'-->[q_decimal]--dígito+--> [q_numero_decimal] ✓

[q0] --'m'--> [q_m] --'e'--> [q_me] --'n'--> [q_men] --'o'--> [q_meno] --'r'--> [q_menor]
                                                                    |
                                                                    v
                                                            --espacio--> [q_menor_] --'a'--> [q_menor_a] ✓

[q0] --letra--> [q_palabra] --letra*--> [q_palabra_generica] ✓
```

### 4.3 Tabla de Transiciones Simplificada

| Estado | Entrada | Próximo Estado | Token Reconocido |
|--------|---------|----------------|------------------|
| q0 | 'c' | q1 | - |
| q1 | 'o' | q2 | - |
| q2 | 'c' | q_coca | - |
| q_coca | 'a' | q_cola | - |
| q_cola | ' ' | q_prod_multi | - |
| q_prod_multi | 's' | q_sin | - |
| q_sin | 'i' | q_sin2 | - |
| q_sin2 | 'n' | q_sin3 | NEGACION |
| q_prod_multi | otro | q_final | PRODUCTO_MULTIPALABRA |
| q0 | dígito | q_num | - |
| q_num | dígito | q_num | - |
| q_num | otro | q_final | NUMERO |

### 4.4 Implementación del AFD con Desambiguación

```python
class AFDConDesambiguacion:
    def __init__(self):
        self.estado_actual = 'q0'
        self.buffer = ""
        self.tokens = []
        self.productos_conocidos = {
            "coca cola sin azucar": "PRODUCTO_COMPLETO",
            "coca cola": "PRODUCTO_MULTIPALABRA",
            "manzana verde": "PRODUCTO_COMPLETO"
        }
        
    def procesar_entrada(self, entrada):
        """Procesa la entrada completa con look-ahead para desambiguación"""
        palabras = entrada.lower().split()
        i = 0
        
        while i < len(palabras):
            # Look-ahead para productos multi-palabra
            for longitud in range(min(4, len(palabras) - i), 0, -1):
                frase = " ".join(palabras[i:i+longitud])
                
                if frase in self.productos_conocidos:
                    self.tokens.append({
                        'tipo': self.productos_conocidos[frase],
                        'valor': frase,
                        'posicion': i,
                        'prioridad': 1 if longitud > 2 else 2
                    })
                    i += longitud
                    break
            else:
                # Procesar palabra individual
                token = self.procesar_palabra(palabras[i])
                self.tokens.append(token)
                i += 1
                
        return self.resolver_ambiguedades()
    
    def resolver_ambiguedades(self):
        """Aplica reglas de desambiguación contextual"""
        for i, token in enumerate(self.tokens):
            # Regla: "sin" o "con" convierten la siguiente palabra en ATRIBUTO
            if token['tipo'] in ['NEGACION', 'INCLUSION'] and i + 1 < len(self.tokens):
                if self.tokens[i + 1]['tipo'] == 'PALABRA_GENERICA':
                    self.tokens[i + 1]['tipo'] = 'ATRIBUTO'
            
            # Regla: número + unidad
            if token['tipo'] == 'NUMERO' and i + 1 < len(self.tokens):
                if self.tokens[i + 1]['valor'] in ['pesos', 'peso']:
                    self.tokens[i + 1]['tipo'] = 'UNIDAD_MONEDA'
                elif self.tokens[i + 1]['valor'] in ['litros', 'gramos', 'ml']:
                    self.tokens[i + 1]['tipo'] = 'UNIDAD_MEDIDA'
        
        return self.tokens
```

## 5. Algoritmo de Procesamiento

### 5.1 Flujo General
```
1. ENTRADA: "coca cola sin azucar menor a 20 pesos"
2. TOKENIZACIÓN INICIAL:
   - Identificar productos conocidos multi-palabra
   - Tokenizar elementos restantes
3. ANÁLISIS CONTEXTUAL:
   - Aplicar reglas de desambiguación
   - Asignar tipos según contexto
4. CONSTRUCCIÓN AST:
   - Crear árbol sintáctico con prioridades
5. SALIDA JSON:
   {
     "producto": "coca cola sin azucar",
     "tipo": "PRODUCTO_COMPLETO",
     "filtros": {
       "precio": {
         "operador": "menor_a",
         "valor": 20,
         "unidad": "pesos"
       }
     }
   }
```

### 5.2 Casos de Prueba con Ambigüedades Resueltas

| Entrada | Tokens Identificados | Salida Desambiguada |
|---------|---------------------|---------------------|
| "coca cola sin azucar" | [PRODUCTO_COMPLETO] | Producto específico |
| "coca cola sin conservadores" | [PRODUCTO_MULTIPALABRA, NEGACION, ATRIBUTO] | Producto + filtro |
| "bebidas sin azucar" | [CATEGORIA, NEGACION, ATRIBUTO] | Categoría + filtro |
| "manzana verde menor a 15 pesos" | [PRODUCTO_COMPLETO, OP_MENOR, NUMERO, UNIDAD_MONEDA] | Producto específico + precio |
| "frutas y verduras baratas" | [CATEGORIA, CONECTOR_Y, CATEGORIA, ATRIBUTO] | Múltiples categorías + filtro |

## 6. Métricas de Éxito

1. **Precisión en desambiguación**: >90% en casos de prueba
2. **Tiempo de procesamiento**: <100ms por consulta
3. **Cobertura de productos**: 100% de productos en BD
4. **Manejo de errores**: Sugerencias en casos ambiguos

## 7. Integración con LYNX

```javascript
// Endpoint del microservicio
POST /api/nlp/parse
{
  "query": "coca cola sin azucar menor a 20 pesos"
}

// Respuesta
{
  "success": true,
  "interpretation": {
    "tipo": "PRODUCTO_COMPLETO",
    "producto": "coca cola sin azucar",
    "filtros": {
      "precio_max": 20
    }
  },
  "sql_query": "SELECT * FROM Productos WHERE nombre = 'Coca-Cola Sin Azúcar' AND precio <= 20"
}
```