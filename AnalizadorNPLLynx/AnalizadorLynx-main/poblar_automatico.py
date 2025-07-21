"""
SCRIPT AUTOMÁTICO PARA POBLAR DATOS LCLN
Sin emojis para evitar errores de codificación en Windows
Poblado automático sin intervención del usuario

Autor: Sistema LCLN v2.0
Fecha: Julio 2025
"""

import mysql.connector
import re
from datetime import datetime
from typing import List, Dict, Tuple, Any

# Configuración MySQL
mysql_config = {
    'host': 'localhost',
    'database': 'lynxshop',
    'user': 'root',
    'password': '12345678',
    'charset': 'utf8mb4',
    'autocommit': True
}

class PobladorAutomaticoLCLN:
    """
    Clase para poblar datos iniciales del sistema LCLN mejorado
    """
    
    def __init__(self):
        self.sinonimos_generados = []
        self.atributos_generados = []
        self.productos_analizados = []

    def conectar_bd(self) -> Tuple[Any, Any]:
        """Conectar a la base de datos"""
        try:
            conn = mysql.connector.connect(**mysql_config)
            cursor = conn.cursor(dictionary=True)
            return conn, cursor
        except Exception as e:
            print(f"Error conectando a BD: {e}")
            return None, None

    def obtener_productos_existentes(self) -> List[Dict]:
        """Obtener todos los productos activos de la BD"""
        conn, cursor = self.conectar_bd()
        if not conn:
            return []
        
        try:
            query = """
            SELECT 
                p.id_producto,
                p.nombre,
                p.precio,
                c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            ORDER BY p.id_producto
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            print(f"Encontrados {len(productos)} productos activos en la BD")
            return productos
            
        except Exception as e:
            print(f"Error obteniendo productos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def generar_sinonimos_basicos(self, nombre: str, categoria: str) -> List[str]:
        """Generar sinónimos básicos para un producto"""
        nombre_lower = nombre.lower().strip()
        sinonimos = set()
        
        # Mapeo de sinónimos comunes
        mapeos = {
            'coca': ['coka', 'coca-cola', 'cocacola'],
            'coca cola': ['coca', 'coka', 'refresco cola'],
            'doritos': ['dorito', 'papas doritos'],
            'cheetos': ['chettos', 'crujitos'],
            'agua': ['agua natural', 'agua pura'],
            'galletas': ['galleta', 'cookie'],
            'papas': ['papa', 'chips'],
            'jugo': ['jugos', 'nectar']
        }
        
        # Buscar coincidencias
        for clave, valores in mapeos.items():
            if clave in nombre_lower:
                sinonimos.update(valores)
        
        # Sinónimos por categoría
        if 'bebida' in categoria.lower():
            sinonimos.update(['bebida', 'refresco', 'tomar'])
        elif 'snack' in categoria.lower():
            sinonimos.update(['botana', 'snack', 'fritura'])
        
        # Filtrar y limpiar
        sinonimos_finales = []
        for sin in sinonimos:
            if sin != nombre_lower and len(sin) > 2:
                sinonimos_finales.append(sin)
        
        return sinonimos_finales[:5]  # Máximo 5 por producto

    def generar_atributos_basicos(self, nombre: str, categoria: str, precio: float) -> List[Dict]:
        """Generar atributos básicos para un producto"""
        nombre_lower = nombre.lower()
        categoria_lower = categoria.lower()
        atributos = []
        
        # Atributos de picante
        if any(palabra in nombre_lower for palabra in ['picante', 'fuego', 'dinamita', 'chile']):
            atributos.append({'atributo': 'picante', 'valor': True, 'intensidad': 7})
        elif 'snack' in categoria_lower:
            atributos.append({'atributo': 'picante', 'valor': False, 'intensidad': 0})
        
        # Atributos de azúcar
        if any(palabra in nombre_lower for palabra in ['sin azucar', 'zero', 'light', 'diet']):
            atributos.append({'atributo': 'azucar', 'valor': False, 'intensidad': 0})
        elif 'bebida' in categoria_lower and 'agua' not in nombre_lower:
            atributos.append({'atributo': 'azucar', 'valor': True, 'intensidad': 6})
        
        # Atributo económico
        if precio < 20:
            atributos.append({'atributo': 'economico', 'valor': True, 'intensidad': 8})
        
        return atributos

    def insertar_sinonimos_bd(self, producto_id: int, sinonimos: List[str]) -> int:
        """Insertar sinónimos en la base de datos"""
        conn, cursor = self.conectar_bd()
        if not conn:
            return 0
        
        insertados = 0
        
        try:
            for sinonimo in sinonimos:
                # Verificar si ya existe
                cursor.execute("""
                    SELECT id FROM producto_sinonimos 
                    WHERE producto_id = %s AND sinonimo = %s
                """, [producto_id, sinonimo])
                
                if cursor.fetchone():
                    continue  # Ya existe
                
                # Insertar nuevo sinónimo
                cursor.execute("""
                    INSERT INTO producto_sinonimos 
                    (producto_id, sinonimo, popularidad, fuente, activo, fecha_creacion, fecha_ultima_actualizacion)
                    VALUES (%s, %s, %s, %s, 1, %s, %s)
                """, [
                    producto_id, 
                    sinonimo, 
                    0,  # Popularidad inicial
                    'auto_generated',
                    datetime.now(),
                    datetime.now()
                ])
                insertados += 1
            
            conn.commit()
            return insertados
            
        except Exception as e:
            print(f"Error insertando sinonimos para producto {producto_id}: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def insertar_atributos_bd(self, producto_id: int, atributos: List[Dict]) -> int:
        """Insertar atributos en la base de datos"""
        conn, cursor = self.conectar_bd()
        if not conn:
            return 0
        
        insertados = 0
        
        try:
            for attr in atributos:
                # Verificar si ya existe
                cursor.execute("""
                    SELECT id FROM producto_atributos 
                    WHERE producto_id = %s AND atributo = %s
                """, [producto_id, attr['atributo']])
                
                if cursor.fetchone():
                    continue  # Ya existe
                
                # Insertar nuevo atributo
                cursor.execute("""
                    INSERT INTO producto_atributos 
                    (producto_id, atributo, valor, intensidad, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s)
                """, [
                    producto_id,
                    attr['atributo'],
                    attr['valor'],
                    attr['intensidad'],
                    datetime.now()
                ])
                insertados += 1
            
            conn.commit()
            return insertados
            
        except Exception as e:
            print(f"Error insertando atributos para producto {producto_id}: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def poblar_sinonimos_criticos(self):
        """Poblar sinónimos críticos más importantes"""
        print("Insertando sinonimos criticos...")
        
        # Obtener IDs de productos reales
        conn, cursor = self.conectar_bd()
        if not conn:
            return
        
        try:
            # Buscar productos por nombre para obtener IDs reales
            productos_criticos = [
                ('coca cola', ['coca', 'coka', 'coca-cola', 'cocacola']),
                ('coca zero', ['coca sin azucar', 'coca light', 'zero']),
                ('agua', ['agua natural', 'agua pura']),
                ('doritos', ['dorito', 'papas doritos']),
                ('cheetos', ['chettos', 'crujitos'])
            ]
            
            total_insertados = 0
            
            for nombre_buscar, sinonimos in productos_criticos:
                cursor.execute("""
                    SELECT id_producto, nombre FROM productos 
                    WHERE LOWER(nombre) LIKE %s AND activo = 1
                    LIMIT 1
                """, [f"%{nombre_buscar}%"])
                
                producto = cursor.fetchone()
                if producto:
                    insertados = self.insertar_sinonimos_bd(producto['id_producto'], sinonimos)
                    total_insertados += insertados
                    print(f"  Producto '{producto['nombre']}': {insertados} sinonimos")
            
            print(f"Total sinonimos criticos insertados: {total_insertados}")
            
        except Exception as e:
            print(f"Error poblando sinonimos criticos: {e}")
        finally:
            cursor.close()
            conn.close()

    def ejecutar_poblado_completo(self):
        """Ejecutar poblado completo automáticamente"""
        print("SISTEMA LCLN - POBLADOR AUTOMATICO")
        print("=" * 50)
        
        # Verificar conexión y tablas
        conn, cursor = self.conectar_bd()
        if not conn:
            print("ERROR: No se pudo conectar a la base de datos")
            return
        
        try:
            # Verificar tablas
            cursor.execute("SHOW TABLES LIKE 'producto_sinonimos'")
            if not cursor.fetchone():
                print("ERROR: Tabla 'producto_sinonimos' no encontrada")
                return
            
            cursor.execute("SHOW TABLES LIKE 'producto_atributos'")  
            if not cursor.fetchone():
                print("ERROR: Tabla 'producto_atributos' no encontrada")
                return
                
        except Exception as e:
            print(f"Error verificando tablas: {e}")
            return
        finally:
            cursor.close()
            conn.close()
        
        # Obtener productos
        productos = self.obtener_productos_existentes()
        if not productos:
            print("No se encontraron productos activos")
            return
        
        print(f"Procesando {len(productos)} productos...")
        
        total_sinonimos = 0
        total_atributos = 0
        
        # Procesar cada producto
        for i, producto in enumerate(productos):
            try:
                print(f"[{i+1}/{len(productos)}] {producto['nombre']}")
                
                # Generar y insertar sinónimos
                sinonimos = self.generar_sinonimos_basicos(
                    producto['nombre'], 
                    producto['categoria']
                )
                if sinonimos:
                    insertados_sin = self.insertar_sinonimos_bd(
                        producto['id_producto'], 
                        sinonimos
                    )
                    total_sinonimos += insertados_sin
                
                # Generar y insertar atributos
                atributos = self.generar_atributos_basicos(
                    producto['nombre'],
                    producto['categoria'],
                    float(producto['precio'])
                )
                if atributos:
                    insertados_attr = self.insertar_atributos_bd(
                        producto['id_producto'],
                        atributos
                    )
                    total_atributos += insertados_attr
                
            except Exception as e:
                print(f"  Error procesando producto {producto['id_producto']}: {e}")
                continue
        
        # Sinónimos críticos adicionales
        self.poblar_sinonimos_criticos()
        
        # Estadísticas finales
        print("\n" + "=" * 50)
        print("RESUMEN FINAL")
        print("=" * 50)
        print(f"Productos procesados: {len(productos)}")
        print(f"Total sinonimos insertados: {total_sinonimos}")
        print(f"Total atributos insertados: {total_atributos}")
        
        # Verificar resultados
        self.mostrar_estadisticas_finales()
        
        print("\nPOBLADO COMPLETADO EXITOSAMENTE")
        print("El sistema LCLN esta listo para usar")

    def mostrar_estadisticas_finales(self):
        """Mostrar estadísticas finales"""
        conn, cursor = self.conectar_bd()
        if not conn:
            return
        
        try:
            # Estadísticas básicas
            cursor.execute("SELECT COUNT(*) as total FROM productos WHERE activo = 1")
            total_productos = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(DISTINCT producto_id) as total FROM producto_sinonimos WHERE activo = 1")
            productos_con_sinonimos = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM producto_sinonimos WHERE activo = 1")
            total_sinonimos = cursor.fetchone()['total']
            
            cobertura = round((productos_con_sinonimos / max(total_productos, 1)) * 100, 1)
            
            print(f"Cobertura sinonimos: {productos_con_sinonimos}/{total_productos} productos ({cobertura}%)")
            
        except Exception as e:
            print(f"Error obteniendo estadisticas: {e}")
        finally:
            cursor.close()
            conn.close()

def main():
    """Función principal"""
    poblador = PobladorAutomaticoLCLN()
    poblador.ejecutar_poblado_completo()

if __name__ == "__main__":
    main()