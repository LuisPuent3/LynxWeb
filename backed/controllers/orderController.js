const pool = require('../config/db');

exports.createOrder = async (req, res) => {
  const connection = await pool; // Esperamos a obtener la conexión del pool
  let orderConnection;

  try {
    orderConnection = await connection.getConnection();
    const { carrito, id_usuario } = req.body;

    // Validar que carrito sea un array y tenga al menos un elemento
    if (!Array.isArray(carrito) || carrito.length === 0) {
      return res.status(400).json({ error: 'El carrito de compras está vacío' });
    }

    // Validar que cada elemento del carrito tenga las propiedades necesarias
    for (const item of carrito) {
      if (!item.id_producto || !item.cantidad || !item.precio) {
        return res.status(400).json({ error: 'Los detalles del producto están incompletos' });
      }
    }

    await orderConnection.beginTransaction();

    // Obtener el ID del usuario (guest o normal)
    let userIdForDB;
    if (id_usuario === 'guest') {
      const [guestUser] = await orderConnection.query(
        'SELECT id_usuario FROM usuarios WHERE correo = ?',
        ['guest@lynxshop.com']
      );
      if (!guestUser || guestUser.length === 0) {
        await orderConnection.rollback();
        return res.status(400).json({ error: 'Usuario invitado no encontrado' });
      }
      userIdForDB = guestUser[0].id_usuario;
    } else {
      userIdForDB = id_usuario;
    }

    const [orderResult] = await orderConnection.query(
      'INSERT INTO pedidos (id_usuario, id_estado) VALUES (?, 1)',
      [userIdForDB]
    );
    console.log('Pedido insertado correctamente:', orderResult);

    const id_pedido = orderResult.insertId;

    const detalles = carrito.map((item) => [
      id_pedido,
      item.id_producto,
      item.cantidad,
      item.cantidad * item.precio,
    ]);

    await orderConnection.query(
      'INSERT INTO detallepedido (id_pedido, id_producto, cantidad, subtotal) VALUES ?',
      [detalles]
    );
    console.log('Detalles del pedido insertados correctamente');

    await orderConnection.commit();
    
    res.status(201).json({ mensaje: 'Pedido creado exitosamente', id_pedido });
  } catch (error) {
    if (orderConnection) {
      await orderConnection.rollback();
    }
    console.error('Error al crear el pedido:', error);
    if (error.code) {
      console.error('Código de error de MySQL:', error.code);
      console.error('Mensaje de error de MySQL:', error.sqlMessage);
    }
    res.status(500).json({ error: 'Error al procesar el pedido', detalles: error.message });
  } finally {
    if (orderConnection) {
      orderConnection.release();
    }
  }
};

exports.getOrdersByUser = async (req, res) => {
  try {
    const connection = await pool;
    const { id_usuario } = req.params;

    const [orders] = await connection.query(
      'SELECT * FROM pedidos WHERE id_usuario = ?',
      [id_usuario]
    );
    res.json(orders);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener pedidos', detalles: error.message });
  }
};

// Función para obtener detalles de un pedido
exports.getOrderDetails = async (req, res) => {
  try {
    const connection = await pool;
    const { id } = req.params;

    const [details] = await connection.query(
      `SELECT p.id_pedido, p.fecha, dp.id_producto, prod.nombre, dp.cantidad, dp.subtotal
       FROM pedidos p
       JOIN DetallePedido dp ON p.id_pedido = dp.id_pedido
       JOIN Productos prod ON dp.id_producto = prod.id_producto
       WHERE p.id_pedido = ?`,
      [id]
    );
    res.json(details);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener detalles del pedido', detalles: error.message });
  }
};