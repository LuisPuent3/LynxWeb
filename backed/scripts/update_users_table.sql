-- Cambiando el tipo de columna de contraseña de VARBINARY a VARCHAR
ALTER TABLE Usuarios MODIFY contraseña VARCHAR(255);

-- Actualizar contraseñas existentes con valores bcrypt conocidos
-- Suponiendo que tenemos algunos usuarios de prueba con contraseñas conocidas
UPDATE Usuarios SET contraseña = '$2a$10$X7H1QALRRxX9Q1Y4z8P5h.fGxmAw/1xn0R9SWzw1zrg9n8cvJw8hy' WHERE correo = 'juan.perez@example.com';
UPDATE Usuarios SET contraseña = '$2a$10$4XMM5dZ4zMVK5KJN9XZMzu3ZQdaF2TYi5xYzB0H5f8.URVKad0hFa' WHERE correo = 'ana.gomez@example.com';
UPDATE Usuarios SET contraseña = '$2a$10$PoLSg6KfLUQBgDRYm/1B6eH3QphcV7EwkuS3lkBUU8J5zQvbNSJCa' WHERE correo = 'carlos.lopez@example.com';
UPDATE Usuarios SET contraseña = '$2a$10$XeDqLsm6jXHPHU9UcMzCke4kcgYZnZ5BG.fFQi8i/mB.x2uWa0yxu' WHERE correo = 'laura.mendez@example.com';
UPDATE Usuarios SET contraseña = '$2a$10$CcUNzwGZE.JGz/p8.nHjReg.DmdOJoFDimqO6RE.y5fxQ2cUgHIjK' WHERE correo = 'pedro.fernandez@example.com';

-- También puedes agregar un usuario nuevo de prueba con una contraseña predecible
INSERT INTO Nombres (nombre, apellidoP, apellidoM) VALUES ('Usuario', 'De', 'Prueba');
INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) 
VALUES (LAST_INSERT_ID(), 'test@example.com', '5551234567', '$2a$10$Y7nHry1YDMjXkNzG9.gZw.8pWJ2xTKiknrqnEe3LSs2.B1aOYdpUu', 1); -- password: test123 