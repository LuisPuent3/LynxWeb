-- SINÓNIMOS SEMÁNTICOS AVANZADOS PARA SISTEMA LCLN
-- Mejora el reconocimiento de consultas complejas como "bebidas sin azúcar"
-- Fecha: 2025-07-22

-- 1. SINÓNIMOS PARA BEBIDAS SIN AZÚCAR (incluyendo aguas)
INSERT INTO productos_sinonimos (producto_id, sinonimo, popularidad, activo, precision_score, fuente) VALUES

-- Para agua natural/purificada
(25, 'agua sin azucar', 95, 1, 0.95, 'semantic_advanced'),  -- Agua
(25, 'bebida sin azucar', 90, 1, 0.90, 'semantic_advanced'),
(25, 'hidratacion natural', 85, 1, 0.85, 'semantic_advanced'),
(25, 'liquido natural', 80, 1, 0.80, 'semantic_advanced'),

-- Para Coca-Cola Sin Azúcar
(1, 'cola sin azucar', 95, 1, 0.95, 'semantic_advanced'),  -- Si existe Coca sin azúcar
(1, 'refresco sin azucar', 90, 1, 0.90, 'semantic_advanced'),
(1, 'bebida zero', 85, 1, 0.85, 'semantic_advanced'),

-- Para bebidas en general
(18, 'te sin azucar', 90, 1, 0.90, 'semantic_advanced'),    -- Té verde si existe
(24, 'agua saborizada natural', 85, 1, 0.85, 'semantic_advanced'),

-- 2. SINÓNIMOS CONCEPTUALES AMPLIADOS
-- Categoría Bebidas
(1, 'liquido', 70, 1, 0.70, 'semantic_category'),
(18, 'infusion', 75, 1, 0.75, 'semantic_category'),
(24, 'hidratante', 70, 1, 0.70, 'semantic_category'),

-- Categoría Frutas (expansión semántica)
(7, 'citrico natural', 80, 1, 0.80, 'semantic_advanced'),   -- Limón
(7, 'fruta acida', 75, 1, 0.75, 'semantic_advanced'),
(8, 'tropical', 85, 1, 0.85, 'semantic_advanced'),          -- Mango
(8, 'fruta dulce natural', 80, 1, 0.80, 'semantic_advanced'),

-- 3. SINÓNIMOS PARA ATRIBUTOS COMPLEJOS
-- "Sin azúcar" y variantes
(1, 'zero calorias', 85, 1, 0.85, 'semantic_attribute'),
(25, 'natural puro', 90, 1, 0.90, 'semantic_attribute'),
(18, 'sin endulzante', 80, 1, 0.80, 'semantic_attribute'),

-- "Económico/Barato" semántico
(2, 'precio accesible', 75, 1, 0.75, 'semantic_price'),     -- Producto económico
(3, 'oferta', 80, 1, 0.80, 'semantic_price'),
(4, 'promocion', 75, 1, 0.75, 'semantic_price'),

-- 4. SINÓNIMOS CONTEXTUALES (según contexto de uso)
-- Para consultas coloquiales
(1, 'chesco sin azucar', 85, 1, 0.85, 'semantic_colloquial'),
(25, 'agüita', 70, 1, 0.70, 'semantic_colloquial'),
(7, 'limonada natural', 80, 1, 0.80, 'semantic_colloquial'),

-- Para consultas formales
(1, 'refresco dietético', 85, 1, 0.85, 'semantic_formal'),
(25, 'agua embotellada', 90, 1, 0.90, 'semantic_formal'),
(18, 'bebida caliente natural', 80, 1, 0.80, 'semantic_formal'),

-- 5. SINÓNIMOS DE EXPANSIÓN INTELIGENTE
-- Cuando buscan "bebidas sin azúcar" debe incluir:
(25, 'opcion saludable', 85, 1, 0.85, 'semantic_health'),    -- Agua
(18, 'bebida natural', 90, 1, 0.90, 'semantic_health'),      -- Té
(7, 'vitamina natural', 80, 1, 0.80, 'semantic_health'),     -- Frutas

-- 6. SINÓNIMOS SEMÁNTICOS POR NECESIDADES
-- Para hidratación
(25, 'hidratacion', 95, 1, 0.95, 'semantic_need'),
(24, 'refrescante natural', 85, 1, 0.85, 'semantic_need'),

-- Para energía natural
(8, 'energia natural', 80, 1, 0.80, 'semantic_energy'),      -- Frutas
(18, 'estimulante natural', 75, 1, 0.75, 'semantic_energy'), -- Té

-- Para dieta/salud
(1, 'apto dieta', 90, 1, 0.90, 'semantic_diet'),
(25, 'cero azucar', 95, 1, 0.95, 'semantic_diet'),
(18, 'sin calorias', 85, 1, 0.85, 'semantic_diet');

-- 7. ACTUALIZACIÓN DE PRECISIÓN PARA SINÓNIMOS EXISTENTES
-- Mejorar la precisión de sinónimos que pueden causar confusión
UPDATE productos_sinonimos 
SET precision_score = 0.95, popularidad = 90
WHERE sinonimo IN ('agua', 'cola', 'limon', 'te') AND activo = 1;

-- 8. CREAR VISTA PARA CONSULTAS SEMÁNTICAS AVANZADAS
CREATE OR REPLACE VIEW vista_busqueda_semantica AS
SELECT 
    p.id_producto,
    p.nombre,
    p.precio,
    p.categoria as id_categoria,
    c.nombre as categoria_nombre,
    ps.sinonimo,
    ps.fuente as tipo_semantico,
    ps.precision_score,
    ps.popularidad
FROM productos p
JOIN categorias c ON p.categoria = c.id_categoria
LEFT JOIN productos_sinonimos ps ON p.id_producto = ps.producto_id
WHERE p.cantidad > 0 AND (ps.activo = 1 OR ps.activo IS NULL)
ORDER BY ps.precision_score DESC, ps.popularidad DESC;

-- 9. ÍNDICES PARA OPTIMIZAR BÚSQUEDAS SEMÁNTICAS
CREATE INDEX IF NOT EXISTS idx_sinonimos_semanticos 
ON productos_sinonimos (sinonimo, fuente, precision_score, activo);

CREATE INDEX IF NOT EXISTS idx_productos_categoria_precio 
ON productos (categoria, precio, cantidad);

-- 10. ESTADÍSTICAS FINALES
SELECT 
    COUNT(*) as total_sinonimos_semanticos,
    COUNT(DISTINCT producto_id) as productos_con_sinonimos,
    AVG(precision_score) as precision_promedio
FROM productos_sinonimos 
WHERE fuente LIKE 'semantic%' AND activo = 1;