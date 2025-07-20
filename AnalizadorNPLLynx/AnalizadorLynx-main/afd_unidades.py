# afd_unidades.py
from afd_base import AFDBase

class AFDUnidades(AFDBase):
    """AFD para reconocer unidades de medida y moneda"""
    
    def __init__(self, base_datos):
        super().__init__("Unidades")
        self.unidades = base_datos['unidades']
        self.construir_automata()
    
    def construir_automata(self):
        """Construye el autómata para unidades"""
        self.establecer_estado_inicial('q0')
        
        # Pesos
        self.agregar_transicion('q0', 'p', 'q_p')
        self.agregar_transicion('q_p', 'e', 'q_pe')
        self.agregar_transicion('q_pe', 's', 'q_pes')
        self.agregar_transicion('q_pes', 'o', 'q_peso')
        self.agregar_estado('q_peso', es_final=True)
        self.agregar_transicion('q_peso', 's', 'q_pesos')
        self.agregar_estado('q_pesos', es_final=True)
        
        # Litros
        self.agregar_transicion('q0', 'l', 'q_l')
        self.agregar_transicion('q_l', 'i', 'q_li')
        self.agregar_transicion('q_li', 't', 'q_lit')
        self.agregar_transicion('q_lit', 'r', 'q_litr')
        self.agregar_transicion('q_litr', 'o', 'q_litro')
        self.agregar_estado('q_litro', es_final=True)
        self.agregar_transicion('q_litro', 's', 'q_litros')
        self.agregar_estado('q_litros', es_final=True)
        
        # Gramos
        self.agregar_transicion('q0', 'g', 'q_g')
        self.agregar_transicion('q_g', 'r', 'q_gr')
        self.agregar_estado('q_gr', es_final=True)  # "gr"
        self.agregar_transicion('q_gr', 'a', 'q_gra')
        self.agregar_transicion('q_gra', 'm', 'q_gram')
        self.agregar_transicion('q_gram', 'o', 'q_gramo')
        self.agregar_estado('q_gramo', es_final=True)
        self.agregar_transicion('q_gramo', 's', 'q_gramos')
        self.agregar_estado('q_gramos', es_final=True)
        
        # Kilogramos
        self.agregar_transicion('q0', 'k', 'q_k')
        self.agregar_transicion('q_k', 'g', 'q_kg')
        self.agregar_estado('q_kg', es_final=True)
        
        # Mililitros
        self.agregar_transicion('q0', 'm', 'q_m')
        self.agregar_transicion('q_m', 'l', 'q_ml')
        self.agregar_estado('q_ml', es_final=True)
        
        # Agregar estados intermedios
        estados = ['q_p', 'q_pe', 'q_pes', 'q_l', 'q_li', 'q_lit', 'q_litr',
                  'q_g', 'q_gra', 'q_gram', 'q_k', 'q_m']
        for estado in estados:
            self.agregar_estado(estado)
    
    def get_tipo_token(self, lexema):
        """Retorna el tipo de unidad"""
        if lexema.lower() in ['pesos', 'peso']:
            return 'UNIDAD_MONEDA'
        else:
            return 'UNIDAD_MEDIDA'