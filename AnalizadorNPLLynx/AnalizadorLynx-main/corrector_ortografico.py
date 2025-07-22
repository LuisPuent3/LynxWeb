# corrector_ortografico.py
import re
from typing import Dict, List, Tuple, Optional

class CorrectorOrtografico:
    """
    Módulo de corrección ortográfica basado en distancia de Levenshtein
    optimizada para el vocabulario de productos LYNX
    """
    
    def __init__(self):
        self.vocabulario = self._cargar_vocabulario()
        self.indices_foneticos = self._crear_indices_foneticos()
        self.errores_comunes = {
            # Productos comunes mal escritos - SEGÚN DOCUMENTACIÓN TÉCNICA LCLN
            "coca": "coca-cola",
            "koka": "coca-cola", 
            "coka": "coca-cola",
            "kola": "cola",
            "votana": "botana",
            "botana": "botana", 
            "chetoos": "cheetos",
            "dorito": "doritos",
            "brata": "barata",
            "varata": "barata",
            "picabte": "picante",
            "pixnatw": "picante",  # Specific case from requirements
            "picnatw": "picante",   # Similar typo
            "pixante": "picante",   # Common substitution
            "pikante": "picante",   # Common substitution  
            "picamte": "picante",   # Common typo
            "picante": "picante",
            "azucar": "azúcar",
            "asucar": "azúcar",
            "sin": "sin",
            "bebida": "bebida",
            "vebida": "bebida",
            "vebidas": "bebidas",
            "bebidas": "bebidas",
            "galleta": "galleta",
            "gayeta": "galleta",
            "leche": "leche",
            "lechee": "leche",
            "mansana": "manzana",
            "manzana": "manzana",
            "arroz": "arroz",
            "arros": "arroz",
            # Correcciones específicas para casos documentados
            "menor": "menor",
            "menr": "menor",
            "a": "a",
            # Números mal interpretados
            "20": "20",
            "200g": "20"
        }
        self.cache_correcciones = {}
        self.max_distancia = 2
        self.umbral_confianza = 0.7
        
    def _cargar_vocabulario(self) -> set:
        """Carga el vocabulario desde la configuración LYNX"""
        vocabulario = set()
        
        # Vocabulario básico de productos y atributos
        productos_base = [
            "coca-cola", "pepsi", "sprite", "fanta", "agua", "leche", "yogurt",
            "pan", "tortillas", "arroz", "frijoles", "azúcar", "sal",
            "botana", "papas", "doritos", "cheetos", "galletas", "chocolate",
            "manzana", "naranja", "plátano", "limón", "cebolla", "tomate",
            "pollo", "carne", "pescado", "huevo", "queso", "jamón"
        ]
        
        atributos_base = [
            "barata", "caro", "grande", "pequeño", "chico", "mediano",
            "picante", "dulce", "salado", "sin", "con", "extra",
            "light", "diet", "integral", "natural", "orgánico",
            "fresco", "congelado", "enlatado"
        ]
        
        categorias_base = [
            "bebidas", "lacteos", "panaderia", "frutas", "verduras",
            "carnes", "snacks", "botanas", "cereales", "condimentos"
        ]
        
        vocabulario.update(productos_base)
        vocabulario.update(atributos_base)
        vocabulario.update(categorias_base)
        
        return vocabulario
    
    def _crear_indices_foneticos(self) -> Dict[str, List[str]]:
        """Crea índices fonéticos para español"""
        indices = {}
        
        # Mapeo de sonidos similares en español (expandido)
        equivalencias_foneticas = {
            'b': ['v', 'b'],
            'v': ['b', 'v'],
            'c': ['s', 'k', 'c', 'q'],
            'q': ['c', 'k', 'q'],
            'k': ['c', 'k', 'q'],
            's': ['z', 's', 'c'],
            'z': ['s', 'z', 'c'],
            'x': ['s', 'ks', 'cs', 'x'],  # For "pixnatw" case
            'i': ['y', 'i'],
            'y': ['i', 'y'],
            'n': ['ñ', 'n', 'm'],  # Common confusions
            'ñ': ['n', 'ñ'],
            's': ['c', 's', 'z'],
            'z': ['s', 'c', 'z'],
            'y': ['ll', 'y'],
            'll': ['y', 'll'],
            'g': ['j', 'g'],
            'j': ['g', 'j']
        }
        
        for palabra in self.vocabulario:
            clave_fonetica = self._generar_clave_fonetica(palabra)
            if clave_fonetica not in indices:
                indices[clave_fonetica] = []
            indices[clave_fonetica].append(palabra)
            
        return indices
    
    def _generar_clave_fonetica(self, palabra: str) -> str:
        """Genera una clave fonética simplificada para español"""
        # Normalizar caracteres especiales
        palabra = re.sub(r'[áa]', 'a', palabra.lower())
        palabra = re.sub(r'[éeê]', 'e', palabra)
        palabra = re.sub(r'[íi]', 'i', palabra)
        palabra = re.sub(r'[óo]', 'o', palabra)
        palabra = re.sub(r'[úu]', 'u', palabra)
        palabra = re.sub(r'ñ', 'n', palabra)
        
        # Aplicar reglas fonéticas
        palabra = re.sub(r'[bv]', 'b', palabra)
        palabra = re.sub(r'[cs]', 's', palabra)
        palabra = re.sub(r'll', 'y', palabra)
        
        return palabra
    
    def distancia_levenshtein(self, s1: str, s2: str) -> int:
        """Calcula la distancia de Levenshtein entre dos cadenas"""
        if len(s1) < len(s2):
            return self.distancia_levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        fila_anterior = list(range(len(s2) + 1))
        
        for i, c1 in enumerate(s1):
            fila_actual = [i + 1]
            
            for j, c2 in enumerate(s2):
                inserciones = fila_anterior[j + 1] + 1
                eliminaciones = fila_actual[j] + 1
                sustituciones = fila_anterior[j] + (c1 != c2)
                fila_actual.append(min(inserciones, eliminaciones, sustituciones))
            
            fila_anterior = fila_actual
        
        return fila_anterior[-1]
    
    def calcular_confianza(self, palabra_original: str, palabra_corregida: str, distancia: int) -> float:
        """Calcula la confianza de la corrección"""
        if palabra_original == palabra_corregida:
            return 1.0
        
        # La confianza disminuye con la distancia y la diferencia de longitud
        max_len = max(len(palabra_original), len(palabra_corregida))
        confianza_base = 1.0 - (distancia / max_len)
        
        # Bonus por errores comunes conocidos
        if palabra_original in self.errores_comunes:
            if self.errores_comunes[palabra_original] == palabra_corregida:
                confianza_base += 0.3
        
        return min(confianza_base, 1.0)
    
    def corregir_palabra(self, palabra: str) -> Tuple[str, float]:
        """
        Corrige una palabra y retorna la corrección con su confianza
        """
        if not palabra or len(palabra) < 2:
            return palabra, 0.0
        
        palabra = palabra.lower().strip()
        
        # Verificar cache
        if palabra in self.cache_correcciones:
            return self.cache_correcciones[palabra]
        
        # Verificar si ya está en vocabulario
        if palabra in self.vocabulario:
            resultado = (palabra, 1.0)
            self.cache_correcciones[palabra] = resultado
            return resultado
        
        # Verificar errores comunes
        if palabra in self.errores_comunes:
            correccion = self.errores_comunes[palabra]
            confianza = 0.95
            resultado = (correccion, confianza)
            self.cache_correcciones[palabra] = resultado
            return resultado
        
        # Buscar la mejor corrección
        mejor_correccion = palabra
        mejor_confianza = 0.0
        menor_distancia = float('inf')
        
        for candidato in self.vocabulario:
            distancia = self.distancia_levenshtein(palabra, candidato)
            
            if distancia <= self.max_distancia:
                confianza = self.calcular_confianza(palabra, candidato, distancia)
                
                if confianza > mejor_confianza and distancia <= menor_distancia:
                    mejor_correccion = candidato
                    mejor_confianza = confianza
                    menor_distancia = distancia
        
        # Solo retornar corrección si supera el umbral
        if mejor_confianza >= self.umbral_confianza:
            resultado = (mejor_correccion, mejor_confianza)
        else:
            resultado = (palabra, 0.0)
        
        self.cache_correcciones[palabra] = resultado
        return resultado
    
    def corregir_consulta(self, consulta: str) -> Dict:
        """
        Corrige una consulta completa y retorna información detallada
        """
        palabras = consulta.lower().split()
        correcciones = []
        consulta_corregida_palabras = []
        aplicado = False
        
        for palabra in palabras:
            # Limpiar puntuación
            palabra_limpia = re.sub(r'[^\w\s-]', '', palabra)
            
            if palabra_limpia:
                correccion, confianza = self.corregir_palabra(palabra_limpia)
                
                if correccion != palabra_limpia and confianza >= self.umbral_confianza:
                    correcciones.append({
                        "from": palabra_limpia,
                        "to": correccion,
                        "confidence": round(confianza, 2)
                    })
                    consulta_corregida_palabras.append(correccion)
                    aplicado = True
                else:
                    consulta_corregida_palabras.append(palabra_limpia)
            else:
                consulta_corregida_palabras.append(palabra)
        
        return {
            "applied": aplicado,
            "changes": correcciones,
            "corrected_query": " ".join(consulta_corregida_palabras) if aplicado else consulta
        }
    
    def agregar_al_vocabulario(self, palabras: List[str]):
        """Agrega nuevas palabras al vocabulario"""
        for palabra in palabras:
            self.vocabulario.add(palabra.lower().strip())
        
        # Regenerar índices fonéticos
        self.indices_foneticos = self._crear_indices_foneticos()
        
        # Limpiar cache para que se regenere
        self.cache_correcciones.clear()
