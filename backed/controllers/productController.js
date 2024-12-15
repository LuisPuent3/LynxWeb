

const db = require('../config/db'); // Conexión a la base de datos

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
};

module.exports = ProductoController;
