# afd_moderno.py
from afd_base import AFDBase
from generador_diagramas_modernos import GeneradorDiagramasModernos

class AFDModerno(AFDBase):
    """
    Extensión de AFDBase que utiliza GeneradorDiagramasModernos para
    generar visualizaciones mejoradas de los autómatas finitos deterministas
    """
    
    def __init__(self, nombre):
        super().__init__(nombre)
        self.generador_diagramas = GeneradorDiagramasModernos()
        
    def generar_diagrama_moderno(self, layout='spring', mostrar_completo=True):
        """
        Genera un diagrama moderno del autómata utilizando NetworkX y Matplotlib
        
        Args:
            layout: Tipo de layout ('spring', 'hierarchical', 'radial', 'linear', 'layers')
            mostrar_completo: Si es True, muestra todas las transiciones individuales
        """
        return self.generador_diagramas.generar_diagrama(self, layout, mostrar_completo)
