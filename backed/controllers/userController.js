const db = require('../db');

// Registrar un usuario
const registerUser = async (req, res) => {
    const { id_nombre, correo, telefono, contraseña, id_rol } = req.body;
    try {
        const [result] = await db.query(
            `INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) 
            VALUES (?, ?, ?, AES_ENCRYPT(?, 'clave_secreta'), ?)`,
            [id_nombre, correo, telefono, contraseña, id_rol]
        );
        res.status(201).json({ message: 'Usuario registrado con éxito', id_usuario: result.insertId });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// Iniciar sesión
const loginUser = async (req, res) => {
    const { correo, contraseña } = req.body;
    try {
        const [rows] = await db.query(
            `SELECT id_usuario, id_nombre, correo, id_rol, AES_DECRYPT(contraseña, 'clave_secreta') AS contraseña 
            FROM Usuarios WHERE correo = ?`,
            [correo]
        );
        if (rows.length === 0 || rows[0].contraseña !== contraseña) {
            return res.status(401).json({ message: 'Credenciales incorrectas' });
        }
        res.status(200).json({ message: 'Inicio de sesión exitoso', usuario: rows[0] });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// Obtener detalles del usuario
const getUserDetails = async (req, res) => {
    const { id } = req.params;
    try {
        const [rows] = await db.query(
            `SELECT id_usuario, correo, telefono, id_rol, fecha_registro FROM Usuarios WHERE id_usuario = ?`,
            [id]
        );
        if (rows.length === 0) {
            return res.status(404).json({ message: 'Usuario no encontrado' });
        }
        res.status(200).json(rows[0]);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// Listar todos los usuarios
exports.listarUsuarios = async (req, res) => {
    try {
      const [usuarios] = await db.execute(`
        SELECT 
          Usuarios.id_usuario, 
          Nombres.nombre, 
          Nombres.apellidoP, 
          Nombres.apellidoM, 
          Usuarios.correo, 
          Usuarios.telefono, 
          Roles.nombre AS rol 
        FROM Usuarios
        JOIN Nombres ON Usuarios.id_nombre = Nombres.id_nombre
        JOIN Roles ON Usuarios.id_rol = Roles.id_rol
      `);
      res.status(200).json(usuarios);
    } catch (error) {
      console.error(error);
      res.status(500).json({ mensaje: "Error al obtener los usuarios" });
    }
  };
  
  // Crear un nuevo usuario
  exports.crearUsuario = async (req, res) => {
    const { nombre, apellidoP, apellidoM, correo, telefono, contraseña, id_rol } = req.body;
    try {
      const [nombreRegistro] = await db.execute(
        "INSERT INTO Nombres (nombre, apellidoP, apellidoM) VALUES (?, ?, ?)",
        [nombre, apellidoP, apellidoM]
      );
  
      const id_nombre = nombreRegistro.insertId;
  
      await db.execute(
        "INSERT INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES (?, ?, ?, AES_ENCRYPT(?, 'clave_secreta'), ?)",
        [id_nombre, correo, telefono, contraseña, id_rol]
      );
  
      res.status(201).json({ mensaje: "Usuario creado con éxito" });
    } catch (error) {
      console.error(error);
      res.status(500).json({ mensaje: "Error al crear el usuario" });
    }
  };

  
module.exports = { registerUser, loginUser, getUserDetails };
