# ut# Importar adaptador escalable para ConfiguracionLYNX mejorada
from adaptador_escalable import ConfiguracionLYNXEscalable
from adaptador_bd import AdaptadorBaseDatos

class ConfiguracionLYNX:
    """Configuración LYNX con arquitectura escalable"""
    
    def __init__(self):
        # Usar configuración escalable en lugar de la original
        self._config_escalable = ConfiguracionLYNXEscalable()
        
        # Mantener compatibilidad con propiedades existentes
        self.simulador = self._config_escalable.simulador
        self.bd_escalable = self._config_escalable.bd_escalable  # Exponer bd_escalable
        self.base_datos = self._config_escalable.base_datos
        
        # Crear adaptador para motor de recomendaciones
        self.adaptador_bd = AdaptadorBaseDatos(self.bd_escalable)
        
        print(f"🚀 ConfiguracionLYNX escalable cargada:")
        stats = self.simulador.obtener_estadisticas()
        print(f"   • Productos: {stats['productos']['total']}")
        print(f"   • Sinónimos: {stats.get('sinonimos', {}).get('total', 0)}")
        print(f"   • Categorías: {len(self.base_datos.get('categorias', []))}")
import os

# Importar adaptador escalable para ConfiguracionLYNX mejorada
from adaptador_escalable import ConfiguracionLYNXEscalable

class ConfiguracionLYNX:
    """Configuración LYNX con arquitectura escalable"""
    
    def __init__(self):
        # Usar configuración escalable en lugar de la original
        self._config_escalable = ConfiguracionLYNXEscalable()
        
        # Mantener compatibilidad con propiedades existentes
        self.simulador = self._config_escalable.simulador
        self.base_datos = self._config_escalable.base_datos
        
        # Exponer bd_escalable para el motor de recomendaciones
        self.bd_escalable = self._config_escalable.bd_escalable
        
        # Crear adaptador para compatibilidad con motor de recomendaciones
        from adaptador_bd import AdaptadorBaseDatos
        self.adaptador_bd = AdaptadorBaseDatos(self.bd_escalable)
        
        print(f"🚀 ConfiguracionLYNX escalable cargada:")
        stats = self.simulador.obtener_estadisticas()
        print(f"   • Productos: {stats['productos']['total']}")
        print(f"   • Sinónimos: {stats.get('sinonimos', {}).get('total', 0)}")
        print(f"   • Categorías: {len(self.base_datos.get('categorias', []))}")
    
    def obtener_estadisticas(self):
        """Obtener estadísticas del sistema"""
        return self.simulador.obtener_estadisticas()


def verificar_graphviz():
    """
    Verifica si Graphviz está correctamente instalado y disponible.
    
    Returns:
        tuple: (bool, str) - (instalado correctamente, mensaje)
    """
    try:
        # Intentar importar graphviz
        import graphviz
        
        # Verificar si dot está disponible en el sistema
        try:
            version = graphviz.version()
            return True, f"Graphviz instalado correctamente. Versión: {version}"
        except graphviz.ExecutableNotFound:
            return False, ("Graphviz Python está instalado pero el ejecutable 'dot' no se encuentra. "
                         "Asegúrese de que Graphviz esté instalado y en el PATH del sistema. "
                         "Descargue en: https://graphviz.org/download/")
    except ImportError:
        return False, ("El paquete graphviz para Python no está instalado. "
                     "Instale con: pip install graphviz")

def abrir_archivo(ruta):
    """
    Abre un archivo con la aplicación predeterminada del sistema.
    
    Args:
        ruta: Ruta al archivo que se desea abrir
    """
    import os
    import platform
    import subprocess
    sistema = platform.system()
    try:
        if sistema == 'Windows':
            os.startfile(ruta)
        elif sistema == 'Darwin':
            subprocess.call(['open', ruta])
        else:
            subprocess.call(['xdg-open', ruta])
        return True
    except Exception as e:
        print(f"Error al abrir el archivo {ruta}: {e}")
        return False

