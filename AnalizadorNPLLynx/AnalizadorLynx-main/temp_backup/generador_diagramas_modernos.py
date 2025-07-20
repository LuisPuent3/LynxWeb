# generador_diagramas_modernos.py
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
from datetime import datetime
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

class GeneradorDiagramasModernos:
    """
    Clase para generar diagramas modernos para AFDs utilizando NetworkX y Matplotlib
    """
    
    def __init__(self):
        # Colores para los nodos
        self.colores = {
            'inicial': '#90EE90',  # Verde claro
            'final': '#FFB6C1',    # Coral claro
            'normal': '#87CEEB',   # Azul cielo
            'borde_inicial': '#2E8B57',  # Verde mar
            'borde_final': '#CD5C5C',    # Rojo indio
            'borde_normal': '#4682B4',   # Azul acero
        }
        
        # Directorio para guardar los diagramas
        self.directorio_salida = "diagramas_modernos"
        self._crear_directorio()
        
        # Configuración de estilos de matplotlib
        plt.style.use('ggplot')
        
    def _crear_directorio(self):
        """Crea el directorio de salida si no existe"""
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
            
    def generar_diagrama(self, afd, layout='spring', mostrar_completo=True):
        """
        Genera un diagrama moderno para un AFD
        
        Args:
            afd: Instancia de AFDBase que contiene los estados y transiciones
            layout: Tipo de layout ('spring', 'hierarchical', 'radial', 'linear', 'layers')
            mostrar_completo: Si es True, muestra todas las transiciones individuales
        """
        # Crear grafo dirigido
        G = nx.DiGraph()
        
        # Agregar nodos para cada estado
        for estado in afd.estados:
            # Determinar si es estado inicial o final
            es_inicial = estado == afd.estado_inicial
            es_final = estado in afd.estados_finales
            
            # Agregar nodo con atributos
            G.add_node(estado, 
                       es_inicial=es_inicial,
                       es_final=es_final)
        
        # Agregar aristas para cada transición
        if mostrar_completo:
            # Versión detallada
            for origen, transiciones in afd.transiciones.items():
                for simbolo, destino in transiciones.items():
                    G.add_edge(origen, destino, simbolo=simbolo)
        else:
            # Versión simplificada agrupando transiciones
            for origen, transiciones in afd.transiciones.items():
                destinos = {}
                for simbolo, destino in transiciones.items():
                    if destino not in destinos:
                        destinos[destino] = []
                    destinos[destino].append(simbolo)
                
                for destino, simbolos in destinos.items():
                    if len(simbolos) > 3:
                        etiqueta = f"{simbolos[0]},{simbolos[1]},...,{simbolos[-1]}"
                    else:
                        etiqueta = ','.join(simbolos)
                    G.add_edge(origen, destino, simbolo=etiqueta)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
        
        # Configurar el layout según el tipo
        pos = self._configurar_layout(G, layout, afd.estado_inicial)
        
        # Dibujar nodos
        self._dibujar_nodos(G, pos, ax)
        
        # Dibujar aristas con etiquetas
        self._dibujar_aristas(G, pos, ax)
        
        # Configurar el título y la leyenda
        ax.set_title(f'Autómata Finito Determinista: {afd.nombre}', fontsize=16, pad=20)
        
        # Agregar leyenda
        self._agregar_leyenda(ax)
        
        # Configurar el aspecto general
        ax.axis('off')
        ax.set_aspect('equal')
        fig.tight_layout()
        
        # Agregar grid sutil
        ax.grid(True, linestyle='--', alpha=0.2)
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.directorio_salida}/afd_{afd.nombre}_{timestamp}"
        plt.savefig(f"{filename}.png", dpi=300, bbox_inches='tight')
        print(f"Diagrama moderno guardado: {filename}.png")
        
        plt.close(fig)
        return fig, ax
    
    def _configurar_layout(self, G, layout_type, estado_inicial):
        """Configura el layout del grafo según el tipo especificado"""
        if layout_type == 'hierarchical':
            # Layout jerárquico para estructuras de árbol
            pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
        elif layout_type == 'radial':
            # Layout radial desde el estado inicial
            pos = nx.spring_layout(G, seed=42)
            # Ajustar para que el estado inicial esté en el centro
            if estado_inicial in pos:
                pos[estado_inicial] = np.array([0, 0])
        elif layout_type == 'linear':
            # Layout lineal de izquierda a derecha
            pos = {}
            nodes = list(G.nodes())
            for i, node in enumerate(nodes):
                pos[node] = (i, 0)
        elif layout_type == 'layers':
            # Layout en capas (clusters)
            pos = nx.multipartite_layout(G, subset_key='layer')
        else:  # 'spring' por defecto
            # Layout de spring (resorte)
            pos = nx.spring_layout(G, k=0.5, iterations=100, seed=42)
        
        return pos
    
    def _dibujar_nodos(self, G, pos, ax):
        """Dibuja los nodos con estilos modernos"""
        for node in G.nodes():
            es_inicial = G.nodes[node].get('es_inicial', False)
            es_final = G.nodes[node].get('es_final', False)
            
            # Determinar color según tipo de nodo
            if es_inicial:
                color_fondo = self.colores['inicial']
                color_borde = self.colores['borde_inicial']
                linewidth = 3
            elif es_final:
                color_fondo = self.colores['final']
                color_borde = self.colores['borde_final']
                linewidth = 3
            else:
                color_fondo = self.colores['normal']
                color_borde = self.colores['borde_normal']
                linewidth = 2
            
            # Coordenadas del nodo
            x, y = pos[node]
            
            # Dibujar círculo principal
            circle = plt.Circle((x, y), 0.2, facecolor=color_fondo, 
                                edgecolor=color_borde, linewidth=linewidth,
                                alpha=0.9, zorder=2, 
                                path_effects=[self._shadow_effect()])
            ax.add_patch(circle)
            
            # Dibujar doble círculo para estados finales
            if es_final:
                outer_circle = plt.Circle((x, y), 0.25, facecolor='none',
                                         edgecolor=color_borde, linewidth=linewidth,
                                         alpha=0.9, zorder=1)
                ax.add_patch(outer_circle)
            
            # Agregar texto del nodo
            ax.text(x, y, node, fontsize=12, ha='center', va='center',
                    fontweight='bold', color='black', zorder=3)
            
            # Flecha hacia el estado inicial
            if es_inicial:
                dx, dy = -0.4, 0  # Dirección de la flecha
                arrow = plt.arrow(x + dx, y + dy, 0.2, 0, 
                                 head_width=0.1, head_length=0.1,
                                 fc=color_borde, ec=color_borde, 
                                 linewidth=linewidth, zorder=1)
                ax.add_patch(arrow)
    
    def _dibujar_aristas(self, G, pos, ax):
        """Dibuja las aristas con estilos modernos y etiquetas"""
        # Crear gradiente de color para las aristas
        cmap = LinearSegmentedColormap.from_list("edge_colors", ['#4682B4', '#2E8B57'])
        
        # Dibujar cada arista
        for u, v, data in G.edges(data=True):
            # Obtener coordenadas de origen y destino
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            
            # Si es un bucle (self-loop)
            if u == v:
                # Dibujar bucle
                loop = plt.Circle((x1, y1 + 0.3), 0.1, fill=False,
                                 edgecolor='gray', linewidth=1.5,
                                 alpha=0.7, zorder=1)
                ax.add_patch(loop)
                
                # Etiqueta para el bucle
                ax.text(x1, y1 + 0.45, data.get('simbolo', ''),
                        fontsize=10, ha='center', va='center',
                        bbox=dict(facecolor='white', alpha=0.7,
                                boxstyle='round,pad=0.2'))
            else:
                # Calcular puntos para curvar la flecha
                rad = 0.15  # Radio de curvatura
                
                # Verificar si ya existe una arista en sentido contrario
                if G.has_edge(v, u):
                    rad = 0.3  # Mayor curvatura para evitar superposición
                
                # Crear conexión curva
                connection = FancyArrowPatch(
                    posA=(x1, y1), 
                    posB=(x2, y2),
                    arrowstyle='-|>', 
                    connectionstyle=f'arc3,rad={rad}',
                    mutation_scale=15, 
                    linewidth=2,
                    alpha=0.8,
                    color='#4682B4',  # Color azul acero
                    zorder=1
                )
                ax.add_patch(connection)
                
                # Calcular posición para la etiqueta
                # Para flechas curvas, la etiqueta debe estar en un punto intermedio de la curva
                middle_x = (x1 + x2) / 2 + rad * (y2 - y1)
                middle_y = (y1 + y2) / 2 + rad * (x1 - x2)
                
                # Agregar etiqueta
                ax.text(middle_x, middle_y, data.get('simbolo', ''),
                        fontsize=10, ha='center', va='center',
                        bbox=dict(facecolor='white', alpha=0.8,
                                boxstyle='round,pad=0.2'))
    
    def _shadow_effect(self):
        """Crea un efecto de sombra para los nodos"""
        from matplotlib.patheffects import withStroke
        return withStroke(linewidth=4, foreground='black', alpha=0.2)
    
    def _agregar_leyenda(self, ax):
        """Agrega una leyenda al diagrama"""
        # Crear leyenda personalizada
        from matplotlib.lines import Line2D
        
        leyenda_elementos = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colores['inicial'],
                  markersize=15, label='Estado Inicial'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colores['final'],
                  markersize=15, label='Estado Final'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=self.colores['normal'],
                  markersize=15, label='Estado Normal')
        ]
        
        ax.legend(handles=leyenda_elementos, loc='upper right', frameon=True,
                 framealpha=0.9, facecolor='white', edgecolor='gray')
    
    def generar_diagrama_general(self, analizador):
        """
        Genera un diagrama general del sistema de análisis
        
        Args:
            analizador: Instancia de AnalizadorLexicoLYNX
        """
        # Crear grafo dirigido
        G = nx.DiGraph()
        
        # Nodos principales del sistema
        G.add_node('entrada', tipo='entrada', label='Texto de Entrada', layer=0)
        G.add_node('analizador', tipo='proceso', label='Analizador Principal', layer=1)
        
        # Nodos para cada AFD
        afds_info = [
            ('afd_multi', 'AFD\nMulti-palabra', 2),
            ('afd_op', 'AFD\nOperadores', 2),
            ('afd_num', 'AFD\nNúmeros', 2),
            ('afd_uni', 'AFD\nUnidades', 2),
            ('afd_pal', 'AFD\nPalabras', 2)
        ]
        
        for nodo, label, layer in afds_info:
            G.add_node(nodo, tipo='afd', label=label, layer=layer)
        
        # Nodos de salida
        G.add_node('tokens', tipo='salida', label='Tokens\nReconocidos', layer=3)
        G.add_node('contexto', tipo='proceso', label='Análisis\nContextual', layer=4)
        G.add_node('semantico', tipo='proceso', label='Análisis\nSemántico', layer=5)
        G.add_node('json', tipo='salida', label='Salida JSON', layer=6)
        
        # Conexiones
        G.add_edge('entrada', 'analizador')
        
        for nodo, _, _ in afds_info:
            G.add_edge('analizador', nodo)
            G.add_edge(nodo, 'tokens')
        
        G.add_edge('tokens', 'contexto')
        G.add_edge('contexto', 'semantico')
        G.add_edge('semantico', 'json')
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
        
        # Configurar el layout en capas
        pos = nx.multipartite_layout(G, subset_key='layer', scale=1.5)
        
        # Diccionario de colores por tipo
        colores_tipo = {
            'entrada': '#AADDFF',  # Azul claro
            'proceso': '#FFCC88',  # Naranja claro
            'afd': '#CCFFCC',      # Verde claro
            'salida': '#FFDDDD',   # Rojo claro
        }
        
        # Diccionario de formas por tipo
        formas = {
            'entrada': 'rectangle',
            'proceso': 'ellipse',
            'afd': 'ellipse',
            'salida': 'rectangle'
        }
        
        # Dibujar nodos con estilos según tipo
        for node, attrs in G.nodes(data=True):
            x, y = pos[node]
            tipo = attrs.get('tipo', 'proceso')
            label = attrs.get('label', node)
            
            # Color según tipo
            color = colores_tipo.get(tipo, '#DDDDDD')
            
            # Forma según tipo
            forma = formas.get(tipo, 'ellipse')
            
            if forma == 'rectangle':
                rect = plt.Rectangle((x-0.25, y-0.15), 0.5, 0.3, 
                                    facecolor=color, edgecolor='black',
                                    linewidth=2, alpha=0.9, zorder=2,
                                    boxstyle='round,pad=0.3')
                ax.add_patch(rect)
            else:
                circle = plt.Circle((x, y), 0.25, 
                                   facecolor=color, edgecolor='black',
                                   linewidth=2, alpha=0.9, zorder=2)
                ax.add_patch(circle)
            
            # Agregar texto del nodo
            ax.text(x, y, label, fontsize=12, ha='center', va='center',
                    fontweight='bold', color='black', zorder=3,
                    wrap=True)
        
        # Dibujar aristas
        for u, v in G.edges():
            # Obtener coordenadas
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            
            # Crear flecha
            arrow = FancyArrowPatch(
                (x1, y1), (x2, y2),
                arrowstyle='-|>', 
                connectionstyle='arc3,rad=0.1',
                mutation_scale=15,
                linewidth=2,
                color='#555555',
                alpha=0.8,
                zorder=1
            )
            ax.add_patch(arrow)
        
        # Configurar título y aspecto general
        ax.set_title('Sistema de Análisis Léxico LYNX', fontsize=18, pad=20)
        ax.axis('off')
        fig.tight_layout()
        
        # Guardar diagrama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.directorio_salida}/sistema_general_{timestamp}"
        plt.savefig(f"{filename}.png", dpi=300, bbox_inches='tight')
        print(f"Diagrama general moderno guardado: {filename}.png")
        
        plt.close(fig)
        return fig, ax
