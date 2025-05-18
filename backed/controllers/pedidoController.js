const db = require('../config/db');

// Crear un pedido
const createOrder = async (req, res) => {
    const { id_usuario, carrito, nombre_completo, telefono_contacto, informacion_adicional, metodo_pago } = req.body;
    
    if (!carrito || carrito.length === 0) {
        return res.status(400).json({ error: 'El carrito está vacío' });
    }
    
    try {
        // Verificar si la tabla Pedidos tiene las columnas necesarias
        let tablasActualizadas = false;
        
        try {
            // Verificar si las columnas existen
            const [columnas] = await db.query('SHOW COLUMNS FROM Pedidos');
            const columnasExistentes = columnas.map(col => col.Field);
            
            // Si no existen las columnas adicionales, añadirlas
            if (!columnasExistentes.includes('nombre_completo')) {
                await db.query('ALTER TABLE Pedidos ADD COLUMN nombre_completo VARCHAR(100)');
                tablasActualizadas = true;
            }
            if (!columnasExistentes.includes('telefono_contacto')) {
                await db.query('ALTER TABLE Pedidos ADD COLUMN telefono_contacto VARCHAR(20)');
                tablasActualizadas = true;
            }
            if (!columnasExistentes.includes('informacion_adicional')) {
                await db.query('ALTER TABLE Pedidos ADD COLUMN informacion_adicional TEXT');
                tablasActualizadas = true;
            }
            if (!columnasExistentes.includes('metodo_pago')) {
                await db.query('ALTER TABLE Pedidos ADD COLUMN metodo_pago VARCHAR(20) DEFAULT "efectivo"');
                tablasActualizadas = true;
            }
            
            if (tablasActualizadas) {
                console.log('Se han añadido nuevas columnas a la tabla Pedidos');
            }
        } catch (error) {
            console.error('Error al verificar/actualizar estructura de tabla:', error);
            // Continuar con la creación del pedido aunque falle la verificación
        }
        
        // Insertar el pedido principal con la estructura actualizada
        const [pedido] = await db.query(
            `INSERT INTO Pedidos (
                id_usuario, estado, id_estado, 
                nombre_completo, telefono_contacto, 
                informacion_adicional, metodo_pago
            ) VALUES (?, 'pendiente', 1, ?, ?, ?, ?)`,
            [id_usuario, nombre_completo || null, telefono_contacto || null, informacion_adicional || null, metodo_pago || 'efectivo']
        );
        const id_pedido = pedido.insertId;

        // Insertar cada producto en DetallePedido
        const detallePromises = carrito.map(({ id_producto, cantidad, precio }) => {
            const subtotal = cantidad * precio;
            return db.query(
                `INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) 
                VALUES (?, ?, ?, ?)`,
                [id_pedido, id_producto, cantidad, subtotal]
            );
        });

        await Promise.all(detallePromises);
        
        // Si es un usuario invitado o nuevo, actualizar su teléfono en la BD
        if (telefono_contacto) {
            try {
                // Primero verificar si el usuario existe y tiene un teléfono generado automáticamente
                const [usuario] = await db.query(
                    'SELECT telefono FROM Usuarios WHERE id_usuario = ?',
                    [id_usuario]
                );
                
                if (usuario.length > 0) {
                    const telefonoActual = usuario[0].telefono;
                    // Actualizar solo si no tiene teléfono o si el teléfono comienza con '000' (generado automáticamente)
                    if (!telefonoActual || telefonoActual.startsWith('000')) {
                        await db.query(
                            'UPDATE Usuarios SET telefono = ? WHERE id_usuario = ?',
                            [telefono_contacto, id_usuario]
                        );
                        console.log(`Teléfono actualizado para el usuario ${id_usuario}`);
                    }
                }
            } catch (error) {
                console.error('Error al actualizar teléfono del usuario:', error);
                // No interrumpir el flujo si falla la actualización del teléfono
            }
        }
        
        res.status(201).json({ mensaje: 'Pedido creado con éxito', id_pedido });
    } catch (error) {
        console.error('Error al crear pedido:', error);
        res.status(500).json({ error: error.message });
    }
};

// Obtener pedidos de un usuario con detalles completos
const getOrdersByUser = async (req, res) => {
    console.log('[pedidoController.js] Entrando a getOrdersByUser');
    const { id } = req.params;
    
    console.log(`[pedidoController.js] Buscando pedidos para usuario con ID: ${id}`);
    console.log('[pedidoController.js] Parámetros completos de la solicitud:', req.params);
    
    if (!id) {
        console.error('[pedidoController.js] ID de usuario no encontrado en req.params');
        return res.status(400).json({ error: 'ID de usuario es requerido' });
    }

    try {
        // Primero obtenemos los pedidos básicos con la estructura actual
        const [orders] = await db.query(
            `SELECT p.id_pedido, p.fecha, p.estado, ep.nombre AS estado_nombre, 
                   p.nombre_completo, p.telefono_contacto, p.informacion_adicional, p.metodo_pago
             FROM Pedidos p
             LEFT JOIN EstadosPedidos ep ON p.id_estado = ep.id_estado
             WHERE p.id_usuario = ?
             ORDER BY p.fecha DESC`,
            [id]
        );
        console.log(`[pedidoController.js] Pedidos encontrados en DB: ${orders.length}`);

        // Si no hay pedidos, devolvemos array vacío
        if (orders.length === 0) {
            return res.status(200).json([]);
        }

        // Obtenemos todos los detalles de productos para todos los pedidos
        const pedidoIds = orders.map(order => order.id_pedido);
        console.log('[pedidoController.js] IDs de pedidos para buscar detalles:', pedidoIds);
        const [detalles] = await db.query(
            `SELECT dp.id_pedido, dp.id_producto, dp.cantidad, dp.subtotal, 
                    p.nombre, p.precio
             FROM DetallePedido dp
             JOIN Productos p ON dp.id_producto = p.id_producto
             WHERE dp.id_pedido IN (?)`,
            [pedidoIds]
        );
        console.log(`[pedidoController.js] Detalles de productos encontrados: ${detalles.length}`);

        // Calculamos el total para cada pedido y agregamos los productos
        const ordersWithDetails = orders.map(order => {
            const productos = detalles.filter(d => d.id_pedido === order.id_pedido);
            const total = productos.reduce((sum, p) => sum + Number(p.subtotal), 0);
            
            const estadoFinal = order.estado_nombre || order.estado;
            
            return {
                ...order,
                estado: estadoFinal.toLowerCase(),
                metodo_pago: order.metodo_pago || 'efectivo', 
                tracking_code: '', 
                total,
                productos: productos.map(p => ({
                    id_producto: p.id_producto,
                    nombre: p.nombre,
                    cantidad: p.cantidad,
                    precio: p.precio
                }))
            };
        });
        console.log('[pedidoController.js] Pedidos procesados con detalles:', ordersWithDetails.length);
        res.status(200).json(ordersWithDetails);
    } catch (error) {
        console.error('[pedidoController.js] Error al obtener pedidos del usuario:', error);
        res.status(500).json({ error: error.message, controllerError: 'getOrdersByUser' });
    }
};

// Obtener todos los pedidos
const getAllOrders = async (req, res) => {
    try {
        const [orders] = await db.query(
            `SELECT p.id_pedido, u.correo AS usuario, p.fecha, p.estado, ep.nombre AS estado_nombre,
                    p.nombre_completo, p.telefono_contacto, p.informacion_adicional, p.metodo_pago
             FROM Pedidos p
             JOIN Usuarios u ON p.id_usuario = u.id_usuario
             LEFT JOIN EstadosPedidos ep ON p.id_estado = ep.id_estado`
        );
        res.status(200).json(orders);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// Actualizar estado de un pedido
const updateOrderStatus = async (req, res) => {
    const { id } = req.params;
    const { id_estado, estado } = req.body;
    try {
        // Actualizamos ambos campos de estado para mantener consistencia
        const [result] = await db.query(
            `UPDATE Pedidos SET id_estado = ?, estado = ? WHERE id_pedido = ?`,
            [id_estado, estado, id]
        );
        if (result.affectedRows === 0) {
            return res.status(404).json({ message: 'Pedido no encontrado' });
        }
        res.status(200).json({ message: 'Estado del pedido actualizado' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = { createOrder, getOrdersByUser, getAllOrders, updateOrderStatus };
