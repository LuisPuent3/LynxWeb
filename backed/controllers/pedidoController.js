const db = require('../config/db');

// Crear un pedido
const createOrder = async (req, res) => {
    const { id_usuario, productos } = req.body; // productos es un array [{ id_producto, cantidad, subtotal }]
    try {
        const [pedido] = await db.query(
            `INSERT INTO Pedidos (id_usuario, id_estado) VALUES (?, 1)`,
            [id_usuario]
        );
        const id_pedido = pedido.insertId;

        const detallePromises = productos.map(({ id_producto, cantidad, subtotal }) => {
            return db.query(
                `INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) 
                VALUES (?, ?, ?, ?)`,
                [id_pedido, id_producto, cantidad, subtotal]
            );
        });

        await Promise.all(detallePromises);
        res.status(201).json({ message: 'Pedido creado con éxito', id_pedido });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// Obtener pedidos de un usuario
const getOrdersByUser = async (req, res) => {
    const { id } = req.params;
    try {
        const [orders] = await db.query(
            `SELECT p.id_pedido, p.fecha, ep.nombre AS estado
             FROM Pedidos p
             JOIN EstadosPedidos ep ON p.id_estado = ep.id_estado
             WHERE p.id_usuario = ?`,
            [id]
        );
        res.status(200).json(orders);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// Obtener todos los pedidos
const getAllOrders = async (req, res) => {
    try {
        const [orders] = await db.query(
            `SELECT p.id_pedido, u.correo AS usuario, p.fecha, ep.nombre AS estado
             FROM Pedidos p
             JOIN Usuarios u ON p.id_usuario = u.id_usuario
             JOIN EstadosPedidos ep ON p.id_estado = ep.id_estado`
        );
        res.status(200).json(orders);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// Actualizar estado de un pedido
const updateOrderStatus = async (req, res) => {
    const { id } = req.params;
    const { id_estado } = req.body;
    try {
        const [result] = await db.query(
            `UPDATE Pedidos SET id_estado = ? WHERE id_pedido = ?`,
            [id_estado, id]
        );
        if (result.affectedRows === 0) {
            return res.status(404).json({ message: 'Pedido no encontrado' });
        }
        res.status(200).json({ message: 'Estado del pedido actualizado' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = { createOrder, getOrdersByUser, getAllOrders, updateOrderStatus };

exports.crearPedido = async (req, res) => {
    const { carrito, id_usuario, id_estado } = req.body;
  
    if (!carrito || carrito.length === 0) {
      return res.status(400).json({ mensaje: "El carrito está vacío" });
    }
  
    try {
      const [pedido] = await db.execute(
        "INSERT INTO Pedidos (id_usuario, id_estado) VALUES (?, ?)",
        [id_usuario, id_estado || 1]
      );
  
      const id_pedido = pedido.insertId;
  
      for (const item of carrito) {
        await db.execute(
          "INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) VALUES (?, ?, ?, ?)",
          [id_pedido, item.id_producto, item.cantidad, item.cantidad * item.precio]
        );
      }
  
      res.status(201).json({ mensaje: "Pedido creado con éxito", id_pedido });
    } catch (error) {
      console.error(error);
      res.status(500).json({ mensaje: "Error al crear el pedido" });
    }
  };
  