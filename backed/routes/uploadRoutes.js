const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Directorio de uploads
const uploadDir = path.join(__dirname, '../../uploads');

// Asegurarnos de que el directorio de uploads exista
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
    console.log('Directorio de uploads creado:', uploadDir);
}

// Configuración básica para guardar archivos temporalmente en memoria
const upload = multer({ 
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 5 * 1024 * 1024 // Límite de 5MB
    },
    fileFilter: function(req, file, cb) {
        // Aceptar solo imágenes
        if (file.mimetype.startsWith('image/')) {
            cb(null, true);
        } else {
            cb(new Error('Solo se permiten archivos de imagen'), false);
        }
    }
});

// Ruta para subir una imagen
router.post('/', upload.single('imagen'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No se ha proporcionado ninguna imagen' });
        }
        
        // Generar nombre de archivo único
        const uniqueName = Date.now() + '-' + Math.round(Math.random() * 1E9) + path.extname(req.file.originalname);
        const filePath = path.join(uploadDir, uniqueName);
        
        // Escribir el archivo al disco
        fs.writeFileSync(filePath, req.file.buffer);
        
        // Devolver ruta de la imagen
        res.status(201).json({ 
            message: 'Imagen subida correctamente',
            filename: uniqueName,
            path: `/uploads/${uniqueName}`
        });
    } catch (error) {
        console.error('Error al subir imagen:', error);
        res.status(500).json({ error: error.message });
    }
});

// Ruta para subir una imagen con nombre personalizado
router.post('/custom', upload.single('imagen'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No se ha proporcionado ninguna imagen' });
        }
        
        console.log('Datos recibidos:', {
            fieldname: req.file.fieldname,
            mimetype: req.file.mimetype,
            size: req.file.size,
            originalname: req.file.originalname
        });
        
        console.log('Body completo:', req.body);
        
        // Verificar y extraer el nombre personalizado
        let customFilename = req.body.customFilename;
        
        if (!customFilename) {
            console.warn('No se recibió nombre personalizado, usando nombre por defecto');
            customFilename = Date.now() + '-' + Math.round(Math.random() * 1E9) + path.extname(req.file.originalname);
        } else {
            console.log('Nombre personalizado recibido:', customFilename);
            
            // Verificar que el nombre tenga una extensión válida
            const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];
            let hasValidExtension = false;
            
            for (const ext of validExtensions) {
                if (customFilename.toLowerCase().endsWith(ext)) {
                    hasValidExtension = true;
                    break;
                }
            }
            
            // Si no tiene extensión, añadir la del archivo original
            if (!hasValidExtension) {
                const originalExt = path.extname(req.file.originalname);
                customFilename = `${customFilename}${originalExt}`;
                console.log('Añadida extensión al nombre:', customFilename);
            }
        }
        
        // Ruta donde se guardará el archivo
        const filePath = path.join(uploadDir, customFilename);
        
        // Si ya existe un archivo con ese nombre, eliminarlo
        if (fs.existsSync(filePath)) {
            console.log(`El archivo ${customFilename} ya existe y será reemplazado`);
            fs.unlinkSync(filePath);
        }
        
        // Guardar la imagen directamente con el nombre personalizado
        fs.writeFileSync(filePath, req.file.buffer);
        
        // Verificar que el archivo se haya guardado correctamente
        if (!fs.existsSync(filePath)) {
            console.error(`Error: No se pudo guardar ${customFilename}`);
            return res.status(500).json({ error: 'Error al guardar la imagen' });
        }
        
        console.log(`Archivo guardado exitosamente como ${customFilename}`);
        
        // Devolver información del archivo guardado
        res.status(201).json({ 
            message: 'Imagen subida correctamente',
            filename: customFilename,
            path: `/uploads/${customFilename}`
        });
    } catch (error) {
        console.error('Error al subir imagen personalizada:', error);
        res.status(500).json({ error: error.message });
    }
});

// Ruta para cargar una imagen temporal (productos nuevos)
router.post('/temp', upload.single('imagen'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No se ha proporcionado ninguna imagen' });
        }
        
        // Generar nombre temporal
        const tempName = 'temp-' + Date.now() + '-' + Math.round(Math.random() * 1E9) + path.extname(req.file.originalname);
        const filePath = path.join(uploadDir, tempName);
        
        // Escribir el archivo al disco
        fs.writeFileSync(filePath, req.file.buffer);
        
        // Devolver ruta de la imagen temporal
        res.status(201).json({ 
            message: 'Imagen temporal subida correctamente',
            filename: tempName,
            path: `/uploads/${tempName}`
        });
    } catch (error) {
        console.error('Error al subir imagen temporal:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 