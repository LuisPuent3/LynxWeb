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
        // Primero obtenemos el producto para eliminar la imagen si existe
        const [producto] = await connection.query('SELECT imagen FROM Productos WHERE id_producto = ?', [req.params.id]);
        
        if (producto.length > 0 && producto[0].imagen) {
            const fs = require('fs');
            const path = require('path');
            const imagePath = path.join(__dirname, '../../uploads', producto[0].imagen);
            
            // Verificar si el archivo existe antes de intentar eliminarlo
            if (fs.existsSync(imagePath)) {
                fs.unlinkSync(imagePath);
            }
        }
        
        await connection.query('DELETE FROM Productos WHERE id_producto = ?', [req.params.id]);
        res.json({ message: 'Producto eliminado exitosamente' });
    } catch (error) {
        console.error('Error en deleteProduct:', error);
        res.status(500).json({ error: error.message });
    }
};

// Nuevo método para actualizar solo la imagen de un producto
exports.updateProductImage = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No se ha proporcionado ninguna imagen' });
        }
        
        const productId = req.params.id;
        const newImageName = req.file.filename;
        
        const connection = await db;
        
        // Primero obtener la imagen actual para eliminarla
        const [producto] = await connection.query('SELECT imagen FROM Productos WHERE id_producto = ?', [productId]);
        
        if (producto.length === 0) {
            return res.status(404).json({ message: 'Producto no encontrado' });
        }
        
        // Eliminar la imagen anterior si existe
        if (producto[0].imagen) {
            const fs = require('fs');
            const path = require('path');
            const oldImagePath = path.join(__dirname, '../../uploads', producto[0].imagen);
            
            if (fs.existsSync(oldImagePath)) {
                fs.unlinkSync(oldImagePath);
            }
        }
        
        // Actualizar con la nueva imagen
        await connection.query('UPDATE Productos SET imagen = ? WHERE id_producto = ?', [newImageName, productId]);
        
        res.json({ 
            message: 'Imagen de producto actualizada exitosamente',
            filename: newImageName 
        });
    } catch (error) {
        console.error('Error en updateProductImage:', error);
        res.status(500).json({ error: error.message });
    }
};