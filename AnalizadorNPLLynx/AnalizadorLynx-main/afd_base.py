# afd_base.py
from abc import ABC, abstractmethod
from graphviz import Digraph
import os
from datetime import datetime

class AFDBase(ABC):
    """Clase base abstracta para todos los AFDs del sistema"""
    
    def __init__(self, nombre):
        self.nombre = nombre
        self.estados = set()
        self.alfabeto = set()
        self.transiciones = {}
        self.estado_inicial = None
        self.estados_finales = set()
        self.tokens_reconocidos = []
        self.directorio_salida = "diagramas_afd"
        self._crear_directorio()
    
    def _crear_directorio(self):
        """Crea el directorio de salida si no existe"""
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
    
    @abstractmethod
    def construir_automata(self):
        """Método abstracto para construir el autómata específico"""
        pass
    
    @abstractmethod
    def get_tipo_token(self, lexema):
        """Retorna el tipo de token para un lexema dado"""
        pass
    
    def agregar_estado(self, estado, es_final=False):
        """Agrega un estado al autómata"""
        self.estados.add(estado)
        if es_final:
            self.estados_finales.add(estado)
    
    def agregar_transicion(self, estado_origen, simbolo, estado_destino):
        """Agrega una transición al autómata"""
        if estado_origen not in self.transiciones:
            self.transiciones[estado_origen] = {}
        self.transiciones[estado_origen][simbolo] = estado_destino
        self.alfabeto.add(simbolo)
    
    def establecer_estado_inicial(self, estado):
        """Establece el estado inicial"""
        self.estado_inicial = estado
        self.estados.add(estado)
    
    def procesar_cadena(self, cadena, posicion_inicial=0):
        """Procesa una cadena y retorna el token reconocido si existe"""
        estado_actual = self.estado_inicial
        lexema = ""
        i = posicion_inicial
        ultima_aceptacion = None
        ultima_posicion = posicion_inicial
        
        while i < len(cadena):
            simbolo = cadena[i]
            
            # Verificar si hay transición
            if estado_actual in self.transiciones and simbolo in self.transiciones[estado_actual]:
                estado_actual = self.transiciones[estado_actual][simbolo]
                lexema += simbolo
                
                # Si es estado final, guardar esta posición
                if estado_actual in self.estados_finales:
                    ultima_aceptacion = lexema
                    ultima_posicion = i + 1
                
                i += 1
            else:
                break
        
        # Retornar el último token válido encontrado
        if ultima_aceptacion:
            return {
                'tipo': self.get_tipo_token(ultima_aceptacion),
                'valor': ultima_aceptacion,
                'posicion_inicial': posicion_inicial,
                'posicion_final': ultima_posicion,
                'longitud': len(ultima_aceptacion)
            }
        
        return None
    
    def generar_diagrama(self, mostrar_completo=True, estilo_moderno=False, formato='png'):
        """
        Genera el diagrama del autómata
        
        Args:
            mostrar_completo: Si es True, muestra todas las transiciones individuales
            estilo_moderno: Si es True, utiliza un estilo más moderno para el diagrama
            formato: Formato de salida ('png', 'svg', 'pdf')
        """
        dot = Digraph(comment=f'AFD {self.nombre}')
        
        # Configuraciones según estilo
        if estilo_moderno:
            # Estilo moderno con colores suaves y mejor formato
            dot.attr(rankdir='LR', size='12,10', bgcolor='#fafafa', 
                    fontname='Arial', pad='0.5', nodesep='0.8')
            dot.attr('graph', fontsize='16', fontcolor='#333333', 
                    splines='curved', style='filled')
            dot.attr('node', shape='circle', style='filled,rounded', 
                    fontname='Arial', fontsize='14', fontcolor='#333333',
                    height='0.6', width='0.6', penwidth='2')
            dot.attr('edge', fontname='Arial', fontsize='12', fontcolor='#555555', 
                    arrowsize='0.8', penwidth='1.5')
            
            # Colores específicos para los nodos
            color_inicial = "#90EE90"  # Verde claro
            color_final = "#FFB6C1"    # Rosa claro
            color_normal = "#87CEEB"   # Azul cielo
        else:
            # Estilo clásico
            dot.attr(rankdir='LR', size='10,8')
            dot.attr('node', shape='circle')
            
            # Colores básicos
            color_inicial = "lightgreen"
            color_final = "lightgreen"
            color_normal = "white"
        
        # Configurar nodo inicial con flecha de entrada
        dot.node('inicio', shape='point', height='0.1', width='0.1', style='filled', fillcolor='black')
        
        if estilo_moderno:
            dot.edge('inicio', self.estado_inicial, penwidth='1.5', arrowsize='1')
        else:
            dot.edge('inicio', self.estado_inicial)
        
        # Agregar estados
        for estado in self.estados:
            if estado == self.estado_inicial and estado in self.estados_finales:
                # Estado inicial y final
                dot.node(estado, shape='doublecircle', style='filled', fillcolor=color_inicial, 
                        color='#2E8B57' if estilo_moderno else 'black')
            elif estado == self.estado_inicial:
                # Solo estado inicial
                dot.node(estado, style='filled', fillcolor=color_inicial,
                        color='#2E8B57' if estilo_moderno else 'black')
            elif estado in self.estados_finales:
                # Solo estado final
                dot.node(estado, shape='doublecircle', style='filled', fillcolor=color_final,
                        color='#CD5C5C' if estilo_moderno else 'black')
            else:
                # Estado normal
                if estilo_moderno:
                    dot.node(estado, style='filled', fillcolor=color_normal, color='#4682B4')
                else:
                    dot.node(estado)
        
        # Agregar transiciones
        if mostrar_completo:
            for origen, trans in self.transiciones.items():
                for simbolo, destino in trans.items():
                    dot.edge(origen, destino, label=simbolo)
        else:
            # Versión simplificada agrupando transiciones
            for origen in self.transiciones:
                destinos = {}
                for simbolo, destino in self.transiciones[origen].items():
                    if destino not in destinos:
                        destinos[destino] = []
                    destinos[destino].append(simbolo)
                
                for destino, simbolos in destinos.items():
                    if len(simbolos) > 3:
                        label = f"{simbolos[0]},{simbolos[1]},...,{simbolos[-1]}"
                    else:
                        label = ','.join(simbolos)
                    
                    # Estilo de las flechas según el modo
                    if estilo_moderno:
                        # Arcos curvos para mejor visualización
                        es_bucle = origen == destino
                        curve_distance = '1' if es_bucle else '0.3'
                        dot.edge(origen, destino, label=label, dir='forward',
                                minlen='2' if es_bucle else '1', 
                                constraint='true',
                                style='solid',
                                penwidth='1.2',
                                color='#555555',
                                fontcolor='#333333')
                    else:
                        dot.edge(origen, destino, label=label)
        
        # Título del diagrama (solo en modo moderno)
        if estilo_moderno:
            dot.attr(label=f'Autómata Finito Determinista: {self.nombre}')
            dot.attr(labelloc='t')
            dot.attr(labelfontsize='18')
            dot.attr(labelfontcolor='#333333')
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.directorio_salida}/afd_{self.nombre}"
        
        if estilo_moderno:
            filename += "_moderno"
        
        filename += f"_{timestamp}"
        
        # Renderizar en el formato especificado
        dot.render(filename, format=formato, cleanup=True)
        ruta_completa = f"{filename}.{formato}"
        print(f"Diagrama guardado: {ruta_completa}")
        
        # Devolver tanto el objeto dot como la ruta del archivo generado
        return dot, ruta_completa