const db = require('../config/db');

exports.getProducts = (req, res) => {
    try {
        const query = 'SELECT * FROM Productos';
        db.query(query, (err, results) => {
            if (err) {
                console.error('Error en la consulta:', err);
                return res.status(500).json({ 
                    error: 'Error al obtener productos',
                    details: err.message 
                });
            }
            res.json(results);
        });
    } catch (error) {
        console.error('Error en getProducts:', error);
        res.status(500).json({ 
            error: 'Error interno del servidor',
            details: error.message 
        });
    }
};

exports.createProduct = (req, res) => {
    try {
        const { nombre, precio, cantidad, id_categoria, imagen } = req.body;
        const query = 'INSERT INTO Productos (nombre, precio, cantidad, id_categoria, imagen) VALUES (?, ?, ?, ?, ?)';
        db.query(query, [nombre, precio, cantidad, id_categoria, imagen], (err, result) => {
            if (err) {
                console.error('Error al crear producto:', err);
                return res.status(500).json({ error: err.message });
            }
            res.status(201).json({ 
                message: 'Producto creado exitosamente',
                id: result.insertId 
            });
        });
    } catch (error) {
        console.error('Error en createProduct:', error);
        res.status(500).json({ error: error.message });
    }
};

exports.getProductById = (req, res) => {
    try {
        const query = 'SELECT * FROM Productos WHERE id_producto = ?';
        db.query(query, [req.params.id], (err, results) => {
            if (err) {
                console.error('Error al obtener producto:', err);
                return res.status(500).json({ error: err.message });
            }
            if (results.length === 0) {
                return res.status(404).json({ message: 'Producto no encontrado' });
            }
            res.json(results[0]);
        });
    } catch (error) {
        console.error('Error en getProductById:', error);
        res.status(500).json({ error: error.message });
    }
};

exports.updateProduct = (req, res) => {
    try {
        const { nombre, precio, cantidad, id_categoria, imagen } = req.body;
        const query = 'UPDATE Productos SET nombre = ?, precio = ?, cantidad = ?, id_categoria = ?, imagen = ? WHERE id_producto = ?';
        db.query(query, [nombre, precio, cantidad, id_categoria, imagen, req.params.id], (err, result) => {
            if (err) {
                console.error('Error al actualizar producto:', err);
                return res.status(500).json({ error: err.message });
            }
            res.json({ message: 'Producto actualizado exitosamente' });
        });
    } catch (error) {
        console.error('Error en updateProduct:', error);
        res.status(500).json({ error: error.message });
    }
};

exports.deleteProduct = (req, res) => {
    try {
        const query = 'DELETE FROM Productos WHERE id_producto = ?';
        db.query(query, [req.params.id], (err, result) => {
            if (err) {
                console.error('Error al eliminar producto:', err);
                return res.status(500).json({ error: err.message });
            }
            res.json({ message: 'Producto eliminado exitosamente' });
        });
    } catch (error) {
        console.error('Error en deleteProduct:', error);
        res.status(500).json({ error: error.message });
    }
};