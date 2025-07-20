-- Script para poblar la base de datos con datos de ejemplo

-- Asegúrate que las tablas existen y están vacías si es necesario antes de correr este script.
-- Por ejemplo:
-- DELETE FROM DetallePedido;
-- DELETE FROM Pedidos;
-- DELETE FROM Productos;
-- DELETE FROM Categorias;
-- DELETE FROM Usuarios;
-- ALTER TABLE Productos AUTO_INCREMENT = 1;
-- ALTER TABLE Categorias AUTO_INCREMENT = 1;
-- ALTER TABLE Usuarios AUTO_INCREMENT = 1;
-- ALTER TABLE Pedidos AUTO_INCREMENT = 1;
-- ALTER TABLE DetallePedido AUTO_INCREMENT = 1;

-- Crear Categorías de ejemplo (si no existen)
INSERT INTO Categorias (nombre, descripcion) VALUES
('Electrónicos', 'Dispositivos y accesorios electrónicos'),
('Ropa', 'Prendas de vestir para todas las edades'),
('Hogar', 'Artículos para el hogar y decoración'),
('Libros', 'Libros de diversos géneros'),
('Alimentos', 'Comestibles y bebidas')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre); -- Para evitar error si ya existen

-- Crear Productos de ejemplo (10 productos)
-- Asumiendo que la tabla Productos tiene columnas: id (autoincremental), nombre, descripcion, precio, stock, categoriaId, imagenUrl
INSERT INTO Productos (nombre, descripcion, precio, stock, categoriaId, imagenUrl) VALUES
('Laptop Pro X', 'Laptop de alto rendimiento para profesionales.', 1200.00, 50, 1, 'uploads/default.jpg'),
('Smartphone Z', 'Teléfono inteligente con cámara de alta resolución.', 799.99, 150, 1, 'uploads/default.jpg'),
('Camiseta Casual', 'Camiseta de algodón cómoda para uso diario.', 25.50, 200, 2, 'uploads/default.jpg'),
('Jeans Slim Fit', 'Pantalones vaqueros ajustados de moda.', 59.95, 120, 2, 'uploads/default.jpg'),
('Cafetera Express', 'Máquina para preparar café espresso en casa.', 89.00, 75, 3, 'uploads/default.jpg'),
('Lámpara de Escritorio LED', 'Lámpara moderna con luz LED ajustable.', 35.00, 90, 3, 'uploads/default.jpg'),
('Novela de Misterio', 'Un bestseller internacional lleno de suspenso.', 19.99, 300, 4, 'uploads/default.jpg'),
('Libro de Cocina Saludable', 'Recetas fáciles y nutritivas para toda la familia.', 22.50, 180, 4, 'uploads/default.jpg'),
('Galletas Artesanales', 'Paquete de galletas horneadas con ingredientes naturales.', 5.75, 500, 5, 'uploads/default.jpg'),
('Jugo Orgánico de Naranja', 'Jugo 100% natural sin azúcares añadidos.', 3.99, 250, 5, 'uploads/default.jpg');

-- Crear Usuarios de ejemplo (admin y shopper)
-- Asumiendo que la tabla Usuarios tiene columnas: id (autoincremental), nombre, apellido, email, password (hasheada), rol ('admin', 'shopper')
-- IMPORTANTE: Las contraseñas deben ser hasheadas en un entorno real. Aquí se usan placeholders.
-- TODO: Reemplazar contraseñas con hashes seguros (ej. bcrypt)
INSERT INTO Usuarios (nombre, apellido, email, password, rol) VALUES
('Admin', 'User', 'admin@example.com', '$2b$10$abcdefghijklmnopqrstuv', 'admin'), -- Contraseña: 'adminpassword' (hasheada)
('Shopper', 'User', 'shopper@example.com', '$2b$10$1234567890abcdefghijkl', 'shopper'); -- Contraseña: 'password123' (hasheada)

-- TODO: Considerar añadir datos para:
-- Pedidos
-- DetallePedido
-- Relaciones entre usuarios y pedidos

SELECT '* FROM Productos' AS 'Productos Insertados';
SELECT '* FROM Usuarios' AS 'Usuarios Insertados';
SELECT '* FROM Categorias' AS 'Categorias Insertadas';
