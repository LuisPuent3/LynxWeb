const pool = require('../config/db');

exports.getCart = async (req, res) => {
  const { id_usuario } = req.params;

  try {
    const [items] = await pool.query(
      `SELECT dp.id_detalle, dp.id_producto, prod.nombre, dp.cantidad, dp.subtotal
       FROM Pedidos p
       JOIN DetallePedido dp ON p.id_pedido = dp.id_pedido
       JOIN Productos prod ON dp.id_producto = prod.id_producto
       WHERE p.id_usuario = ? AND p.id_estado = 1`,
      [id_usuario]
    );
    res.json(items);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener el carrito', detalles: error });
  }
};

exports.addToCart = async (req, res) => {
  const { id_usuario, id_producto, cantidad } = req.body;

  try {
    const [[product]] = await pool.query('SELECT precio FROM Productos WHERE id_producto = ?', [
      id_producto,
    ]);

    const subtotal = cantidad * product.precio;

    await pool.query(
      `INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal)
       VALUES ((SELECT id_pedido FROM Pedidos WHERE id_usuario = ? AND id_estado = 1), ?, ?, ?)`,
      [id_usuario, id_producto, cantidad, subtotal]
    );

    res.status(201).json({ mensaje: 'Producto agregado al carrito' });
  } catch (error) {
    res.status(500).json({ error: 'Error al agregar al carrito', detalles: error });
  }
};

exports.removeFromCart = async (req, res) => {
  const { id } = req.params;

  try {
    await pool.query('DELETE FROM DetallePedido WHERE id_detalle = ?', [id]);
    res.json({ mensaje: 'Producto eliminado del carrito' });
  } catch (error) {
    res.status(500).json({ error: 'Error al eliminar producto', detalles: error });
  }
};
