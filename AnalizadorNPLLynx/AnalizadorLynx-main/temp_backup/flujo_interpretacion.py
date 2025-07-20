import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

def crear_diagrama_interpretacion():
    """
    Crea un diagrama visual que muestra el flujo de procesamiento para la interpretación
    de términos sinónimos y con errores ortográficos.
    """
    plt.figure(figsize=(14, 10))
    
    # Crear el grafo dirigido
    G = nx.DiGraph()
    
    # Nodos
    nodos = {
        "entrada": "Consulta de Usuario\n'botana barata menor a 10'",
        "tokenizacion": "Tokenización",
        "tokens": "Tokens Iniciales\n'botana', 'barata', 'menor a', '10'",
        "interpretador": "Interpretador Semántico",
        "sinonimos": "Búsqueda de Sinónimos\nbotana → snacks",
        "fuzzy": "Búsqueda Aproximada\n(Levenshtein)",
        "precios": "Mapeo de Adjetivos\nbarata → < 50",
        "sql": "Generación SQL\nSELECT * FROM productos WHERE\ncategoria = 'snacks' AND precio < 10",
        "resultado": "Resultados"
    }
    
    # Añadir nodos
    posiciones = {
        "entrada": (0, 6),
        "tokenizacion": (0, 4),
        "tokens": (0, 2),
        "interpretador": (0, 0),
        "sinonimos": (-3, -2),
        "fuzzy": (-3, -4),
        "precios": (3, -2),
        "sql": (0, -6),
        "resultado": (0, -8)
    }
    
    # Añadir nodos con posiciones
    for node, label in nodos.items():
        G.add_node(node, label=label)
    
    # Añadir aristas
    edges = [
        ("entrada", "tokenizacion"),
        ("tokenizacion", "tokens"),
        ("tokens", "interpretador"),
        ("interpretador", "sinonimos"),
        ("interpretador", "precios"),
        ("sinonimos", "fuzzy"),
        ("sinonimos", "sql"),
        ("fuzzy", "sql"),
        ("precios", "sql"),
        ("sql", "resultado")
    ]
    G.add_edges_from(edges)
    
    # Dibujar el grafo
    plt.axis('off')
    plt.title("Flujo de procesamiento para 'botana barata menor a 10'", fontsize=16)
    
    # Dibujar nodos
    for node, pos in posiciones.items():
        draw_node_with_text(plt.gca(), pos[0], pos[1], nodos[node], node)
    
    # Dibujar aristas
    for edge in edges:
        start_pos = posiciones[edge[0]]
        end_pos = posiciones[edge[1]]
        plt.annotate("", xy=end_pos, xytext=start_pos,
                    arrowprops=dict(facecolor='black', shrink=0.05,
                                   width=1.5, headwidth=8))
    
    # Guardar imagen
    plt.tight_layout()
    plt.savefig("flujo_interpretacion.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    print("Diagrama creado correctamente: flujo_interpretacion.png")

def draw_node_with_text(ax, x, y, text, node_type):
    """Dibuja un nodo con texto en el interior"""
    colors = {
        "entrada": "#AADDFF",
        "tokenizacion": "#FFD700",
        "tokens": "#90EE90",
        "interpretador": "#FFB6C1",
        "sinonimos": "#D8BFD8",
        "fuzzy": "#FFD580",
        "precios": "#ADD8E6",
        "sql": "#98FB98",
        "resultado": "#E6E6E6"
    }
    
    # Crear el rectángulo redondeado
    rect = patches.FancyBboxPatch((x-2, y-0.7), 4, 1.4, 
                                 boxstyle=patches.BoxStyle("Round", pad=0.6),
                                 facecolor=colors.get(node_type, "white"),
                                 edgecolor='black', linewidth=1.5)
    ax.add_patch(rect)
    
    # Añadir el texto
    ax.text(x, y, text, ha='center', va='center', 
           fontsize=10, fontweight='bold')

if __name__ == "__main__":
    crear_diagrama_interpretacion()
