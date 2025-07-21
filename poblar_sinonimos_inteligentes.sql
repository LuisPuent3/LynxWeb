-- ========================================
-- SCRIPT DE SINÓNIMOS INTELIGENTES PARA LCLN
-- Basado en comportamiento real de usuarios
-- ========================================

USE lynxshop;

-- Limpiar sinónimos si ya existen (los voy a re-crear)
-- No eliminamos nada por ahora, solo agregamos

-- ========================================
-- BEBIDAS - Pensando como buscaría un usuario real
-- ========================================

-- COCA-COLA (ID: 1 y 17)
INSERT INTO producto_sinonimos (producto_id, sinonimo, popularidad, fuente) VALUES
-- Coca-Cola normal
(1, 'coca', 25, 'admin'),
(1, 'coka', 15, 'admin'),
(1, 'coca cola', 20, 'admin'),
(1, 'coque', 8, 'admin'),
(1, 'refresco de cola', 12, 'admin'),
(1, 'cola', 18, 'admin'),
(1, 'coke', 10, 'admin'),
(1, 'bebida de cola', 8, 'admin'),

-- Coca-Cola sin azúcar
(17, 'coca sin azucar', 20, 'admin'),
(17, 'coca light', 15, 'admin'),
(17, 'coca diet', 12, 'admin'),
(17, 'coca zero', 18, 'admin'),
(17, 'refresco sin azucar', 10, 'admin'),
(17, 'cola sin azucar', 14, 'admin'),

-- SPRITE (ID: 18)
(18, 'sprite', 20, 'admin'),
(18, 'esprite', 8, 'admin'),
(18, 'refresco de limon', 15, 'admin'),
(18, 'limon soda', 12, 'admin'),
(18, 'refresco limon', 14, 'admin'),
(18, 'soda limon', 10, 'admin'),

-- AGUA (ID: 13, 14)
(13, 'agua', 30, 'admin'),
(13, 'aguita', 15, 'admin'),
(13, 'agua mineral', 25, 'admin'),
(13, 'hidratante', 8, 'admin'),
(14, 'agua', 28, 'admin'),
(14, 'agua natural', 25, 'admin'),
(14, 'aguita natural', 12, 'admin'),

-- BOING MANGO (ID: 16)
(16, 'boing', 18, 'admin'),
(16, 'jugo de mango', 20, 'admin'),
(16, 'jugo mango', 22, 'admin'),
(16, 'bebida de mango', 12, 'admin'),
(16, 'mango drink', 8, 'admin'),

-- LIMONADA (ID: 7)
(7, 'limonada', 20, 'admin'),
(7, 'jugo de limon', 18, 'admin'),
(7, 'agua de limon', 15, 'admin'),
(7, 'limon agua', 12, 'admin'),

-- NARANJADA (ID: 12)
(12, 'naranjada', 18, 'admin'),
(12, 'jugo de naranja', 22, 'admin'),
(12, 'jugo naranja', 20, 'admin'),
(12, 'agua de naranja', 15, 'admin'),
(12, 'bebida naranja', 12, 'admin'),

-- POWERADE (ID: 19)
(19, 'powerade', 15, 'admin'),
(19, 'bebida deportiva', 18, 'admin'),
(19, 'hidratante deportivo', 12, 'admin'),
(19, 'isotonica', 10, 'admin'),
(19, 'energizante', 8, 'admin'),

-- RED BULL (ID: 11)
(11, 'red bull', 20, 'admin'),
(11, 'redbull', 18, 'admin'),
(11, 'energetico', 25, 'admin'),
(11, 'bebida energetica', 22, 'admin'),
(11, 'energy drink', 15, 'admin'),
(11, 'estimulante', 8, 'admin'),

-- TÉ NEGRO (ID: 15)
(15, 'te negro', 15, 'admin'),
(15, 'te', 20, 'admin'),
(15, 'te limon', 18, 'admin'),
(15, 'bebida de te', 12, 'admin'),

-- ========================================
-- FRUTAS - Como las buscaría naturalmente
-- ========================================

-- MANZANAS (ID: 38, 48)
(38, 'manzana', 30, 'admin'),
(38, 'mansana', 15, 'admin'),  -- Error común
(38, 'manzana roja', 25, 'admin'),
(38, 'fruta roja', 12, 'admin'),
(48, 'manzana', 28, 'admin'),
(48, 'manzana golden', 20, 'admin'),
(48, 'manzana amarilla', 15, 'admin'),
(48, 'mansana golden', 8, 'admin'),

-- PLÁTANO (ID: 41)
(41, 'platano', 25, 'admin'),
(41, 'banano', 20, 'admin'),
(41, 'banana', 18, 'admin'),
(41, 'guineo', 12, 'admin'),
(41, 'fruta amarilla', 10, 'admin'),

-- NARANJA - Podría buscarla así aunque no esté en lista
-- LIMÓN (ID: 47)
(47, 'limon', 25, 'admin'),
(47, 'limon verde', 20, 'admin'),
(47, 'lima', 15, 'admin'),
(47, 'citrico', 8, 'admin'),

-- MANGO (ID: 43)
(43, 'mango', 30, 'admin'),
(43, 'mango manila', 15, 'admin'),
(43, 'fruta tropical', 12, 'admin'),

-- DURAZNO (ID: 44)
(44, 'durazno', 25, 'admin'),
(44, 'melocoton', 15, 'admin'),
(44, 'fruta dulce', 10, 'admin'),

-- PERA (ID: 40)
(40, 'pera', 25, 'admin'),
(40, 'pera verde', 15, 'admin'),

-- OTRAS FRUTAS
(39, 'guayaba', 20, 'admin'),
(42, 'ciruela', 18, 'admin'),
(45, 'mamey', 15, 'admin'),
(46, 'mandarina', 20, 'admin'),
(46, 'tangerina', 12, 'admin'),

-- ========================================
-- SNACKS - Cómo buscaría botanas realmente
-- ========================================

-- CHEETOS (ID: 23)
(23, 'cheetos', 30, 'admin'),
(23, 'chettos', 25, 'admin'),  -- Ya existe pero reforzamos
(23, 'cheetos mix', 20, 'admin'),
(23, 'papitas de queso', 18, 'admin'),
(23, 'botanas de queso', 15, 'admin'),
(23, 'snack queso', 12, 'admin'),
(23, 'colitas', 10, 'admin'),

-- DORITOS (ID: 8)
(8, 'doritos', 35, 'admin'),
(8, 'dorito', 30, 'admin'),
(8, 'tortillas', 15, 'admin'),
(8, 'nachos', 20, 'admin'),
(8, 'papitas triangulares', 12, 'admin'),
(8, 'botanas picantes', 18, 'admin'),
(8, 'dinamita', 15, 'admin'),

-- CRUJITOS (ID: 20)
(20, 'crujitos', 25, 'admin'),
(20, 'crujitos fuego', 20, 'admin'),
(20, 'papitas picantes', 18, 'admin'),
(20, 'botanas fuego', 15, 'admin'),

-- FRITOS (ID: 21)
(21, 'fritos', 25, 'admin'),
(21, 'papitas sal limon', 20, 'admin'),
(21, 'fritos sal y limon', 22, 'admin'),
(21, 'botanas sal', 15, 'admin'),

-- OREO (ID: 24)
(24, 'oreo', 30, 'admin'),
(24, 'galletas oreo', 25, 'admin'),
(24, 'galletas chocolate', 20, 'admin'),
(24, 'galletas crema', 18, 'admin'),
(24, 'cookies', 15, 'admin'),

-- OTROS SNACKS
(25, 'emperador', 20, 'admin'),
(25, 'galletas emperador', 18, 'admin'),
(28, 'flor de naranjo', 15, 'admin'),
(28, 'cacahuates', 25, 'admin'),
(22, 'karate', 15, 'admin'),
(22, 'japones', 18, 'admin'),
(49, 'pastisetas', 15, 'admin'),
(49, 'galletas', 20, 'admin'),
(27, 'susalia', 12, 'admin'),
(27, 'flama', 15, 'admin'),

-- ========================================
-- GOLOSINAS - Dulces como los busco yo
-- ========================================

-- MAZAPÁN (ID: 33)
(33, 'mazapan', 25, 'admin'),
(33, 'dulce de cacahuate', 20, 'admin'),
(33, 'dulce mexicano', 18, 'admin'),

-- PALETAS (ID: 32, 35)
(32, 'rockaleta', 20, 'admin'),
(32, 'paleta rockaleta', 25, 'admin'),
(32, 'paleta picante', 18, 'admin'),
(35, 'paleton', 18, 'admin'),
(35, 'paleton bombon', 20, 'admin'),
(35, 'paleta chocolate', 15, 'admin'),

-- PELONES (ID: 34, 36)
(34, 'pelon', 25, 'admin'),
(34, 'pelon pelo rico', 22, 'admin'),
(34, 'dulce liquido', 15, 'admin'),
(36, 'pelon ricatira', 20, 'admin'),
(36, 'ricatira', 18, 'admin'),

-- OTROS DULCES
(26, 'b-ready', 15, 'admin'),
(26, 'nutella', 20, 'admin'),
(26, 'barrita nutella', 18, 'admin'),
(31, 'dulcigomas', 15, 'admin'),
(31, 'gomitas', 25, 'admin'),
(29, 'freskas', 12, 'admin'),
(29, 'caramelos', 20, 'admin'),
(37, 'panditas', 20, 'admin'),
(37, 'ositos gomita', 22, 'admin'),
(30, 'trident', 15, 'admin'),
(30, 'chicle', 25, 'admin'),

-- ========================================
-- PAPELERÍA - Artículos escolares
-- ========================================

-- BOLÍGRAFOS (ID: 50, 51)
(50, 'boligrafo', 20, 'admin'),
(50, 'pluma', 25, 'admin'),
(50, 'lapicero', 22, 'admin'),
(50, 'pen', 15, 'admin'),
(51, 'boligrafo rojo', 18, 'admin'),
(51, 'pluma roja', 20, 'admin'),

-- MARCADORES
(52, 'marcador', 20, 'admin'),
(52, 'marcador pizarron', 18, 'admin'),
(52, 'plumón', 15, 'admin'),
(54, 'marcatexto', 18, 'admin'),
(54, 'resaltador', 20, 'admin'),
(54, 'highlighter', 12, 'admin'),
(56, 'sharpie', 15, 'admin'),

-- CUADERNOS
(58, 'cuaderno', 25, 'admin'),
(58, 'libreta', 20, 'admin'),
(59, 'cuaderno rayado', 18, 'admin'),

-- BIC
(53, 'bic', 15, 'admin'),
(57, 'bic boligrafos', 12, 'admin'),
(55, 'boligrafos fashion', 10, 'admin'),

-- ========================================
-- SINÓNIMOS GENÉRICOS POR CATEGORÍA
-- ========================================

-- Para búsquedas genéricas que deberían mostrar toda la categoría
-- Estos los asociamos con productos representativos pero el sistema debe ampliar a toda la categoría

-- BEBIDAS GENÉRICAS
(1, 'bebida', 15, 'admin'),
(1, 'refresco', 20, 'admin'),
(1, 'drink', 8, 'admin'),

-- FRUTAS GENÉRICAS
(38, 'fruta', 18, 'admin'),
(38, 'frutas', 16, 'admin'),

-- SNACKS GENÉRICOS
(23, 'botana', 25, 'admin'),
(23, 'snack', 22, 'admin'),
(23, 'papitas', 28, 'admin'),

-- DULCES GENÉRICOS
(33, 'dulce', 20, 'admin'),
(33, 'dulces', 18, 'admin'),
(33, 'golosina', 15, 'admin'),

-- PAPELERÍA GENÉRICA
(50, 'escolar', 12, 'admin'),
(50, 'papeleria', 15, 'admin');

-- ========================================
-- VERIFICAR RESULTADOS
-- ========================================

-- Ver cuántos sinónimos hay por categoría
SELECT 
    c.nombre as categoria,
    COUNT(ps.id) as total_sinonimos
FROM producto_sinonimos ps
JOIN productos p ON ps.producto_id = p.id_producto
JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE ps.activo = 1
GROUP BY c.nombre
ORDER BY total_sinonimos DESC;

-- Ver productos con más sinónimos
SELECT 
    p.nombre as producto,
    COUNT(ps.id) as total_sinonimos,
    GROUP_CONCAT(ps.sinonimo SEPARATOR ', ') as ejemplos
FROM producto_sinonimos ps
JOIN productos p ON ps.producto_id = p.id_producto
WHERE ps.activo = 1
GROUP BY p.id_producto
ORDER BY total_sinonimos DESC
LIMIT 10;

SELECT CONCAT('✅ Total de sinónimos activos: ', COUNT(*)) as resultado
FROM producto_sinonimos 
WHERE activo = 1;