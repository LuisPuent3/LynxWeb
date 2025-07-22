# Documento Técnico Detallado: Flujo Completo del Sistema LCLN
## Procesamiento Paso a Paso de una Consulta en Lenguaje Natural

---

## 1. INTRODUCCIÓN

Este documento describe con **máximo detalle** cada paso que realiza el sistema LCLN (Lenguaje de Consulta en Lenguaje Natural) cuando procesa una cadena de entrada. Se explicará cada iteración, cada decisión y cada transformación de datos.

### Sistema LCLN
- **Propósito**: Convertir búsquedas en lenguaje natural a consultas SQL estructuradas
- **Contexto**: Microservicio para el sistema LYNX de gestión de inventarios
- **Entrada**: String en español con errores, sinónimos y lenguaje coloquial
- **Salida**: JSON con interpretación + SQL query

---

## 2. EJEMPLO DE PROCESAMIENTO COMPLETO

### Entrada de ejemplo:
```
"koka kola sin asucar barata menor a 20 pesos"
```

### Salida esperada:
```json
{
  "query_original": "koka kola sin asucar barata menor a 20 pesos",
  "query_corregida": "coca cola sin azucar barata menor a 20 pesos",
  "tokens": [...],
  "interpretacion": {
    "producto": "coca cola sin azucar",
    "filtros": {
      "precio": {"max": 20, "tendencia": "bajo"}
    }
  },
  "sql": "SELECT * FROM Productos WHERE nombre = 'Coca-Cola Sin Azúcar' AND precio <= 20 ORDER BY precio ASC"
}
```

---

## 3. FLUJO DETALLADO PASO A PASO

### PASO 1: RECEPCIÓN Y VALIDACIÓN INICIAL

```python
def procesar_consulta(entrada_cruda):
    """
    PASO 1: Validación y preparación inicial
    """
    # 1.1 Recibir entrada
    entrada_cruda = "koka kola sin asucar barata menor a 20 pesos"
    
    # 1.2 Validar que no esté vacía
    if not entrada_cruda or entrada_cruda.strip() == "":
        return {"error": "Consulta vacía"}
    
    # 1.3 Limpiar entrada básica
    entrada_limpia = entrada_cruda.strip().lower()
    # Resultado: "koka kola sin asucar barata menor a 20 pesos"
    
    # 1.4 Validar longitud máxima (protección DoS)
    if len(entrada_limpia) > 200:
        return {"error": "Consulta demasiado larga"}
    
    # 1.5 Registrar en log
    log_entry = {
        "timestamp": "2024-01-20T10:15:30Z",
        "entrada_original": entrada_cruda,
        "longitud": len(entrada_limpia)
    }
```

### PASO 2: CORRECCIÓN ORTOGRÁFICA

```python
def corregir_ortografia(entrada_limpia):
    """
    PASO 2: Corregir errores ortográficos palabra por palabra
    """
    # 2.1 Dividir en palabras
    palabras = entrada_limpia.split()
    # ["koka", "kola", "sin", "asucar", "barata", "menor", "a", "20", "pesos"]
    
    palabras_corregidas = []
    correcciones_aplicadas = []
    
    # 2.2 Conectar a BD para obtener correcciones
    # QUERY SQL:
    # SELECT termino_correcto FROM CorreccionesOrtograficas WHERE termino_incorrecto IN (...)
    
    # 2.3 Procesar cada palabra
    for i, palabra in enumerate(palabras):
        # Iteración 1: palabra = "koka"
        # Buscar en tabla CorreccionesOrtograficas
        correccion = buscar_correccion(palabra)
        # SQL: SELECT termino_correcto FROM CorreccionesOrtograficas WHERE termino_incorrecto = 'koka'
        # Resultado: "coca"
        
        if correccion:
            palabras_corregidas.append(correccion)
            correcciones_aplicadas.append({
                "original": palabra,
                "corregida": correccion,
                "posicion": i,
                "tipo": "ortografica"
            })
        else:
            palabras_corregidas.append(palabra)
    
    # 2.4 Resultado de correcciones:
    # palabras_corregidas = ["coca", "cola", "sin", "azucar", "barata", "menor", "a", "20", "pesos"]
    # correcciones_aplicadas = [
    #   {"original": "koka", "corregida": "coca", "posicion": 0},
    #   {"original": "asucar", "corregida": "azucar", "posicion": 3}
    # ]
    
    entrada_corregida = " ".join(palabras_corregidas)
    # "coca cola sin azucar barata menor a 20 pesos"
    
    return entrada_corregida, correcciones_aplicadas
```

### PASO 3: TOKENIZACIÓN CON AFD

```python
def tokenizar_con_afd(entrada_corregida):
    """
    PASO 3: Análisis léxico usando Autómata Finito Determinista
    """
    entrada = "coca cola sin azucar barata menor a 20 pesos"
    tokens = []
    posicion = 0
    
    # 3.1 Inicializar AFD en estado q0
    estado_actual = "q0"
    buffer = ""
    
    # 3.2 Procesar carácter por carácter
    i = 0
    while i < len(entrada):
        char = entrada[i]
        
        # 3.3 FASE DE LOOK-AHEAD para productos multi-palabra
        # Verificar si las próximas palabras forman un producto conocido
        ventana_4_palabras = extraer_palabras(entrada[i:], 4)
        # ["coca", "cola", "sin", "azucar"]
        
        # 3.3.1 Verificar producto completo (máxima prioridad)
        if " ".join(ventana_4_palabras) == "coca cola sin azucar":
            tokens.append({
                "tipo": "PRODUCTO_COMPLETO",
                "valor": "coca cola sin azucar",
                "inicio": i,
                "fin": i + len("coca cola sin azucar"),
                "prioridad": 1
            })
            i += len("coca cola sin azucar") + 1
            continue
        
        # 3.3.2 Verificar producto de 2 palabras
        ventana_2_palabras = ventana_4_palabras[:2]
        if " ".join(ventana_2_palabras) == "coca cola":
            # Verificar contexto: ¿viene "sin azucar" después?
            if i + len("coca cola") < len(entrada):
                siguientes = entrada[i + len("coca cola"):].strip().split()
                if len(siguientes) >= 2 and siguientes[0] == "sin" and siguientes[1] == "azucar":
                    # No tokenizar aún, es parte de producto completo
                    pass
                else:
                    tokens.append({
                        "tipo": "PRODUCTO_MULTIPALABRA",
                        "valor": "coca cola",
                        "inicio": i,
                        "fin": i + len("coca cola"),
                        "prioridad": 2
                    })
                    i += len("coca cola") + 1
                    continue
    
    # 3.4 Después del look-ahead, continuar con análisis palabra por palabra
    # Entrada restante: "barata menor a 20 pesos"
    
    palabras_restantes = entrada[i:].split()
    for palabra in palabras_restantes:
        token = clasificar_palabra(palabra)
        tokens.append(token)
```

### PASO 4: CLASIFICACIÓN DE TOKENS INDIVIDUALES

```python
def clasificar_palabra(palabra, contexto_anterior=None):
    """
    PASO 4: Clasificar cada palabra según su tipo
    """
    # 4.1 Verificar si es número
    if es_numero(palabra):  # regex: ^\d+(\.\d+)?$
        return {"tipo": "NUMERO", "valor": palabra, "prioridad": 9}
    
    # 4.2 Verificar en diccionarios
    # SQL: SELECT * FROM SinonimosProductos WHERE termino = ?
    
    # Ejemplo: palabra = "barata"
    # 4.2.1 Buscar en sinónimos de atributos
    resultado = ejecutar_sql("""
        SELECT atributo_normalizado, categoria_atributo, valor_asociado 
        FROM SinonimosAtributos 
        WHERE atributo_usado = 'barata'
    """)
    # Resultado: atributo_normalizado = "precio_bajo", categoria = "precio"
    
    if resultado:
        return {
            "tipo": "ATRIBUTO_PRECIO",
            "valor": palabra,
            "valor_normalizado": "precio_bajo",
            "prioridad": 5
        }
    
    # 4.2.2 Verificar operadores
    if palabra == "menor":
        return {"tipo": "OP_MENOR_INCOMPLETO", "valor": palabra, "prioridad": 8}
    
    # 4.2.3 Verificar categorías
    if palabra in ["bebidas", "snacks", "frutas", "verduras", "abarrotes"]:
        return {"tipo": "CATEGORIA", "valor": palabra, "prioridad": 4}
    
    # 4.2.4 Verificar unidades
    if palabra in ["pesos", "peso"]:
        return {"tipo": "UNIDAD_MONEDA", "valor": palabra, "prioridad": 10}
    
    # 4.2.5 Si no se reconoce
    return {"tipo": "PALABRA_GENERICA", "valor": palabra, "prioridad": 13}
```

### PASO 5: ANÁLISIS CONTEXTUAL

```python
def analisis_contextual(tokens):
    """
    PASO 5: Refinar tokens basándose en contexto
    """
    # tokens = [
    #   {"tipo": "PRODUCTO_COMPLETO", "valor": "coca cola sin azucar"},
    #   {"tipo": "ATRIBUTO_PRECIO", "valor": "barata"},
    #   {"tipo": "OP_MENOR_INCOMPLETO", "valor": "menor"},
    #   {"tipo": "PREPOSICION", "valor": "a"},
    #   {"tipo": "NUMERO", "valor": "20"},
    #   {"tipo": "UNIDAD_MONEDA", "valor": "pesos"}
    # ]
    
    tokens_refinados = []
    i = 0
    
    while i < len(tokens):
        token_actual = tokens[i]
        
        # 5.1 Regla: Combinar operadores compuestos
        if token_actual["tipo"] == "OP_MENOR_INCOMPLETO":
            if i + 1 < len(tokens) and tokens[i + 1]["valor"] == "a":
                # Combinar "menor" + "a" = "menor a"
                token_combinado = {
                    "tipo": "OP_MENOR",
                    "valor": "menor a",
                    "prioridad": 8
                }
                tokens_refinados.append(token_combinado)
                i += 2  # Saltar el "a"
                continue
        
        # 5.2 Regla: Asociar números con unidades
        if token_actual["tipo"] == "NUMERO":
            if i + 1 < len(tokens) and tokens[i + 1]["tipo"] == "UNIDAD_MONEDA":
                token_actual["unidad"] = tokens[i + 1]["valor"]
                token_actual["contexto"] = "precio"
        
        # 5.3 Regla: Negación + palabra = atributo
        if token_actual["tipo"] == "NEGACION":
            if i + 1 < len(tokens) and tokens[i + 1]["tipo"] == "PALABRA_GENERICA":
                tokens[i + 1]["tipo"] = "ATRIBUTO"
                tokens[i + 1]["modificador"] = "sin"
        
        tokens_refinados.append(token_actual)
        i += 1
    
    return tokens_refinados
```

### PASO 6: CONSTRUCCIÓN DE INTERPRETACIÓN SEMÁNTICA

```python
def construir_interpretacion(tokens_refinados):
    """
    PASO 6: Construir estructura semántica de la consulta
    """
    interpretacion = {
        "elemento_principal": None,
        "filtros": {
            "precio": {},
            "atributos": {"incluir": [], "excluir": []},
            "cantidad": {}
        },
        "ordenamiento": None
    }
    
    # 6.1 Identificar elemento principal (producto o categoría)
    for token in tokens_refinados:
        if token["tipo"] in ["PRODUCTO_COMPLETO", "PRODUCTO_MULTIPALABRA"]:
            interpretacion["elemento_principal"] = {
                "tipo": "producto",
                "valor": token["valor"],
                "nombre_bd": mapear_a_nombre_bd(token["valor"])
            }
            break
        elif token["tipo"] == "CATEGORIA":
            interpretacion["elemento_principal"] = {
                "tipo": "categoria",
                "valor": token["valor"],
                "id_categoria": obtener_id_categoria(token["valor"])
            }
            break
    
    # 6.2 Procesar filtros y modificadores
    i = 0
    while i < len(tokens_refinados):
        token = tokens_refinados[i]
        
        # 6.2.1 Filtros de precio
        if token["tipo"] == "OP_MENOR":
            # Buscar el número siguiente
            for j in range(i + 1, len(tokens_refinados)):
                if tokens_refinados[j]["tipo"] == "NUMERO":
                    interpretacion["filtros"]["precio"]["max"] = float(tokens_refinados[j]["valor"])
                    interpretacion["filtros"]["precio"]["operador"] = "menor_igual"
                    break
        
        # 6.2.2 Atributos de precio
        if token["tipo"] == "ATRIBUTO_PRECIO":
            if token["valor_normalizado"] == "precio_bajo":
                interpretacion["ordenamiento"] = "precio_asc"
                # También podría agregar un filtro implícito
                if "max" not in interpretacion["filtros"]["precio"]:
                    # Calcular precio promedio de la categoría
                    precio_promedio = calcular_precio_promedio()
                    interpretacion["filtros"]["precio"]["max_implicito"] = precio_promedio * 0.8
        
        i += 1
    
    # Resultado:
    # interpretacion = {
    #   "elemento_principal": {"tipo": "producto", "valor": "coca cola sin azucar"},
    #   "filtros": {"precio": {"max": 20, "operador": "menor_igual"}},
    #   "ordenamiento": "precio_asc"
    # }
    
    return interpretacion
```

### PASO 7: VALIDACIÓN Y RESOLUCIÓN DE AMBIGÜEDADES

```python
def resolver_ambiguedades(interpretacion):
    """
    PASO 7: Resolver posibles ambigüedades en la interpretación
    """
    # 7.1 Verificar si el producto existe
    if interpretacion["elemento_principal"]["tipo"] == "producto":
        nombre_producto = interpretacion["elemento_principal"]["valor"]
        
        # SQL para verificar existencia
        existe = ejecutar_sql("""
            SELECT COUNT(*) as cuenta 
            FROM Productos 
            WHERE nombre = ? OR nombre LIKE ?
        """, [nombre_producto, f"%{nombre_producto}%"])
        
        if existe["cuenta"] == 0:
            # 7.2 Buscar productos similares
            similares = ejecutar_sql("""
                SELECT p.*, ps.score_similitud, ps.razon_similitud
                FROM ProductosSimilares ps
                JOIN Productos p ON ps.id_producto_sugerido = p.id_producto
                WHERE ps.producto_solicitado_texto = ?
                ORDER BY ps.score_similitud DESC
                LIMIT 3
            """, [nombre_producto])
            
            if similares:
                interpretacion["producto_no_encontrado"] = True
                interpretacion["sugerencias"] = similares
    
    # 7.3 Resolver conflictos de filtros
    if interpretacion["filtros"]["precio"].get("max") and interpretacion["filtros"]["precio"].get("max_implicito"):
        # Usar el más restrictivo
        interpretacion["filtros"]["precio"]["max"] = min(
            interpretacion["filtros"]["precio"]["max"],
            interpretacion["filtros"]["precio"]["max_implicito"]
        )
    
    return interpretacion
```

### PASO 8: GENERACIÓN DE CONSULTA SQL

```python
def generar_sql(interpretacion):
    """
    PASO 8: Construir la consulta SQL final
    """
    # 8.1 Iniciar construcción SQL
    sql_parts = {
        "select": "SELECT p.*, c.nombre as categoria_nombre",
        "from": "FROM Productos p",
        "join": "JOIN Categorias c ON p.id_categoria = c.id_categoria",
        "where": [],
        "order_by": "",
        "limit": ""
    }
    
    # 8.2 Agregar condición principal
    if interpretacion["elemento_principal"]["tipo"] == "producto":
        # Mapear nombre a formato de BD
        nombre_bd = interpretacion["elemento_principal"]["valor"]
        if nombre_bd == "coca cola sin azucar":
            nombre_bd = "Coca-Cola Sin Azúcar 600ml"
        
        sql_parts["where"].append(f"p.nombre = '{nombre_bd}'")
    
    elif interpretacion["elemento_principal"]["tipo"] == "categoria":
        id_cat = interpretacion["elemento_principal"]["id_categoria"]
        sql_parts["where"].append(f"p.id_categoria = {id_cat}")
    
    # 8.3 Agregar filtros de precio
    if "max" in interpretacion["filtros"]["precio"]:
        precio_max = interpretacion["filtros"]["precio"]["max"]
        sql_parts["where"].append(f"p.precio <= {precio_max}")
    
    # 8.4 Agregar ordenamiento
    if interpretacion.get("ordenamiento") == "precio_asc":
        sql_parts["order_by"] = "ORDER BY p.precio ASC"
    
    # 8.5 Construir SQL final
    sql_final = f"""
    {sql_parts['select']}
    {sql_parts['from']}
    {sql_parts['join']}
    WHERE {' AND '.join(sql_parts['where'])}
    {sql_parts['order_by']}
    """
    
    # Resultado:
    # SELECT p.*, c.nombre as categoria_nombre
    # FROM Productos p
    # JOIN Categorias c ON p.id_categoria = c.id_categoria
    # WHERE p.nombre = 'Coca-Cola Sin Azúcar 600ml' AND p.precio <= 20
    # ORDER BY p.precio ASC
    
    return sql_final.strip()
```

### PASO 9: EJECUCIÓN Y ENRIQUECIMIENTO DE RESULTADOS

```python
def ejecutar_y_enriquecer(sql_query, interpretacion):
    """
    PASO 9: Ejecutar SQL y enriquecer resultados
    """
    # 9.1 Ejecutar consulta
    resultados = ejecutar_sql(sql_query)
    
    # 9.2 Si no hay resultados y hay sugerencias
    if len(resultados) == 0 and interpretacion.get("sugerencias"):
        # Ejecutar búsqueda con productos sugeridos
        productos_sugeridos = interpretacion["sugerencias"]
        resultados = []
        for sugerido in productos_sugeridos:
            resultados.append({
                **sugerido,
                "es_sugerencia": True,
                "mensaje": f"No encontramos '{interpretacion['elemento_principal']['valor']}', pero te puede interesar:"
            })
    
    # 9.3 Enriquecer cada resultado
    for resultado in resultados:
        # Agregar información adicional
        resultado["disponibilidad"] = "En stock" if resultado["cantidad"] > 0 else "Agotado"
        resultado["es_oferta"] = resultado["precio"] < calcular_precio_promedio_categoria(resultado["id_categoria"]) * 0.8
        
        # Calcular score de relevancia
        resultado["relevancia"] = calcular_relevancia(resultado, interpretacion)
    
    # 9.4 Ordenar por relevancia si no hay orden específico
    if not interpretacion.get("ordenamiento"):
        resultados.sort(key=lambda x: x["relevancia"], reverse=True)
    
    return resultados
```

### PASO 10: CONSTRUCCIÓN DE RESPUESTA FINAL

```python
def construir_respuesta_final(entrada_original, correcciones, tokens, interpretacion, sql, resultados):
    """
    PASO 10: Construir JSON de respuesta completo
    """
    respuesta = {
        "success": True,
        "query": {
            "original": entrada_original,
            "corregida": " ".join([c["corregida"] for c in correcciones]) if correcciones else entrada_original,
            "correcciones_aplicadas": correcciones
        },
        "analisis": {
            "tokens_detectados": [
                {
                    "tipo": t["tipo"],
                    "valor": t["valor"],
                    "prioridad": t.get("prioridad", 99)
                } for t in tokens
            ],
            "interpretacion": interpretacion,
            "confianza": calcular_confianza_interpretacion(tokens, interpretacion)
        },
        "sql_generado": sql,
        "resultados": {
            "cantidad": len(resultados),
            "productos": resultados,
            "mensaje_usuario": generar_mensaje_usuario(interpretacion, resultados)
        },
        "metadata": {
            "tiempo_procesamiento_ms": 45,
            "version_analizador": "2.0",
            "fecha_proceso": "2024-01-20T10:15:30Z"
        }
    }
    
    # Ejemplo de mensaje usuario:
    # "Mostrando Coca-Cola Sin Azúcar por menos de $20, ordenado por precio más bajo primero"
    
    return respuesta
```

---

## 4. DIAGRAMAS DE FLUJO DETALLADOS

### 4.1 Flujo General del Sistema

```
[ENTRADA] "koka kola sin asucar barata menor a 20 pesos"
    |
    v
[VALIDACIÓN INICIAL]
    | - No vacío
    | - Longitud < 200
    | - Caracteres válidos
    v
[CORRECCIÓN ORTOGRÁFICA]
    | - koka → coca
    | - asucar → azucar
    v
[TOKENIZACIÓN CON AFD]
    | - Look-ahead 4 palabras
    | - Detecta "coca cola sin azucar"
    | - Clasifica tokens restantes
    v
[ANÁLISIS CONTEXTUAL]
    | - Combina "menor" + "a"
    | - Asocia "20" + "pesos"
    | - Interpreta "barata"
    v
[INTERPRETACIÓN SEMÁNTICA]
    | - Producto principal
    | - Filtros de precio
    | - Ordenamiento implícito
    v
[VALIDACIÓN Y AMBIGÜEDADES]
    | - Verifica existencia
    | - Busca similares si no existe
    v
[GENERACIÓN SQL]
    | - SELECT con JOINs
    | - WHERE con filtros
    | - ORDER BY precio
    v
[EJECUCIÓN Y ENRIQUECIMIENTO]
    | - Ejecuta query
    | - Agrega metadata
    | - Calcula relevancia
    v
[RESPUESTA JSON]
```

### 4.2 Detalle del AFD para Tokenización

```
Estado: q0 (inicial)
  |
  | Lee 'c'
  v
Estado: q1
  |
  | Lee 'o'
  v
Estado: q2
  |
  | Lee 'c'
  v
Estado: q3
  |
  | Lee 'a'
  v
Estado: q4
  |
  | Lee ' ' (espacio)
  v
Estado: q5
  |
  | Lee 'c'
  v
Estado: q6
  |
  | Lee 'o'
  v
Estado: q7
  |
  | Lee 'l'
  v
Estado: q8
  |
  | Lee 'a'
  v
Estado: q9 (ACEPTA: PRODUCTO_MULTIPALABRA)
  |
  | Verifica contexto: ¿sigue "sin azucar"?
  | SÍ → Continúa
  v
Estado: q10
  |
  | Lee ' sin azucar'
  v
Estado: q13 (ACEPTA: PRODUCTO_COMPLETO - Mayor prioridad)
```

---

## 5. MANEJO DE CASOS ESPECIALES

### 5.1 Productos No Existentes

Cuando se busca "cheetos picantes" (producto que no existe):

```python
# Flujo especial:
1. Tokenización detecta: ["cheetos", "picantes"]
2. Clasificación: 
   - "cheetos" → PRODUCTO_NO_RECONOCIDO
   - "picantes" → ATRIBUTO_SABOR

3. Búsqueda en ProductosSimilares:
   SQL: SELECT * FROM ProductosSimilares WHERE producto_solicitado_texto = 'cheetos'
   Resultado: Sugiere "Doritos" con score 0.85

4. Interpretación alternativa:
   - Inferir categoría: "snacks" (por similitud)
   - Aplicar filtro: sabor = "picante"

5. SQL generado:
   SELECT * FROM Productos p
   WHERE p.id_categoria = 2 
   AND (p.nombre LIKE '%picante%' OR p.descripcion LIKE '%picante%')
   ORDER BY 
     CASE WHEN p.id_producto = 2 THEN 0 ELSE 1 END,  -- Doritos primero
     p.nombre
```

### 5.2 Queries Ambiguas

Para "manzana" (¿producto o categoría?):

```python
# Estrategia de desambiguación:
1. Buscar coincidencia exacta en productos
   SQL: SELECT * FROM Productos WHERE nombre = 'Manzana'
   
2. Si existe → Es producto
   Si no existe → Buscar en categorías relacionadas
   
3. Aplicar scoring:
   - Coincidencia exacta producto: 1.0
   - Producto parcial: 0.8
   - Categoría relacionada: 0.6
   
4. Tomar la de mayor score
```

---

## 6. MÉTRICAS Y LOGGING

### 6.1 Información Registrada en Cada Paso

```json
{
  "request_id": "req_12345",
  "timestamp": "2024-01-20T10:15:30Z",
  "pasos": {
    "validacion": {
      "duracion_ms": 1,
      "resultado": "ok"
    },
    "correccion": {
      "duracion_ms": 5,
      "correcciones": 2,
      "palabras_corregidas": ["koka", "asucar"]
    },
    "tokenizacion": {
      "duracion_ms": 12,
      "tokens_generados": 6,
      "producto_detectado": "PRODUCTO_COMPLETO"
    },
    "analisis_contextual": {
      "duracion_ms": 3,
      "reglas_aplicadas": ["combinar_operador", "asociar_precio"]
    },
    "interpretacion": {
      "duracion_ms": 8,
      "tipo": "busqueda_producto_con_filtros",
      "confianza": 0.92
    },
    "generacion_sql": {
      "duracion_ms": 2,
      "complejidad": "media"
    },
    "ejecucion": {
      "duracion_ms": 15,
      "resultados": 1
    }
  },
  "total_ms": 46
}
```

---

## 7. CONCLUSIÓN

Este documento detalla cada operación que realiza el sistema LCLN:

1. **Validación**: Protege contra entradas maliciosas
2. **Corrección**: Maneja errores ortográficos comunes
3. **Tokenización**: Usa AFD con look-ahead para máxima precisión
4. **Análisis contextual**: Refina tokens según su contexto
5. **Interpretación**: Construye significado semántico
6. **Validación**: Resuelve ambigüedades
7. **SQL**: Genera consultas optimizadas
8. **Ejecución**: Enriquece resultados
9. **Respuesta**: Estructura JSON completa

El sistema es robusto, maneja casos edge y proporciona sugerencias inteligentes cuando no encuentra coincidencias exactas.