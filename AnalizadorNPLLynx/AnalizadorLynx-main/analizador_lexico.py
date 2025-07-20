# analizador_lexico.py
from afd_palabras import AFDPalabras
from afd_multipalabra import AFDMultipalabra
from afd_numeros import AFDNumeros
from afd_operadores import AFDOperadores
from afd_unidades import AFDUnidades
from interpretador_semantico import InterpretadorSemantico
from corrector_ortografico import CorrectorOrtografico
from motor_recomendaciones import MotorRecomendaciones
from adaptador_bd import AdaptadorBaseDatos  # Nuevo adaptador
from graphviz import Digraph
from datetime import datetime
import json

class AnalizadorLexicoLYNX:
    """Analizador léxico principal que coordina todos los AFDs"""
    
    def __init__(self, configuracion):
        self.configuracion = configuracion
        self.bd_escalable = configuracion.bd_escalable  # Usar bd_escalable en lugar de base_datos
        
        # Crear adaptador para compatibilidad con AFDs legacy
        self.adaptador_bd = AdaptadorBaseDatos(self.bd_escalable)
        self.base_datos = self.adaptador_bd  # Los AFDs esperan este nombre
        
        # Inicializar todos los AFDs
        self.afd_multipalabra = AFDMultipalabra(self.base_datos)
        self.afd_operadores = AFDOperadores(self.base_datos)
        self.afd_palabras = AFDPalabras(self.base_datos)
        self.afd_numeros = AFDNumeros()
        self.afd_unidades = AFDUnidades(self.base_datos)
        
        # Inicializar nuevos módulos
        self.corrector_ortografico = CorrectorOrtografico()
        self.interpretador_semantico = InterpretadorSemantico()
        
        # Crear configuración compatible para motor de recomendaciones
        configuracion_compatible = type('ConfiguracionCompatible', (), {
            'base_datos': self.adaptador_bd,  # Para compatibilidad legacy
            'adaptador_bd': self.adaptador_bd,  # Para motor inteligente 
            'bd_escalable': self.bd_escalable,
            'simulador': self.bd_escalable,  # Usar bd_escalable como simulador
            'obtener_estadisticas': configuracion.obtener_estadisticas
        })()
        
        self.motor_recomendaciones = MotorRecomendaciones(configuracion_compatible)
        
        # Lista de AFDs en orden de prioridad
        self.afds_prioritarios = [
            self.afd_multipalabra,
            self.afd_operadores,
            self.afd_numeros,
            self.afd_unidades,
            self.afd_palabras
        ]
        
        self.tokens_procesados = []
    
    def analizar(self, texto):
        """Analiza el texto y retorna los tokens encontrados"""
        self.tokens_procesados = []
        texto = texto.lower()
        posicion = 0
        
        while posicion < len(texto):
            # Saltar espacios en blanco
            if posicion < len(texto) and texto[posicion].isspace():
                posicion += 1
                continue
            
            # Intentar con cada AFD en orden de prioridad
            token_encontrado = False
            
            for afd in self.afds_prioritarios:
                resultado = afd.procesar_cadena(texto, posicion)
                
                if resultado:
                    self.tokens_procesados.append(resultado)
                    posicion = resultado['posicion_final']
                    token_encontrado = True
                    break
            
            # Si no se encontró token, avanzar un carácter
            if not token_encontrado:
                posicion += 1
        
        # Aplicar análisis contextual
        self.aplicar_contexto()
        
        # Aplicar interpretación semántica
        self.tokens_procesados = self.interpretador_semantico.interpretar_tokens(
            self.tokens_procesados
        )
        
        return self.tokens_procesados
    
    def aplicar_contexto(self):
        """Aplica reglas de contexto para mejorar la clasificación"""
        for i in range(len(self.tokens_procesados)):
            token_actual = self.tokens_procesados[i]
            
            # Regla 1: CATEGORIA_KEYWORD + PALABRA_GENERICA = CATEGORIA
            if (token_actual['tipo'] == 'CATEGORIA_KEYWORD' and 
                i + 1 < len(self.tokens_procesados) and
                self.tokens_procesados[i + 1]['tipo'] == 'PALABRA_GENERICA'):
                self.tokens_procesados[i + 1]['tipo'] = 'CATEGORIA'
            
            # Regla 2: MODIFICADOR + PALABRA_GENERICA = ATRIBUTO
            if (token_actual['tipo'] == 'MODIFICADOR' and 
                i + 1 < len(self.tokens_procesados) and
                self.tokens_procesados[i + 1]['tipo'] in ['PALABRA_GENERICA', 'MODIFICADOR']):
                self.tokens_procesados[i + 1]['tipo'] = 'ATRIBUTO'
            
            # Regla 3: NUMERO + PALABRA_GENERICA (si es unidad) = UNIDAD
            if (token_actual['tipo'] in ['NUMERO_ENTERO', 'NUMERO_DECIMAL'] and 
                i + 1 < len(self.tokens_procesados)):
                siguiente = self.tokens_procesados[i + 1]
                if siguiente['valor'] in self.base_datos['unidades']:
                    if siguiente['valor'] in ['pesos', 'peso']:
                        siguiente['tipo'] = 'UNIDAD_MONEDA'
                    else:
                        siguiente['tipo'] = 'UNIDAD_MEDIDA'
    
    def generar_json_resultado(self, texto_original):
        """Genera el resultado en formato JSON"""
        resultado = {
            'consulta_original': texto_original,
            'tokens': self.tokens_procesados,
            'interpretacion': self._interpretar_tokens(),
            'sql_sugerido': self._generar_sql()
        }
        
        return json.dumps(resultado, ensure_ascii=False, indent=2)
    
    def _interpretar_tokens(self):
        """Interpreta los tokens para generar la estructura semántica"""
        interpretacion = {
            'productos': [],
            'categorias': [],
            'filtros': {
                'atributos': [],
                'precio': {},
                'cantidad': {},
                'tamano': {},  # NUEVO
                'calidad': {}  # NUEVO
            }
        }
        
        i = 0
        while i < len(self.tokens_procesados):
            token = self.tokens_procesados[i]
            
            # Productos
            if token['tipo'] in ['PRODUCTO_COMPLETO', 'PRODUCTO_MULTI', 'PRODUCTO_SIMPLE']:
                interpretacion['productos'].append({
                    'nombre': token['valor'],
                    'tipo': token['tipo']
                })
            
            # Categorías
            elif token['tipo'] == 'CATEGORIA':
                interpretacion['categorias'].append(token['valor'])
            
            # Operadores de precio
            elif token['tipo'] in ['OP_MENOR', 'OP_MAYOR', 'OP_ENTRE', 'OP_IGUAL']:
                if i + 1 < len(self.tokens_procesados):
                    siguiente = self.tokens_procesados[i + 1]
                    if siguiente['tipo'] in ['NUMERO_ENTERO', 'NUMERO_DECIMAL']:
                        valor = float(siguiente['valor'])
                        
                        if token['tipo'] == 'OP_MENOR':
                            interpretacion['filtros']['precio']['max'] = valor
                        elif token['tipo'] == 'OP_MAYOR':
                            interpretacion['filtros']['precio']['min'] = valor
                        elif token['tipo'] == 'OP_IGUAL':
                            interpretacion['filtros']['precio']['exacto'] = valor
                        
                        i += 1  # Saltar el número
            
            # Atributos con modificadores
            elif token['tipo'] == 'MODIFICADOR':
                if i + 1 < len(self.tokens_procesados):
                    siguiente = self.tokens_procesados[i + 1]
                    if siguiente['tipo'] == 'ATRIBUTO':
                        # Agregar a los filtros de atributos
                        filtro_atributo = {
                            'modificador': token['valor'],
                            'atributo': siguiente['valor']
                        }
                        interpretacion['filtros']['atributos'].append(filtro_atributo)
                        i += 1  # Saltar el atributo
            
            # Filtros semánticos de precio
            elif token['tipo'] == 'FILTRO_PRECIO':
                interp = token['interpretacion']
                if interp['op'] == 'menor_a':
                    interpretacion['filtros']['precio']['max'] = interp['valor']
                elif interp['op'] == 'mayor_a':
                    interpretacion['filtros']['precio']['min'] = interp['valor']
                elif interp['op'] == 'entre':
                    interpretacion['filtros']['precio']['min'] = interp['min']
                    interpretacion['filtros']['precio']['max'] = interp['max']
            
            # Filtros de tamaño
            elif token['tipo'] == 'FILTRO_TAMANO':
                interp = token['interpretacion']
                interpretacion['filtros']['tamano'] = {
                    'campo': interp['campo'],
                    'operador': interp['op'],
                    'valor': interp['valor']
                }
            
            i += 1
        
        return interpretacion
    
    def _generar_sql(self):
        """Genera una consulta SQL basada en los tokens"""
        interpretacion = self._interpretar_tokens()
        
        # Construcción de condiciones
        condiciones = []
        
        # Agregar filtros de productos
        if interpretacion['productos']:
            nombres = [p['nombre'] for p in interpretacion['productos']]
            condiciones.append(f"nombre IN ({', '.join([f'\'{n}\'' for n in nombres])})")
        
        # Agregar filtros de categorías
        if interpretacion['categorias']:
            condiciones.append(f"categoria IN ({', '.join([f'\'{c}\'' for c in interpretacion['categorias']])})")
        
        # Agregar filtros de precio
        if 'max' in interpretacion['filtros']['precio']:
            condiciones.append(f"precio <= {interpretacion['filtros']['precio']['max']}")
        if 'min' in interpretacion['filtros']['precio']:
            condiciones.append(f"precio >= {interpretacion['filtros']['precio']['min']}")
            
        # Filtros de tamaño
        if interpretacion['filtros'].get('tamano'):
            tam = interpretacion['filtros']['tamano']
            if tam['operador'] == 'mayor_a':
                condiciones.append(f"{tam['campo']} >= {tam['valor']}")
            elif tam['operador'] == 'menor_a':
                condiciones.append(f"{tam['campo']} <= {tam['valor']}")
            
        # Agregar filtros de atributos
        if interpretacion['filtros']['atributos']:
            for filtro in interpretacion['filtros']['atributos']:
                modificador = filtro['modificador']
                atributo = filtro['atributo']
                
                if modificador == 'sin':
                    condiciones.append(f"NOT (atributos LIKE '%{atributo}%')")
                elif modificador == 'con':
                    condiciones.append(f"atributos LIKE '%{atributo}%'")
                elif modificador == 'extra':
                    condiciones.append(f"atributos LIKE '%extra {atributo}%'")
        
        # Construir SQL final
        sql = "SELECT * FROM productos"
        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)
        
        return sql
    
    def generar_diagrama_general(self, estilo_moderno=False, formato='png'):
        """
        Genera un diagrama que muestra la interacción entre todos los AFDs
        
        Args:
            estilo_moderno: Si es True, utiliza un estilo más moderno para el diagrama
            formato: Formato de salida ('png', 'svg', 'pdf')
        """
        dot = Digraph(comment='Sistema AFD LYNX - Vista General')
        
        # Configuraciones según estilo
        if estilo_moderno:
            # Estilo moderno con colores suaves y mejor formato
            dot.attr(rankdir='TB', size='14,12', bgcolor='#fafafa')
            dot.attr('graph', fontname='Arial', fontsize='18', fontcolor='#333333',
                    splines='ortho', nodesep='0.8', ranksep='1.2')
            dot.attr('node', fontname='Arial', fontsize='14', fontcolor='#333333',
                    height='0.8', width='1.5', penwidth='2', margin='0.15')
            dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555',
                    arrowsize='0.8', penwidth='1.5')
            
            # Colores específicos para los nodos
            color_entrada = "#AADDFF"  # Azul claro
            color_analizador = "#FFD700"  # Dorado
            color_afds = {
                'afd_multi': "#90EE90",  # Verde claro
                'afd_op': "#FFB6C1",     # Rosa claro
                'afd_num': "#FFD580",    # Amarillo melocotón
                'afd_uni': "#D8BFD8",    # Cardo
                'afd_pal': "#ADD8E6"     # Azul claro
            }
            color_salida = "#E6E6E6"     # Gris claro
            color_json = "#98FB98"       # Verde menta
        else:
            # Estilo clásico
            dot.attr(rankdir='TB', size='12,10')
            
            # Colores básicos
            color_entrada = "lightblue"
            color_analizador = "yellow"
            color_afds = {
                'afd_multi': "lightgreen",
                'afd_op': "lightcoral",
                'afd_num': "lightsalmon",
                'afd_uni': "lightpink",
                'afd_pal': "lightcyan"
            }
            color_salida = "lightgray"
            color_json = "lightgreen"
        
        # Formas de nodos según estilo
        if estilo_moderno:
            forma_proceso = 'box'
            forma_afd = 'ellipse'
            estilo_nodo = 'filled,rounded'
            estilo_borde = '1px'
        else:
            forma_proceso = 'box'
            forma_afd = 'ellipse'
            estilo_nodo = 'filled'
            estilo_borde = ''
        
        # Nodo principal
        dot.node('entrada', 'Texto de Entrada', shape=forma_proceso, style=estilo_nodo, 
                fillcolor=color_entrada)
        dot.node('analizador', 'Analizador Principal', shape=forma_proceso, style=estilo_nodo, 
                fillcolor=color_analizador)
        
        # Nodos AFDs
        afds_info = [
            ('afd_multi', 'AFD\nMulti-palabra'),
            ('afd_op', 'AFD\nOperadores'),
            ('afd_num', 'AFD\nNúmeros'),
            ('afd_uni', 'AFD\nUnidades'),
            ('afd_pal', 'AFD\nPalabras')
        ]
        
        for nodo, label in afds_info:
            dot.node(nodo, label, shape=forma_afd, style=estilo_nodo, 
                    fillcolor=color_afds.get(nodo, "lightgray"))
        
        # Nodos semánticos (nuevo en estilo moderno)
        if estilo_moderno:
            dot.node('tokens', 'Tokens\nReconocidos', shape=forma_proceso, style=estilo_nodo, 
                    fillcolor=color_salida)
            dot.node('contexto', 'Análisis\nContextual', shape=forma_proceso, style=estilo_nodo, 
                    fillcolor=color_salida)
            dot.node('semantico', 'Interpretación\nSemántica', shape=forma_proceso, style=estilo_nodo, 
                    fillcolor=color_salida)
            dot.node('json', 'Salida JSON', shape=forma_proceso, style=estilo_nodo, 
                    fillcolor=color_json)
            
            # Conexiones adicionales
            dot.edge('contexto', 'semantico')
            dot.edge('semantico', 'json')
        else:
            # Nodos de salida (estilo original)
            dot.node('tokens', 'Tokens\nReconocidos', shape='box', style='filled', 
                    fillcolor=color_salida)
            dot.node('contexto', 'Análisis\nContextual', shape='box', style='filled', 
                    fillcolor=color_salida)
            dot.node('json', 'Salida JSON', shape='box', style='filled', 
                    fillcolor=color_json)
            
            # Conexiones originales
            dot.edge('contexto', 'json')
        
        # Conexiones comunes
        if estilo_moderno:
            # Estilo de flecha mejorado
            dot.edge('entrada', 'analizador', penwidth='1.8', color='#333333')
            
            for nodo, _ in afds_info:
                dot.edge('analizador', nodo, style='dashed', penwidth='1.3', color='#555555')
                dot.edge(nodo, 'tokens', penwidth='1.3', color='#333333')
            
            dot.edge('tokens', 'contexto', penwidth='1.5', color='#333333')
        else:
            # Estilo de flecha original
            dot.edge('entrada', 'analizador')
            
            for nodo, _ in afds_info:
                dot.edge('analizador', nodo, style='dashed')
                dot.edge(nodo, 'tokens')
            
            dot.edge('tokens', 'contexto')
        
        # Título del diagrama (solo en modo moderno)
        if estilo_moderno:
            dot.attr(label='Sistema de Análisis Léxico LYNX')
            dot.attr(labelloc='t')
            dot.attr(labelfontsize='20')
            dot.attr(labelfontcolor='#333333')
        
        # Guardar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.configuracion.directorio_salida}/sistema_general"
        
        if estilo_moderno:
            filename += "_moderno"
            
        filename += f"_{timestamp}"
        
        # Renderizar en el formato especificado
        dot.render(filename, format=formato, cleanup=True)
        ruta_completa = f"{filename}.{formato}"
        print(f"Diagrama general guardado: {ruta_completa}")
        
        # Devolver tanto el objeto dot como la ruta del archivo generado
        return dot, ruta_completa
    
    def analizar_con_correccion(self, texto):
        """
        Analiza texto con corrección ortográfica integrada
        """
        # Paso 1: Aplicar corrección ortográfica
        resultado_correccion = self.corrector_ortografico.corregir_consulta(texto)
        
        # Paso 2: Analizar con el texto corregido
        texto_final = resultado_correccion.get('corrected_query', texto)
        tokens = self.analizar(texto_final)
        
        return {
            'tokens': tokens,
            'correcciones': resultado_correccion
        }
    
    def generar_json_resultado_completo(self, consulta_original):
        """
        Genera respuesta JSON completa con corrección, análisis e interpretación
        """
        # Análisis con corrección
        resultado_analisis = self.analizar_con_correccion(consulta_original)
        tokens = resultado_analisis['tokens']
        correcciones = resultado_analisis['correcciones']
        
        # Interpretación semántica
        interpretacion = self.interpretador_semantico.interpretar_consulta_completa(
            tokens, consulta_original
        )
        
        # Mapear datos para el motor de recomendaciones
        interpretacion_para_motor = {
            'producto': interpretacion['interpretacion_semantica'].get('producto'),
            'categoria': interpretacion['interpretacion_semantica'].get('categoria'),
            'filtros': {
                'precio': {},
                'atributos': []
            },
            'atributos': []
        }
        
        # NUEVO: Detectar productos por nombre si no hay producto específico
        texto_completo = consulta_original.lower()
        
        if not interpretacion_para_motor['producto']:
            # Lista de nombres de productos comunes que deberían buscarse como productos
            productos_comunes = [
                'chocolate', 'coca', 'pepsi', 'sprite', 'fanta', 
                'leche', 'yogurt', 'queso', 'pan', 'tortilla',
                'papitas', 'doritos', 'cheetos', 'sabritas', 
                'agua', 'jugo', 'cerveza', 'vino', 'refresco',
                'botana', 'frituras', 'galletas', 'dulces',
                'arroz', 'frijoles', 'aceite', 'sal', 'azucar'
            ]
            
            for producto_comun in productos_comunes:
                if producto_comun in texto_completo:
                    interpretacion_para_motor['producto'] = producto_comun
                    print(f"🔍 Producto detectado por nombre: {producto_comun}")
                    break
        
        # NUEVO: Extraer atributos directamente de los tokens
        
        # Detectar atributos compuestos primero
        atributos_compuestos = {
            'sin azucar': 'sin_azucar',
            'sin azúcar': 'sin_azucar', 
            'sin lactosa': 'sin_lactosa',
            'sin gluten': 'sin_gluten',
            'sin picante': 'sin_picante',
            'sin sal': 'sin_sal',
            'sin gas': 'sin_gas',
            'extra picante': 'extra_picante',
            'extra fuego': 'extra_picante',
            'flaming hot': 'picante',
            'flamming hot': 'picante',
            'sabor fuego': 'picante',
            'con fuego': 'picante',
            'muy picante': 'extra_picante',
            'muy dulce': 'muy_dulce',
            'poco salado': 'poco_salado',
            'deslactosado': 'sin_lactosa',
            'deslactosada': 'sin_lactosa',
            # AGREGADO: Mapeo directo individual
            'fuego': 'picante',
            'fuegos': 'picante'
        }
        
        for frase, atributo_normalizado in atributos_compuestos.items():
            if frase in texto_completo:
                interpretacion_para_motor['atributos'].append(atributo_normalizado)
                print(f"🎯 Atributo compuesto detectado: {frase} -> {atributo_normalizado}")
        
        # Detectar patrones de precio específicos (ej: "mayor a 50")
        import re  # Mover la importación aquí para evitar conflictos
        
        patron_mayor_precio = re.search(r'(mayor\s+a|mas\s+de|superior\s+a)\s+(\d+)', texto_completo)
        if patron_mayor_precio:
            valor_precio = float(patron_mayor_precio.group(2))
            interpretacion_para_motor['filtros']['precio']['min'] = valor_precio
            print(f"💰 Filtro precio mínimo detectado: ${valor_precio}")
        
        patron_menor_precio = re.search(r'(menor\s+a|menos\s+de|inferior\s+a|bajo\s+(\d+))\s+(\d+)', texto_completo)
        if patron_menor_precio:
            valor_precio = float(patron_menor_precio.group(-1))  # Último grupo capturado
            interpretacion_para_motor['filtros']['precio']['max'] = valor_precio
            print(f"💰 Filtro precio máximo detectado: ${valor_precio}")
        
        # Detectar contexto "botana mayor a X" específicamente
        patron_categoria_precio = re.search(r'(botana[s]?|snack[s]?|bebida[s]?|producto[s]?)\s+(mayor\s+a|mas\s+de)\s+(\d+)', texto_completo)
        if patron_categoria_precio:
            categoria_detectada = patron_categoria_precio.group(1)
            valor_precio = float(patron_categoria_precio.group(3))
            
            # Mapear categoría
            mapeo_categorias = {
                'botana': 'snacks',
                'botanas': 'snacks',
                'bebida': 'bebidas',
                'bebidas': 'bebidas',
                'producto': None,
                'productos': None
            }
            
            categoria_final = mapeo_categorias.get(categoria_detectada, categoria_detectada)
            if categoria_final and not interpretacion_para_motor.get('categoria'):
                interpretacion_para_motor['categoria'] = categoria_final
                print(f"📂 Categoría por contexto precio: {categoria_final}")
            
            interpretacion_para_motor['filtros']['precio']['min'] = valor_precio
            print(f"💰 Filtro combinado detectado: {categoria_detectada} mayor a ${valor_precio}")
        
        # Detectar atributos individuales
        for token in tokens:
            if token['tipo'] in ['ATRIBUTO', 'PALABRA_GENERICA']:
                # Verificar si es un atributo conocido
                valor_token = token['valor'].lower()
                if valor_token in ['dulce', 'picante', 'salado', 'barato', 'caro', 'grande', 'pequeño', 'fuego', 'flaming', 'hot']:
                    # Mapear sinónimos de picante
                    if valor_token in ['fuego', 'flaming', 'hot']:
                        valor_token = 'picante'  # Normalizar a picante
                    
                    if valor_token not in interpretacion_para_motor['atributos']:
                        interpretacion_para_motor['atributos'].append(valor_token)
                        print(f"🎯 Atributo individual detectado: {valor_token}")
        
        # Detectar atributos en contexto (ej: "productos picantes")
        patrones_contexto = {
            r'producto[s]?\s+picante[s]?': 'picante',
            r'producto[s]?\s+fuego': 'picante',
            r'producto[s]?\s+flaming': 'picante',
            r'producto[s]?\s+hot': 'picante',
            r'papitas?\s+fuego': 'picante',
            r'papitas?\s+flaming\s+hot': 'picante',
            r'botana[s]?\s+fuego': 'picante',
            r'snack[s]?\s+hot': 'picante',
            # AGREGADO: Patrones específicos para Takis Fuego
            r'takis\s+fuego[s]?': 'picante',
            r'takis\s+flaming': 'picante',
            r'takis\s+hot': 'picante',
            r'dorito[s]?\s+fuego[s]?': 'picante',
            r'cheeto[s]?\s+fuego[s]?': 'picante',
            r'cheeto[s]?\s+flaming': 'picante',
            # Otros patrones existentes
            r'bebida[s]?\s+dulce[s]?': 'dulce', 
            r'comida[s]?\s+salada[s]?': 'salado',
            r'cosa[s]?\s+barata[s]?': 'barato',
            r'articulo[s]?\s+caro[s]?': 'caro',
            r'botana[s]?\s+mayor\s+a\s+(\d+)': 'precio_alto',
            r'frituras?\s+salada[s]?': 'salado',
            r'papitas?\s+sin\s+picante': 'sin_picante',
            r'refresco[s]?\s+grande[s]?': 'grande',
            r'agua\s+sin\s+gas': 'sin_gas'
        }
        
        for patron, atributo in patrones_contexto.items():
            if re.search(patron, texto_completo):
                if atributo not in interpretacion_para_motor['atributos']:
                    interpretacion_para_motor['atributos'].append(atributo)
                    print(f"🎯 Atributo en contexto detectado: {atributo}")
        
        # También revisar si hay filtros de sabor en la interpretación semántica
        if 'filtros_sabor' in interpretacion['interpretacion_semantica']:
            for sabor in interpretacion['interpretacion_semantica']['filtros_sabor']:
                if sabor not in interpretacion_para_motor['atributos']:
                    interpretacion_para_motor['atributos'].append(sabor)
        
        # Procesar filtros de precio
        filtros_precio = interpretacion['interpretacion_semantica'].get('filtros_precio', [])
        if filtros_precio:
            for filtro in filtros_precio:
                if filtro.get('op') == 'menor_a':
                    interpretacion_para_motor['filtros']['precio']['max'] = filtro.get('valor')
                elif filtro.get('op') == 'mayor_a':
                    interpretacion_para_motor['filtros']['precio']['min'] = filtro.get('valor')
        
        # Generar recomendaciones usando la BD simulada
        recomendaciones = []
        try:
            recomendaciones = self.motor_recomendaciones.generar_recomendaciones(
                interpretacion_para_motor
            )
        except Exception as e:
            print(f"Error generando recomendaciones: {e}")
            # Fallback a productos populares
            from configuracion_bd import simulador_bd
            productos_populares = simulador_bd.obtener_productos_populares(5)
            for producto in productos_populares:
                recomendaciones.append({
                    'product_id': producto['id'],
                    'name': producto['nombre'],
                    'category': producto['categoria'],
                    'price': producto['precio'],
                    'available': True,
                    'match_score': 0.6,
                    'match_reasons': ['producto_popular']
                })
        
        # Generar consulta SQL
        sql_query = interpretacion.get('sql_generado', 'SELECT * FROM Productos LIMIT 10')
        
        # Generar mensaje para el usuario basado en resultados
        if recomendaciones:
            mensaje_usuario = f"Se encontraron {len(recomendaciones)} productos que coinciden con tu búsqueda."
        else:
            mensaje_usuario = "No se encontraron productos que coincidan con tu búsqueda."
        
        # Estructura de respuesta según documento técnico
        respuesta = {
            "success": True,
            "processing_time_ms": 0,
            "original_query": consulta_original,
            "corrections": correcciones,
            "interpretation": interpretacion_para_motor,
            "sql_query": sql_query,
            "recommendations": recomendaciones,
            "user_message": mensaje_usuario
        }
        
        return json.dumps(respuesta, ensure_ascii=False, indent=2)
    
    def _generar_consulta_sql_desde_interpretacion(self, interpretacion):
        """Genera consulta SQL basada en la interpretación"""
        if not interpretacion or 'interpretacion' not in interpretacion:
            return "SELECT * FROM Productos LIMIT 10"
        
        interp = interpretacion['interpretacion']
        
        # Base de la consulta
        sql = "SELECT p.*, c.nombre as categoria FROM Productos p JOIN Categorias c ON p.id_categoria = c.id_categoria"
        condiciones = []
        
        # Filtrar por categoría
        if interp.get('categoria'):
            condiciones.append(f"c.nombre = '{interp['categoria']}'")
        
        # Filtros de precio
        filtros = interp.get('filtros', {})
        if filtros.get('precio'):
            precio_filtros = filtros['precio']
            if 'max' in precio_filtros:
                condiciones.append(f"p.precio <= {precio_filtros['max']}")
            if 'min' in precio_filtros:
                condiciones.append(f"p.precio >= {precio_filtros['min']}")
            if 'exacto' in precio_filtros:
                condiciones.append(f"p.precio = {precio_filtros['exacto']}")
        
        # Filtros de atributos
        if filtros.get('atributos'):
            for attr in filtros['atributos']:
                if isinstance(attr, dict):
                    atributo = attr.get('atributo', '')
                    modificador = attr.get('modificador', 'con')
                    
                    if modificador == 'sin':
                        condiciones.append(f"(p.nombre NOT LIKE '%{atributo}%' AND p.descripcion NOT LIKE '%{atributo}%')")
                    else:
                        condiciones.append(f"(p.nombre LIKE '%{atributo}%' OR p.descripcion LIKE '%{atributo}%')")
        
        # Productos específicos
        if interp.get('productos'):
            productos_condiciones = []
            for producto in interp['productos']:
                nombre = producto.get('nombre', '')
                productos_condiciones.append(f"p.nombre LIKE '%{nombre}%'")
            if productos_condiciones:
                condiciones.append(f"({' OR '.join(productos_condiciones)})")
        
        # Construir WHERE clause
        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)
        
        # Ordenamiento
        if filtros.get('precio', {}).get('tendency') == 'low':
            sql += " ORDER BY p.precio ASC"
        elif filtros.get('precio', {}).get('tendency') == 'high':
            sql += " ORDER BY p.precio DESC"
        else:
            sql += " ORDER BY p.nombre ASC"
        
        sql += " LIMIT 20"
        return sql
        
        # Generar diagramas individuales con estilos específicos
        for afd, layout in config_afds:
            visualizador.visualizar(afd, layout=layout, mostrar_completo=False)
        
        # Generar diagrama del sistema completo
        visualizador.visualizar_sistema(self)
        
        print("Todos los diagramas modernos han sido generados!")
        
        # Mostrar mensaje informativo
        print("\nPuede encontrar los diagramas modernos en la carpeta 'diagramas_modernos/'")
        
    def generar_todos_los_diagramas(self, incluir_modernos=False, estilo_moderno=False, formato='png'):
        """Genera todos los diagramas individuales y el general
        
        Args:
            incluir_modernos: Si es True, genera también diagramas usando NetworkX/Matplotlib
            estilo_moderno: Si es True, utiliza estilos modernos para los diagramas de Graphviz
            formato: Formato de salida para los diagramas ('png', 'svg', 'pdf')
            
        Returns:
            tuple: (ruta_general, rutas_diagramas) - Rutas a los archivos generados
        """
        print(f"Generando diagramas AFD{' con estilo moderno' if estilo_moderno else ''}...")
        
        rutas_diagramas = []
        
        # Diagramas individuales
        for afd in self.afds_prioritarios:
            _, ruta = afd.generar_diagrama(mostrar_completo=False, estilo_moderno=estilo_moderno, formato=formato)
            rutas_diagramas.append(ruta)
        
        # Diagrama general
        _, ruta_general = self.generar_diagrama_general(estilo_moderno=estilo_moderno, formato=formato)
        
        # Opcionalmente generar diagramas modernos con NetworkX/Matplotlib
        if incluir_modernos:
            try:
                self.generar_diagramas_modernos()
            except ImportError as e:
                print(f"No se pudieron generar diagramas modernos: {e}")
                print("Para utilizar diagramas modernos, instale las dependencias requeridas:")
                print("  pip install networkx matplotlib numpy")
                
        print("Todos los diagramas han sido generados!")
        
        # Devolver la ruta al diagrama general y la lista de todas las rutas
        return ruta_general, rutas_diagramas