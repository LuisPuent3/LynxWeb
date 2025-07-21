-- CREAR TABLAS LCLN SIMPLIFICADO
-- Ejecutar en base de datos lynxshop

USE lynxshop;

-- Tabla de sinónimos específicos por producto
CREATE TABLE producto_sinonimos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    sinonimo VARCHAR(255) NOT NULL,
    popularidad INT DEFAULT 0,
    precision_score DECIMAL(3,2) DEFAULT 1.00,
    creado_por VARCHAR(50) DEFAULT 'admin',
    fuente ENUM('admin', 'auto_learning', 'user_feedback') DEFAULT 'admin',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    UNIQUE KEY unique_producto_sinonimo (producto_id, sinonimo),
    INDEX idx_sinonimo_activo (sinonimo, activo)
);

-- Tabla de atributos de productos
CREATE TABLE producto_atributos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    atributo VARCHAR(100) NOT NULL,
    valor BOOLEAN DEFAULT TRUE,
    intensidad TINYINT DEFAULT 5,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    UNIQUE KEY unique_producto_atributo (producto_id, atributo),
    INDEX idx_atributo_valor (atributo, valor)
);

-- Tabla de métricas de búsqueda
CREATE TABLE busqueda_metricas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    termino_busqueda VARCHAR(255) NOT NULL,
    producto_id INT,
    clicks INT DEFAULT 0,
    tiempo_en_pagina INT DEFAULT 0,
    conversiones INT DEFAULT 0,
    rating_utilidad TINYINT,
    fecha_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    INDEX idx_termino_fecha (termino_busqueda, fecha_busqueda)
);

-- Verificar que se crearon las tablas
SHOW TABLES LIKE '%sinoni%';
SHOW TABLES LIKE '%atributo%';
SHOW TABLES LIKE '%metrica%';

SELECT 'Tablas creadas exitosamente' as resultado;