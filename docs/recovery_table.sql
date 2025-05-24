-- Tabla para tokens de recuperación de contraseña
CREATE TABLE TokensRecuperacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    fecha_expiracion DATETIME NOT NULL,
    utilizado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_token (token),
    INDEX idx_usuario (id_usuario)
);
