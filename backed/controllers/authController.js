const pool = require('../config/db');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

exports.registerUser = async (req, res) => {
  const { nombre, apellidoP, apellidoM, correo, telefono, contraseña } = req.body;

  try {
    // Hash de la contraseña
    const hashedPassword = await bcrypt.hash(contraseña, 10);

    // Crear entrada en tabla Nombres
    const [nombreResult] = await pool.query(
      'INSERT INTO Nombres (nombre, apellidoP, apellidoM) VALUES (?, ?, ?)',
      [nombre, apellidoP, apellidoM]
    );

    const id_nombre = nombreResult.insertId;

    // Crear entrada en tabla Usuarios
    await pool.query(
      'INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES (?, ?, ?, ?, ?)',
      [id_nombre, correo, telefono, hashedPassword, 1] // 1 = Cliente
    );

    res.status(201).json({ mensaje: 'Usuario registrado exitosamente' });
  } catch (error) {
    res.status(500).json({ error: 'Error al registrar usuario', detalles: error.message });
  }
};

exports.loginUser = async (req, res) => {
  const { correo, contraseña } = req.body;

  try {
    const [rows] = await pool.query('SELECT * FROM Usuarios WHERE correo = ?', [correo]);

    if (rows.length === 0) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    const usuario = rows[0];
    const match = await bcrypt.compare(contraseña, usuario.contraseña);

    if (!match) {
      return res.status(401).json({ error: 'Credenciales incorrectas' });
    }

    // Crear token
    const token = jwt.sign({ id: usuario.id_usuario }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.json({ token, rol: usuario.id_rol });
  } catch (error) {
    res.status(500).json({ error: 'Error al iniciar sesión', detalles: error.message });
  }
  /// En authController.js
  const token = jwt.sign({ 
  id: usuario.id_usuario, 
  rol: usuario.id_rol,
  exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1 hora de expiración
  }, process.env.JWT_SECRET);
};
