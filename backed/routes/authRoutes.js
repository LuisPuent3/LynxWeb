const express = require('express');
const router = express.Router();
const db = require('../config/db');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { verifyToken } = require('../middlewares/authMiddleware');

// Registro de usuario
router.post('/register', async (req, res) => {
    try {
        const { nombre, apellidoP, apellidoM, correo, telefono, contraseña } = req.body;
        
        // Verificar si el correo ya existe
        const [existingUsers] = await db.query(
            'SELECT id_usuario FROM Usuarios WHERE correo = ?',
            [correo]
        );
        
        if (existingUsers.length > 0) {
            return res.status(400).json({ error: 'El correo ya está registrado' });
        }

        // Hash de la contraseña
        const hashedPassword = await bcrypt.hash(contraseña, 10);
        
        // Insertar en la tabla Nombres
        const [nombreResult] = await db.query(
            'INSERT INTO Nombres (nombre, apellidoP, apellidoM) VALUES (?, ?, ?)',
            [nombre, apellidoP, apellidoM]
        );

        const id_nombre = nombreResult.insertId;

        // Insertar en la tabla Usuarios
        await db.query(
            'INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES (?, ?, ?, ?, 1)',
            [id_nombre, correo, telefono, hashedPassword]
        );

        res.status(201).json({ mensaje: 'Usuario registrado exitosamente' });
    } catch (error) {
        console.error('Error en registro:', error);
        res.status(500).json({ error: 'Error al registrar usuario' });
    }
});

// Login de usuario
router.post('/login', async (req, res) => {
    try {
        const { correo, contraseña } = req.body;
        
        const [results] = await db.query(`
            SELECT u.*, r.nombre as rol 
            FROM Usuarios u 
            JOIN Roles r ON u.id_rol = r.id_rol 
            WHERE u.correo = ?
        `, [correo]);
        
        if (results.length === 0) {
            return res.status(401).json({ error: 'Usuario no encontrado' });
        }

        const usuario = results[0];
        const validPassword = await bcrypt.compare(contraseña, usuario.contraseña);
        
        if (!validPassword) {
            return res.status(401).json({ error: 'Contraseña incorrecta' });
        }

        const token = jwt.sign(
            { 
                id: usuario.id_usuario,
                rol: usuario.rol
            },
            process.env.JWT_SECRET,
            { expiresIn: process.env.JWT_EXPIRES_IN }
        );

        res.json({
            token,
            usuario: {
                id: usuario.id_usuario,
                correo: usuario.correo,
                rol: usuario.rol,
                nombre: usuario.nombre
            }
        });
    } catch (error) {
        console.error('Error en login:', error);
        res.status(500).json({ error: 'Error en el servidor' });
    }
});

// Verificar token y obtener información del usuario
router.get('/verify', verifyToken, async (req, res) => {
    try {
        const [results] = await db.query(`
            SELECT u.id_usuario, u.correo, u.nombre, r.nombre as rol
            FROM Usuarios u
            JOIN Roles r ON u.id_rol = r.id_rol
            WHERE u.id_usuario = ?
        `, [req.userId]);

        if (results.length === 0) {
            return res.status(404).json({ error: 'Usuario no encontrado' });
        }

        res.json({
            usuario: results[0]
        });
    } catch (error) {
        console.error('Error en verificación:', error);
        res.status(500).json({ error: 'Error en el servidor' });
    }
});

module.exports = router;