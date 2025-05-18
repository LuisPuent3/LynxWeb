const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Configurar almacenamiento para multer
const storage = multer.diskStorage({
    destination: function(req, file, cb) {
        const uploadDir = path.join(__dirname, '../../uploads');
        // Crear directorio si no existe
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function(req, file, cb) {
        // Si se proporcionó un nombre personalizado, usarlo
        if (req.body && req.body.customFilename) {
            const customName = req.body.customFilename;
            cb(null, customName);
        } else {
            // Caso predeterminado: generar nombre único
            const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
            const ext = path.extname(file.originalname);
            cb(null, uniqueSuffix + ext);
        }
    }
});

// Filtrar archivos para aceptar solo imágenes
const fileFilter = (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
        cb(null, true);
    } else {
        cb(new Error('Solo se permiten archivos de imagen'), false);
    }
};

const upload = multer({ 
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 5 * 1024 * 1024 // Límite de 5MB
    }
});

// Ruta para subir una imagen
router.post('/', upload.single('imagen'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No se ha proporcionado ninguna imagen' });
        }
        
        // Devolver ruta de la imagen
        res.status(201).json({ 
            message: 'Imagen subida correctamente',
            filename: req.file.filename,
            path: `/uploads/${req.file.filename}`
        });
    } catch (error) {
        console.error('Error al subir imagen:', error);
        res.status(500).json({ error: error.message });
    }
});

// Ruta para cargar una imagen temporal (productos nuevos)
router.post('/temp', upload.single('imagen'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No se ha proporcionado ninguna imagen' });
        }
        
        // Devolver ruta de la imagen temporal
        res.status(201).json({ 
            message: 'Imagen temporal subida correctamente',
            filename: req.file.filename,
            path: `/uploads/${req.file.filename}`
        });
    } catch (error) {
        console.error('Error al subir imagen temporal:', error);
        res.status(500).json({ error: error.message });
    }
});

// Ruta para subir una imagen con nombre personalizado
router.post('/custom', upload.single('imagen'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No se ha proporcionado ninguna imagen' });
        }
        
        // Devolver ruta de la imagen con el nombre personalizado
        res.status(201).json({ 
            message: 'Imagen subida correctamente',
            filename: req.file.filename,
            path: `/uploads/${req.file.filename}`
        });
    } catch (error) {
        console.error('Error al subir imagen personalizada:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 