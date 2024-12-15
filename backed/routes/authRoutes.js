const express = require('express');
const router = express.Router();
const db = require('../config/db');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

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

module.exports = router;