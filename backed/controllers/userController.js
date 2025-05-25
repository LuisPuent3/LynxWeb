const db = require('../config/db');
const bcrypt = require('bcryptjs');

exports.register = async (req, res) => {
    const { nombre, apellidoP, apellidoM, correo, telefono, contraseña } = req.body;
    
    // Primero insertar en la tabla nombres
    const nombreQuery = 'INSERT INTO nombres (nombre, apellidoP, apellidoM) VALUES (?, ?, ?)';
    db.query(nombreQuery, [nombre, apellidoP, apellidoM], (err, nombreResult) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }

        // Luego insertar en la tabla Usuarios
        const hashedPassword = bcrypt.hashSync(contraseña, 10);
        const usuarioQuery = 'INSERT INTO usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES (?, ?, ?, ?, 1)';
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
    const query = 'SELECT * FROM usuarios WHERE correo = ?';
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
        FROM usuarios u 
        JOIN nombres n ON u.id_nombre = n.id_nombre 
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

    // Primero actualizar la tabla nombres
    const getUserQuery = 'SELECT id_nombre FROM usuarios WHERE id_usuario = ?';
    db.query(getUserQuery, [userId], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ message: 'Usuario no encontrado' });
        }

        const idNombre = results[0].id_nombre;
        const updateNombreQuery = 'UPDATE nombres SET nombre = ?, apellidoP = ?, apellidoM = ? WHERE id_nombre = ?';
        db.query(updateNombreQuery, [nombre, apellidoP, apellidoM, idNombre], (err) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }

            // Luego actualizar la tabla Usuarios
            const updateUsuarioQuery = 'UPDATE usuarios SET correo = ?, telefono = ? WHERE id_usuario = ?';
            db.query(updateUsuarioQuery, [correo, telefono, userId], (err) => {
                if (err) {
                    return res.status(500).json({ error: err.message });
                }
                res.json({ message: 'Usuario actualizado exitosamente' });
            });
        });
    });
};