# adaptador_bd.py - Adaptador para compatibilidad con AFDs legacy
"""
Adaptador que permite que los AFDs legacy accedan a BaseDatosEscalable
como si fuera un diccionario tradicional
"""

class AdaptadorBaseDatos:
    """Adaptador que convierte BaseDatosEscalable en interfaz de diccionario"""
    
    def __init__(self, bd_escalable):
        self.bd_escalable = bd_escalable
        self._cache_productos = {}
        self._cache_construido = False
        
    def __getitem__(self, key):
        """Permite acceso como diccionario: adaptador['productos_completos']"""
        if not self._cache_construido:
            self._construir_cache()
            
        if key in self._cache_productos:
            return self._cache_productos[key]
        else:
            raise KeyError(f"Clave '{key}' no encontrada en adaptador")
    
    def get(self, key, default=None):
        """Permite acceso seguro: adaptador.get('productos_multi', [])"""
        try:
            return self[key]
        except KeyError:
            return default
    
    def _construir_cache(self):
        """Construye cache de productos para compatibilidad con AFDs"""
        try:
            # Obtener productos de la base de datos escalable
            productos_raw = self.bd_escalable.obtener_todos_productos()
            
            productos_simples = []
            productos_completos = []
            productos_multi = []
            categorias = set()
            
            # Clasificar productos
            for producto in productos_raw:
                nombre = producto.get('nombre', '')
                categoria = producto.get('categoria', 'General')
                
                categorias.add(categoria)
                
                # Clasificar por tipo
                palabras = nombre.split()
                if len(palabras) == 1:
                    productos_simples.append(nombre.lower())
                    productos_completos.append(nombre.lower())
                elif len(palabras) > 1:
                    productos_multi.append(nombre.lower())
                    productos_completos.append(nombre.lower())
            
            # Construir estructura compatible
            self._cache_productos = {
                'productos_simples': list(set(productos_simples)),
                'productos_multi': list(set(productos_multi)),
                'productos_completos': list(set(productos_completos)),
                'categorias': list(categorias),
                'atributos': ['picante', 'dulce', 'salado', 'sin azucar', 'natural', 'light', 'barato', 'caro'],
                'marcas': ['coca cola', 'sabritas', 'bimbo', 'lala', 'gamesa'],
                'unidades': ['ml', 'l', 'g', 'kg', 'pz', 'pzas', 'litro', 'gramo'],
                'operadores': ['>', '<', '>=', '<=', '=', '!=', 'mayor', 'menor', 'igual'],
                'modificadores': ['sin', 'con', 'extra', 'menos', 'mas', 'muy', 'poco']
            }
            
            self._cache_construido = True
            
        except Exception as e:
            # Fallback a datos básicos
            self._cache_productos = {
                'productos_simples': ['coca', 'sabritas', 'agua', 'leche'],
                'productos_multi': ['coca cola', 'agua mineral', 'leche deslactosada'],
                'productos_completos': ['coca', 'sabritas', 'coca cola', 'agua mineral'],
                'categorias': ['bebidas', 'botanas', 'lacteos'],
                'atributos': ['picante', 'dulce', 'salado', 'sin azucar', 'barato'],
                'marcas': ['coca cola', 'sabritas'],
                'unidades': ['ml', 'l', 'g'],
                'operadores': ['>', '<', '=', 'mayor', 'menor'],
                'modificadores': ['sin', 'con', 'extra']
            }
            self._cache_construido = True
    
    def keys(self):
        """Devuelve las claves disponibles"""
        if not self._cache_construido:
            self._construir_cache()
        return self._cache_productos.keys()
    
    def values(self):
        """Devuelve los valores disponibles"""
        if not self._cache_construido:
            self._construir_cache()
        return self._cache_productos.values()
    
    def items(self):
        """Devuelve pares clave-valor"""
        if not self._cache_construido:
            self._construir_cache()
        return self._cache_productos.items()
    
    def __contains__(self, key):
        """Permite usar 'in' operator"""
        if not self._cache_construido:
            self._construir_cache()
        return key in self._cache_productos
    
    def __len__(self):
        """Devuelve número de claves"""
        if not self._cache_construido:
            self._construir_cache()
        return len(self._cache_productos)
    
    def obtener_productos_por_categoria(self, categoria, limite=None):
        """Método específico para obtener productos de una categoría con límite"""
        try:
            productos = self.bd_escalable.obtener_productos_por_categoria(categoria)
            if limite:
                productos = productos[:limite]
            return productos
        except Exception as e:
            print(f"Error en obtener_productos_por_categoria: {e}")
            return []
    
    def buscar_productos_inteligente(self, query, limite=None):
        """Método para búsqueda inteligente de productos"""
        try:
            # Si la consulta es simple, usar búsqueda por texto
            if isinstance(query, str) and not query.startswith('categoria:'):
                productos = self.bd_escalable.buscar_productos_texto(query, limite=limite)
            else:
                # Si es consulta estructurada como "categoria:snacks"
                if query.startswith('categoria:'):
                    categoria = query.replace('categoria:', '').strip()
                    productos = self.bd_escalable.obtener_productos_por_categoria(categoria)
                else:
                    productos = self.bd_escalable.buscar_productos_texto(query, limite=limite)
            
            if limite and len(productos) > limite:
                productos = productos[:limite]
            
            return productos
        except Exception as e:
            print(f"Error en buscar_productos_inteligente: {e}")
            return []
    
    def obtener_productos_populares(self, limite=10):
        """Método para obtener productos populares"""
        try:
            productos = self.bd_escalable.obtener_productos_populares(limite)
            return productos
        except Exception as e:
            print(f"Error en obtener_productos_populares: {e}")
            # Fallback a productos básicos
            try:
                productos = self.bd_escalable.obtener_todos_productos()
                return productos[:limite] if productos else []
            except:
                return []
    
    def buscar_por_atributo(self, atributo, limite=10):
        """Método para buscar productos por atributo específico"""
        try:
            productos = self.bd_escalable.buscar_por_atributo(atributo, limite)
            return productos
        except Exception as e:
            print(f"Error en buscar_por_atributo: {e}")
            return []

    def buscar_productos_texto(self, texto):
        """Método específico para búsqueda de texto"""
        try:
            productos = self.bd_escalable.buscar_productos_texto(texto)
            return productos
        except:
            return []
