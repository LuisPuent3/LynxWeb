# afd_multipalabra.py
from afd_base import AFDBase

class AFDMultipalabra(AFDBase):
    """AFD para reconocer productos de múltiples palabras"""
    
    def __init__(self, base_datos):
        super().__init__("Multipalabra")
        self.base_datos = base_datos
        # Ordenar productos por longitud (primero los más largos, para dar prioridad a productos completos)
        self.productos_completos = sorted(base_datos['productos_completos'], key=len, reverse=True)
        self.productos_multi = sorted(base_datos['productos_multi'], key=len, reverse=True)
        # Combinar productos completos primero para darles prioridad
        self.productos_multi_all = self.productos_completos + self.productos_multi
        self.construir_automata()
    
    def construir_automata(self):
        """Construye el autómata tipo Trie para productos multi-palabra"""
        self.establecer_estado_inicial('q0')
        estado_contador = 1
        
        # Construir un Trie para cada producto multi-palabra
        # Ya están ordenados para dar prioridad a productos completos y luego a los más largos
        for producto in self.productos_multi_all:
            estado_actual = 'q0'
            palabras = producto.split()
            
            for i, palabra in enumerate(palabras):
                # Para cada carácter de la palabra
                for j, char in enumerate(palabra):
                    estado_siguiente = f'q{estado_contador}'
                    
                    # Verificar si ya existe la transición
                    if (estado_actual in self.transiciones and 
                        char in self.transiciones[estado_actual]):
                        estado_siguiente = self.transiciones[estado_actual][char]
                    else:
                        self.agregar_estado(estado_siguiente)
                        self.agregar_transicion(estado_actual, char, estado_siguiente)
                        estado_contador += 1
                    
                    estado_actual = estado_siguiente
                
                # Agregar espacio entre palabras (excepto la última)
                if i < len(palabras) - 1:
                    estado_espacio = f'q{estado_contador}'
                    self.agregar_estado(estado_espacio)
                    self.agregar_transicion(estado_actual, ' ', estado_espacio)
                    estado_actual = estado_espacio
                    estado_contador += 1
            
            # Marcar el último estado como final
            self.agregar_estado(estado_actual, es_final=True)
            
            # Guardar qué producto corresponde a este estado final
            if not hasattr(self, 'productos_por_estado'):
                self.productos_por_estado = {}
            self.productos_por_estado[estado_actual] = producto
    
    def get_tipo_token(self, lexema):
        """Retorna el tipo de token para productos multi-palabra"""
        lexema_lower = lexema.lower()
        
        # Debug - verificar el tipo de token
        print(f"DEBUG - get_tipo_token: verificando '{lexema_lower}'")
        
        # Primero verificar si es un producto completo
        if lexema_lower in [p.lower() for p in self.base_datos['productos_completos']]:
            print(f"DEBUG - Es PRODUCTO_COMPLETO")
            return 'PRODUCTO_COMPLETO'
        # Luego verificar si es un producto multi
        elif lexema_lower in [p.lower() for p in self.base_datos['productos_multi']]:
            print(f"DEBUG - Es PRODUCTO_MULTI")
            return 'PRODUCTO_MULTI'
        else:
            # Verificación adicional por si hay problemas de formato/espacios
            for producto in self.base_datos['productos_completos']:
                if producto.lower() == lexema_lower:
                    print(f"DEBUG - Es PRODUCTO_COMPLETO (verificación adicional)")
                    return 'PRODUCTO_COMPLETO'
            
            print(f"DEBUG - No encontrado en listas, asignando PRODUCTO_MULTI")
            return 'PRODUCTO_MULTI'
    
    def procesar_cadena(self, cadena, posicion_inicial=0):
        """
        Procesa una cadena y retorna el token reconocido si existe
        Esta versión mejorada prioriza las coincidencias más largas y productos completos
        """
        # Debug - revisar qué estamos procesando
        print(f"\nDEBUG AFD Multipalabra - Procesando desde pos {posicion_inicial}: '{cadena[posicion_inicial:]}'")
        print(f"Productos completos disponibles: {self.productos_completos}")
        
        # Construir un diccionario para guardar todas las posibles coincidencias
        coincidencias = []
        
        # Iterar por cada producto completo primero y luego por productos multi
        for producto in self.productos_multi_all:
            # Verificar si el producto está presente en la posición actual
            # Corregido para que compare en minúsculas
            cadena_lower = cadena.lower()
            producto_lower = producto.lower()
            if (cadena_lower[posicion_inicial:].startswith(producto_lower + ' ') or 
                cadena_lower[posicion_inicial:].startswith(producto_lower) and 
                (posicion_inicial + len(producto_lower) == len(cadena_lower))):
                
                tipo_token = 'PRODUCTO_COMPLETO' if producto in self.base_datos['productos_completos'] else 'PRODUCTO_MULTI'
                
                coincidencias.append({
                    'tipo': tipo_token,
                    'valor': producto,
                    'posicion_inicial': posicion_inicial,
                    'posicion_final': posicion_inicial + len(producto),
                    'longitud': len(producto)
                })
        
        # Si encontramos alguna coincidencia, retornar la más larga
        if coincidencias:
            # Debug - mostrar todas las coincidencias encontradas
            print(f"DEBUG - Coincidencias encontradas: {len(coincidencias)}")
            for c in coincidencias:
                print(f"  - {c['tipo']}: '{c['valor']}' (longitud: {c['longitud']})")
            
            # Ordenar primero por tipo (PRODUCTO_COMPLETO tiene prioridad) y luego por longitud (descendente)
            coincidencias.sort(key=lambda x: (x['tipo'] == 'PRODUCTO_MULTI', -x['longitud']), reverse=False)
            
            # Debug - mostrar coincidencia seleccionada
            print(f"DEBUG - Seleccionada: {coincidencias[0]['tipo']} - '{coincidencias[0]['valor']}'")
            
            return coincidencias[0]
        
        # Si no hay coincidencias con este enfoque, intentar con el método estándar
        return super().procesar_cadena(cadena, posicion_inicial)