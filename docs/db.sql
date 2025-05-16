create database lynxshop;
use lynxshop;

-- Crear tabla de Roles
CREATE TABLE Roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del rol
    nombre VARCHAR(50) UNIQUE NOT NULL      -- Nombre del rol(Cliente, Administrador, Invitado)
);
select * from Roles;

-- Crear tabla de Nombres 
CREATE TABLE Nombres (
    id_nombre INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del nombre
    nombre VARCHAR(100) NOT NULL,               -- Nombre del usuario
    apellidoP varchar(70) not null, -- apellido paterno del usurio
    apellidoM varchar(70) -- apellido materno del usuario no obligatorio
);

-- Crear tabla de Usuarios
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY, -- Identificador único del usuario
    id_nombre INT DEFAULT NULL,                -- Relación con Nombres
    correo VARCHAR(100) UNIQUE DEFAULT NULL,   -- Correo único (puede ser NULL para invitados)
    telefono VARCHAR(15) UNIQUE DEFAULT NULL,  -- Teléfono único (puede ser NULL para invitados)
    contraseña VARBINARY(255) DEFAULT NULL,    -- Contraseña encriptada (NULL para invitados)
    id_rol INT NOT NULL,                       -- Relación con Roles
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Fecha de registro
    FOREIGN KEY (id_nombre) REFERENCES Nombres(id_nombre) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Crear tabla de Categorías
CREATE TABLE Categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único de la categoría
    nombre VARCHAR(50) UNIQUE NOT NULL,           -- Nombre único de la categoría
    descripcion VARCHAR(255)                      -- Descripción de la categoría
);

-- Crear tabla de Productos
CREATE TABLE Productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del producto
    nombre VARCHAR(100) UNIQUE NOT NULL,         -- Nombre único del producto
    precio DECIMAL(10,2) NOT NULL,               -- Precio del producto
    cantidad INT NOT NULL,                       -- Cantidad en inventario
    id_categoria INT NOT NULL,                   -- Relación con Categorías
    imagen VARCHAR(255),                         -- URL o nombre del archivo de imagen
    FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Crear tabla de Pedidos
CREATE TABLE Pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,    -- Identificador único del pedido
    id_usuario INT NOT NULL,                     -- Relación con Usuarios
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,    -- Fecha del pedido
    estado VARCHAR(20) DEFAULT 'pendiente',      -- Estado del pedido
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Crear tabla de DetallePedido
CREATE TABLE DetallePedido (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del detalle
    id_pedido INT NOT NULL,                     -- Relación con Pedidos
    id_producto INT NOT NULL,                   -- Relación con Productos
    cantidad INT NOT NULL,                      -- Cantidad de productos
    subtotal DECIMAL(10,2) NOT NULL,            -- Precio total por producto
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE EstadosPedidos (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único del estado
    nombre VARCHAR(50) UNIQUE NOT NULL         -- Nombre del estado (Pendiente, Entregado, Cancelado, etc.)
);

-- Agregar la columna id_estado a la tabla Pedidos
ALTER TABLE Pedidos
ADD COLUMN id_estado INT NOT NULL DEFAULT 1;

-- Agregar la restricción de clave foránea para id_estado
ALTER TABLE Pedidos
ADD CONSTRAINT fk_estado_pedido
FOREIGN KEY (id_estado) REFERENCES EstadosPedidos(id_estado)
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Insertar los roles necesarios
INSERT INTO Roles (nombre) 
VALUES ('Cliente'), ('Administrador'), ('Invitado');

-- Insertar datos en la tabla Nombres
INSERT INTO Nombres (nombre, apellidoP, apellidoM) 
VALUES
('Juan Uribe', 'Pérez', 'Gómez'),
('Luis Rafael', 'Gómez', NULL),  -- Usando NULL para el apellido materno
('Carlos López', 'López', 'Martínez'),
('Laura', 'Méndez', NULL),       -- Usando NULL para el apellido materno
('Pedro', 'Fernández', 'Ramírez');



INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) 
VALUES 
(1, 'juan.perez@example.com', '5551234567', AES_ENCRYPT('mi_contraseña', 'clave_secreta'), 1),
(2, 'ana.gomez@example.com', '5559876543', AES_ENCRYPT('otra_contraseña', 'clave_secreta'), 2),
(3, 'carlos.lopez@example.com', '5557891234', AES_ENCRYPT('password', 'clave_secreta'), 1),
(4, 'laura.mendez@example.com', '5556549870', AES_ENCRYPT('contraseña123', 'clave_secreta'), 2),
(5, 'pedro.fernandez@example.com', '5553214569', AES_ENCRYPT('12345', 'clave_secreta'), 3);


INSERT INTO Categorias (nombre, descripcion) 
VALUES 
('Bebidas', 'Todo tipo de bebidas'),
('Snacks', 'Snacks y golosinas'),
('Abarrotes', 'Productos básicos de abarrotes'),
('Frutas', 'Frutas frescas'),
('Verduras', 'Verduras frescas');

INSERT INTO Productos (nombre, precio, cantidad, id_categoria, imagen) 
VALUES 
('Coca-Cola', 15.50, 100, 1, 'coca-cola.jpg'),
('Doritos', 25.00, 200, 2, 'doritos.jpg'),
('Arroz', 10.00, 50, 3, 'arroz.jpg'),
('Manzana', 12.00, 150, 4, 'manzana.jpg'),
('Lechuga', 8.00, 120, 5, 'lechuga.jpg');

INSERT INTO EstadosPedidos (nombre) 
VALUES 
('Pendiente'),
('Entregado'),
('Cancelado');

-- Insertar detalles de pedido
INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) 
VALUES
(1, 1, 2, 31.00),  -- 2 Coca-Colas, subtotal = 2 * 15.50
(1, 2, 3, 75.00),  -- 3 Doritos, subtotal = 3 * 25.00
(2, 3, 1, 10.00),  -- 1 Arroz, subtotal = 1 * 10.00
(2, 4, 1, 12.00),  -- 1 Manzana, subtotal = 1 * 12.00
(3, 5, 5, 40.00),  -- 5 Lechugas, subtotal = 5 * 8.00
(3, 1, 2, 31.00);  -- 2 Coca-Colas, subtotal = 2 * 15.50

-- Insertar 5 registros en la tabla Pedidos
INSERT INTO Pedidos (id_usuario, id_estado, fecha)
VALUES 
(6, 1, CURRENT_TIMESTAMP),  -- Pedido 1: Usuario 1, Estado 1 (Pendiente)
(7, 1, CURRENT_TIMESTAMP),  -- Pedido 2: Usuario 2, Estado 1 (Pendiente)
(9, 2, CURRENT_TIMESTAMP),  -- Pedido 3: Usuario 3, Estado 2 (Enviado)
(10, 3, CURRENT_TIMESTAMP),  -- Pedido 4: Usuario 4, Estado 3 (Cancelado)
(8, 1, CURRENT_TIMESTAMP);  -- Pedido 5: Usuario 5, Estado 1 (Pendiente)

SELECT * FROM Usuarios;

SELECT * FROM Productos;

SELECT * FROM DetallePedido;

-- Insertar detalles de pedido con productos existentes
INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal)
VALUES
(11, 1, 2, 31.00),  -- Pedido 1: 2 Coca-Colas, subtotal = 2 * 15.50
(12, 2, 3, 75.00),  -- Pedido 2: 3 Doritos, subtotal = 3 * 25.00
(13, 3, 1, 10.00),  -- Pedido 3: 1 Arroz, subtotal = 1 * 10.00
(14, 4, 1, 12.00);  -- Pedido 4: 1 Manzana, subtotal = 1 * 12.00


SELECT Pedidos.id_pedido, Pedidos.fecha, Productos.nombre, DetallePedido.cantidad, DetallePedido.subtotal
FROM Pedidos
JOIN DetallePedido ON Pedidos.id_pedido = DetallePedido.id_pedido
JOIN Productos ON DetallePedido.id_producto = Productos.id_producto;


-- Verifica los registros en la tabla Pedidos
SELECT * FROM Pedidos;

-- Verifica los registros en la tabla Productos
SELECT * FROM Productos;
-- nombre pedido y productos
SELECT 
    Nombres.nombre AS Usuario,         -- Nombres.nombre
    Pedidos.id_pedido,
    Pedidos.fecha,
    Productos.nombre AS Producto,
    DetallePedido.cantidad,
    DetallePedido.subtotal
FROM 
    Pedidos
JOIN 
    Usuarios ON Pedidos.id_usuario = Usuarios.id_usuario
JOIN 
    Nombres ON Usuarios.id_nombre = Nombres.id_nombre  -- Aquí unimos Usuarios con Nombres
JOIN 
    DetallePedido ON Pedidos.id_pedido = DetallePedido.id_pedido
JOIN 
    Productos ON DetallePedido.id_producto = Productos.id_producto
ORDER BY 
    Pedidos.id_pedido, Nombres.nombre;  -- También ordenamos por Nombres.nombre

GRANT ALL PRIVILEGES ON *.* TO 'admin_user'@'localhost' WITH GRANT OPTION;
GRANT SELECT, INSERT, UPDATE, DELETE ON lynxshop.* TO 'dev_user'@'localhost';
