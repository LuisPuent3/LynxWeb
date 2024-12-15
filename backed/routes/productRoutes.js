const db = require('../config/db');

const ProductoController = {
  async getAllProducts(req, res) {
    try {
      const [productos] = await db.query('SELECT * FROM Productos');
      res.json(productos);
    } catch (error) {
      console.error('Error al obtener productos:', error);
      res.status(500).json({ mensaje: 'Error al obtener productos' });
    }
  },

  async addProduct(req, res) {
    try {
      const { nombre, precio, descripcion } = req.body;
      const query = 'INSERT INTO Productos (nombre, precio, descripcion) VALUES (?, ?, ?)';
      const [result] = await db.query(query, [nombre, precio, descripcion]);
      res.status(201).json({ mensaje: 'Producto agregado', id: result.insertId });
    } catch (error) {
      console.error('Error al agregar producto:', error);
      res.status(500).json({ mensaje: 'Error al agregar producto' });
    }
  },

  async updateProduct(req, res) {
    try {
      const { id } = req.params;
      const { nombre, precio, descripcion } = req.body;
      const query = 'UPDATE Productos SET nombre = ?, precio = ?, descripcion = ? WHERE id_producto = ?';
      await db.query(query, [nombre, precio, descripcion, id]);
      res.json({ mensaje: 'Producto actualizado' });
    } catch (error) {
      console.error('Error al actualizar producto:', error);
      res.status(500).json({ mensaje: 'Error al actualizar producto' });
    }
  },

  async deleteProduct(req, res) {
    try {
      const { id } = req.params;
      const query = 'DELETE FROM Productos WHERE id_producto = ?';
      await db.query(query, [id]);
      res.json({ mensaje: 'Producto eliminado' });
    } catch (error) {
      console.error('Error al eliminar producto:', error);
      res.status(500).json({ mensaje: 'Error al eliminar producto' });
    }
  }
};

module.exports = ProductoController;
