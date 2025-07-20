# configuracion_bd.py - VERSIÓN ESCALABLE COMPATIBLE
"""
Configuración de BD escalable que mantiene compatibilidad
con el sistema original mientras usa 1000+ productos y sinónimos
"""

# Importar adaptador escalable
from adaptador_escalable import simulador_bd

# Mantener compatibilidad exportando la instancia global
# Este es el mismo nombre que usa el código original
simulador_bd = simulador_bd

# Clase para compatibilidad total
class SimuladorBDLynxShop:
    """Wrapper de compatibilidad para el simulador escalable"""
    
    def __init__(self):
        global simulador_bd
        self.simulador = simulador_bd
        
        # Propiedades compatibles
        self.productos = simulador_bd.productos
        self.categorias = simulador_bd.categorias
    
    def buscar_productos(self, consulta_sql=None, filtros=None):
        return self.simulador.buscar_productos(consulta_sql, filtros)
    
    def buscar_por_similitud(self, termino, categoria=None):
        return self.simulador.buscar_por_similitud(termino, categoria)
    
    def obtener_productos_populares(self, limit=10):
        return self.simulador.obtener_productos_populares(limit)
    
    def obtener_ofertas(self, limit=5):
        return self.simulador.obtener_ofertas(limit)
    
    def obtener_estadisticas(self):
        return self.simulador.obtener_estadisticas()

# Instancia global para compatibilidad
simulador_bd = simulador_bd  # Usa el adaptador escalable
