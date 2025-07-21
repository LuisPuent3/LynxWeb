CASOS DE USO PARA PROBAR EL SISTEMA LCLN
1. CASOS BÁSICOS - Búsqueda Exacta
CASO 1.1: Producto específico existe
Entrada: "coca cola 600ml"
Resultado esperado:
- Token: PRODUCTO_SIMPLE
- Encuentra: Coca-Cola 600ml
- SQL: SELECT * FROM Productos WHERE nombre = 'Coca-Cola 600ml'

CASO 1.2: Categoría directa
Entrada: "bebidas"
Resultado esperado:
- Token: CATEGORIA
- Lista todos los productos de bebidas
- SQL: SELECT * FROM Productos WHERE id_categoria = 1

CASO 1.3: Búsqueda con precio
Entrada: "doritos menor a 25 pesos"
Resultado esperado:
- Tokens: PRODUCTO_SIMPLE + OP_MENOR + NUMERO + UNIDAD_MONEDA
- Encuentra: Doritos Nacho 62g ($20.00)
- SQL: SELECT * FROM Productos WHERE nombre LIKE '%Doritos%' AND precio < 25
2. CASOS CON ERRORES ORTOGRÁFICOS
CASO 2.1: Error simple
Entrada: "koka kola"
Proceso:
- Corrección: "koka" → "coca" (tabla CorreccionesOrtograficas)
- Búsqueda: "coca cola"
- Resultado: Lista todas las Coca-Colas

CASO 2.2: Múltiples errores
Entrada: "dortios nachos baratos"
Proceso:
- Corrección: "dortios" → "doritos"
- Interpretación: "baratos" → precio_bajo
- Resultado: Doritos ordenados por precio ascendente

CASO 2.3: Error fonético regional
Entrada: "chescos frios"
Proceso:
- Corrección: "chescos" → "refrescos" (regional)
- Mapeo: "refrescos" → categoría bebidas
- Resultado: Todas las bebidas
3. CASOS CON SINÓNIMOS
CASO 3.1: Sinónimo de producto
Entrada: "refresco de cola"
Proceso:
- Búsqueda en SinonimosProductos
- Mapeo: "refresco de cola" → "coca-cola"
- Resultado: Productos Coca-Cola

CASO 3.2: Término genérico
Entrada: "botana para la tarde"
Proceso:
- Mapeo: "botana" → categoría snacks
- Ignorar: "para la tarde" (palabras no relevantes)
- Resultado: Todos los snacks

CASO 3.3: Atributo sinónimo
Entrada: "papitas baratas"
Proceso:
- "papitas" → categoría snacks
- "baratas" → precio_bajo
- SQL: SELECT * FROM Productos WHERE id_categoria = 2 ORDER BY precio ASC
4. CASOS DE PRODUCTOS NO EXISTENTES
CASO 4.1: Producto similar existe
Entrada: "cheetos flamin hot"
Proceso:
- Búsqueda exacta: No encuentra
- Búsqueda en ProductosSimilares
- Sugerencia: Doritos (score: 0.85)
Mensaje: "No tenemos Cheetos, pero te puede interesar Doritos"

CASO 4.2: Marca no existente
Entrada: "takis fuego"
Proceso:
- "takis" no existe
- Busca en ProductosSimilares
- Sugiere: Doritos Incógnita (snacks picantes)

CASO 4.3: Categoría inferida
Entrada: "galletas oreo"
Proceso:
- "oreo" no existe
- "galletas" → mapeo a categoría snacks
- Muestra: Todos los snacks tipo galleta
5. CASOS COMPLEJOS - Múltiples Filtros
CASO 5.1: Categoría + precio + atributo
Entrada: "bebidas sin azucar menor a 20 pesos"
Proceso:
- "bebidas" → CATEGORIA
- "sin azucar" → NEGACION + ATRIBUTO
- "menor a 20 pesos" → OP_MENOR + NUMERO + UNIDAD
SQL: SELECT * FROM Productos 
     WHERE id_categoria = 1 
     AND nombre LIKE '%Sin Azúcar%' 
     AND precio < 20

CASO 5.2: Rango de precios
Entrada: "snacks entre 15 y 25 pesos"
Proceso:
- "snacks" → CATEGORIA
- "entre 15 y 25 pesos" → OP_ENTRE + rango
SQL: SELECT * FROM Productos 
     WHERE id_categoria = 2 
     AND precio BETWEEN 15 AND 25

CASO 5.3: Múltiples productos
Entrada: "coca cola y doritos"
Proceso:
- Detecta operador Y
- Busca ambos productos
- Retorna lista combinada
6. CASOS DE AMBIGÜEDAD
CASO 6.1: Producto vs Categoría
Entrada: "manzana"
Ambigüedad:
- ¿Producto "Manzana"?
- ¿Categoría "Frutas"?
Resolución: Prioridad a producto exacto

CASO 6.2: Atributo ambiguo
Entrada: "coca sin azucar fria"
Ambigüedad:
- ¿"Coca-Cola Sin Azúcar" (producto)?
- ¿Cualquier Coca-Cola sin azúcar?
Resolución: Prioridad a producto completo

CASO 6.3: Modificador sin contexto
Entrada: "barato"
Proceso:
- Sin producto → buscar todos ordenados por precio
- Mensaje: "Mostrando todos los productos ordenados por precio"
7. CASOS DE QUERIES EN LENGUAJE NATURAL
CASO 7.1: Pregunta completa
Entrada: "qué bebidas tienes por menos de 15 pesos"
Proceso:
- Ignorar: "qué", "tienes", "por"
- Extraer: "bebidas" + "menos de 15 pesos"
- Resultado: Bebidas < $15

CASO 7.2: Jerga estudiantil
Entrada: "algo para la sed bien helado"
Proceso:
- "algo para la sed" → inferir bebidas
- "bien helado" → atributo (ignorado si no hay info de temperatura)
- Resultado: Categoría bebidas

CASO 7.3: Búsqueda por uso
Entrada: "para el lonche"
Proceso:
- "lonche" → término regional para almuerzo
- Inferir: snacks + bebidas + frutas
- Resultado: Productos de esas categorías
8. CASOS DE PRUEBA SQL DIRECTOS
sql-- Probar sinónimos
SELECT p.* FROM Productos p
JOIN SinonimosProductos sp ON p.nombre LIKE CONCAT('%', sp.producto_real, '%')
WHERE sp.termino = 'refresco de cola';

-- Probar correcciones
SELECT termino_correcto FROM CorreccionesOrtograficas 
WHERE termino_incorrecto = 'koka';

-- Probar productos similares
SELECT p.*, ps.score_similitud, ps.razon_similitud
FROM ProductosSimilares ps
JOIN Productos p ON ps.id_producto_sugerido = p.id_producto
WHERE ps.producto_solicitado_texto = 'cheetos';

-- Probar mapeo de categorías
SELECT p.* FROM Productos p
JOIN Categorias c ON p.id_categoria = c.id_categoria
JOIN MapeoCategoriasGenericas mcg ON mcg.id_categoria = c.id_categoria
WHERE mcg.termino_generico = 'botana';
9. CASOS DE RENDIMIENTO
CASO 9.1: Query simple
Entrada: "coca cola"
Tiempo esperado: < 50ms

CASO 9.2: Query con corrección
Entrada: "koka kola sin asucar barata"
Tiempo esperado: < 100ms

CASO 9.3: Query compleja
Entrada: "bebidas y snacks entre 10 y 30 pesos sin azucar"
Tiempo esperado: < 150ms
10. CASOS DE EDGE (LÍMITE)
CASO 10.1: Query vacía
Entrada: ""
Resultado: Error - "Por favor ingresa un término de búsqueda"

CASO 10.2: Solo números
Entrada: "20"
Resultado: Buscar productos con precio cerca de $20

CASO 10.3: Caracteres especiales
Entrada: "coca-cola!!!"
Proceso: Limpiar caracteres especiales
Resultado: Buscar "coca-cola"

CASO 10.4: Query muy larga
Entrada: "quiero comprar coca cola doritos sabritas jumex boing y todo lo que tengas barato"
Proceso: Extraer términos relevantes
Límite: Máximo 5 productos por búsquedafijate en los casos de uso que esta en casos uso