const db = require('../config/db');

// Crear un pedido
const createOrder = async (req, res) => {
    const { id_usuario, carrito, nombre_completo, telefono_contacto, informacion_adicional, metodo_pago } = req.body;
    
    if (!carrito || carrito.length === 0) {
        return res.status(400).json({ error: 'El carrito está vacío' });
    }
    
    // Iniciar una conexión para la transacción
    const connection = await db.getConnection();
    
    try {
        // Iniciar transacción
        await connection.beginTransaction();
        
        // Verificar stock disponible antes de procesar el pedido
        const stockChecks = await Promise.all(
            carrito.map(async ({ id_producto, cantidad }) => {
                const [productRows] = await connection.query(
                    'SELECT id_producto, nombre, cantidad as stock FROM Productos WHERE id_producto = ? FOR UPDATE',
                    [id_producto]
                );
                
                if (productRows.length === 0) {
                    return { 
                        disponible: false, 
                        producto: { id_producto },
                        mensaje: 'Producto no encontrado' 
                    };
                }
                
                const producto = productRows[0];
                return {
                    disponible: producto.stock >= cantidad,
                    producto,
                    cantidadSolicitada: cantidad,
                    mensaje: producto.stock >= cantidad 
                        ? 'Disponible' 
                        : `Stock insuficiente (${producto.stock} disponibles)`
                };
            })
        );
        
        // Filtrar productos sin stock suficiente
        const productosNoDisponibles = stockChecks.filter(check => !check.disponible);
        
        if (productosNoDisponibles.length > 0) {
            // Hacemos rollback y retornamos error
            await connection.rollback();
            connection.release();
            
            return res.status(400).json({
                error: 'Algunos productos no tienen stock suficiente',
                detalles: productosNoDisponibles
            });
        }
        
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
            if (!columnasExistentes.includes('total')) {
                await db.query('ALTER TABLE Pedidos ADD COLUMN total DECIMAL(10,2)');
                tablasActualizadas = true;
            }
            
            if (tablasActualizadas) {
                console.log('Se han añadido nuevas columnas a la tabla Pedidos');
            }
        } catch (error) {
            console.error('Error al verificar/actualizar estructura de tabla:', error);
            // Continuar con la creación del pedido aunque falle la verificación
        }
          // Calcular el total del pedido
        const total = carrito.reduce((sum, item) => sum + (item.cantidad * item.precio), 0);
        
        // Insertar el pedido principal con la estructura actualizada (dentro de la misma transacción)
        const [pedido] = await connection.query(
            `INSERT INTO Pedidos (
                id_usuario, estado, id_estado, 
                nombre_completo, telefono_contacto, 
                informacion_adicional, metodo_pago, total
            ) VALUES (?, 'pendiente', 1, ?, ?, ?, ?, ?)`,
            [id_usuario, nombre_completo || null, telefono_contacto || null, informacion_adicional || null, metodo_pago || 'efectivo', total]
        );
        const id_pedido = pedido.insertId;

        // Insertar cada producto en DetallePedido (dentro de la misma transacción)
        for (const { id_producto, cantidad, precio } of carrito) {
            const subtotal = cantidad * precio;
            await connection.query(
                `INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) 
                VALUES (?, ?, ?, ?)`,
                [id_pedido, id_producto, cantidad, subtotal]
            );
        }
        
        // No actualizamos el stock aquí, lo haremos cuando el pedido sea entregado
        
        // Confirmar transacción
        await connection.commit();
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
          
        // Liberar la conexión después de completar la transacción
        connection.release();
          res.status(201).json({ 
            mensaje: 'Pedido creado con éxito', 
            id_pedido,
            stockActualizado: false // Indicamos que el stock no se actualizó en este momento
        });
    } catch (error) {
        console.error('Error al crear pedido:', error);
        
        // Si hay algún error, hacer rollback de la transacción
        try {
            await connection.rollback();
        } catch (rollbackError) {
            console.error('Error al hacer rollback:', rollbackError);
        }
        
        // Liberar la conexión
        connection.release();
        
        // Proporcionar mensajes más descriptivos según el tipo de error
        if (error.name === 'ReferenceError') {
            console.error('Error de referencia (variable no definida):', error.message);
            res.status(500).json({ error: `Variable no definida: ${error.message}` });
        } else if (error.code && error.sqlMessage) {
            console.error('Error SQL:', error.sqlMessage);
            res.status(500).json({ error: `Error en base de datos: ${error.sqlMessage}` });
        } else {
            res.status(500).json({ error: error.message });
        }
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
                    p.nombre, p.precio, p.imagen
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
                    precio: p.precio,
                    imagen: p.imagen
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
            `SELECT p.id_pedido, p.id_usuario, u.correo AS usuario, p.fecha, p.estado, ep.nombre AS estado_nombre,
                    p.nombre_completo, p.telefono_contacto, p.informacion_adicional, p.metodo_pago, p.total
             FROM Pedidos p
             JOIN Usuarios u ON p.id_usuario = u.id_usuario
             LEFT JOIN EstadosPedidos ep ON p.id_estado = ep.id_estado
             ORDER BY p.fecha DESC`
        );
        
        // Si no hay totales calculados en algunos pedidos, intentar calcularlos
        const pedidosIds = orders.filter(p => p.total === null).map(p => p.id_pedido);
        
        // Solo si hay pedidos sin total calculado
        if (pedidosIds.length > 0) {
            try {
                // Obtener detalles y calcular totales
                const [detalles] = await db.query(
                    `SELECT id_pedido, SUM(subtotal) as total 
                     FROM DetallePedido 
                     WHERE id_pedido IN (?) 
                     GROUP BY id_pedido`,
                    [pedidosIds]
                );
                
                // Actualizar totales en los resultados
                for (const order of orders) {
                    if (order.total === null) {
                        const detalle = detalles.find(d => d.id_pedido === order.id_pedido);
                        if (detalle) {
                            order.total = detalle.total;
                            // Actualizar en la base de datos también
                            await db.query(
                                `UPDATE Pedidos SET total = ? WHERE id_pedido = ?`,
                                [detalle.total, order.id_pedido]
                            );
                        }
                    }
                }
            } catch (err) {
                console.error('Error al calcular totales faltantes:', err);
                // No interrumpir el flujo principal
            }
        }
        
        res.status(200).json(orders);
    } catch (error) {
        console.error('Error al obtener pedidos:', error);
        res.status(500).json({ error: error.message });
    }
};

// Actualizar estado de un pedido
const updateOrderStatus = async (req, res) => {
    const { id } = req.params;
    const { id_estado, estado } = req.body;
    
    // Iniciar una conexión para posible transacción
    const connection = await db.getConnection();
    
    try {
        // Iniciar transacción si el estado es "entregado" o "cancelado"
        if (estado === 'entregado' || estado === 'cancelado') {
            await connection.beginTransaction();
        }
        
        // Actualizamos ambos campos de estado para mantener consistencia
        const [result] = await connection.query(
            `UPDATE Pedidos SET id_estado = ?, estado = ? WHERE id_pedido = ?`,
            [id_estado, estado, id]
        );
        
        if (result.affectedRows === 0) {
            if (estado === 'entregado' || estado === 'cancelado') {
                await connection.rollback();
            }
            connection.release();
            return res.status(404).json({ message: 'Pedido no encontrado' });
        }
        
        // Si el estado es "entregado", actualizar el stock
        if (estado === 'entregado') {
            console.log(`[pedidoController] Actualizando stock para pedido ${id} marcado como entregado`);
            
            // Obtener todos los productos del pedido
            const [detalles] = await connection.query(
                `SELECT id_producto, cantidad FROM DetallePedido WHERE id_pedido = ?`,
                [id]
            );
            
            console.log(`[pedidoController] ${detalles.length} productos encontrados para actualizar stock`);
            
            // Actualizar el stock de cada producto
            for (const { id_producto, cantidad } of detalles) {
                console.log(`[pedidoController] Actualizando stock del producto ${id_producto}, reduciendo ${cantidad} unidades`);
                
                const [updateResult] = await connection.query(
                    `UPDATE Productos SET cantidad = cantidad - ? WHERE id_producto = ? AND cantidad >= ?`,
                    [cantidad, id_producto, cantidad]
                );
                
                if (updateResult.affectedRows === 0) {
                    // Si algún producto no tenía stock suficiente, registramos el error pero continuamos
                    console.warn(`No se pudo actualizar el stock del producto ${id_producto}. Stock insuficiente.`);
                }
            }
            
            // Confirmar la transacción
            await connection.commit();
            connection.release();
            console.log(`[pedidoController] Stock actualizado correctamente para el pedido ${id}`);
            
            res.status(200).json({ 
                message: 'Estado del pedido actualizado y stock descontado', 
                stockActualizado: true 
            });
        }
        // Si el estado es "cancelado" y el pedido estaba previamente "entregado",
        // podríamos restaurar el stock (implementación futura)
        else {
            // Para otros estados, simplemente devolvemos éxito
            if (estado === 'entregado' || estado === 'cancelado') {
                await connection.commit();
            }
            connection.release();
            res.status(200).json({ message: 'Estado del pedido actualizado' });
        }
    } catch (error) {
        console.error(`[pedidoController] Error al actualizar estado del pedido ${id}:`, error);
        
        // Si hay un error y estábamos en una transacción, hacer rollback
        if (estado === 'entregado' || estado === 'cancelado') {
            try {
                await connection.rollback();
            } catch (rollbackError) {
                console.error('Error al hacer rollback:', rollbackError);
            }
        }
        
        connection.release();
        res.status(500).json({ error: error.message });
    }
};

// Obtener un pedido específico con sus detalles
const getOrderById = async (req, res) => {
    let { id } = req.params;
    
    console.log(`[pedidoController.js] Recibido ID: ${id}, tipo: ${typeof id}`);
    
    // Asegurar que id sea un número
    id = parseInt(id, 10);
    
    if (isNaN(id) || id <= 0) {
        console.error(`[pedidoController.js] Error: ID de pedido inválido: ${id}`);
        return res.status(400).json({ error: 'ID de pedido inválido' });
    }
    
    console.log(`[pedidoController.js] Buscando detalles del pedido con ID: ${id}`);

    try {
        // Obtener información básica del pedido
        console.log('[pedidoController.js] Ejecutando consulta para obtener datos básicos del pedido');
        const [orderData] = await db.query(
            `SELECT p.id_pedido, p.id_usuario, p.fecha, p.estado, ep.nombre AS estado_nombre, 
                   p.nombre_completo, p.telefono_contacto, p.informacion_adicional, p.metodo_pago, p.total,
                   u.correo AS usuario
             FROM Pedidos p
             LEFT JOIN Usuarios u ON p.id_usuario = u.id_usuario
             LEFT JOIN EstadosPedidos ep ON p.id_estado = ep.id_estado
             WHERE p.id_pedido = ?`,
            [id]
        );
        console.log(`[pedidoController.js] Resultado de consulta básica:`, orderData.length > 0 ? 'Pedido encontrado' : 'Pedido no encontrado');

        if (orderData.length === 0) {
            console.error(`[pedidoController.js] Error: Pedido ${id} no encontrado en la base de datos`);
            return res.status(404).json({ error: 'Pedido no encontrado' });
        }

        const order = orderData[0];
        console.log(`[pedidoController.js] Datos básicos del pedido:`, { 
            id_pedido: order.id_pedido,
            id_usuario: order.id_usuario,
            estado: order.estado,
            total: order.total
        });

        // Obtener detalles de productos
        console.log('[pedidoController.js] Consultando detalles de productos del pedido');
        const [productsData] = await db.query(
            `SELECT dp.id_detalle, dp.id_producto, dp.cantidad, dp.subtotal,
                    p.nombre, p.precio, p.imagen
             FROM DetallePedido dp
             JOIN Productos p ON dp.id_producto = p.id_producto
             WHERE dp.id_pedido = ?`,
            [id]
        );
        console.log(`[pedidoController.js] Productos encontrados: ${productsData.length}`);

        // Añadir productos al objeto del pedido
        order.productos = productsData.map(product => ({
            id_detalle: product.id_detalle,
            id_producto: product.id_producto,
            nombre: product.nombre,
            cantidad: product.cantidad,
            precio: product.precio,
            subtotal: product.subtotal,
            imagen: product.imagen
        }));

        console.log(`[pedidoController.js] Enviando respuesta completa para pedido ${id} con ${productsData.length} productos`);
        res.status(200).json(order);
    } catch (error) {
        console.error(`[pedidoController.js] Error al obtener pedido ${id}:`, error);
        res.status(500).json({ error: error.message, controllerError: 'getOrderById' });
    }
};

module.exports = { createOrder, getOrdersByUser, getAllOrders, updateOrderStatus, getOrderById };
