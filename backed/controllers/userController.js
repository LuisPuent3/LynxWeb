const db = require('../config/db');
const bcrypt = require('bcryptjs');

exports.register = async (req, res) => {
    const { nombre, apellidoP, apellidoM, correo, telefono, contraseña } = req.body;
    
    // Primero insertar en la tabla Nombres
    const nombreQuery = 'INSERT INTO Nombres (nombre, apellidoP, apellidoM) VALUES (?, ?, ?)';
    db.query(nombreQuery, [nombre, apellidoP, apellidoM], (err, nombreResult) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }

        // Luego insertar en la tabla Usuarios
        const hashedPassword = bcrypt.hashSync(contraseña, 10);
        const usuarioQuery = 'INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES (?, ?, ?, ?, 1)';
        db.query(usuarioQuery, [nombreResult.insertId, correo, telefono, hashedPassword], (err, usuarioResult) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.status(201).json({ message: 'Usuario registrado exitosamente' });
        });
    });
};

exports.login = (req, res) => {
    const { correo, contraseña } = req.body;
    const query = 'SELECT * FROM Usuarios WHERE correo = ?';
    db.query(query, [correo], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(401).json({ message: 'Credenciales inválidas' });
        }
        const user = results[0];
        const validPassword = bcrypt.compareSync(contraseña, user.contraseña);
        if (!validPassword) {
            return res.status(401).json({ message: 'Credenciales inválidas' });
        }
        res.json({ message: 'Login exitoso', userId: user.id_usuario });
    });
};

exports.getUserById = (req, res) => {
    const query = `
        SELECT u.*, n.nombre, n.apellidoP, n.apellidoM 
        FROM Usuarios u 
        JOIN Nombres n ON u.id_nombre = n.id_nombre 
        WHERE u.id_usuario = ?`;
    db.query(query, [req.params.id], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ message: 'Usuario no encontrado' });
        }
        res.json(results[0]);
    });
};

exports.updateUser = (req, res) => {
    const { nombre, apellidoP, apellidoM, correo, telefono } = req.body;
    const userId = req.params.id;

    // Primero actualizar la tabla Nombres
    const getUserQuery = 'SELECT id_nombre FROM Usuarios WHERE id_usuario = ?';
    db.query(getUserQuery, [userId], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ message: 'Usuario no encontrado' });
        }

        const idNombre = results[0].id_nombre;
        const updateNombreQuery = 'UPDATE Nombres SET nombre = ?, apellidoP = ?, apellidoM = ? WHERE id_nombre = ?';
        db.query(updateNombreQuery, [nombre, apellidoP, apellidoM, idNombre], (err) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }

            // Luego actualizar la tabla Usuarios
            const updateUsuarioQuery = 'UPDATE Usuarios SET correo = ?, telefono = ? WHERE id_usuario = ?';
            db.query(updateUsuarioQuery, [correo, telefono, userId], (err) => {
                if (err) {
                    return res.status(500).json({ error: err.message });
                }
                res.json({ message: 'Usuario actualizado exitosamente' });
            });
        });
    });
};