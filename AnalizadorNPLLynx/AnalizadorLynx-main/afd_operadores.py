# afd_operadores.py
from afd_base import AFDBase

class AFDOperadores(AFDBase):
    """AFD para reconocer operadores de comparación"""
    
    def __init__(self, base_datos):
        super().__init__("Operadores")
        self.operadores = base_datos['operadores']
        self.construir_automata()
    
    def construir_automata(self):
        """Construye el autómata para operadores"""
        self.establecer_estado_inicial('q0')
        
        # Construcción específica para cada operador
        # "menor a"
        self.agregar_transicion('q0', 'm', 'q_m')
        self.agregar_transicion('q_m', 'e', 'q_me')
        self.agregar_transicion('q_me', 'n', 'q_men')
        self.agregar_transicion('q_men', 'o', 'q_meno')
        self.agregar_transicion('q_meno', 'r', 'q_menor')
        self.agregar_transicion('q_menor', ' ', 'q_menor_')
        self.agregar_transicion('q_menor_', 'a', 'q_menor_a')
        self.agregar_estado('q_menor_a', es_final=True)
        
        # "mayor a"
        self.agregar_transicion('q_m', 'a', 'q_ma')
        self.agregar_transicion('q_ma', 'y', 'q_may')
        self.agregar_transicion('q_may', 'o', 'q_mayo')
        self.agregar_transicion('q_mayo', 'r', 'q_mayor')
        self.agregar_transicion('q_mayor', ' ', 'q_mayor_')
        self.agregar_transicion('q_mayor_', 'a', 'q_mayor_a')
        self.agregar_estado('q_mayor_a', es_final=True)
        
        # "entre"
        self.agregar_transicion('q0', 'e', 'q_e')
        self.agregar_transicion('q_e', 'n', 'q_en')
        self.agregar_transicion('q_en', 't', 'q_ent')
        self.agregar_transicion('q_ent', 'r', 'q_entr')
        self.agregar_transicion('q_entr', 'e', 'q_entre')
        self.agregar_estado('q_entre', es_final=True)
        
        # "igual a"
        self.agregar_transicion('q0', 'i', 'q_i')
        self.agregar_transicion('q_i', 'g', 'q_ig')
        self.agregar_transicion('q_ig', 'u', 'q_igu')
        self.agregar_transicion('q_igu', 'a', 'q_igua')
        self.agregar_transicion('q_igua', 'l', 'q_igual')
        self.agregar_transicion('q_igual', ' ', 'q_igual_')
        self.agregar_transicion('q_igual_', 'a', 'q_igual_a')
        self.agregar_estado('q_igual_a', es_final=True)
        
        # Agregar todos los estados intermedios
                # Continuar agregando estados intermedios
        estados_intermedios = ['q_m', 'q_me', 'q_men', 'q_meno', 'q_menor', 'q_menor_',
                              'q_ma', 'q_may', 'q_mayo', 'q_mayor', 'q_mayor_',
                              'q_e', 'q_en', 'q_ent', 'q_entr',
                              'q_i', 'q_ig', 'q_igu', 'q_igua', 'q_igual', 'q_igual_']
        
        for estado in estados_intermedios:
            self.agregar_estado(estado)
    
    def get_tipo_token(self, lexema):
        """Retorna el tipo de operador"""
        operador_map = {
            'menor a': 'OP_MENOR',
            'mayor a': 'OP_MAYOR',
            'entre': 'OP_ENTRE',
            'igual a': 'OP_IGUAL'
        }
        return operador_map.get(lexema.lower(), 'OPERADOR')