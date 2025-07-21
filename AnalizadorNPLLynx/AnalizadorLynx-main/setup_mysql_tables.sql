-- ================================================
-- SETUP TABLAS MYSQL PARA SISTEMA LCLN MEJORADO
-- Base de datos: lynxshop
-- Fecha: Julio 2025
-- ================================================

USE lynxshop;

-- ================================================
-- 1. TABLA DE SINÓNIMOS ESPECÍFICOS POR PRODUCTO
-- ================================================
CREATE TABLE IF NOT EXISTS producto_sinonimos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    sinonimo VARCHAR(255) NOT NULL COLLATE utf8mb4_general_ci,
    popularidad INT DEFAULT 0,
    precision_score DECIMAL(3,2) DEFAULT 1.00,
    creado_por VARCHAR(50) DEFAULT 'admin',
    fuente ENUM('admin', 'auto_learning', 'user_feedback') DEFAULT 'admin',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    
    UNIQUE KEY unique_producto_sinonimo (producto_id, sinonimo),
    INDEX idx_sinonimo_activo (sinonimo, activo),
    INDEX idx_producto_activo (producto_id, activo),
    INDEX idx_popularidad (popularidad DESC),
    FULLTEXT idx_sinonimo_fulltext (sinonimo)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ================================================
-- 2. TABLA DE ATRIBUTOS DE PRODUCTOS
-- ================================================
CREATE TABLE IF NOT EXISTS producto_atributos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    atributo VARCHAR(100) NOT NULL,
    valor BOOLEAN DEFAULT TRUE,
    intensidad TINYINT DEFAULT 5 CHECK (intensidad BETWEEN 1 AND 10),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    
    UNIQUE KEY unique_producto_atributo (producto_id, atributo),
    INDEX idx_atributo_valor (atributo, valor)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ================================================
-- 3. TABLA DE MÉTRICAS PARA APRENDIZAJE AUTOMÁTICO
-- ================================================
CREATE TABLE IF NOT EXISTS busqueda_metricas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    termino_busqueda VARCHAR(255) NOT NULL,
    producto_id INT,
    clicks INT DEFAULT 0,
    tiempo_en_pagina INT DEFAULT 0,
    conversiones INT DEFAULT 0,
    rating_utilidad TINYINT CHECK (rating_utilidad BETWEEN 1 AND 5),
    fecha_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    
    INDEX idx_termino_fecha (termino_busqueda, fecha_busqueda),
    INDEX idx_producto_metricas (producto_id, conversiones DESC, clicks DESC),
    INDEX idx_fecha_session (fecha_busqueda, session_id)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ================================================
-- 4. POBLAR DATOS INICIALES CRÍTICOS
-- ================================================

-- ================================================
-- 4.1 SINÓNIMOS MÁS COMUNES (BASADOS EN ANÁLISIS REAL)
-- ================================================

-- Primero verificar que los productos existen y obtener sus IDs reales
-- Nota: Los IDs pueden variar según la BD real

INSERT IGNORE INTO producto_sinonimos (producto_id, sinonimo, popularidad, fuente) VALUES
-- BEBIDAS (verificar IDs reales en tu BD)
-- Coca Cola Normal
(2, 'coca', 25, 'admin'),
(2, 'coca-cola', 30, 'admin'),
(2, 'coka', 12, 'admin'),
(2, 'cocacola', 18, 'admin'),

-- Coca Cola Sin Azúcar
(3, 'coca zero', 22, 'admin'),
(3, 'coca sin azucar', 28, 'admin'),
(3, 'coca light', 15, 'admin'),
(3, 'coca diet', 8, 'admin'),

-- Agua
(4, 'agua natural', 10, 'admin'),
(4, 'agua pura', 8, 'admin'),

-- SNACKS POPULARES
-- Doritos (ID aproximado 8)
(8, 'doritos', 35, 'admin'),
(8, 'dorito', 20, 'admin'),
(8, 'doritos dinamita', 15, 'admin'),

-- Cheetos/Crujitos (verificar ID real)
(20, 'cheetos', 30, 'admin'),
(20, 'chettos', 25, 'admin'),
(20, 'crujitos', 20, 'admin'),
(20, 'cheetos fuego', 18, 'admin'),

-- Cheetos Mix (si existe)
(15, 'cheetos mix', 15, 'admin'),
(15, 'chettos mix', 12, 'admin'),
(15, 'mix cheetos', 8, 'admin'),

-- TÉRMINOS GENÉRICOS IMPORTANTES
-- Botanas/Snacks
(8, 'botana', 40, 'admin'),
(20, 'botana', 35, 'admin'),
(8, 'snack', 25, 'admin'),
(20, 'snack', 22, 'admin'),

-- Refrescos/Bebidas
(2, 'refresco', 20, 'admin'),
(3, 'refresco', 15, 'admin'),
(2, 'bebida', 18, 'admin'),
(3, 'bebida', 16, 'admin');

-- ================================================
-- 4.2 ATRIBUTOS CRÍTICOS PARA NEGACIONES
-- ================================================

INSERT IGNORE INTO producto_atributos (producto_id, atributo, valor, intensidad) VALUES
-- BEBIDAS - Atributo Azúcar
(2, 'azucar', TRUE, 8),      -- Coca Cola Normal - CON azúcar
(3, 'azucar', FALSE, 0),     -- Coca Cola Sin Azúcar - SIN azúcar
(4, 'azucar', FALSE, 0),     -- Agua - SIN azúcar

-- SNACKS - Atributo Picante
(8, 'picante', TRUE, 9),     -- Doritos Dinamita - MUY picante
(20, 'picante', TRUE, 7),    -- Crujitos Fuego - Picante
(15, 'picante', TRUE, 6),    -- Cheetos Mix - Moderadamente picante

-- Productos NO picantes (ejemplos)
(21, 'picante', FALSE, 0),   -- Galletas - NO picante
(22, 'picante', FALSE, 0),   -- Pan - NO picante
(23, 'picante', FALSE, 0),   -- Frutas - NO picante

-- ATRIBUTOS ADICIONALES ÚTILES
-- Sal
(8, 'sal', TRUE, 7),         -- Doritos - CON sal
(20, 'sal', TRUE, 6),        -- Crujitos - CON sal
(4, 'sal', FALSE, 0),        -- Agua - SIN sal

-- Grasa
(8, 'grasa', TRUE, 6),       -- Snacks fritos - CON grasa
(20, 'grasa', TRUE, 6),      -- Snacks fritos - CON grasa
(4, 'grasa', FALSE, 0),      -- Agua - SIN grasa

-- Gluten
(21, 'gluten', TRUE, 5),     -- Galletas - CON gluten
(22, 'gluten', TRUE, 8),     -- Pan - CON gluten
(4, 'gluten', FALSE, 0);     -- Agua - SIN gluten

-- ================================================
-- 5. ÍNDICES DE RENDIMIENTO ADICIONALES
-- ================================================

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_sinonimos_busqueda ON producto_sinonimos (sinonimo, activo, popularidad DESC);
CREATE INDEX IF NOT EXISTS idx_productos_categoria_precio ON productos (id_categoria, precio ASC, activo);
CREATE INDEX IF NOT EXISTS idx_atributos_busqueda ON producto_atributos (atributo, valor, producto_id);

-- Índice de texto completo si no existe
-- ALTER TABLE productos ADD FULLTEXT(nombre, descripcion);

-- ================================================
-- 6. VERIFICACIÓN Y ESTADÍSTICAS
-- ================================================

-- Verificar que las tablas se crearon correctamente
SHOW TABLES LIKE '%sinonimo%';
SHOW TABLES LIKE '%atributo%';
SHOW TABLES LIKE '%metrica%';

-- Estadísticas rápidas
SELECT 
    'producto_sinonimos' as tabla,
    COUNT(*) as total_registros,
    COUNT(DISTINCT producto_id) as productos_con_sinonimos
FROM producto_sinonimos 
WHERE activo = 1
UNION ALL
SELECT 
    'producto_atributos' as tabla,
    COUNT(*) as total_registros,
    COUNT(DISTINCT producto_id) as productos_con_atributos
FROM producto_atributos;

-- Ver sinónimos más populares
SELECT 
    p.nombre as producto,
    ps.sinonimo,
    ps.popularidad
FROM producto_sinonimos ps
JOIN productos p ON ps.producto_id = p.id_producto
WHERE ps.activo = 1
ORDER BY ps.popularidad DESC
LIMIT 20;

-- Ver productos con más sinónimos
SELECT 
    p.nombre as producto,
    COUNT(ps.sinonimo) as total_sinonimos,
    GROUP_CONCAT(ps.sinonimo ORDER BY ps.popularidad DESC) as sinonimos
FROM productos p
LEFT JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id AND ps.activo = 1
WHERE p.activo = 1
GROUP BY p.id_producto, p.nombre
HAVING total_sinonimos > 0
ORDER BY total_sinonimos DESC;

-- ================================================
-- SETUP COMPLETO - TABLAS LISTAS PARA USAR
-- ================================================

/*
NOTAS IMPORTANTES:

1. VERIFICAR IDs DE PRODUCTOS:
   Los IDs usados (2, 3, 4, 8, 15, 20, etc.) son aproximados.
   Ejecutar antes: SELECT * FROM productos ORDER BY id_producto;
   Ajustar los IDs según tu BD real.

2. PERSONALIZACIÓN:
   - Agregar más sinónimos según patrones de búsqueda reales
   - Ajustar valores de popularidad basados en analytics
   - Configurar atributos específicos por categoría

3. MANTENIMIENTO:
   - Revisar sinónimos periódicamente
   - Actualizar popularidad basada en métricas
   - Limpiar sinónimos obsoletos

4. SEGURIDAD:
   - Los sinónimos se almacenan en lowercase
   - UNIQUE constraint previene duplicados
   - Foreign keys mantienen integridad referencial

PRÓXIMOS PASOS:
1. Ejecutar este SQL en tu BD lynxshop
2. Verificar que se crearon las tablas
3. Ajustar IDs de productos según tu BD real
4. Continuar con implementación del motor mejorado
*/