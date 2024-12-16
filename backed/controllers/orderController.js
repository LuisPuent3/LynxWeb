const pool = require('../config/db'); // Asegúrate de que la ruta sea correcta

// Controlador para crear una orden
exports.createOrder = async (req, res) => {
  try {
    // Extrae los datos de la solicitud
    const { productos, id_usuario } = req.body;

    // Verifica que los datos estén presentes
    if (!productos || !Array.isArray(productos) || productos.length === 0) {
      return res.status(400).json({
        success: false,
        mensaje: 'Debe proporcionar una lista de productos válida.'
      });
    }

    if (!id_usuario) {
      return res.status(400).json({
        success: false,
        mensaje: 'El ID de usuario es obligatorio.'
      });
    }

    console.log('Datos recibidos:', { productos, id_usuario });

    // Conexión a la base de datos
    const connection = await pool;

    // Obtener el ID del usuario invitado si es necesario
    let userIdForDB;
    if (id_usuario === 'guest') {
      const [guestUser] = await connection.query(
        'SELECT id_usuario FROM Usuarios WHERE correo = ?',
        ['guest@lynxshop.com']
      );
      userIdForDB = guestUser[0]?.id_usuario || null;

      if (!userIdForDB) {
        return res.status(404).json({
          success: false,
          mensaje: 'No se encontró un usuario invitado con el correo proporcionado.'
        });
      }
    } else {
      userIdForDB = id_usuario;
    }

    // Insertar el pedido en la tabla "Pedidos"
    const [orderResult] = await connection.query(
      'INSERT INTO Pedidos (id_usuario, id_estado, fecha) VALUES (?, 1, NOW())',
      [userIdForDB]
    );

    const id_pedido = orderResult.insertId;

    // Insertar los detalles del pedido en la tabla "DetallePedido"
    for (const producto of productos) {
      if (!producto.id_producto || !producto.cantidad || !producto.precio) {
        return res.status(400).json({
          success: false,
          mensaje: 'Cada producto debe tener id_producto, cantidad y precio.'
        });
      }

      await connection.query(
        'INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) VALUES (?, ?, ?, ?)',
        [
          id_pedido, 
          producto.id_producto, 
          producto.cantidad, 
          producto.precio * producto.cantidad
        ]
      );
    }

    // Respuesta exitosa
    res.status(201).json({
      success: true,
      mensaje: 'Pedido creado exitosamente',
      id_pedido
    });

  } catch (error) {
    console.error('Error completo:', error);
    res.status(500).json({
      success: false,
      mensaje: 'Error al crear el pedido',
      detalles: error.message
    });
  }
};
