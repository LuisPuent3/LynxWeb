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
        
        # CONSTRUCCIÓN ESPECÍFICA PARA CADA OPERADOR
        
        # "menor a" y "menor que"
        self.agregar_transicion('q0', 'm', 'q_m')
        self.agregar_transicion('q_m', 'e', 'q_me')
        self.agregar_transicion('q_me', 'n', 'q_men')
        self.agregar_transicion('q_men', 'o', 'q_meno')
        self.agregar_transicion('q_meno', 'r', 'q_menor')
        self.agregar_transicion('q_menor', ' ', 'q_menor_')
        self.agregar_transicion('q_menor_', 'a', 'q_menor_a')
        self.agregar_transicion('q_menor_', 'q', 'q_menor_q')
        self.agregar_transicion('q_menor_q', 'u', 'q_menor_qu')
        self.agregar_transicion('q_menor_qu', 'e', 'q_menor_que')
        self.agregar_estado('q_menor_a', es_final=True)
        self.agregar_estado('q_menor_que', es_final=True)
        
        # "menores a" (plural)
        self.agregar_transicion('q_meno', 'r', 'q_menor')
        self.agregar_transicion('q_menor', 'e', 'q_menore')
        self.agregar_transicion('q_menore', 's', 'q_menores')
        self.agregar_transicion('q_menores', ' ', 'q_menores_')
        self.agregar_transicion('q_menores_', 'a', 'q_menores_a')
        self.agregar_estado('q_menores_a', es_final=True)
        
        # "mayor a" y "mayor que"  
        self.agregar_transicion('q_m', 'a', 'q_ma')
        self.agregar_transicion('q_ma', 'y', 'q_may')
        self.agregar_transicion('q_may', 'o', 'q_mayo')
        self.agregar_transicion('q_mayo', 'r', 'q_mayor')
        self.agregar_transicion('q_mayor', ' ', 'q_mayor_')
        self.agregar_transicion('q_mayor_', 'a', 'q_mayor_a')
        self.agregar_transicion('q_mayor_', 'q', 'q_mayor_q')
        self.agregar_transicion('q_mayor_q', 'u', 'q_mayor_qu')
        self.agregar_transicion('q_mayor_qu', 'e', 'q_mayor_que')
        self.agregar_estado('q_mayor_a', es_final=True)
        self.agregar_estado('q_mayor_que', es_final=True)
        
        # "mayores a" (plural)
        self.agregar_transicion('q_mayo', 'r', 'q_mayor')
        self.agregar_transicion('q_mayor', 'e', 'q_mayore')
        self.agregar_transicion('q_mayore', 's', 'q_mayores')
        self.agregar_transicion('q_mayores', ' ', 'q_mayores_')
        self.agregar_transicion('q_mayores_', 'a', 'q_mayores_a')
        self.agregar_estado('q_mayores_a', es_final=True)
        
        # "más de" y "mas de"
        self.agregar_transicion('q_m', 'á', 'q_má')
        self.agregar_transicion('q_m', 'a', 'q_ma_mas')  # sin acento
        self.agregar_transicion('q_má', 's', 'q_más')
        self.agregar_transicion('q_ma_mas', 's', 'q_mas')
        self.agregar_transicion('q_más', ' ', 'q_más_')
        self.agregar_transicion('q_mas', ' ', 'q_mas_')
        self.agregar_transicion('q_más_', 'd', 'q_más_d')
        self.agregar_transicion('q_mas_', 'd', 'q_mas_d')
        self.agregar_transicion('q_más_d', 'e', 'q_más_de')
        self.agregar_transicion('q_mas_d', 'e', 'q_mas_de')
        self.agregar_estado('q_más_de', es_final=True)
        self.agregar_estado('q_mas_de', es_final=True)
        
        # "menos de"
        self.agregar_transicion('q_men', 'o', 'q_meno_menos')
        self.agregar_transicion('q_meno_menos', 's', 'q_menos')
        self.agregar_transicion('q_menos', ' ', 'q_menos_')
        self.agregar_transicion('q_menos_', 'd', 'q_menos_d')
        self.agregar_transicion('q_menos_d', 'e', 'q_menos_de')
        self.agregar_estado('q_menos_de', es_final=True)
        
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
        estados_intermedios = [
            # Estados básicos existentes
            'q_m', 'q_me', 'q_men', 'q_meno', 'q_menor', 'q_menor_', 'q_menor_q', 'q_menor_qu',
            'q_ma', 'q_may', 'q_mayo', 'q_mayor', 'q_mayor_', 'q_mayor_q', 'q_mayor_qu',
            'q_e', 'q_en', 'q_ent', 'q_entr',
            'q_i', 'q_ig', 'q_igu', 'q_igua', 'q_igual', 'q_igual_',
            # Estados nuevos
            'q_menore', 'q_menores', 'q_menores_',
            'q_mayore', 'q_mayores', 'q_mayores_',
            'q_má', 'q_más', 'q_más_', 'q_más_d',
            'q_ma_mas', 'q_mas', 'q_mas_', 'q_mas_d',
            'q_meno_menos', 'q_menos', 'q_menos_', 'q_menos_d'
        ]
        
        for estado in estados_intermedios:
            self.agregar_estado(estado)
    
    def get_tipo_token(self, lexema):
        """Retorna el tipo de operador"""
        lexema_lower = lexema.lower().strip()
        operador_map = {
            'menor a': 'OP_MENOR',
            'menor que': 'OP_MENOR', 
            'menores a': 'OP_MENOR',
            'mayor a': 'OP_MAYOR',
            'mayor que': 'OP_MAYOR',
            'mayores a': 'OP_MAYOR',
            'más de': 'OP_MAYOR',
            'mas de': 'OP_MAYOR',
            'menos de': 'OP_MENOR',
            'entre': 'OP_ENTRE',
            'igual a': 'OP_IGUAL'
        }
        return operador_map.get(lexema_lower, 'OPERADOR')