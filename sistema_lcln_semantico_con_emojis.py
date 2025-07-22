import mysql.connector
import re
import unicodedata
from datetime import datetime
import json

class SistemaLCLNSemanticoConEmojis:
    def __init__(self):
        # 🔗 Configuración de base de datos  
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Sin contraseña en XAMPP por defecto
            'database': 'lynxshop',
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_general_ci'
        }
        
        # 📚 Diccionario semántico con emojis
        self.diccionario_semantico = {
            'frutas': {
                'emoji': '🍎',
                'palabras_clave': ['fruta', 'frutas', 'fresco', 'fresca', 'frescas', 'natural', 'vitamina', 'jugosa'],
                'caracteristicas': ['citrico', 'tropical', 'acido', 'dulce natural', 'jugoso', 'fresco'],
                'filtros': ['organico', 'importado', 'nacional'],
                'color_contexto': '#4CAF50'
            },
            'bebidas': {
                'emoji': '🥤', 
                'palabras_clave': ['bebida', 'bebidas', 'liquido', 'refresco', 'agua', 'jugo', 'té', 'limonada'],
                'caracteristicas': ['frio', 'caliente', 'gasificado', 'natural', 'energizante', 'hidratante', 'sin azucar'],
                'filtros': ['light', 'zero', 'diet', 'energizante'],
                'color_contexto': '#2196F3'
            },
            'snacks': {
                'emoji': '🍿',
                'palabras_clave': ['snack', 'snacks', 'botana', 'botanas', 'papitas', 'chips', 'doritos', 'cheetos'],
                'caracteristicas': ['crujiente', 'salado', 'picante', 'queso', 'chile', 'fuego', 'spicy'],
                'filtros': ['picante', 'familiar', 'individual'],
                'color_contexto': '#FF9800'
            },
            'golosinas': {
                'emoji': '🍭',
                'palabras_clave': ['dulce', 'dulces', 'golosina', 'golosinas', 'caramelo', 'chocolate', 'chicle'],
                'caracteristicas': ['dulce', 'masticable', 'chocolate', 'azucar', 'confite'],
                'filtros': ['sin azucar', 'organico', 'diet'],
                'color_contexto': '#E91E63'
            },
            'papeleria': {
                'emoji': '📝',
                'palabras_clave': ['papeleria', 'escolar', 'oficina', 'escribir', 'dibujar', 'boligrafo', 'cuaderno'],
                'caracteristicas': ['negro', 'rojo', 'azul', 'profesional', 'escolar'],
                'filtros': ['profesional', 'escolar', 'colores'],
                'color_contexto': '#795548'
            }
        }
        
        # 💰 Sistema de precios con emojis
        self.rangos_precio = {
            'muy_barato': {'max': 5, 'emoji': '💸', 'palabras': ['muy barato', 'super barato', 'económico', 'centavos', 'regalado']},
            'barato': {'max': 15, 'emoji': '💰', 'palabras': ['barato', 'economico', 'accesible', 'low cost', 'cosas baratas']},
            'medio': {'max': 30, 'emoji': '💵', 'palabras': ['medio', 'normal', 'regular', 'promedio']},
            'caro': {'max': 50, 'emoji': '💸', 'palabras': ['caro', 'costoso', 'premium']},
            'muy_caro': {'max': 999, 'emoji': '💎', 'palabras': ['muy caro', 'premium', 'lujo', 'exclusivo']}
        }
        
        # 🔧 Normalizador de caracteres especiales
        self.caracteres_especiales = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U', 'Ñ': 'N'
        }
        
        # 📊 Cache para mejores tiempos de respuesta
        self.cache_productos = None
        self.cache_sinonimos = None
        self.cache_expiry = None
        
    def normalizar_texto(self, texto):
        """🔧 Normalizar texto removiendo acentos, espacios extra y caracteres especiales"""
        if not texto:
            return ""
            
        # Convertir a minúsculas
        texto = texto.lower().strip()
        
        # Reemplazar caracteres especiales
        for especial, normal in self.caracteres_especiales.items():
            texto = texto.replace(especial, normal)
        
        # Remover caracteres no alfanuméricos excepto espacios
        texto = re.sub(r'[^a-zA-Z0-9\s]', ' ', texto)
        
        # Normalizar espacios
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def detectar_categoria_semantica(self, consulta):
        """🎯 Detectar categoría semántica con puntuación de confianza"""
        consulta_normalizada = self.normalizar_texto(consulta)
        palabras = consulta_normalizada.split()
        
        puntuaciones = {}
        for categoria in self.diccionario_semantico:
            puntuaciones[categoria] = 0
        
        # Analizar cada palabra
        for palabra in palabras:
            for categoria, config in self.diccionario_semantico.items():
                # Palabras clave principales (peso 10)
                if any(palabra in pk or pk in palabra for pk in config['palabras_clave']):
                    puntuaciones[categoria] += 10
                    
                # Características (peso 8)
                if any(palabra in car or car in palabra for car in config['caracteristicas']):
                    puntuaciones[categoria] += 8
                    
                # Filtros específicos (peso 6)
                if any(palabra in fil or fil in palabra for fil in config['filtros']):
                    puntuaciones[categoria] += 6
        
        # Encontrar la mejor categoría
        mejor_categoria = max(puntuaciones.items(), key=lambda x: x[1])
        
        if mejor_categoria[1] > 0:
            config = self.diccionario_semantico[mejor_categoria[0]]
            return {
                'categoria': mejor_categoria[0],
                'emoji': config['emoji'],
                'puntuacion': mejor_categoria[1],
                'confianza': min(mejor_categoria[1] / 10, 1.0),
                'color': config['color_contexto']
            }
        
        return None
    
    def detectar_filtro_precio(self, consulta):
        """💰 Detectar filtros de precio semánticos"""
        consulta_normalizada = self.normalizar_texto(consulta)
        
        # Buscar rangos de precio por palabras clave
        for rango, config in self.rangos_precio.items():
            for palabra_precio in config['palabras']:
                if palabra_precio in consulta_normalizada:
                    return {
                        'rango': rango,
                        'precio_max': config['max'],
                        'emoji': config['emoji'],
                        'palabras_detectadas': [palabra_precio],
                        'sql_filter': f"precio <= {config['max']}"
                    }
        
        # Detectar números específicos
        numero_match = re.search(r'(?:menos de|menor a|hasta|máximo|max)\s+(\d+)', consulta_normalizada)
        if numero_match:
            precio = int(numero_match.group(1))
            return {
                'rango': 'personalizado',
                'precio_max': precio,
                'emoji': '💰',
                'palabras_detectadas': [numero_match.group(0)],
                'sql_filter': f"precio <= {precio}"
            }
        
        return None
    
    def detectar_contradicciones_semanticas(self, consulta, categoria_detectada, resultados):
        """🚫 Detectar contradicciones semánticas en los resultados"""
        contradicciones = []
        consulta_norm = self.normalizar_texto(consulta)
        
        # Si busca frutas pero encuentra snacks/dulces
        if 'fruta' in consulta_norm and categoria_detectada != 'frutas':
            categorias_encontradas = set(r.get('categoria', '').lower() for r in resultados)
            if any(cat in ['snacks', 'golosinas'] for cat in categorias_encontradas):
                contradicciones.append({
                    'tipo': 'categoria_incorrecta',
                    'mensaje': '⚠️ Buscas frutas 🍎 pero encontré snacks/dulces',
                    'sugerencia': 'Intenta: "frutas frescas" o especifica la fruta',
                    'icono': '⚠️'
                })
        
        # Si busca snacks picantes pero encuentra té
        if any(palabra in consulta_norm for palabra in ['chetos', 'picante', 'cheetos']):
            productos_te = [r for r in resultados if 'té' in r.get('nombre', '').lower()]
            if productos_te:
                contradicciones.append({
                    'tipo': 'producto_incorrecto',
                    'mensaje': '🌶️ Buscas snacks picantes pero encontré té',
                    'sugerencia': 'Intenta: "cheetos fuego" o "snacks picantes"',
                    'icono': '🌶️'
                })
        
        # Si busca precios pero los resultados no coinciden
        filtro_precio = self.detectar_filtro_precio(consulta)
        if filtro_precio and resultados:
            productos_caros = [r for r in resultados if r.get('precio', 0) > filtro_precio['precio_max']]
            if productos_caros:
                contradicciones.append({
                    'tipo': 'precio_inconsistente', 
                    'mensaje': f"{filtro_precio['emoji']} Algunos productos superan tu presupuesto de ${filtro_precio['precio_max']}",
                    'sugerencia': f"Filtra por productos menores a ${filtro_precio['precio_max']}",
                    'icono': filtro_precio['emoji']
                })
        
        return contradicciones
    
    def obtener_productos_cache(self):
        """📊 Obtener productos con cache inteligente"""
        now = datetime.now()
        
        # Verificar si el cache es válido (5 minutos)
        if (self.cache_productos is not None and 
            self.cache_expiry is not None and 
            (now - self.cache_expiry).seconds < 300):
            return self.cache_productos
        
        # Actualizar cache
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT 
                p.id_producto,
                p.nombre,
                p.precio,
                p.stock,
                p.descripcion,
                p.imagen,
                c.nombre as categoria,
                c.id_categoria,
                GROUP_CONCAT(DISTINCT ps.sinonimo SEPARATOR ', ') as sinonimos,
                AVG(ps.popularidad) as popularidad_promedio
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria  
            LEFT JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id AND ps.activo = 1
            WHERE p.activo = 1
            GROUP BY p.id_producto, p.nombre, p.precio, p.stock, p.descripcion, p.imagen, c.nombre, c.id_categoria
            ORDER BY p.nombre
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            # Procesar productos
            for producto in productos:
                if producto['sinonimos']:
                    producto['lista_sinonimos'] = [s.strip() for s in producto['sinonimos'].split(',')]
                else:
                    producto['lista_sinonimos'] = []
                    
                # Detectar categoría semántica del producto
                categoria_semantica = self.detectar_categoria_semantica(producto['nombre'])
                if categoria_semantica:
                    producto['categoria_semantica'] = categoria_semantica
                    producto['emoji'] = categoria_semantica['emoji']
                else:
                    producto['emoji'] = '📦'
            
            self.cache_productos = productos
            self.cache_expiry = now
            
            cursor.close()
            conn.close()
            
            return productos
            
        except Exception as e:
            print(f"❌ Error al obtener productos: {e}")
            return []
    
    def buscar_productos_semantico(self, consulta):
        """🔍 Búsqueda semántica mejorada con análisis de contexto"""
        inicio = datetime.now()
        
        print(f"🔍 === BÚSQUEDA SEMÁNTICA MEJORADA ===")
        print(f"📝 Consulta original: \"{consulta}\"")
        
        # PASO 0: Normalización y análisis semántico
        consulta_normalizada = self.normalizar_texto(consulta)
        print(f"🔧 Consulta normalizada: \"{consulta_normalizada}\"")
        
        # PASO 0.5: Detección de contexto semántico
        categoria_semantica = self.detectar_categoria_semantica(consulta)
        if categoria_semantica:
            print(f"{categoria_semantica['emoji']} Categoría detectada: {categoria_semantica['categoria']} (confianza: {categoria_semantica['confianza']*100:.1f}%)")
        
        filtro_precio = self.detectar_filtro_precio(consulta)
        if filtro_precio:
            print(f"{filtro_precio['emoji']} Filtro precio: ≤ ${filtro_precio['precio_max']} ({', '.join(filtro_precio['palabras_detectadas'])})")
        
        # PASO 1: Obtener productos
        productos = self.obtener_productos_cache()
        if not productos:
            return {'productos': [], 'tiempo_ms': 0, 'analisis': {}}
        
        print(f"📦 Productos en base de datos: {len(productos)}")
        
        # PASO 1.5: Búsqueda multi-criterio
        resultados_ponderados = []
        palabras_busqueda = consulta_normalizada.split()
        
        for producto in productos:
            puntuacion_total = 0
            coincidencias = []
            
            # Datos del producto normalizados
            nombre_norm = self.normalizar_texto(producto['nombre'])
            desc_norm = self.normalizar_texto(producto.get('descripcion', ''))
            categoria_norm = self.normalizar_texto(producto.get('categoria', ''))
            
            # 🎯 CRITERIO 1: Coincidencia exacta de nombre (peso 50)
            if consulta_normalizada == nombre_norm:
                puntuacion_total += 50
                coincidencias.append("nombre_exacto")
            
            # 🎯 CRITERIO 2: Palabras en nombre (peso 30)
            for palabra in palabras_busqueda:
                if palabra in nombre_norm:
                    puntuacion_total += 30
                    coincidencias.append(f"nombre_contiene_{palabra}")
            
            # 🎯 CRITERIO 3: Sinónimos (peso 25)
            if producto['lista_sinonimos']:
                for sinonimo in producto['lista_sinonimos']:
                    sinonimo_norm = self.normalizar_texto(sinonimo)
                    for palabra in palabras_busqueda:
                        if palabra == sinonimo_norm or palabra in sinonimo_norm:
                            puntuacion_total += 25
                            coincidencias.append(f"sinonimo_{sinonimo}")
            
            # 🎯 CRITERIO 4: Contexto semántico (peso 20)
            if categoria_semantica and categoria_semantica['categoria'] == categoria_norm:
                puntuacion_total += 20 * categoria_semantica['confianza']
                coincidencias.append(f"categoria_semantica_{categoria_semantica['categoria']}")
            
            # 🎯 CRITERIO 5: Descripción (peso 10)
            for palabra in palabras_busqueda:
                if palabra in desc_norm:
                    puntuacion_total += 10
                    coincidencias.append(f"descripcion_{palabra}")
            
            # 🎯 CRITERIO 6: Filtros de precio (aplicar si coincide)
            cumple_precio = True
            if filtro_precio:
                if producto['precio'] > filtro_precio['precio_max']:
                    cumple_precio = False
                    puntuacion_total *= 0.3  # Penalizar pero no eliminar
                else:
                    puntuacion_total += 15  # Bonus por cumplir precio
                    coincidencias.append(f"precio_ok_{filtro_precio['rango']}")
            
            # Solo incluir si hay puntuación
            if puntuacion_total > 0:
                producto_resultado = producto.copy()
                producto_resultado['puntuacion'] = puntuacion_total
                producto_resultado['coincidencias'] = coincidencias
                producto_resultado['cumple_precio'] = cumple_precio
                resultados_ponderados.append(producto_resultado)
        
        # PASO 2: Ordenar por puntuación
        resultados_ponderados.sort(key=lambda x: x['puntuacion'], reverse=True)
        
        # PASO 2.5: Análisis de contradicciones
        contradicciones = self.detectar_contradicciones_semanticas(
            consulta, 
            categoria_semantica['categoria'] if categoria_semantica else None, 
            resultados_ponderados
        )
        
        # PASO 3: Preparar respuesta
        tiempo_ms = (datetime.now() - inicio).total_seconds() * 1000
        
        print(f"🎯 Resultados encontrados: {len(resultados_ponderados)}")
        print(f"⏱️ Tiempo de búsqueda: {tiempo_ms:.1f}ms")
        
        if contradicciones:
            print("🚫 Contradicciones detectadas:")
            for cont in contradicciones:
                print(f"  {cont['icono']} {cont['mensaje']}")
        
        analisis_completo = {
            'consulta_original': consulta,
            'consulta_normalizada': consulta_normalizada,
            'categoria_semantica': categoria_semantica,
            'filtro_precio': filtro_precio,
            'contradicciones': contradicciones,
            'total_productos_analizados': len(productos),
            'productos_encontrados': len(resultados_ponderados),
            'tiempo_ms': tiempo_ms
        }
        
        return {
            'productos': resultados_ponderados[:10],  # Top 10 resultados
            'analisis': analisis_completo,
            'tiempo_ms': tiempo_ms
        }

def probar_casos_problematicos():
    """🧪 Probar los casos que reportaron problemas"""
    sistema = SistemaLCLNSemanticoConEmojis()
    
    casos_prueba = [
        'fruta fresca',
        'cosas baratas', 
        'chetos picantes',
        'agüita',
        'té negro',
        'snacks dulces',
        'bebidas sin azucar'
    ]
    
    print("🧪 === PRUEBAS DE CASOS PROBLEMÁTICOS ===\\n")
    
    for caso in casos_prueba:
        print(f"\\n{'='*60}")
        resultado = sistema.buscar_productos_semantico(caso)
        
        if resultado['productos']:
            print("🎯 RESULTADOS:")
            for i, producto in enumerate(resultado['productos'][:3], 1):
                emoji = producto.get('emoji', '📦')
                print(f"  {i}. {emoji} {producto['nombre']} - ${producto['precio']} ({producto['categoria']})")
                print(f"     Puntuación: {producto['puntuacion']:.1f} | Coincidencias: {', '.join(producto['coincidencias'][:3])}")
        
        # Mostrar contradicciones
        if resultado.get('analisis', {}).get('contradicciones'):
            print("\\n⚠️ ADVERTENCIAS:")
            for cont in resultado['analisis']['contradicciones']:
                print(f"  {cont['mensaje']}")
                print(f"  💡 Sugerencia: {cont['sugerencia']}")

if __name__ == "__main__":
    probar_casos_problematicos()
