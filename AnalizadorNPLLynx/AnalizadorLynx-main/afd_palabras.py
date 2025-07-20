# afd_palabras.py
from afd_base import AFDBase

class AFDPalabras(AFDBase):
    """AFD para reconocer palabras genéricas y productos"""
    
    def __init__(self, base_datos):
        super().__init__("Palabras")
        self.base_datos = base_datos
        self.construir_automata()
    
    def construir_automata(self):
        """Construye el autómata para palabras"""
        # Estado inicial
        self.establecer_estado_inicial('q0')
        
        # Estados para palabras simples
        self.agregar_estado('q_letra')
        self.agregar_estado('q_palabra', es_final=True)
        
        # Alfabeto de letras
        letras = 'abcdefghijklmnopqrstuvwxyzáéíóúñ'
        
        # Transiciones desde q0
        for letra in letras:
            self.agregar_transicion('q0', letra, 'q_letra')
        
        # Transiciones para formar palabras
        for letra in letras:
            self.agregar_transicion('q_letra', letra, 'q_palabra')
            self.agregar_transicion('q_palabra', letra, 'q_palabra')
        
        # Transición para espacios (para detectar fin de palabra)
        self.agregar_transicion('q_palabra', ' ', 'q_fin')
        self.agregar_estado('q_fin', es_final=True)
    
    def get_tipo_token(self, lexema):
        """Clasifica el tipo de palabra"""
        lexema_lower = lexema.lower().strip()
        
        if lexema_lower in self.base_datos['productos_simples']:
            return 'PRODUCTO_SIMPLE'
        elif lexema_lower in self.base_datos['categorias']:
            return 'CATEGORIA'
        elif lexema_lower in self.base_datos['modificadores']:
            return 'MODIFICADOR'
        elif lexema_lower in self.base_datos['atributos']:
            return 'ATRIBUTO'
        elif lexema_lower == 'categoria' or lexema_lower == 'categoría':
            return 'CATEGORIA_KEYWORD'
        else:
            return 'PALABRA_GENERICA'