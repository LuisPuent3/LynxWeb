Necesito que me crees un archivo SQL para poblar mi base de datos MySQL llamada 'lynxshop' con datos de prueba. La estructura de las tablas ya existe y es la siguiente:

ESTRUCTURA DE LA BASE DE DATOS:

1. Tabla Roles:
   - id_rol (INT, PK, AUTO_INCREMENT)
   - nombre (VARCHAR(50), UNIQUE, NOT NULL)

2. Tabla Nombres:
   - id_nombre (INT, PK, AUTO_INCREMENT)
   - nombre (VARCHAR(100), NOT NULL)
   - apellidoP (VARCHAR(70), NOT NULL)
   - apellidoM (VARCHAR(70), NULL)

3. Tabla Usuarios:
   - id_usuario (INT, PK, AUTO_INCREMENT)
   - id_nombre (INT, FK → Nombres.id_nombre)
   - correo (VARCHAR(100), UNIQUE)
   - telefono (VARCHAR(15), UNIQUE)
   - contraseña (VARBINARY(255))
   - id_rol (INT, FK → Roles.id_rol)
   - fecha_registro (DATETIME, DEFAULT CURRENT_TIMESTAMP)

4. Tabla Categorias:
   - id_categoria (INT, PK, AUTO_INCREMENT)
   - nombre (VARCHAR(50), UNIQUE, NOT NULL)
   - descripcion (VARCHAR(255))

5. Tabla Productos:
   - id_producto (INT, PK, AUTO_INCREMENT)
   - nombre (VARCHAR(100), UNIQUE, NOT NULL)
   - precio (DECIMAL(10,2), NOT NULL)
   - cantidad (INT, NOT NULL)
   - id_categoria (INT, FK → Categorias.id_categoria)
   - imagen (VARCHAR(255))

6. Tabla EstadosPedidos:
   - id_estado (INT, PK, AUTO_INCREMENT)
   - nombre (VARCHAR(50), UNIQUE, NOT NULL)

7. Tabla Pedidos:
   - id_pedido (INT, PK, AUTO_INCREMENT)
   - id_usuario (INT, FK → Usuarios.id_usuario)
   - fecha (DATETIME, DEFAULT CURRENT_TIMESTAMP)
   - id_estado (INT, FK → EstadosPedidos.id_estado, DEFAULT 1)

8. Tabla DetallePedido:
   - id_detalle (INT, PK, AUTO_INCREMENT)
   - id_pedido (INT, FK → Pedidos.id_pedido)
   - id_producto (INT, FK → Productos.id_producto)
   - cantidad (INT, NOT NULL)
   - subtotal (DECIMAL(10,2), NOT NULL)

DATOS QUE NECESITO:

1. NO borres datos existentes, solo inserta nuevos
2. Inserta 50 productos realistas de una tienda de abarrotes escolar con:
   - Bebidas: refrescos (Coca-Cola, Pepsi, etc), jugos (Jumex, Boing), agua, café
   - Snacks: papas (Sabritas, Doritos, Cheetos), galletas, dulces
   - Abarrotes: productos básicos
   - Frutas: manzanas, plátanos, naranjas
   - Verduras: productos frescos básicos

3. Los precios deben ser en pesos mexicanos y realistas para una tienda escolar
4. Las cantidades en inventario deben variar (algunas altas, algunas bajas)
5. Los nombres de productos deben incluir la presentación (600ml, 45g, etc)
6. Para las contraseñas usa AES_ENCRYPT con la clave 'clave_secreta'

El script debe empezar con:
USE lynxshop;

Y debe respetar las claves foráneas insertando en el orden correcto.