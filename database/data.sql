-- 02-data.sql - DATOS REALES EXPORTADOS DESDE MYSQL WORKBENCH
-- Aquí pegarás los resultados del script export-script.sql

-- TODO: Ejecutar export-script.sql en MySQL Workbench y pegar los resultados aquí

-- EJEMPLO DE DATOS (sustituir por datos reales):
-- Aquí van los INSERT statements generados por el script de exportación

-- Por ahora, datos de ejemplo para desarrollo:
INSERT INTO Nombres (nombre, apellidoP, apellidoM) VALUES 
('Juan Carlos', 'Pérez', 'Gómez'),
('Ana María', 'López', 'Martínez'),
('Carlos Eduardo', 'Rodríguez', NULL),
('Laura Patricia', 'Méndez', 'Fernández');

INSERT INTO Categorias (nombre, descripcion) VALUES 
('Bebidas', 'Todo tipo de bebidas'),
('Snacks', 'Snacks y golosinas'),
('Abarrotes', 'Productos básicos de abarrotes'),
('Frutas', 'Frutas frescas'),
('Verduras', 'Verduras frescas');

INSERT INTO Productos (nombre, precio, cantidad, id_categoria, imagen) VALUES 
('Coca-Cola 600ml', 15.50, 100, 1, 'coca-cola.jpg'),
('Doritos Nacho', 25.00, 200, 2, 'doritos.jpg'),
('Arroz 1kg', 10.00, 50, 3, 'arroz.jpg'),
('Manzana Roja kg', 12.00, 150, 4, 'manzana.jpg'),
('Lechuga Hidropónica', 8.00, 120, 5, 'lechuga.jpg');

-- Usuarios de ejemplo (se sustituirán por datos reales)
INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES 
(2, 'juan.perez@example.com', '5551234567', '$2a$10$X7H1QALRRxX9Q1Y4z8P5h.fGxmAw/1xn0R9SWzw1zrg9n8cvJw8hy', 1),
(3, 'ana.lopez@example.com', '5559876543', '$2a$10$4XMM5dZ4zMVK5KJN9XZMzu3ZQdaF2TYi5xYzB0H5f8.URVKad0hFa', 1),
(4, 'carlos.rodriguez@example.com', '5557891234', '$2a$10$PoLSg6KfLUQBgDRYm/1B6eH3QphcV7EwkuS3lkBUU8J5zQvbNSJCa', 1);

-- Pedidos de ejemplo
INSERT INTO Pedidos (id_usuario, id_estado, fecha) VALUES 
(2, 1, '2024-01-15 10:30:00'),
(3, 1, '2024-01-15 14:45:00'),
(4, 4, '2024-01-14 16:20:00');

-- Detalles de pedidos de ejemplo
INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) VALUES 
(1, 1, 2, 31.00),
(1, 2, 1, 25.00),
(2, 3, 1, 10.00),
(2, 4, 2, 24.00),
(3, 5, 3, 24.00);
