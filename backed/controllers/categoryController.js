const db = require('../config/db');

exports.createCategory = async (req, res) => {
    try {
        const { nombre, descripcion } = req.body;
        const query = 'INSERT INTO Categorias (nombre, descripcion) VALUES (?, ?)';
        const [result] = await db.query(query, [nombre, descripcion]);
        res.status(201).json({ id: result.insertId, nombre, descripcion });
    } catch (err) {
        console.error('Error al crear categoría:', err);
        res.status(500).json({ error: err.message });
    }
};

exports.getCategories = async (req, res) => {
    try {
        const query = 'SELECT * FROM Categorias';
        const [results] = await db.query(query);
        res.json(results);
    } catch (err) {
        console.error('Error al obtener categorías:', err);
        res.status(500).json({ error: err.message });
    }
};

exports.getCategoryById = async (req, res) => {
    try {
        const query = 'SELECT * FROM Categorias WHERE id_categoria = ?';
        const [results] = await db.query(query, [req.params.id]);
        
        if (results.length === 0) {
            return res.status(404).json({ message: 'Categoría no encontrada' });
        }
        
        res.json(results[0]);
    } catch (err) {
        console.error('Error al obtener categoría por ID:', err);
        res.status(500).json({ error: err.message });
    }
};

exports.updateCategory = async (req, res) => {
    try {
        const { nombre, descripcion } = req.body;
        const query = 'UPDATE Categorias SET nombre = ?, descripcion = ? WHERE id_categoria = ?';
        await db.query(query, [nombre, descripcion, req.params.id]);
        res.json({ message: 'Categoría actualizada' });
    } catch (err) {
        console.error('Error al actualizar categoría:', err);
        res.status(500).json({ error: err.message });
    }
};

exports.deleteCategory = async (req, res) => {
    try {
        const query = 'DELETE FROM Categorias WHERE id_categoria = ?';
        await db.query(query, [req.params.id]);
        res.json({ message: 'Categoría eliminada' });
    } catch (err) {
        console.error('Error al eliminar categoría:', err);
        res.status(500).json({ error: err.message });
    }
};