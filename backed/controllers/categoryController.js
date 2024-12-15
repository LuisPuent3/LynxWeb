const db = require('../config/db');

exports.createCategory = (req, res) => {
    const { nombre, descripcion } = req.body;
    const query = 'INSERT INTO Categorias (nombre, descripcion) VALUES (?, ?)';
    db.query(query, [nombre, descripcion], (err, result) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.status(201).json({ id: result.insertId, nombre, descripcion });
    });
};

exports.getCategories = (req, res) => {
    const query = 'SELECT * FROM Categorias';
    db.query(query, (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(results);
    });
};

exports.getCategoryById = (req, res) => {
    const query = 'SELECT * FROM Categorias WHERE id_categoria = ?';
    db.query(query, [req.params.id], (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (results.length === 0) {
            return res.status(404).json({ message: 'Categoría no encontrada' });
        }
        res.json(results[0]);
    });
};

exports.updateCategory = (req, res) => {
    const { nombre, descripcion } = req.body;
    const query = 'UPDATE Categorias SET nombre = ?, descripcion = ? WHERE id_categoria = ?';
    db.query(query, [nombre, descripcion, req.params.id], (err, result) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({ message: 'Categoría actualizada' });
    });
};

exports.deleteCategory = (req, res) => {
    const query = 'DELETE FROM Categorias WHERE id_categoria = ?';
    db.query(query, [req.params.id], (err, result) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({ message: 'Categoría eliminada' });
    });
};