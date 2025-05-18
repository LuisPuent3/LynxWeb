const db = require('../config/db');
const path = require('path');
const fs = require('fs');

// Imagen por defecto
const DEFAULT_IMAGE = 'default.jpg';

// Directorio de uploads
const uploadsDir = path.join(__dirname, '../../uploads');

// Función para verificar si una imagen existe
function imageExists(filename) {
    if (!filename) return false;
    const filePath = path.join(uploadsDir, filename);
    return fs.existsSync(filePath);
}

// Función para obtener un nombre de imagen válido
function getValidImageName(filename) {
    // Si no se proporciona nombre o es la imagen por defecto, devolver la imagen por defecto
    if (!filename || filename === DEFAULT_IMAGE) {
        return DEFAULT_IMAGE;
    }
    
    // Verificar si la imagen existe
    if (imageExists(filename)) {
        return filename;
    }
    
    // Si la imagen no existe, devolver la imagen por defecto
    console.warn(`Advertencia: La imagen ${filename} no existe en uploads, se usará ${DEFAULT_IMAGE}`);
    return DEFAULT_IMAGE;
}

// Asegurarnos de que existe el directorio de uploads
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
    console.log('Directorio de uploads creado:', uploadsDir);
}

// Asegurarnos de que existe la imagen por defecto
const defaultImagePath = path.join(uploadsDir, DEFAULT_IMAGE);
if (!fs.existsSync(defaultImagePath)) {
    console.log('Creando imagen por defecto');
    const svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <rect width="200" height="200" fill="#f8f9fa"/>
        <text x="100" y="100" font-family="Arial" font-size="14" text-anchor="middle" fill="#6c757d">Producto sin imagen</text>
    </svg>`;
    
    fs.writeFileSync(defaultImagePath, svgContent);
}

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
        
        // Verificar que la imagen existe, si no, usar la imagen por defecto
        const imagenFinal = getValidImageName(imagen);
        
        // Verificar si ya existe un producto con el mismo nombre
        const connection = await db;
        const [existingProducts] = await connection.query('SELECT * FROM Productos WHERE nombre = ?', [nombre]);
        
        if (existingProducts.length > 0) {
            return res.status(400).json({ 
                error: 'Ya existe un producto con este nombre',
                code: 'DUPLICATE_NAME'
            });
        }
        
        const query = 'INSERT INTO Productos (nombre, precio, cantidad, id_categoria, imagen) VALUES (?, ?, ?, ?, ?)';
        const [result] = await connection.query(query, [nombre, precio, cantidad, id_categoria, imagenFinal]);
        
        res.status(201).json({ 
            message: 'Producto creado exitosamente',
            id: result.insertId,
            imagen: imagenFinal
        });
    } catch (error) {
        console.error('Error en createProduct:', error);
        
        // Verificar si es un error de clave duplicada
        if (error.code === 'ER_DUP_ENTRY') {
            if (error.message.includes("for key 'nombre'")) {
                return res.status(400).json({ 
                    error: 'Ya existe un producto con este nombre',
                    code: 'DUPLICATE_NAME'
                });
            }
            return res.status(400).json({ 
                error: 'Entrada duplicada en la base de datos',
                code: 'DUPLICATE_ENTRY'
            });
        }
        
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
        const productId = req.params.id;
        
        // Verificar si la imagen existe
        const imagenFinal = getValidImageName(imagen);
        
        const connection = await db;
        
        // Verificar si ya existe otro producto con el mismo nombre
        const [existingProducts] = await connection.query(
            'SELECT * FROM Productos WHERE nombre = ? AND id_producto != ?', 
            [nombre, productId]
        );
        
        if (existingProducts.length > 0) {
            return res.status(400).json({ 
                error: 'Ya existe otro producto con este nombre',
                code: 'DUPLICATE_NAME'
            });
        }
        
        const query = 'UPDATE Productos SET nombre = ?, precio = ?, cantidad = ?, id_categoria = ?, imagen = ? WHERE id_producto = ?';
        
        await connection.query(query, [nombre, precio, cantidad, id_categoria, imagenFinal, productId]);
        res.json({ 
            message: 'Producto actualizado exitosamente',
            imagen: imagenFinal
        });
    } catch (error) {
        console.error('Error en updateProduct:', error);
        
        // Verificar si es un error de clave duplicada
        if (error.code === 'ER_DUP_ENTRY') {
            if (error.message.includes("for key 'nombre'")) {
                return res.status(400).json({ 
                    error: 'Ya existe otro producto con este nombre',
                    code: 'DUPLICATE_NAME'
                });
            }
            return res.status(400).json({ 
                error: 'Entrada duplicada en la base de datos',
                code: 'DUPLICATE_ENTRY'
            });
        }
        
        res.status(500).json({ error: error.message });
    }
};

exports.deleteProduct = async (req, res) => {
    try {
        const connection = await db;
        // Primero obtenemos el producto para eliminar la imagen si existe
        const [producto] = await connection.query('SELECT imagen FROM Productos WHERE id_producto = ?', [req.params.id]);
        
        if (producto.length > 0 && producto[0].imagen && producto[0].imagen !== DEFAULT_IMAGE) {
            const imagePath = path.join(uploadsDir, producto[0].imagen);
            
            // Verificar si el archivo existe antes de intentar eliminarlo
            if (fs.existsSync(imagePath)) {
                fs.unlinkSync(imagePath);
                console.log(`Imagen eliminada: ${producto[0].imagen}`);
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
        
        // Verificar que la imagen se guardó correctamente
        if (!imageExists(newImageName)) {
            return res.status(500).json({ error: 'Error al guardar la imagen' });
        }
        
        const connection = await db;
        
        // Primero obtener la imagen actual para eliminarla
        const [producto] = await connection.query('SELECT imagen FROM Productos WHERE id_producto = ?', [productId]);
        
        if (producto.length === 0) {
            return res.status(404).json({ message: 'Producto no encontrado' });
        }
        
        // Eliminar la imagen anterior si existe
        if (producto[0].imagen && producto[0].imagen !== DEFAULT_IMAGE) {
            const oldImagePath = path.join(uploadsDir, producto[0].imagen);
            
            if (fs.existsSync(oldImagePath)) {
                fs.unlinkSync(oldImagePath);
                console.log(`Imagen anterior eliminada: ${producto[0].imagen}`);
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