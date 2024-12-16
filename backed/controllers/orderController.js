const pool = require('../config/db');

exports.createOrder = async (req, res) => {
  try {
    const { productos, id_usuario } = req.body;
    console.log('Datos recibidos:', { productos, id_usuario });

    const connection = await pool;

    // Obtener el ID del usuario invitado si es necesario
    let userIdForDB;
    if (id_usuario === 'guest') {
      const [guestUser] = await connection.query(
        'SELECT id_usuario FROM Usuarios WHERE correo = ?',
        ['guest@lynxshop.com']
      );
      userIdForDB = guestUser[0]?.id_usuario || null;
    } else {
      userIdForDB = id_usuario;
    }

    // Insertar el pedido
    const [orderResult] = await connection.query(
      'INSERT INTO Pedidos (id_usuario, id_estado, fecha) VALUES (?, 1, NOW())',
      [userIdForDB]
    );

    const id_pedido = orderResult.insertId;

    // Insertar los detalles del pedido
    for (const producto of productos) {
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

    res.status(201).json({
      success: true,
      mensaje: 'Pedido creado exitosamente',
      id_pedido
    });

  } catch (error) {
    console.error('Error completo:', error);
    res.status(500).json({
      success: false,
      error: 'Error al crear pedido',
      detalles: error.message
    });
  }
};