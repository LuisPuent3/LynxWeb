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
