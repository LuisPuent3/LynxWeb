-- Script para añadir la columna firebase_uid a la tabla Usuarios
ALTER TABLE Usuarios ADD COLUMN firebase_uid VARCHAR(128) NULL;
-- Crear un índice para mejorar el rendimiento de las consultas
CREATE INDEX idx_firebase_uid ON Usuarios(firebase_uid); 