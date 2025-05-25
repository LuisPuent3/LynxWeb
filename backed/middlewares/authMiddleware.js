const jwt = require('jsonwebtoken');
const db = require('../config/db');

const verifyToken = (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Token no proporcionado' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.userId = decoded.id;
        req.userRole = decoded.rol;
        next();
    } catch (error) {
        if (error.name === 'TokenExpiredError') {
            return res.status(401).json({ error: 'Token expirado' });
        }
        return res.status(401).json({ error: 'Token inválido' });
    }
};

const verifyRole = (roles) => {
    return async (req, res, next) => {
        try {
            if (!req.userRole) {
                const query = `
                    SELECT r.nombre as rol 
                    FROM usuarios u 
                    JOIN Roles r ON u.id_rol = r.id_rol 
                    WHERE u.id_usuario = ?
                `;
                
                const [results] = await db.query(query, [req.userId]);
                
                if (results.length === 0) {
                    return res.status(404).json({ error: 'Usuario no encontrado' });
                }

                req.userRole = results[0].rol;
            }
            
            if (!roles.includes(req.userRole)) {
                return res.status(403).json({ 
                    error: 'No tiene permisos para realizar esta acción',
                    requiredRoles: roles,
                    userRole: req.userRole
                });
            }

            next();
        } catch (error) {
            console.error('Error en middleware de roles:', error);
            res.status(500).json({ error: 'Error al verificar permisos' });
        }
    };
};

module.exports = {
    verifyToken,
    verifyRole
};
