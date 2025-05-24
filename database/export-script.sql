-- SCRIPT PARA EXPORTAR DATOS REALES DESDE MYSQL WORKBENCH
-- Ejecuta este script en MySQL Workbench para obtener los datos actuales
-- Copia el resultado y pégalo en el archivo data.sql

-- EXPORT DE DATOS EXISTENTES
USE lynxshop;

-- Exportar Nombres
SELECT CONCAT(
    'INSERT INTO Nombres (id_nombre, nombre, apellidoP, apellidoM) VALUES (',
    IFNULL(id_nombre, 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(nombre, '"', '\\"'), '"'), 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(apellidoP, '"', '\\"'), '"'), 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(apellidoM, '"', '\\"'), '"'), 'NULL'),
    ');'
) AS insert_statement
FROM Nombres;

-- Exportar Usuarios
SELECT CONCAT(
    'INSERT INTO Usuarios (id_usuario, id_nombre, correo, telefono, contraseña, id_rol, fecha_registro) VALUES (',
    IFNULL(id_usuario, 'NULL'), ', ',
    IFNULL(id_nombre, 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(correo, '"', '\\"'), '"'), 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(telefono, '"', '\\"'), '"'), 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(contraseña, '"', '\\"'), '"'), 'NULL'), ', ',
    IFNULL(id_rol, 'NULL'), ', ',
    IFNULL(CONCAT('"', fecha_registro, '"'), 'NULL'),
    ');'
) AS insert_statement
FROM Usuarios;

-- Exportar Categorias
SELECT CONCAT(
    'INSERT INTO Categorias (id_categoria, nombre, descripcion) VALUES (',
    IFNULL(id_categoria, 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(nombre, '"', '\\"'), '"'), 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(descripcion, '"', '\\"'), '"'), 'NULL'),
    ');'
) AS insert_statement
FROM Categorias;

-- Exportar Productos
SELECT CONCAT(
    'INSERT INTO Productos (id_producto, nombre, precio, cantidad, id_categoria, imagen) VALUES (',
    IFNULL(id_producto, 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(nombre, '"', '\\"'), '"'), 'NULL'), ', ',
    IFNULL(precio, 'NULL'), ', ',
    IFNULL(cantidad, 'NULL'), ', ',
    IFNULL(id_categoria, 'NULL'), ', ',
    IFNULL(CONCAT('"', REPLACE(imagen, '"', '\\"'), '"'), 'NULL'),
    ');'
) AS insert_statement
FROM Productos;

-- Exportar Pedidos
SELECT CONCAT(
    'INSERT INTO Pedidos (id_pedido, id_usuario, fecha, id_estado) VALUES (',
    IFNULL(id_pedido, 'NULL'), ', ',
    IFNULL(id_usuario, 'NULL'), ', ',
    IFNULL(CONCAT('"', fecha, '"'), 'NULL'), ', ',
    IFNULL(id_estado, 'NULL'),
    ');'
) AS insert_statement
FROM Pedidos;

-- Exportar DetallePedido
SELECT CONCAT(
    'INSERT INTO DetallePedido (id_detalle, id_pedido, id_producto, cantidad, subtotal) VALUES (',
    IFNULL(id_detalle, 'NULL'), ', ',
    IFNULL(id_pedido, 'NULL'), ', ',
    IFNULL(id_producto, 'NULL'), ', ',
    IFNULL(cantidad, 'NULL'), ', ',
    IFNULL(subtotal, 'NULL'),
    ');'
) AS insert_statement
FROM DetallePedido;
