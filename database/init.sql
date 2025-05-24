-- 01-init.sql - Inicialización de la base de datos LynxShop
CREATE DATABASE IF NOT EXISTS lynxshop;
USE lynxshop;

-- Crear tabla de Roles
CREATE TABLE Roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

-- Crear tabla de Nombres 
CREATE TABLE Nombres (
    id_nombre INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidoP VARCHAR(70) NOT NULL,
    apellidoM VARCHAR(70)
);

-- Crear tabla de Usuarios
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_nombre INT DEFAULT NULL,
    correo VARCHAR(100) UNIQUE DEFAULT NULL,
    telefono VARCHAR(15) UNIQUE DEFAULT NULL,
    contraseña VARCHAR(255) DEFAULT NULL,
    id_rol INT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_nombre) REFERENCES Nombres(id_nombre) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Crear tabla de Categorías
CREATE TABLE Categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255)
);

-- Crear tabla de Productos
CREATE TABLE Productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    id_categoria INT NOT NULL,
    imagen VARCHAR(255),
    FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Crear tabla de EstadosPedidos
CREATE TABLE EstadosPedidos (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

-- Crear tabla de Pedidos
CREATE TABLE Pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_estado) REFERENCES EstadosPedidos(id_estado) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Crear tabla de DetallePedido
CREATE TABLE DetallePedido (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Insertar datos básicos necesarios para el funcionamiento
INSERT INTO Roles (nombre) VALUES 
('Cliente'), 
('Administrador'), 
('Invitado');

INSERT INTO EstadosPedidos (nombre) VALUES 
('Pendiente'),
('Entregado'),
('Cancelado'),
('Aceptado');

-- Crear usuario administrador por defecto
INSERT INTO Nombres (nombre, apellidoP, apellidoM) VALUES 
('Admin', 'Sistema', NULL);

INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES 
(1, 'admin@lynxshop.com', '5555555555', '$2a$10$X7H1QALRRxX9Q1Y4z8P5h.fGxmAw/1xn0R9SWzw1zrg9n8cvJw8hy', 2);

-- Crear al menos una categoría por defecto
INSERT INTO Categorias (nombre, descripcion) VALUES 
('General', 'Productos generales');
