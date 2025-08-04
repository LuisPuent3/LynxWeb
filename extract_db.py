#!/usr/bin/env python3
import mysql.connector
import os
from datetime import datetime

# Configuración de la base de datos Railway
db_config = {
    'host': 'mysql.railway.internal',
    'user': 'root',
    'password': 'QVdGKaAfrqRaowZcQgmlFxrAGvOcFKtw',
    'database': 'railway',
    'port': 3306
}

def extract_database_schema():
    """Extrae el esquema completo de la base de datos actual"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("🔍 Conectado a la base de datos Railway")
        
        # Obtener lista de todas las tablas
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table}")
        
        # Crear archivo SQL con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_backup_{timestamp}.sql"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- Backup de la base de datos Railway\n")
            f.write(f"-- Generado el: {datetime.now()}\n")
            f.write("-- USE railway;\n\n")
            
            # Para cada tabla, extraer estructura y datos
            for table in tables:
                print(f"📄 Procesando tabla: {table}")
                
                # Obtener estructura de la tabla
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_table = cursor.fetchone()[1]
                
                f.write(f"-- Estructura de tabla {table}\n")
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                f.write(f"{create_table};\n\n")
                
                # Obtener datos de la tabla
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()
                
                if rows:
                    # Obtener nombres de columnas
                    cursor.execute(f"DESCRIBE `{table}`")
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    f.write(f"-- Datos para tabla {table}\n")
                    f.write(f"INSERT INTO `{table}` (`{'`, `'.join(columns)}`) VALUES\n")
                    
                    for i, row in enumerate(rows):
                        # Escapar valores
                        escaped_values = []
                        for value in row:
                            if value is None:
                                escaped_values.append('NULL')
                            elif isinstance(value, str):
                                escaped_values.append(f"'{value.replace("'", "''")}'")
                            elif isinstance(value, datetime):
                                escaped_values.append(f"'{value}'")
                            else:
                                escaped_values.append(str(value))
                        
                        if i == len(rows) - 1:
                            f.write(f"({', '.join(escaped_values)});\n\n")
                        else:
                            f.write(f"({', '.join(escaped_values)}),\n")
        
        print(f"✅ Backup generado en: {filename}")
        
        # Ahora agregar las tablas faltantes
        with open(filename, 'a', encoding='utf-8') as f:
            f.write("\n-- ========================================\n")
            f.write("-- TABLAS ADICIONALES PARA SINÓNIMOS Y MÉTRICAS\n")
            f.write("-- ========================================\n\n")
            
            # Tabla producto_sinonimos
            f.write("""-- Tabla para sinónimos de productos
DROP TABLE IF EXISTS `producto_sinonimos`;
CREATE TABLE `producto_sinonimos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `sinonimo` varchar(255) NOT NULL,
  `popularidad` int DEFAULT 1,
  `precision_score` decimal(3,2) DEFAULT 0.50,
  `fuente` enum('manual','automatico','user_generated') DEFAULT 'manual',
  `activo` tinyint(1) DEFAULT 1,
  `fecha_creacion` timestamp DEFAULT CURRENT_TIMESTAMP,
  `fecha_ultima_actualizacion` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_producto_id` (`producto_id`),
  KEY `idx_sinonimo` (`sinonimo`),
  KEY `idx_activo` (`activo`),
  CONSTRAINT `fk_producto_sinonimos_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

""")
            
            # Tabla busqueda_metricas
            f.write("""-- Tabla para métricas de búsqueda
DROP TABLE IF EXISTS `busqueda_metricas`;
CREATE TABLE `busqueda_metricas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `termino_busqueda` varchar(255) NOT NULL,
  `producto_id` int DEFAULT NULL,
  `clicks` int DEFAULT 0,
  `fecha_busqueda` timestamp DEFAULT CURRENT_TIMESTAMP,
  `session_id` varchar(255) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text,
  PRIMARY KEY (`id`),
  KEY `idx_termino_busqueda` (`termino_busqueda`),
  KEY `idx_producto_id` (`producto_id`),
  KEY `idx_usuario_id` (`usuario_id`),
  KEY `idx_fecha_busqueda` (`fecha_busqueda`),
  CONSTRAINT `fk_busqueda_metricas_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE SET NULL,
  CONSTRAINT `fk_busqueda_metricas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

""")
            
            # Datos de ejemplo para sinónimos
            f.write("""-- Datos de ejemplo para sinónimos
INSERT INTO `producto_sinonimos` (`producto_id`, `sinonimo`, `popularidad`, `precision_score`, `fuente`) VALUES
(1, 'coca cola', 5, 0.95, 'manual'),
(1, 'refresco cola', 3, 0.80, 'manual'),
(1, 'bebida cola', 2, 0.75, 'manual'),
(2, 'galletas oreo', 4, 0.90, 'manual'),
(2, 'galletas chocolate', 3, 0.70, 'manual'),
(3, 'papa frito', 3, 0.85, 'manual'),
(3, 'fritura', 2, 0.60, 'manual');

""")
        
        print(f"✅ Tablas de sinónimos y métricas agregadas al backup")
        return filename
        
    except mysql.connector.Error as err:
        print(f"❌ Error de base de datos: {err}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    filename = extract_database_schema()
    if filename:
        print(f"\n🎉 ¡Backup completado exitosamente!")
        print(f"📁 Archivo generado: {filename}")
        print(f"🔧 Puedes usar este archivo para recrear la base de datos completa")
    else:
        print("\n❌ Error al generar el backup")
