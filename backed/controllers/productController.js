const db = require('../config/db');

exports.getProducts = (req, res) => {
    const query = 'SELECT * FROM Productos';
    db.query(query, (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(results);
    });
};

exports.createProduct = (req, res) => {
    const { nombre, precio, cantidad, id_categoria, imagen } = req.body;
    const query = 'INSERT INTO Productos (nombre, precio, cantidad, id_categoria, imagen) VALUES (?, ?, ?, ?, ?)';
    db.query(query, [nombre, precio, cantidad, id_categoria, imagen], (err, result) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.status(201).json({ id: result.insertId, ...req.body });
    });
};

exports.getProductById = (req, res) => {
    const query = 'SELECT * FROM Productos WHERE id_producto = ?';
    db.query(query, [req.params.id], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ message: 'Producto no encontrado' });
        }
        res.json(results[0]);
    });
};

exports.updateProduct = (req, res) => {
    const { nombre, precio, cantidad, id_categoria, imagen } = req.body;
    const query = 'UPDATE Productos SET nombre = ?, precio = ?, cantidad = ?, id_categoria = ?, imagen = ? WHERE id_producto = ?';
    db.query(query, [nombre, precio, cantidad, id_categoria, imagen, req.params.id], (err, result) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({ message: 'Producto actualizado' });
    });
};

exports.deleteProduct = (req, res) => {
    const query = 'DELETE FROM Productos WHERE id_producto = ?';
    db.query(query, [req.params.id], (err, result) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({ message: 'Producto eliminado' });
    });
};