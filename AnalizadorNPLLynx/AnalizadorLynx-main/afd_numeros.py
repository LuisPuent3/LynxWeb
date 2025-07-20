# afd_numeros.py
from afd_base import AFDBase

class AFDNumeros(AFDBase):
    """AFD para reconocer números enteros y decimales"""
    
    def __init__(self):
        super().__init__("Numeros")
        self.construir_automata()
    
    def construir_automata(self):
        """Construye el autómata para números"""
        self.establecer_estado_inicial('q0')
        
        # Estados
        self.agregar_estado('q_entero', es_final=True)
        self.agregar_estado('q_punto')
        self.agregar_estado('q_decimal', es_final=True)
        
        # Transiciones para dígitos
        digitos = '0123456789'
        
        # Desde q0 a entero
        for d in digitos:
            self.agregar_transicion('q0', d, 'q_entero')
        
        # Mantener en entero
        for d in digitos:
            self.agregar_transicion('q_entero', d, 'q_entero')
        
        # Punto decimal
        self.agregar_transicion('q_entero', '.', 'q_punto')
        
        # Después del punto
        for d in digitos:
            self.agregar_transicion('q_punto', d, 'q_decimal')
            self.agregar_transicion('q_decimal', d, 'q_decimal')
    
    def get_tipo_token(self, lexema):
        """Retorna el tipo de número"""
        if '.' in lexema:
            return 'NUMERO_DECIMAL'
        else:
            return 'NUMERO_ENTERO'