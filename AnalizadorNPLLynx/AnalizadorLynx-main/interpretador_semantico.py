# interpretador_semantico.py
class InterpretadorSemantico:
    """
    Módulo para interpretar adjetivos y frases coloquiales
    convirtiéndolas en filtros SQL concretos
    """
    
    def __init__(self, config_negocio=None):
        # Valores por defecto para tienda general
        self.config = config_negocio or {'tipo': 'general'}
        
        # Mapeos de adjetivos a filtros (100+ términos semánticos)
        self.mapeo_precios = {
            # Económicos (15+ sinónimos)
            'barato': {'op': 'menor_a', 'valor': 50}, 'barata': {'op': 'menor_a', 'valor': 50},
            'economico': {'op': 'menor_a', 'valor': 30}, 'economica': {'op': 'menor_a', 'valor': 30},
            'accesible': {'op': 'menor_a', 'valor': 40}, 'low-cost': {'op': 'menor_a', 'valor': 35},
            'rebajado': {'op': 'menor_a', 'valor': 45}, 'descuento': {'op': 'menor_a', 'valor': 40},
            'oferta': {'op': 'menor_a', 'valor': 45}, 'promocion': {'op': 'menor_a', 'valor': 40},
            'conveniente': {'op': 'menor_a', 'valor': 35}, 'estudiante': {'op': 'menor_a', 'valor': 25},
            'ahorro': {'op': 'menor_a', 'valor': 35}, 'rebaja': {'op': 'menor_a', 'valor': 40},
            
            # Caros (10+ sinónimos)
            'caro': {'op': 'mayor_a', 'valor': 100}, 'cara': {'op': 'mayor_a', 'valor': 100},
            'costoso': {'op': 'mayor_a', 'valor': 150}, 'costosa': {'op': 'mayor_a', 'valor': 150},
            'premium': {'op': 'mayor_a', 'valor': 120}, 'gourmet': {'op': 'mayor_a', 'valor': 200},
            'importado': {'op': 'mayor_a', 'valor': 180}, 'especialidad': {'op': 'mayor_a', 'valor': 160},
            'lujo': {'op': 'mayor_a', 'valor': 250}, 'exclusivo': {'op': 'mayor_a', 'valor': 200},
            
            # Rangos medios (5+ sinónimos)
            'moderado': {'op': 'entre', 'min': 40, 'max': 80}, 'regular': {'op': 'entre', 'min': 30, 'max': 70},
            'promedio': {'op': 'entre', 'min': 35, 'max': 75}, 'normal': {'op': 'entre', 'min': 40, 'max': 80},
            'estandar': {'op': 'entre', 'min': 30, 'max': 70}
        }
        
        self.mapeo_tamanos = {
            # Tamaños básicos (15+ sinónimos)
            'grande': {'op': 'mayor_a', 'valor': 1000, 'campo': 'contenido_ml'},
            'chico': {'op': 'menor_a', 'valor': 500, 'campo': 'contenido_ml'},
            'pequeño': {'op': 'menor_a', 'valor': 500, 'campo': 'contenido_ml'},
            'familiar': {'op': 'mayor_a', 'valor': 1500, 'campo': 'contenido_ml'},
            'individual': {'op': 'menor_a', 'valor': 250, 'campo': 'contenido_ml'},
            'jumbo': {'op': 'mayor_a', 'valor': 2000, 'campo': 'contenido_ml'},
            'mini': {'op': 'menor_a', 'valor': 200, 'campo': 'contenido_ml'},
            'mediano': {'op': 'entre', 'min': 500, 'max': 1000, 'campo': 'contenido_ml'},
            'xl': {'op': 'mayor_a', 'valor': 1500, 'campo': 'contenido_ml'},
            'compartir': {'op': 'mayor_a', 'valor': 1200, 'campo': 'contenido_ml'},
            'porcion': {'op': 'menor_a', 'valor': 300, 'campo': 'contenido_ml'},
            'mega': {'op': 'mayor_a', 'valor': 1800, 'campo': 'contenido_ml'},
            'super': {'op': 'mayor_a', 'valor': 1300, 'campo': 'contenido_ml'}
        }
        
        # NUEVO: Mapeo de sabores y características (40+ términos)
        self.mapeo_sabores = {
            # Sabores dulces (15+ términos)
            'dulce': 'dulce', 'dulces': 'dulce', 'azucarado': 'dulce', 'endulzado': 'dulce',
            'fresa': 'fresa', 'chocolate': 'chocolate', 'vainilla': 'vainilla', 'mango': 'mango',
            'durazno': 'durazno', 'naranja': 'naranja', 'limon': 'limon', 'uva': 'uva',
            'cereza': 'cereza', 'manzana': 'manzana', 'coco': 'coco', 'caramelo': 'caramelo',
            
            # Sabores salados/picantes (15+ términos)
            'salado': 'salado', 'salados': 'salado', 'picante': 'picante', 'picantes': 'picante',
            'picoso': 'picante', 'picosos': 'picante', 'enchilado': 'picante', 'chile': 'picante',
            'queso': 'queso', 'nacho': 'queso', 'cheddar': 'queso', 'natural': 'natural',
            'fuego': 'picante', 'habanero': 'picante', 'jalapeño': 'picante', 'chipotle': 'picante',
            
            # Características especiales (10+ términos)
            'light': 'light', 'diet': 'light', 'zero': 'sin-azucar', 'sin-azucar': 'sin-azucar',
            'descafeinado': 'sin-cafeina', 'organico': 'organico', 'integral': 'integral',
            'deslactosada': 'sin-lactosa', 'vegano': 'vegano', 'fitness': 'saludable'
        }
        
        self.intensificadores = {
            'muy': 1.5, 'super': 2.0, 'poco': 0.7, 'bastante': 1.3, 'mas': 1.2, 'menos': 0.8,
            'extremo': 2.5, 'ultra': 2.2, 'mega': 1.8, 'mini': 0.5, 'maxi': 1.6, 'extra': 1.4
        }
    
    def interpretar_tokens(self, tokens):
        """Convierte tokens genéricos en filtros semánticos"""
        tokens_mejorados = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            interpretado = False
            
            # Detectar intensificador previo
            factor_intensidad = 1.0
            if i > 0 and tokens[i-1]['valor'].lower() in self.intensificadores:
                factor_intensidad = self.intensificadores[tokens[i-1]['valor'].lower()]
            
            if token['tipo'] == 'PALABRA_GENERICA':
                valor = token['valor'].lower().strip()
                
                # Verificar si es precio cualitativo
                if valor in self.mapeo_precios:
                    precio_info = self.mapeo_precios[valor].copy()
                    
                    # Aplicar intensificador
                    if precio_info['op'] == 'menor_a':
                        precio_info['valor'] = precio_info['valor'] / factor_intensidad
                    elif precio_info['op'] == 'mayor_a':
                        precio_info['valor'] = precio_info['valor'] * factor_intensidad
                    
                    token['tipo'] = 'FILTRO_PRECIO'
                    token['interpretacion'] = precio_info
                    interpretado = True
                
                # Verificar si es tamaño
                elif valor in self.mapeo_tamanos:
                    tamano_info = self.mapeo_tamanos[valor].copy()
                    token['tipo'] = 'FILTRO_TAMANO'
                    token['interpretacion'] = tamano_info
                    interpretado = True
                
                # Si no se interpretó, verificar productos y categorías
                elif not interpretado:
                    # Primero buscar si es un producto específico conocido
                    categoria = self.buscar_categoria_similar(valor)
                    
                    if categoria:
                        # Verificar si la palabra está en nuestra lista de productos específicos
                        productos_especificos = {
                            'cheetos', 'doritos', 'sabritas', 'takis', 'ruffles', 'emperador', 'chokis',
                            'coca', 'pepsi', 'sprite', 'fanta', 'jumex', 'boing', 'electrolit',
                            'lala', 'danone', 'philadelphia', 'lactaid', 'chobani',
                            'bimbo', 'gamesa', 'herdez', 'fud', 'morelos', 'costena', 'bonafont',
                            'zote', 'roma', 'regio', 'carlos', 'payaso', 'trident', 'panditas'
                        }
                        
                        if valor in productos_especificos:
                            token['tipo'] = 'PRODUCTO'
                            token['valor_original'] = valor
                            token['categoria_inferida'] = categoria
                        else:
                            token['tipo'] = 'CATEGORIA'
                            token['valor_original'] = valor
                            token['valor'] = categoria
                    else:
                        # Si no hay coincidencia exacta, intentar con búsqueda aproximada
                        categoria = self.buscar_categoria_similar_fuzzy(valor, umbral=2)
                        if categoria:
                            token['tipo'] = 'CATEGORIA'
                            token['valor_original'] = valor
                            token['valor'] = categoria
                            token['coincidencia_aproximada'] = True
            
            tokens_mejorados.append(token)
            i += 1
        
        return tokens_mejorados

    def buscar_categoria_similar(self, palabra):
        """Busca categorías similares o sinónimos para productos específicos"""
        # Mapeo de productos/marcas a categorías específicas de BD (100+ sinónimos)
        productos_especificos = {
            # Snacks específicos (40+ sinónimos)
            'cheetos': 'Snacks Salados', 'doritos': 'Snacks Salados', 'sabritas': 'Snacks Salados',
            'takis': 'Snacks Salados', 'ruffles': 'Snacks Salados', 'emperador': 'Snacks Salados',
            'papitas': 'Snacks Salados', 'papas': 'Snacks Salados', 'frituras': 'Snacks Salados',
            'botanas': 'Snacks Salados', 'snacks': 'Snacks Salados', 'aperitivos': 'Snacks Salados',
            'bocadillos': 'Snacks Salados', 'picantes': 'Snacks Salados', 'picosos': 'Snacks Salados',
            'enchilados': 'Snacks Salados', 'salados': 'Snacks Salados', 'crujientes': 'Snacks Salados',
            'tostados': 'Snacks Salados', 'palomitas': 'Snacks Salados', 'cacahuates': 'Snacks Salados',
            'nueces': 'Snacks Salados', 'almendras': 'Snacks Salados', 'pistaches': 'Snacks Salados',
            'nachos': 'Snacks Salados', 'totopos': 'Snacks Salados', 'chicharrones': 'Snacks Salados',
            
            # Galletas y dulces (20+ sinónimos)
            'chokis': 'Galletas y Dulces', 'galletas': 'Galletas y Dulces', 'crackers': 'Galletas y Dulces',
            'dulce': 'Galletas y Dulces', 'dulces': 'Galletas y Dulces', 'chocolate': 'Galletas y Dulces',
            'caramelo': 'Galletas y Dulces', 'gomita': 'Galletas y Dulces', 'gomitas': 'Galletas y Dulces',
            'paleta': 'Galletas y Dulces', 'paletas': 'Galletas y Dulces', 'mazapán': 'Galletas y Dulces',
            'panditas': 'Galletas y Dulces', 'carlos': 'Galletas y Dulces', 'payaso': 'Galletas y Dulces',
            'trident': 'Galletas y Dulces', 'chicles': 'Galletas y Dulces', 'mentas': 'Galletas y Dulces',
            
            # Bebidas específicas (25+ sinónimos)
            'coca': 'Bebidas', 'cola': 'Bebidas', 'pepsi': 'Bebidas', 'sprite': 'Bebidas',
            'fanta': 'Bebidas', 'jumex': 'Bebidas', 'boing': 'Bebidas', 'electrolit': 'Bebidas',
            'refresco': 'Bebidas', 'refrescos': 'Bebidas', 'bebida': 'Bebidas', 'bebidas': 'Bebidas',
            'gaseosa': 'Bebidas', 'soda': 'Bebidas', 'agua': 'Bebidas', 'jugo': 'Bebidas', 'jugos': 'Bebidas',
            'néctar': 'Bebidas', 'te': 'Bebidas', 'cafe': 'Bebidas', 'latte': 'Bebidas',
            'capuchino': 'Bebidas', 'frape': 'Bebidas', 'energizante': 'Bebidas', 'isotónico': 'Bebidas',
            
            # Lácteos específicos (15+ sinónimos)
            'leche': 'Lácteos', 'yogurt': 'Lácteos', 'yogur': 'Lácteos', 'yoghurt': 'Lácteos',
            'queso': 'Lácteos', 'crema': 'Lácteos', 'mantequilla': 'Lácteos', 'requesón': 'Lácteos',
            'cottage': 'Lácteos', 'philadelphia': 'Lácteos', 'lala': 'Lácteos', 'danone': 'Lácteos',
            'lactaid': 'Lácteos', 'chobani': 'Lácteos', 'deslactosada': 'Lácteos',
            
            # Panadería y pastelería (15+ sinónimos)
            'pan': 'Panadería y Pastelería', 'panes': 'Panadería y Pastelería', 'bimbo': 'Panadería y Pastelería',
            'marinela': 'Panadería y Pastelería', 'wonder': 'Panadería y Pastelería', 'pastel': 'Panadería y Pastelería',
            'pasteles': 'Panadería y Pastelería', 'dona': 'Panadería y Pastelería', 'donas': 'Panadería y Pastelería',
            'muffin': 'Panadería y Pastelería', 'cupcake': 'Panadería y Pastelería', 'brownie': 'Panadería y Pastelería',
            'pay': 'Panadería y Pastelería', 'tostado': 'Panadería y Pastelería', 'integral': 'Panadería y Pastelería',
            
            # Frutas y verduras (10+ sinónimos)
            'fruta': 'Frutas y Verduras', 'frutas': 'Frutas y Verduras', 'verdura': 'Frutas y Verduras',
            'verduras': 'Frutas y Verduras', 'manzana': 'Frutas y Verduras', 'naranja': 'Frutas y Verduras',
            'plátano': 'Frutas y Verduras', 'uvas': 'Frutas y Verduras', 'pera': 'Frutas y Verduras',
            'tomate': 'Frutas y Verduras', 'cebolla': 'Frutas y Verduras', 'lechuga': 'Frutas y Verduras',
            
            # Carnes (10+ sinónimos)
            'carne': 'Carnes y Embutidos', 'carnes': 'Carnes y Embutidos', 'pollo': 'Carnes y Embutidos',
            'res': 'Carnes y Embutidos', 'cerdo': 'Carnes y Embutidos', 'jamón': 'Carnes y Embutidos',
            'salchicha': 'Carnes y Embutidos', 'salchichas': 'Carnes y Embutidos', 'tocino': 'Carnes y Embutidos',
            'chorizo': 'Carnes y Embutidos', 'fud': 'Carnes y Embutidos', 'herdez': 'Carnes y Embutidos',
            
            # Abarrotes (10+ sinónimos)  
            'arroz': 'Abarrotes Básicos', 'frijol': 'Abarrotes Básicos', 'frijoles': 'Abarrotes Básicos',
            'aceite': 'Abarrotes Básicos', 'azúcar': 'Abarrotes Básicos', 'sal': 'Abarrotes Básicos',
            'harina': 'Abarrotes Básicos', 'pasta': 'Abarrotes Básicos', 'atún': 'Abarrotes Básicos',
            'morelos': 'Abarrotes Básicos', 'costena': 'Abarrotes Básicos',
            
            # Limpieza (5+ sinónimos)
            'jabón': 'Limpieza del Hogar', 'detergente': 'Limpieza del Hogar', 'papel': 'Limpieza del Hogar',
            'zote': 'Limpieza del Hogar', 'roma': 'Limpieza del Hogar', 'regio': 'Limpieza del Hogar'
        }
        
        # Buscar en productos específicos primero
        palabra_lower = palabra.lower().strip()
        if palabra_lower in productos_especificos:
            return productos_especificos[palabra_lower]
        
        # Luego buscar en sinónimos de categorías (50+ sinónimos expandidos)
        sinonimos = {
            # Snacks/Botanas (15+ sinónimos)
            'botana': 'snacks', 'botanas': 'snacks', 'papitas': 'snacks', 'papas': 'snacks',
            'frituras': 'snacks', 'aperitivo': 'snacks', 'bocadillo': 'snacks', 'tentempié': 'snacks',
            'picante': 'snacks', 'picantes': 'snacks', 'picoso': 'snacks', 'picosos': 'snacks',
            'salado': 'snacks', 'salados': 'snacks', 'crujiente': 'snacks', 'tostado': 'snacks',
            
            # Bebidas (15+ sinónimos)
            'refresco': 'bebidas', 'refrescos': 'bebidas', 'gaseosa': 'bebidas', 'soda': 'bebidas',
            'bebida': 'bebidas', 'agua': 'bebidas', 'jugo': 'bebidas', 'jugos': 'bebidas',
            'néctar': 'bebidas', 'isotónico': 'bebidas', 'energizante': 'bebidas', 'vitaminada': 'bebidas',
            'mineral': 'bebidas', 'gasificada': 'bebidas', 'natural': 'bebidas',
            
            # Frutas y verduras (8+ sinónimos)
            'verdura': 'verduras', 'vegetal': 'verduras', 'fruta': 'frutas', 'hortaliza': 'verduras',
            'veggie': 'verduras', 'frescos': 'frutas', 'temporada': 'frutas', 'orgánico': 'frutas',
            
            # Lácteos (8+ sinónimos)
            'lacteo': 'lacteos', 'queso': 'lacteos', 'quesos': 'lacteos', 'yogur': 'lacteos',
            'leche': 'lacteos', 'cremoso': 'lacteos', 'descremado': 'lacteos', 'light': 'lacteos',
            
            # Carnes
            'carne': 'carnes',
            'pollo': 'carnes',
            'res': 'carnes',
            'cerdo': 'carnes',
            'pescado': 'carnes',
            
            # Limpieza
            'detergente': 'limpieza',
            'jabon': 'limpieza',
            'limpiador': 'limpieza'
        }
        
        # Normalizar la palabra (quitar espacios y plurales simples)
        palabra = palabra.strip()
        if palabra.endswith('s') and len(palabra) > 3:
            # También intentar con la versión singular
            singular = palabra[:-1]
            if singular in sinonimos:
                return sinonimos[singular]
        
        return sinonimos.get(palabra, None)
    
    def distancia_levenshtein(self, a, b):
        """Calcula la distancia de edición entre cadenas a y b"""
        if len(a) < len(b):
            return self.distancia_levenshtein(b, a)
            
        if len(b) == 0:
            return len(a)
        
        previous_row = range(len(b) + 1)
        for i, c1 in enumerate(a):
            current_row = [i + 1]
            for j, c2 in enumerate(b):
                # Calcular inserciones, eliminaciones y sustituciones
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
    def buscar_categoria_similar_fuzzy(self, palabra, umbral=2):
        """
        Busca categorías similares incluso con errores ortográficos
        
        Args:
            palabra: Palabra a buscar
            umbral: Distancia máxima permitida (menor = más exacto)
            
        Returns:
            str: Categoría encontrada o None
        """
        # Primero intentar con búsqueda exacta
        resultado = self.buscar_categoria_similar(palabra)
        if resultado:
            return resultado
            
        # Si no hay coincidencia exacta, buscar por similitud
        palabra = palabra.strip().lower()
        
        # Obtener todas las palabras clave
        todas_palabras = list(self.buscar_categoria_similar.__self__.__dict__.get('sinonimos', {}).keys())
        
        mejor_coincidencia = None
        menor_distancia = float('inf')
        
        # Buscar la palabra más cercana
        for candidato in todas_palabras:
            distancia = self.distancia_levenshtein(palabra, candidato)
            if distancia <= umbral and distancia < menor_distancia:
                menor_distancia = distancia
                mejor_coincidencia = candidato
        
        # Si encontramos una coincidencia cercana, devolver su categoría
        if mejor_coincidencia:
            return self.buscar_categoria_similar(mejor_coincidencia)
            
        return None
    
    def interpretar_consulta_completa(self, tokens, original_text):
        """
        Interpreta una consulta completa de manera semántica
        
        Args:
            tokens: Lista de tokens analizados léxicamente
            original_text: Texto original de la consulta
            
        Returns:
            dict: Interpretación completa con filtros, productos y SQL
        """
        # Interpretar tokens básicos
        tokens_interpretados = self.interpretar_tokens(tokens)
        
        # Extraer componentes semánticos
        producto = None
        categoria = None
        filtros_precio = []
        filtros_tamano = []
        
        for token in tokens_interpretados:
            if token['tipo'] in ['PRODUCTO', 'PRODUCTO_SIMPLE']:  # AGREGAR PRODUCTO_SIMPLE
                producto = token['valor']
                # INFERIR CATEGORÍA AUTOMÁTICAMENTE basada en el producto
                if not categoria:
                    categoria_inferida = self.buscar_categoria_similar(token['valor'])
                    if categoria_inferida:
                        categoria = categoria_inferida
            elif token['tipo'] == 'CATEGORIA':
                categoria = token['valor']
                # MANEJO ESPECIAL: Si la "categoría" es en realidad un producto específico como "papitas"
                categoria_lower = token['valor'].lower().strip()
                if categoria_lower in ['papitas', 'papas', 'snacks'] and not producto:
                    # Convertir "papitas/papas" en producto específico para consulta de snacks similares
                    if categoria_lower in ['papitas', 'papas']:
                        producto = 'papitas'  # Tratar como producto específico
                        categoria = 'Snacks Salados'  # Asignar categoría correcta
            elif token['tipo'] == 'FILTRO_PRECIO':
                filtros_precio.append(token['interpretacion'])
            elif token['tipo'] == 'FILTRO_TAMANO':
                filtros_tamano.append(token['interpretacion'])
        
        # Generar SQL
        sql_query = self.generar_sql(tokens_interpretados)
        
        # Crear respuesta estructurada
        resultado = {
            'consulta_original': original_text,
            'tokens_interpretados': tokens_interpretados,
            'interpretacion_semantica': {
                'producto': producto,
                'categoria': categoria,
                'filtros_precio': filtros_precio,
                'filtros_tamano': filtros_tamano
            },
            'sql_generado': sql_query,
            'confianza': self.calcular_confianza(tokens_interpretados)
        }
        
        return resultado
    
    def calcular_confianza(self, tokens):
        """Calcula un score de confianza para la interpretación"""
        if not tokens:
            return 0.0
        
        confianza = 0.8  # Base
        
        # Bonificar si hay productos/categorías reconocidas
        productos_encontrados = sum(1 for t in tokens if t['tipo'] in ['PRODUCTO', 'CATEGORIA'])
        confianza += productos_encontrados * 0.1
        
        # Bonificar filtros válidos
        filtros_encontrados = sum(1 for t in tokens if 'FILTRO' in t['tipo'])
        confianza += filtros_encontrados * 0.05
        
        return min(1.0, confianza)
    
    def generar_sql(self, tokens):
        """Genera consulta SQL basada en tokens interpretados"""
        select = "SELECT * FROM productos"
        where_conditions = []
        
        for token in tokens:
            if token['tipo'] in ['PRODUCTO', 'PRODUCTO_SIMPLE']:  # AGREGAR PRODUCTO_SIMPLE
                where_conditions.append(f"nombre LIKE '%{token['valor']}%'")
            elif token['tipo'] == 'CATEGORIA':
                where_conditions.append(f"categoria = '{token['valor']}'")
            elif token['tipo'] == 'FILTRO_PRECIO' and 'interpretacion' in token:
                precio_info = token['interpretacion']
                if precio_info['op'] == 'menor_a':
                    where_conditions.append(f"precio <= {precio_info['valor']}")
                elif precio_info['op'] == 'mayor_a':
                    where_conditions.append(f"precio >= {precio_info['valor']}")
        
        if where_conditions:
            sql = f"{select} WHERE {' AND '.join(where_conditions)}"
        else:
            sql = select
        
        return sql
