const pool = require('../config/db');

exports.createOrder = async (req, res) => {
  const { carrito, id_usuario } = req.body;

  try {
    const [orderResult] = await pool.query(
      'INSERT INTO Pedidos (id_usuario, id_estado) VALUES (?, 1)',
      [id_usuario]
    );
    const id_pedido = orderResult.insertId;

    const detalles = carrito.map((item) => [
      id_pedido,
      item.id_producto,
      item.cantidad,
      item.cantidad * item.precio,
    ]);

    await pool.query(
      'INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) VALUES ?',
      [detalles]
    );

    res.status(201).json({ mensaje: 'Pedido creado exitosamente', id_pedido });
  } catch (error) {
    res.status(500).json({ error: 'Error al crear pedido', detalles: error });
  }
};

exports.getOrdersByUser = async (req, res) => {
  const { id_usuario } = req.params;

  try {
    const [orders] = await pool.query(
      'SELECT * FROM Pedidos WHERE id_usuario = ?',
      [id_usuario]
    );
    res.json(orders);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener pedidos', detalles: error });
  }
};

exports.getOrderDetails = async (req, res) => {
  const { id } = req.params;

  try {
    const [details] = await pool.query(
      `SELECT p.id_pedido, p.fecha, dp.id_producto, prod.nombre, dp.cantidad, dp.subtotal
       FROM Pedidos p
       JOIN DetallePedido dp ON p.id_pedido = dp.id_pedido
       JOIN Productos prod ON dp.id_producto = prod.id_producto
       WHERE p.id_pedido = ?`,
      [id]
    );
    res.json(details);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener detalles del pedido', detalles: error });
  }
};
