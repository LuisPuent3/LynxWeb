# afd_visualizador_moderno.py
from afd_moderno import AFDModerno
from generador_diagramas_modernos import GeneradorDiagramasModernos
import os

class AFDVisualizadorModerno:
    """
    Clase auxiliar para generar visualizaciones modernas de AFDs
    sin modificar las clases originales
    """
    
    def __init__(self):
        self.generador_diagramas = GeneradorDiagramasModernos()
    
    def visualizar(self, afd, layout='spring', mostrar_completo=True):
        """
        Genera una visualización moderna de un AFD existente
        
        Args:
            afd: Instancia de AFDBase a visualizar
            layout: Tipo de layout ('spring', 'hierarchical', 'radial', 'linear', 'layers')
            mostrar_completo: Si es True, muestra todas las transiciones individuales
        """
        return self.generador_diagramas.generar_diagrama(afd, layout, mostrar_completo)
    
    def visualizar_sistema(self, analizador):
        """
        Genera una visualización moderna del sistema completo
        
        Args:
            analizador: Instancia de AnalizadorLexicoLYNX
        """
        return self.generador_diagramas.generar_diagrama_general(analizador)
