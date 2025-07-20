-- Script para poblar la base de datos lynxshop con datos de prueba
-- Base de datos para tienda de abarrotes escolar

USE lynxshop;

-- 1. Insertar Roles
INSERT IGNORE INTO Roles (nombre) VALUES 
('administrador'),
('cliente'),
('empleado'),
('supervisor');

-- 2. Insertar Nombres
INSERT IGNORE INTO Nombres (nombre, apellidoP, apellidoM) VALUES 
('Juan Carlos', 'García', 'López'),
('María Elena', 'Rodríguez', 'Martínez'),
('Pedro Antonio', 'Sánchez', 'Hernández'),
('Ana Sofía', 'López', 'García'),
('Luis Miguel', 'Hernández', 'Pérez'),
('Carmen Rosa', 'Martínez', 'Sánchez'),
('José Luis', 'Pérez', 'Rodríguez'),
('Lucía Isabel', 'González', 'Torres'),
('Roberto Carlos', 'Torres', 'González'),
('Patricia María', 'Ramírez', 'Morales');

-- 3. Insertar Usuarios (con contraseñas encriptadas)
INSERT IGNORE INTO Usuarios (id_nombre, correo, telefono, contraseña, id_rol) VALUES 
(1, 'admin@lynxshop.com', '5551234567', AES_ENCRYPT('admin123', 'clave_secreta'), 1),
(2, 'maria.rodriguez@email.com', '5551234568', AES_ENCRYPT('cliente123', 'clave_secreta'), 2),
(3, 'pedro.sanchez@email.com', '5551234569', AES_ENCRYPT('cliente123', 'clave_secreta'), 2),
(4, 'ana.lopez@email.com', '5551234570', AES_ENCRYPT('cliente123', 'clave_secreta'), 2),
(5, 'luis.hernandez@email.com', '5551234571', AES_ENCRYPT('empleado123', 'clave_secreta'), 3),
(6, 'carmen.martinez@email.com', '5551234572', AES_ENCRYPT('cliente123', 'clave_secreta'), 2),
(7, 'jose.perez@email.com', '5551234573', AES_ENCRYPT('supervisor123', 'clave_secreta'), 4),
(8, 'lucia.gonzalez@email.com', '5551234574', AES_ENCRYPT('cliente123', 'clave_secreta'), 2),
(9, 'roberto.torres@email.com', '5551234575', AES_ENCRYPT('empleado123', 'clave_secreta'), 3),
(10, 'patricia.ramirez@email.com', '5551234576', AES_ENCRYPT('cliente123', 'clave_secreta'), 2);

-- 4. Insertar Categorías
INSERT IGNORE INTO Categorias (nombre, descripcion) VALUES 
('bebidas', 'Refrescos, jugos, agua y bebidas calientes'),
('snacks', 'Botanas, papas fritas, galletas y dulces'),
('lacteos', 'Leche, yogurt, queso y derivados lácteos'),
('frutas', 'Frutas frescas y de temporada'),
('verduras', 'Verduras y hortalizas frescas'),
('panaderia', 'Pan, pasteles y productos de panadería'),
('carnes', 'Carnes frescas y embutidos'),
('abarrotes', 'Productos básicos y despensa'),
('limpieza', 'Productos de limpieza e higiene'),
('dulceria', 'Dulces, chocolates y golosinas');

-- 5. Insertar Estados de Pedidos
INSERT IGNORE INTO EstadosPedidos (nombre) VALUES 
('pendiente'),
('procesando'),
('enviado'),
('entregado'),
('cancelado');

-- 6. Insertar 50 Productos realistas para tienda escolar
INSERT IGNORE INTO Productos (nombre, precio, cantidad, id_categoria, imagen) VALUES 
-- Bebidas (id_categoria = 1)
('Coca Cola 600ml', 18.50, 45, 1, 'coca_cola_600ml.jpg'),
('Pepsi 600ml', 17.00, 38, 1, 'pepsi_600ml.jpg'),
('Sprite 600ml', 17.50, 42, 1, 'sprite_600ml.jpg'),
('Fanta Naranja 600ml', 17.50, 35, 1, 'fanta_naranja_600ml.jpg'),
('Agua Bonafont 500ml', 12.00, 65, 1, 'agua_bonafont_500ml.jpg'),
('Jumex Durazno 500ml', 14.50, 28, 1, 'jumex_durazno_500ml.jpg'),
('Boing Mango 500ml', 13.00, 32, 1, 'boing_mango_500ml.jpg'),
('Electrolit Naranja 625ml', 22.00, 15, 1, 'electrolit_naranja_625ml.jpg'),
('Café Americano 350ml', 25.00, 20, 1, 'cafe_americano_350ml.jpg'),
('Té Helado Fuze Tea 450ml', 16.50, 25, 1, 'fuze_tea_450ml.jpg'),

-- Snacks (id_categoria = 2)
('Sabritas Clásicas 45g', 15.50, 55, 2, 'sabritas_clasicas_45g.jpg'),
('Doritos Nacho 62g', 18.00, 48, 2, 'doritos_nacho_62g.jpg'),
('Cheetos Torciditos 35g', 14.00, 62, 2, 'cheetos_torciditos_35g.jpg'),
('Ruffles Queso 45g', 16.50, 40, 2, 'ruffles_queso_45g.jpg'),
('Takis Fuego 62g', 17.50, 72, 2, 'takis_fuego_62g.jpg'),
('Galletas Marías Gamesa 171g', 22.00, 25, 2, 'galletas_marias_gamesa_171g.jpg'),
('Chokis Original 128g', 28.50, 18, 2, 'chokis_original_128g.jpg'),
('Emperador Chocolate 45g', 12.50, 45, 2, 'emperador_chocolate_45g.jpg'),
('Palomitas Act II Mantequilla 85g', 19.50, 30, 2, 'palomitas_act2_85g.jpg'),
('Cacahuates Japoneses 40g', 13.00, 38, 2, 'cacahuates_japoneses_40g.jpg'),

-- Lácteos (id_categoria = 3)
('Leche Lala Entera 1L', 24.50, 35, 3, 'leche_lala_1l.jpg'),
('Yogurt Danone Fresa 125g', 11.50, 42, 3, 'yogurt_danone_fresa_125g.jpg'),
('Queso Oaxaca Philadelphia 150g', 32.00, 20, 3, 'queso_oaxaca_philadelphia_150g.jpg'),
('Leche Deslactosada Lactaid 1L', 28.00, 15, 3, 'leche_lactaid_1l.jpg'),
('Yogurt Griego Chobani 150g', 19.50, 25, 3, 'yogurt_griego_chobani_150g.jpg'),

-- Frutas (id_categoria = 4)
('Manzana Roja por kg', 45.00, 25, 4, 'manzana_roja_kg.jpg'),
('Plátano Tabasco por kg', 22.00, 40, 4, 'platano_tabasco_kg.jpg'),
('Naranja Valencia por kg', 18.50, 35, 4, 'naranja_valencia_kg.jpg'),
('Uvas Rojas por kg', 65.00, 12, 4, 'uvas_rojas_kg.jpg'),
('Pera Anjou por kg', 52.00, 18, 4, 'pera_anjou_kg.jpg'),

-- Verduras (id_categoria = 5)
('Zanahoria por kg', 16.00, 30, 5, 'zanahoria_kg.jpg'),
('Lechuga Romana pieza', 12.00, 25, 5, 'lechuga_romana_pieza.jpg'),
('Tomate Saladette por kg', 24.00, 28, 5, 'tomate_saladette_kg.jpg'),
('Cebolla Blanca por kg', 19.00, 35, 5, 'cebolla_blanca_kg.jpg'),
('Papa Blanca por kg', 21.00, 45, 5, 'papa_blanca_kg.jpg'),

-- Panadería (id_categoria = 6)
('Pan Blanco Bimbo Grande', 32.00, 22, 6, 'pan_blanco_bimbo_grande.jpg'),
('Dona Glaseada Bimbo', 8.50, 48, 6, 'dona_glaseada_bimbo.jpg'),
('Muffin Chocolate Chips 120g', 15.00, 32, 6, 'muffin_chocolate_120g.jpg'),
('Pan Tostado Bimbo 380g', 28.50, 18, 6, 'pan_tostado_bimbo_380g.jpg'),

-- Carnes (id_categoria = 7)
('Jamón de Pavo FUD 200g', 42.00, 15, 7, 'jamon_pavo_fud_200g.jpg'),
('Salchichas de Pavo FUD 250g', 38.50, 20, 7, 'salchichas_pavo_fud_250g.jpg'),
('Atún Herdez en Agua 140g', 18.50, 65, 7, 'atun_herdez_agua_140g.jpg'),

-- Abarrotes (id_categoria = 8)
('Arroz Morelos 1kg', 26.00, 30, 8, 'arroz_morelos_1kg.jpg'),
('Frijoles Negro La Costeña 560g', 24.50, 35, 8, 'frijoles_negro_costena_560g.jpg'),
('Aceite 123 900ml', 32.50, 25, 8, 'aceite_123_900ml.jpg'),
('Sal La Fina 1kg', 8.50, 40, 8, 'sal_fina_1kg.jpg'),
('Azúcar Estándar 1kg', 19.50, 45, 8, 'azucar_estandar_1kg.jpg'),

-- Limpieza (id_categoria = 9)
('Jabón Zote Rosa 200g', 12.50, 30, 9, 'jabon_zote_rosa_200g.jpg'),
('Detergente Roma 1kg', 28.00, 25, 9, 'detergente_roma_1kg.jpg'),
('Papel Higiénico Regio 4 rollos', 32.00, 40, 9, 'papel_regio_4rollos.jpg'),

-- Dulcería (id_categoria = 10)
('Chocolate Carlos V 30g', 12.00, 85, 10, 'chocolate_carlos_v_30g.jpg'),
('Paleta Payaso 25g', 8.50, 95, 10, 'paleta_payaso_25g.jpg'),
('Chicles Trident Menta 12 piezas', 15.50, 42, 10, 'chicles_trident_menta.jpg'),
('Mazapán De la Rosa 28g', 6.50, 78, 10, 'mazapan_rosa_28g.jpg'),
('Gomitas Panditas 85g', 16.50, 55, 10, 'gomitas_panditas_85g.jpg');

-- Insertar algunos pedidos de ejemplo
INSERT IGNORE INTO Pedidos (id_usuario, id_estado) VALUES 
(2, 1), -- María - Pendiente
(3, 2), -- Pedro - Procesando  
(4, 4), -- Ana - Entregado
(6, 1), -- Carmen - Pendiente
(8, 3); -- Lucía - Enviado

-- Insertar detalles de pedidos
INSERT IGNORE INTO DetallePedido (id_pedido, id_producto, cantidad, subtotal) VALUES 
-- Pedido 1 (María)
(1, 1, 2, 37.00),  -- 2 Coca Colas
(1, 11, 1, 15.50), -- 1 Sabritas
(1, 26, 1, 24.50), -- 1 Leche Lala

-- Pedido 2 (Pedro)
(2, 15, 3, 52.50), -- 3 Takis
(2, 5, 2, 24.00),  -- 2 Aguas Bonafont
(2, 44, 1, 16.50), -- 1 Gomitas Panditas

-- Pedido 3 (Ana - Entregado)
(3, 18, 1, 12.50), -- 1 Emperador
(3, 2, 1, 17.00),  -- 1 Pepsi
(3, 40, 2, 17.00), -- 2 Chocolates Carlos V

-- Pedido 4 (Carmen)
(4, 30, 2, 90.00), -- 2 kg Manzanas
(4, 27, 1, 11.50), -- 1 Yogurt Danone
(4, 7, 1, 13.00),  -- 1 Boing Mango

-- Pedido 5 (Lucía - Enviado)
(5, 39, 1, 19.50), -- 1 Azúcar
(5, 36, 1, 32.00), -- 1 Pan Blanco Bimbo
(5, 35, 1, 21.00); -- 1 kg Papas

-- Verificación de datos insertados
SELECT 'Resumen de datos insertados:' AS Info;
SELECT 'Roles' AS Tabla, COUNT(*) AS Total FROM Roles
UNION ALL
SELECT 'Nombres', COUNT(*) FROM Nombres  
UNION ALL
SELECT 'Usuarios', COUNT(*) FROM Usuarios
UNION ALL
SELECT 'Categorías', COUNT(*) FROM Categorias
UNION ALL
SELECT 'Productos', COUNT(*) FROM Productos
UNION ALL
SELECT 'Estados Pedidos', COUNT(*) FROM EstadosPedidos
UNION ALL
SELECT 'Pedidos', COUNT(*) FROM Pedidos
UNION ALL
SELECT 'Detalle Pedidos', COUNT(*) FROM DetallePedido;

-- Consulta de productos por categoría
SELECT 'Productos por categoría:' AS Info;
SELECT c.nombre AS Categoria, COUNT(p.id_producto) AS Total_Productos, 
       AVG(p.precio) AS Precio_Promedio
FROM Categorias c 
LEFT JOIN Productos p ON c.id_categoria = p.id_categoria
GROUP BY c.id_categoria, c.nombre
ORDER BY Total_Productos DESC;
