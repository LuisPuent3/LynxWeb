const db = require('../config/db');

exports.getProducts = async (req, res) => {
    try {
        const connection = await db;
        const [results] = await connection.query('SELECT * FROM Productos');
        res.json(results);
    } catch (error) {
        console.error('Error en getProducts:', error);
        res.status(500).json({ 
            error: 'Error interno del servidor',
            details: error.message 
        });
    }
};

exports.createProduct = async (req, res) => {
    try {
        const { nombre, precio, cantidad, id_categoria, imagen } = req.body;
        const connection = await db;
        const query = 'INSERT INTO Productos (nombre, precio, cantidad, id_categoria, imagen) VALUES (?, ?, ?, ?, ?)';
        const [result] = await connection.query(query, [nombre, precio, cantidad, id_categoria, imagen]);
        
        res.status(201).json({ 
            message: 'Producto creado exitosamente',
            id: result.insertId 
        });
    } catch (error) {
        console.error('Error en createProduct:', error);
        res.status(500).json({ error: error.message });
    }
};

exports.getProductById = async (req, res) => {
    try {
        const connection = await db;
        const [results] = await connection.query('SELECT * FROM Productos WHERE id_producto = ?', [req.params.id]);
        
        if (results.length === 0) {
            return res.status(404).json({ message: 'Producto no encontrado' });
        }
        res.json(results[0]);
    } catch (error) {
        console.error('Error en getProductById:', error);
        res.status(500).json({ error: error.message });
    }
};

exports.updateProduct = async (req, res) => {
    try {
        const { nombre, precio, cantidad, id_categoria, imagen } = req.body;
        const connection = await db;
        const query = 'UPDATE Productos SET nombre = ?, precio = ?, cantidad = ?, id_categoria = ?, imagen = ? WHERE id_producto = ?';
        
        await connection.query(query, [nombre, precio, cantidad, id_categoria, imagen, req.params.id]);
        res.json({ message: 'Producto actualizado exitosamente' });
    } catch (error) {
        console.error('Error en updateProduct:', error);
        res.status(500).json({ error: error.message });
    }
};

exports.deleteProduct = async (req, res) => {
    try {
        const connection = await db;
        await connection.query('DELETE FROM Productos WHERE id_producto = ?', [req.params.id]);
        res.json({ message: 'Producto eliminado exitosamente' });
    } catch (error) {
        console.error('Error en deleteProduct:', error);
        res.status(500).json({ error: error.message });
    }
};