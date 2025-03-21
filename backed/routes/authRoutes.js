const express = require('express');
const router = express.Router();
const db = require('../config/db');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const admin = require('firebase-admin');
const path = require('path');

// Inicializar Firebase Admin SDK con el archivo de credenciales
const serviceAccount = require('../lynxfire.json');

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

router.post('/login', async (req, res) => {
    try {
        const { correo, contraseña } = req.body;
        
        const query = 'SELECT *, AES_DECRYPT(contraseña, "clave_secreta") as pass_decrypted FROM Usuarios WHERE correo = ?';
        db.query(query, [correo], async (err, results) => {
            if (err) {
                console.error('Error en consulta:', err);
                return res.status(500).json({ error: 'Error en base de datos' });
            }
            
            if (results.length === 0) {
                return res.status(401).json({ error: 'Usuario no encontrado' });
            }

            const usuario = results[0];
            const storedPassword = usuario.pass_decrypted.toString();
            
            if (contraseña !== storedPassword) {
                return res.status(401).json({ error: 'Contraseña incorrecta' });
            }

            const token = jwt.sign(
                { id: usuario.id_usuario },
                'tu_secret_key',
                { expiresIn: '1h' }
            );

            res.json({
                token,
                usuario: {
                    id: usuario.id_usuario,
                    correo: usuario.correo
                }
            });
        });
    } catch (error) {
        console.error('Error en login:', error);
        res.status(500).json({ error: 'Error en el servidor' });
    }
});

// Nuevo endpoint para la autenticación con Firebase
router.post('/firebase-login', async (req, res) => {
    try {
        const { idToken } = req.body;
        
        // Verificar el token de Firebase
        const decodedToken = await admin.auth().verifyIdToken(idToken);
        const { uid, email } = decodedToken;
        
        // Buscar si el usuario ya existe en nuestra base de datos
        const connection = await db;
        const [usuarios] = await connection.query('SELECT * FROM Usuarios WHERE firebase_uid = ?', [uid]);
        
        let usuarioId;
        
        if (usuarios.length > 0) {
            // El usuario ya existe en nuestra base de datos
            usuarioId = usuarios[0].id_usuario;
        } else {
            // El usuario no existe, buscar por correo
            const [usuariosPorEmail] = await connection.query('SELECT * FROM Usuarios WHERE correo = ?', [email]);
            
            if (usuariosPorEmail.length > 0) {
                // Actualizar el usuario existente con el UID de Firebase
                usuarioId = usuariosPorEmail[0].id_usuario;
                await connection.query('UPDATE Usuarios SET firebase_uid = ? WHERE id_usuario = ?', [uid, usuarioId]);
            } else {
                // Crear un nuevo usuario si no existe
                return res.status(401).json({ error: 'Usuario no registrado. Por favor regístrese primero.' });
            }
        }
        
        // Generar un token JWT para nuestra aplicación
        const token = jwt.sign(
            { id: usuarioId },
            'tu_secret_key',
            { expiresIn: '1h' }
        );
        
        res.json({
            token,
            usuario: {
                id: usuarioId,
                correo: email
            }
        });
    } catch (error) {
        console.error('Error en firebase-login:', error);
        res.status(500).json({ error: 'Error de autenticación con Firebase' });
    }
});

// Endpoint para registro con Firebase
router.post('/firebase-register', async (req, res) => {
    try {
        const { nombre, correo, telefono, idToken } = req.body;
        
        // Verificar el token de Firebase
        const decodedToken = await admin.auth().verifyIdToken(idToken);
        const { uid, email } = decodedToken;
        
        const connection = await db;
        
        // Verificar si el usuario ya existe
        const [existingUsers] = await connection.query('SELECT * FROM Usuarios WHERE correo = ?', [email]);
        
        if (existingUsers.length > 0) {
            // Si el usuario ya existe, actualizar su UID de Firebase
            await connection.query('UPDATE Usuarios SET firebase_uid = ? WHERE correo = ?', [uid, email]);
            
            const token = jwt.sign(
                { id: existingUsers[0].id_usuario },
                'tu_secret_key',
                { expiresIn: '1h' }
            );
            
            return res.json({
                token,
                usuario: {
                    id: existingUsers[0].id_usuario,
                    correo: email
                }
            });
        }
        
        // Crear un nuevo usuario
        const [result] = await connection.query(
            'INSERT INTO Usuarios (nombre, correo, telefono, contraseña, firebase_uid) VALUES (?, ?, ?, AES_ENCRYPT(?, "clave_secreta"), ?)',
            [nombre, correo, telefono, `firebase_${Date.now()}`, uid]
        );
        
        const token = jwt.sign(
            { id: result.insertId },
            'tu_secret_key',
            { expiresIn: '1h' }
        );
        
        res.status(201).json({
            token,
            usuario: {
                id: result.insertId,
                correo
            }
        });
    } catch (error) {
        console.error('Error en firebase-register:', error);
        res.status(500).json({ error: 'Error al registrar con Firebase' });
    }
});

module.exports = router;