-- ========================================
-- AGREGAR SINÓNIMOS INTELIGENTES - VERSIÓN SIMPLE
-- ========================================

USE lynxshop;

-- Insertar sinónimos uno por uno, ignorando duplicados
INSERT IGNORE INTO producto_sinonimos (producto_id, sinonimo, popularidad, fuente) VALUES
-- BEBIDAS PRINCIPALES
(1, 'refresco', 25, 'admin'),
(1, 'cola', 20, 'admin'),
(1, 'bebida', 15, 'admin'),
(17, 'coca sin azucar', 20, 'admin'),
(17, 'coca zero', 18, 'admin'),
(18, 'sprite', 25, 'admin'),
(18, 'limon soda', 15, 'admin'),

-- AGUA
(13, 'agua', 30, 'admin'),
(13, 'aguita', 15, 'admin'),
(14, 'agua natural', 25, 'admin'),

-- FRUTAS PRINCIPALES
(38, 'manzana', 30, 'admin'),
(38, 'mansana', 15, 'admin'),
(48, 'manzana golden', 20, 'admin'),
(41, 'platano', 25, 'admin'),
(41, 'banana', 18, 'admin'),
(47, 'limon', 25, 'admin'),
(43, 'mango', 30, 'admin'),

-- SNACKS PRINCIPALES
(23, 'papitas queso', 20, 'admin'),
(23, 'botana queso', 15, 'admin'),
(8, 'tortillas', 15, 'admin'),
(8, 'nachos', 20, 'admin'),
(24, 'galletas', 25, 'admin'),
(24, 'cookies', 15, 'admin'),

-- TÉRMINOS GENÉRICOS
(23, 'botana', 25, 'admin'),
(23, 'snack', 22, 'admin'),
(23, 'papitas', 28, 'admin'),
(38, 'fruta', 18, 'admin'),
(33, 'dulce', 20, 'admin'),

-- GOLOSINAS
(33, 'mazapan', 25, 'admin'),
(32, 'paleta', 20, 'admin'),
(34, 'pelon', 25, 'admin'),
(31, 'gomitas', 25, 'admin'),
(30, 'chicle', 25, 'admin'),

-- PAPELERÍA
(50, 'pluma', 25, 'admin'),
(50, 'lapicero', 22, 'admin'),
(54, 'resaltador', 20, 'admin'),
(58, 'libreta', 20, 'admin');

-- Ver resultados
SELECT 'Total sinónimos después de la inserción:' as mensaje, COUNT(*) as total 
FROM producto_sinonimos WHERE activo = 1;