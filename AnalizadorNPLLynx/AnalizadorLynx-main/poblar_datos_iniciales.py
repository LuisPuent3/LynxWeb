"""
SCRIPT PARA POBLAR DATOS INICIALES DEL SISTEMA LCLN MEJORADO
Poblar sinónimos específicos y atributos basados en productos reales de la BD
Análisis inteligente de la base de datos existente para generar sinónimos relevantes

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

class PobladorDatosLCLN:
    """
    Clase para poblar datos iniciales del sistema LCLN mejorado
    """
    
    def __init__(self):
        self.sinonimos_generados = []
        self.atributos_generados = []
        self.productos_analizados = []
        
        # Mapeo de sinónimos comunes basado en análisis de búsquedas reales
        self.mapeo_sinonimos = {
            # Bebidas - Coca Cola
            'coca': ['coca-cola', 'coka', 'cocacola', 'coca cola'],
            'coca cola': ['coca', 'coka', 'cocacola', 'refresco cola'],
            'coca zero': ['coca sin azucar', 'coca light', 'coca diet', 'zero coca'],
            'coca sin azucar': ['coca zero', 'coca light', 'coca diet'],
            
            # Snacks populares
            'doritos': ['dorito', 'papas doritos', 'botana dorito'],
            'cheetos': ['chettos', 'cheeto', 'quetos', 'crujitos'],
            'crujitos': ['cheetos', 'chettos', 'crujito'],
            
            # Términos genéricos
            'papas': ['papa', 'chips', 'frituras'],
            'galletas': ['galleta', 'galletita', 'cookie'],
            'agua': ['agua natural', 'agua pura', 'agua simple'],
            'jugo': ['jugos', 'néctar', 'bebida de fruta'],
            
            # Variaciones ortográficas comunes
            'azucar': ['azúcar', 'endulzante'],
            'platano': ['plátano', 'banana'],
            'limon': ['limón', 'citrico'],
        }
        
        # Mapeo de atributos por categoría/tipo de producto
        self.mapeo_atributos = {
            # Bebidas
            'bebidas': {
                'azucar': {'coca cola': True, 'coca zero': False, 'coca light': False, 'agua': False, 'jugo': True},
                'gas': {'coca cola': True, 'agua': False, 'jugo': False},
                'calorias': {'coca cola': True, 'coca zero': False, 'agua': False}
            },
            
            # Snacks
            'snacks': {
                'picante': {'doritos dinamita': True, 'cheetos fuego': True, 'papas normales': False},
                'sal': {'doritos': True, 'cheetos': True, 'papas': True},
                'grasa': {'doritos': True, 'cheetos': True, 'papas': True, 'galletas': True},
                'gluten': {'galletas': True, 'papas': False}
            },
            
            # Panadería
            'panaderia': {
                'gluten': {'pan': True, 'galletas': True, 'pasteles': True},
                'azucar': {'pasteles': True, 'galletas dulces': True, 'pan simple': False},
                'lactosa': {'pasteles': True, 'pan de leche': True}
            },
            
            # Frutas y verduras
            'frutas': {
                'organico': {'todas': None},  # Se define por producto específico
                'azucar': {'todas': True},  # Azúcar natural
                'fibra': {'todas': True}
            }
        }

    def conectar_bd(self) -> Tuple[Any, Any]:
        """Conectar a la base de datos"""
        try:
            conn = mysql.connector.connect(**mysql_config)
            cursor = conn.cursor(dictionary=True)
            return conn, cursor
        except Exception as e:
            print(f"❌ Error conectando a BD: {e}")
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
                p.descripcion,
                p.precio,
                c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.activo = 1
            ORDER BY p.id_producto
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            print(f"📊 Encontrados {len(productos)} productos activos en la BD")
            return productos
            
        except Exception as e:
            print(f"❌ Error obteniendo productos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def generar_sinonimos_producto(self, producto: Dict) -> List[str]:
        """Generar sinónimos inteligentes para un producto específico"""
        nombre = producto['nombre'].lower().strip()
        descripcion = (producto['descripcion'] or '').lower().strip()
        categoria = producto['categoria'].lower().strip()
        
        sinonimos = set()
        
        # 1. Sinónimos basados en palabras clave del nombre
        palabras_nombre = re.findall(r'\\b\\w{3,}\\b', nombre)
        for palabra in palabras_nombre:
            if palabra in self.mapeo_sinonimos:
                sinonimos.update(self.mapeo_sinonimos[palabra])
        
        # 2. Variaciones del nombre completo
        # Eliminar palabras comunes
        palabras_filtradas = [p for p in palabras_nombre 
                             if p not in ['de', 'con', 'sin', 'el', 'la', 'los', 'las', 'y', 'o']]
        
        if len(palabras_filtradas) > 1:
            # Combinaciones de palabras principales
            for i, palabra in enumerate(palabras_filtradas):
                for j, otra_palabra in enumerate(palabras_filtradas):
                    if i != j:
                        sinonimos.add(f"{palabra} {otra_palabra}")
        
        # 3. Variaciones ortográficas comunes
        variaciones_ortograficas = {
            'coca': ['coka', 'koca'],
            'cheetos': ['chettos', 'quetos'],
            'azucar': ['azúcar'],
            'limon': ['limón'],
            'platano': ['plátano', 'banana']
        }
        
        for palabra in palabras_nombre:
            if palabra in variaciones_ortograficas:
                sinonimos.update(variaciones_ortograficas[palabra])
        
        # 4. Sinónimos basados en categoría
        sinonimos_categoria = {
            'bebidas': ['refresco', 'bebida', 'tomar'],
            'snacks': ['botana', 'snack', 'fritura', 'picadera'],
            'panaderia': ['pan', 'horneado'],
            'frutas': ['fruta', 'fresco', 'natural'],
            'verduras': ['verdura', 'vegetal', 'natural']
        }
        
        if categoria in sinonimos_categoria:
            sinonimos.update(sinonimos_categoria[categoria])
        
        # 5. Sinónimos específicos por producto conocido
        productos_especificos = {
            'coca cola': ['coca', 'coka', 'refresco de cola'],
            'doritos': ['dorito', 'papas doritos', 'nacho'],
            'cheetos': ['chettos', 'crujitos', 'queso snack'],
            'agua': ['agua natural', 'agua pura'],
            'galletas': ['galleta', 'cookie', 'galletita']
        }
        
        for producto_clave, sinons in productos_especificos.items():
            if producto_clave in nombre:
                sinonimos.update(sinons)
        
        # 6. Limpiar y filtrar sinónimos
        sinonimos_finales = []
        for sinonimo in sinonimos:
            # Filtrar sinónimos muy cortos, muy largos o iguales al nombre
            if (2 <= len(sinonimo) <= 50 and 
                sinonimo != nombre and 
                len(sinonimo.split()) <= 4):
                sinonimos_finales.append(sinonimo.strip())
        
        return list(set(sinonimos_finales))[:10]  # Máximo 10 sinónimos por producto

    def generar_atributos_producto(self, producto: Dict) -> List[Dict]:
        """Generar atributos inteligentes para un producto"""
        nombre = producto['nombre'].lower().strip()
        descripcion = (producto['descripcion'] or '').lower().strip()
        categoria = producto['categoria'].lower().strip()
        precio = float(producto['precio'])
        
        atributos = []
        
        # Detectar atributos basados en palabras clave
        texto_completo = f"{nombre} {descripcion}".lower()
        
        # Atributos de sabor/picante
        if any(palabra in texto_completo for palabra in ['picante', 'fuego', 'dinamita', 'chile', 'hot']):
            intensidad = 8 if 'fuego' in texto_completo or 'dinamita' in texto_completo else 6
            atributos.append({'atributo': 'picante', 'valor': True, 'intensidad': intensidad})
        elif categoria in ['snacks', 'bebidas'] and not any(palabra in texto_completo for palabra in ['dulce', 'natural']):
            atributos.append({'atributo': 'picante', 'valor': False, 'intensidad': 0})
        
        # Atributos de azúcar
        if any(palabra in texto_completo for palabra in ['sin azucar', 'zero', 'light', 'diet']):
            atributos.append({'atributo': 'azucar', 'valor': False, 'intensidad': 0})
        elif categoria == 'bebidas' and 'agua' not in texto_completo:
            atributos.append({'atributo': 'azucar', 'valor': True, 'intensidad': 7})
        elif any(palabra in texto_completo for palabra in ['dulce', 'chocolate', 'miel']):
            atributos.append({'atributo': 'azucar', 'valor': True, 'intensidad': 8})
        
        # Atributos de sal
        if categoria == 'snacks' and not any(palabra in texto_completo for palabra in ['dulce', 'chocolate']):
            atributos.append({'atributo': 'sal', 'valor': True, 'intensidad': 6})
        elif 'agua' in texto_completo:
            atributos.append({'atributo': 'sal', 'valor': False, 'intensidad': 0})
        
        # Atributos de grasa
        if categoria in ['snacks'] and any(palabra in texto_completo for palabra in ['papa', 'frito', 'chips']):
            atributos.append({'atributo': 'grasa', 'valor': True, 'intensidad': 7})
        elif categoria in ['bebidas', 'frutas', 'verduras']:
            atributos.append({'atributo': 'grasa', 'valor': False, 'intensidad': 0})
        
        # Atributos de gluten
        if any(palabra in texto_completo for palabra in ['pan', 'galleta', 'harina', 'trigo']):
            atributos.append({'atributo': 'gluten', 'valor': True, 'intensidad': 8})
        elif categoria in ['frutas', 'verduras', 'bebidas'] and 'cerveza' not in texto_completo:
            atributos.append({'atributo': 'gluten', 'valor': False, 'intensidad': 0})
        
        # Atributo de precio (barato/caro)
        if precio < 20:
            atributos.append({'atributo': 'economico', 'valor': True, 'intensidad': 8})
        elif precio > 50:
            atributos.append({'atributo': 'premium', 'valor': True, 'intensidad': 7})
        
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
            print(f"❌ Error insertando sinónimos para producto {producto_id}: {e}")
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
            print(f"❌ Error insertando atributos para producto {producto_id}: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def poblar_datos_completo(self):
        """Proceso completo de poblado de datos"""
        print("🚀 Iniciando poblado de datos LCLN...")
        print("=" * 60)
        
        # Obtener productos existentes
        productos = self.obtener_productos_existentes()
        if not productos:
            print("❌ No se encontraron productos. Abortando.")
            return
        
        total_sinonimos = 0
        total_atributos = 0
        productos_procesados = 0
        
        print("\\n📝 Procesando productos...")
        
        for producto in productos:
            try:
                print(f"\\n🔄 Procesando: {producto['nombre']} (ID: {producto['id_producto']})")
                
                # Generar sinónimos
                sinonimos = self.generar_sinonimos_producto(producto)
                if sinonimos:
                    insertados_sin = self.insertar_sinonimos_bd(producto['id_producto'], sinonimos)
                    total_sinonimos += insertados_sin
                    print(f"   ✅ {insertados_sin} sinónimos agregados: {', '.join(sinonimos[:3])}{'...' if len(sinonimos) > 3 else ''}")
                
                # Generar atributos
                atributos = self.generar_atributos_producto(producto)
                if atributos:
                    insertados_attr = self.insertar_atributos_bd(producto['id_producto'], atributos)
                    total_atributos += insertados_attr
                    attr_nombres = [f"{a['atributo']}({'✓' if a['valor'] else '✗'})" for a in atributos]
                    print(f"   ✅ {insertados_attr} atributos agregados: {', '.join(attr_nombres)}")
                
                productos_procesados += 1
                
            except Exception as e:
                print(f"   ❌ Error procesando producto {producto['id_producto']}: {e}")
                continue
        
        # Resumen final
        print("\\n" + "=" * 60)
        print("📊 RESUMEN DEL POBLADO DE DATOS")
        print("=" * 60)
        print(f"✅ Productos procesados: {productos_procesados}/{len(productos)}")
        print(f"🏷️  Total sinónimos insertados: {total_sinonimos}")
        print(f"⚡ Total atributos insertados: {total_atributos}")
        print(f"🎯 Promedio sinónimos por producto: {round(total_sinonimos/max(productos_procesados, 1), 1)}")
        print(f"📈 Promedio atributos por producto: {round(total_atributos/max(productos_procesados, 1), 1)}")
        
        # Estadísticas adicionales
        self.mostrar_estadisticas_finales()

    def mostrar_estadisticas_finales(self):
        """Mostrar estadísticas finales después del poblado"""
        conn, cursor = self.conectar_bd()
        if not conn:
            return
        
        try:
            print("\\n📈 ESTADÍSTICAS FINALES")
            print("-" * 40)
            
            # Total productos con sinónimos
            cursor.execute("SELECT COUNT(DISTINCT producto_id) as total FROM producto_sinonimos WHERE activo = 1")
            productos_con_sinonimos = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM productos WHERE activo = 1")
            total_productos = cursor.fetchone()['total']
            
            cobertura_sinonimos = round((productos_con_sinonimos / max(total_productos, 1)) * 100, 1)
            
            print(f"📊 Cobertura sinónimos: {productos_con_sinonimos}/{total_productos} productos ({cobertura_sinonimos}%)")
            
            # Productos con más sinónimos
            cursor.execute("""
                SELECT p.nombre, COUNT(ps.sinonimo) as total_sinonimos
                FROM productos p
                INNER JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id
                WHERE ps.activo = 1
                GROUP BY p.id_producto, p.nombre
                ORDER BY total_sinonimos DESC
                LIMIT 5
            """)
            
            top_productos = cursor.fetchall()
            if top_productos:
                print("\\n🏆 TOP 5 PRODUCTOS CON MÁS SINÓNIMOS:")
                for i, prod in enumerate(top_productos, 1):
                    print(f"   {i}. {prod['nombre']}: {prod['total_sinonimos']} sinónimos")
            
            # Total atributos
            cursor.execute("SELECT COUNT(DISTINCT producto_id) as total FROM producto_atributos")
            productos_con_atributos = cursor.fetchone()['total']
            
            cobertura_atributos = round((productos_con_atributos / max(total_productos, 1)) * 100, 1)
            print(f"\\n⚡ Cobertura atributos: {productos_con_atributos}/{total_productos} productos ({cobertura_atributos}%)")
            
            # Atributos más comunes
            cursor.execute("""
                SELECT atributo, COUNT(*) as total, 
                       SUM(CASE WHEN valor = 1 THEN 1 ELSE 0 END) as positivos,
                       SUM(CASE WHEN valor = 0 THEN 1 ELSE 0 END) as negativos
                FROM producto_atributos
                GROUP BY atributo
                ORDER BY total DESC
                LIMIT 5
            """)
            
            top_atributos = cursor.fetchall()
            if top_atributos:
                print("\\n🎯 ATRIBUTOS MÁS COMUNES:")
                for attr in top_atributos:
                    print(f"   • {attr['atributo']}: {attr['total']} productos (✓{attr['positivos']} ✗{attr['negativos']})")
        
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
        finally:
            cursor.close()
            conn.close()

    def insertar_sinonimos_manuales(self):
        """Insertar sinónimos críticos manualmente identificados"""
        print("\\n🎯 Insertando sinónimos críticos manuales...")
        
        # Estos son sinónimos críticos identificados por análisis de búsquedas reales
        sinonimos_criticos = [
            # Coca Cola (ajustar ID según tu BD)
            (2, ['coca', 'coka', 'coca-cola', 'cocacola', 'refresco cola']),
            (3, ['coca zero', 'coca sin azucar', 'coca light', 'coca diet', 'zero']),
            
            # Agua (ajustar ID)
            (4, ['agua natural', 'agua pura', 'agua simple']),
            
            # Snacks populares (ajustar IDs)
            (8, ['doritos', 'dorito', 'papas doritos', 'nacho chips']),
            (20, ['cheetos', 'chettos', 'crujitos', 'queso snack']),
            
            # Términos genéricos importantes
            (8, ['botana', 'snack', 'fritura']),
            (20, ['botana', 'snack', 'fritura']),
            (2, ['bebida', 'refresco', 'tomar']),
            (3, ['bebida', 'refresco', 'tomar'])
        ]
        
        total_insertados = 0
        
        for producto_id, sinonimos in sinonimos_criticos:
            try:
                insertados = self.insertar_sinonimos_bd(producto_id, sinonimos)
                total_insertados += insertados
                if insertados > 0:
                    print(f"   ✅ Producto {producto_id}: {insertados} sinónimos críticos agregados")
            except Exception as e:
                print(f"   ❌ Error con producto {producto_id}: {e}")
        
        print(f"📌 Total sinónimos críticos insertados: {total_insertados}")


def main():
    """Función principal"""
    print("SISTEMA LCLN - POBLADOR DE DATOS INICIALES")
    print("=" * 60)
    print("Este script analizara tu base de datos de productos existente")
    print("y generara sinonimos y atributos inteligentes automaticamente.")
    print("")
    
    respuesta = input("¿Continuar con el poblado? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Poblado cancelado.")
        return
    
    poblador = PobladorDatosLCLN()
    
    try:
        # Verificar que las tablas existan
        conn, cursor = poblador.conectar_bd()
        if not conn:
            print("❌ No se pudo conectar a la BD. Verifica la configuración.")
            return
        
        cursor.execute("SHOW TABLES LIKE 'producto_sinonimos'")
        if not cursor.fetchone():
            print("❌ Tabla 'producto_sinonimos' no encontrada.")
            print("📋 Ejecuta primero: setup_mysql_tables.sql")
            return
        
        cursor.execute("SHOW TABLES LIKE 'producto_atributos'")
        if not cursor.fetchone():
            print("❌ Tabla 'producto_atributos' no encontrada.")
            print("📋 Ejecuta primero: setup_mysql_tables.sql")
            return
        
        cursor.close()
        conn.close()
        
        # Proceso completo
        poblador.poblar_datos_completo()
        
        # Sinónimos críticos adicionales
        poblador.insertar_sinonimos_manuales()
        
        print("\\n✅ POBLADO COMPLETADO EXITOSAMENTE")
        print("🚀 El sistema LCLN con prioridades está listo para usar")
        print("📖 Puedes probar búsquedas como:")
        print("   • 'chettos picantes'")
        print("   • 'bebidas sin azucar'")
        print("   • 'botanas baratas'")
        print("   • 'coca light'")
        
    except Exception as e:
        print(f"❌ Error durante el poblado: {e}")
        print("💡 Revisa la configuración de la base de datos")

if __name__ == "__main__":
    main()