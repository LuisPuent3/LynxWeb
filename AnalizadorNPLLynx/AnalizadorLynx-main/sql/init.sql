-- init.sql
-- Script de inicialización para la base de datos LYNX

CREATE DATABASE IF NOT EXISTS lynx_products CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lynx_products;

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS Categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Insertar categorías básicas
INSERT INTO Categorias (nombre, descripcion) VALUES
('bebidas', 'Bebidas y refrescos'),
('snacks', 'Botanas y snacks'),
('lacteos', 'Productos lácteos'),
('frutas', 'Frutas frescas'),
('verduras', 'Verduras y hortalizas'),
('panaderia', 'Pan y productos de panadería'),
('carnes', 'Carnes y embutidos'),
('cereales', 'Cereales y granos'),
('condimentos', 'Especias y condimentos'),
('dulces', 'Dulces y confitería')
ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS Productos (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    id_categoria INT,
    precio DECIMAL(10,2) NOT NULL,
    contenido_ml INT DEFAULT NULL,
    contenido_gr INT DEFAULT NULL,
    marca VARCHAR(100),
    codigo_barras VARCHAR(50) UNIQUE,
    stock INT DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria),
    INDEX idx_nombre (nombre),
    INDEX idx_categoria (id_categoria),
    INDEX idx_precio (precio),
    INDEX idx_activo (activo)
) ENGINE=InnoDB;

-- Insertar productos de ejemplo
INSERT INTO Productos (nombre, descripcion, id_categoria, precio, contenido_ml, marca) VALUES
-- Bebidas
('Coca-Cola', 'Refresco de cola original', 1, 25.00, 600, 'Coca-Cola'),
('Coca-Cola Sin Azúcar', 'Refresco de cola sin azúcar', 1, 28.00, 600, 'Coca-Cola'),
('Sprite', 'Refresco de limón', 1, 23.00, 600, 'Coca-Cola'),
('Fanta Naranja', 'Refresco sabor naranja', 1, 23.00, 600, 'Coca-Cola'),
('Pepsi', 'Refresco de cola', 1, 24.00, 600, 'PepsiCo'),
('Agua Ciel', 'Agua purificada', 1, 12.00, 1000, 'Ciel'),

-- Snacks  
('Doritos Nacho', 'Botana de maíz sabor nacho', 2, 18.50, NULL, 'Sabritas'),
('Cheetos Flamin Hot', 'Botana de maíz picante', 2, 22.00, NULL, 'Sabritas'),
('Papas Sabritas Originales', 'Papas fritas clásicas', 2, 15.00, NULL, 'Sabritas'),
('Ruffles Queso', 'Papas onduladas sabor queso', 2, 17.00, NULL, 'Sabritas'),

-- Lácteos
('Leche Lala Entera', 'Leche entera pasteurizada', 3, 28.00, 1000, 'Lala'),
('Leche Lala Deslactosada', 'Leche sin lactosa', 3, 32.00, 1000, 'Lala'),
('Yogurt Danone Natural', 'Yogurt natural', 3, 15.00, 125, 'Danone'),
('Queso Oaxaca', 'Queso tipo Oaxaca', 3, 45.00, NULL, 'Fud')
ON DUPLICATE KEY UPDATE precio = VALUES(precio);

-- Tabla de atributos de productos
CREATE TABLE IF NOT EXISTS ProductoAtributos (
    id_atributo INT PRIMARY KEY AUTO_INCREMENT,
    id_producto INT,
    atributo VARCHAR(100) NOT NULL,
    valor VARCHAR(200),
    
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE CASCADE,
    INDEX idx_producto (id_producto),
    INDEX idx_atributo (atributo)
) ENGINE=InnoDB;

-- Insertar atributos de ejemplo
INSERT INTO ProductoAtributos (id_producto, atributo, valor) VALUES
-- Coca-Cola
(1, 'sabor', 'dulce'),
(1, 'tipo', 'gaseosa'),
(1, 'azucar', 'con azucar'),

-- Coca-Cola Sin Azúcar
(2, 'sabor', 'dulce'),
(2, 'tipo', 'gaseosa'),
(2, 'azucar', 'sin azucar'),
(2, 'calorias', 'cero calorias'),

-- Doritos
(7, 'sabor', 'picante'),
(7, 'textura', 'crujiente'),
(7, 'tipo', 'maiz'),

-- Cheetos
(8, 'sabor', 'picante'),
(8, 'intensidad', 'extra picante'),
(8, 'tipo', 'maiz'),

-- Leche Deslactosada
(12, 'lactosa', 'sin lactosa'),
(12, 'tipo', 'deslactosada')
ON DUPLICATE KEY UPDATE valor = VALUES(valor);

-- Crear índices adicionales para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_productos_busqueda ON Productos(nombre, descripcion);
CREATE INDEX IF NOT EXISTS idx_atributos_busqueda ON ProductoAtributos(atributo, valor);

-- Vista para consultas optimizadas
CREATE OR REPLACE VIEW VistaProductosCompleta AS
SELECT 
    p.id_producto,
    p.nombre,
    p.descripcion,
    c.nombre as categoria,
    p.precio,
    p.contenido_ml,
    p.contenido_gr,
    p.marca,
    p.stock,
    GROUP_CONCAT(CONCAT(pa.atributo, ':', pa.valor) SEPARATOR '|') as atributos
FROM Productos p
LEFT JOIN Categorias c ON p.id_categoria = c.id_categoria
LEFT JOIN ProductoAtributos pa ON p.id_producto = pa.id_producto
WHERE p.activo = TRUE AND c.activa = TRUE
GROUP BY p.id_producto, p.nombre, p.descripcion, c.nombre, p.precio, p.contenido_ml, p.contenido_gr, p.marca, p.stock;

-- Configurar charset y collation
ALTER DATABASE lynx_products CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
