#!/usr/bin/env python3
"""
GENERADOR DE BASE DE DATOS MASIVA - 1000+ PRODUCTOS Y SINÓNIMOS

Genera datos realistas para:
- 1000+ productos únicos  
- 2000+ sinónimos y variaciones
- Categorías diversificadas
- Precios realistas mexicanos
- Marcas auténticas

Autor: GitHub Copilot
Fecha: 2025-01-19
"""

import json
import random
import sqlite3
from typing import List, Dict, Set
from arquitectura_escalable import ConfiguracionEscalableLYNX, SinonimoRegistro, BaseDatosEscalable
from generador_atributos_inteligente import GeneradorAtributosInteligente

class GeneradorDatosMasivos:
    """Generador especializado para crear 1000+ productos realistas"""
    
    def __init__(self):
        self.marcas_mexicanas = {
            'bebidas': ['Coca-Cola', 'Pepsi', 'Boing', 'Jumex', 'Del Valle', 'Bonafont', 'Ciel', 'Electrolit', 'Fuze Tea', 'Powerade'],
            'snacks': ['Sabritas', 'Barcel', 'Totis', 'Ricolino', 'Gamesa', 'Marinela', 'Bimbo', 'Tía Rosa', 'Wonder', 'Donitas'],
            'lacteos': ['Lala', 'Alpura', 'Santa Clara', 'Danone', 'Nestlé', 'Philadelphia', 'Chobani', 'Yoplait', 'Yakult', 'Lactaid'],
            'carnes': ['FUD', 'Herdez', 'San Rafael', 'Kir', 'Parma', 'Zwan', 'Oscar Mayer', 'Chimex', 'Sigma', 'Pilgrim\'s'],
            'abarrotes': ['La Costeña', 'Morelos', 'Verde Valle', 'Embasa', 'Clemente Jacques', 'McCormick', 'La Fina', '123', 'Patrona', 'Del Fuerte'],
            'limpieza': ['Roma', 'Zote', 'Pinol', 'Foca', 'Ariel', 'Ace', 'Maestro Limpio', 'Suavitel', 'Downy', 'Palmolive'],
            'dulceria': ['Ricolino', 'De la Rosa', 'Carlos V', 'Coronado', 'Lucas', 'Vero', 'Sonrics', 'Rockaleta', 'Pelon Pelo Rico', 'Dulces Vero']
        }
        
        self.productos_base = {
            'bebidas': {
                'refrescos': ['Cola', 'Lima-Limón', 'Naranja', 'Toronja', 'Uva', 'Manzana', 'Agua Quina', 'Ginger Ale'],
                'jugos': ['Naranja', 'Mango', 'Durazno', 'Guayaba', 'Manzana', 'Piña', 'Uva', 'Toronja', 'Cranberry', 'Arándano'],
                'agua': ['Natural', 'Mineral', 'Gasificada', 'Saborizada', 'Electrolitos', 'Alcalina', 'Purificada'],
                'cafe_te': ['Americano', 'Cappuccino', 'Latte', 'Frappé', 'Té Verde', 'Té Negro', 'Té Helado', 'Chai']
            },
            'snacks': {
                'papas': ['Clásicas', 'Adobadas', 'Limón', 'Chile', 'Jalapeño', 'Queso', 'BBQ', 'Flamin Hot', 'Crema y Cebolla'],
                'frituras': ['Torciditos', 'Palomitas', 'Cacahuates', 'Chicharrones', 'Doritos', 'Nachos', 'Tostadas', 'Churritos'],
                'galletas': ['Marías', 'Saladas', 'Chocolate', 'Avena', 'Coco', 'Mantequilla', 'Integrales', 'Animalitos'],
                'dulces': ['Chocolate', 'Caramelo', 'Gomitas', 'Paletas', 'Chicles', 'Mazapán', 'Tamarindo', 'Chamoy']
            },
            'lacteos': {
                'leche': ['Entera', 'Descremada', 'Deslactosada', 'Light', 'Chocolate', 'Fresa', 'Vainilla', 'Condensada'],
                'yogurt': ['Natural', 'Griego', 'Fresa', 'Durazno', 'Mango', 'Arándanos', 'Vainilla', 'Bebible'],
                'queso': ['Oaxaca', 'Panela', 'Manchego', 'Americano', 'Crema', 'Cottage', 'Mozzarella', 'Cheddar']
            },
            'frutas': {
                'citricos': ['Naranja Valencia', 'Limón', 'Toronja', 'Mandarina', 'Lima', 'Tangelo'],
                'tropicales': ['Mango Manila', 'Piña', 'Papaya', 'Plátano Tabasco', 'Guayaba', 'Mamey'],
                'temporada': ['Manzana Red', 'Pera', 'Durazno', 'Uvas Rojas', 'Fresas', 'Kiwi']
            },
            'verduras': {
                'basicas': ['Tomate', 'Cebolla', 'Papa', 'Zanahoria', 'Lechuga', 'Pepino', 'Apio'],
                'chiles': ['Jalapeño', 'Serrano', 'Poblano', 'Chipotle', 'Habanero', 'Güero'],
                'hierbas': ['Cilantro', 'Perejil', 'Epazote', 'Romero', 'Tomillo', 'Albahaca']
            },
            'carnes': {
                'res': ['Bistec', 'Molida', 'Arrachera', 'Costilla', 'Milanesa', 'Fajitas'],
                'pollo': ['Pechuga', 'Muslo', 'Pierna', 'Alas', 'Molido', 'Nuggets'],
                'cerdo': ['Chuleta', 'Tocino', 'Chorizo', 'Longaniza', 'Carnitas', 'Jamón'],
                'embutidos': ['Salchicha', 'Mortadela', 'Pavo', 'Atún', 'Sardina', 'Spam']
            },
            'abarrotes': {
                'granos': ['Arroz', 'Frijol Negro', 'Frijol Pinto', 'Lentejas', 'Garbanzos', 'Avena'],
                'enlatados': ['Atún', 'Sardinas', 'Chiles', 'Elote', 'Frijoles', 'Salsa'],
                'condimentos': ['Sal', 'Azúcar', 'Aceite', 'Vinagre', 'Pimienta', 'Ajo en Polvo'],
                'harinas': ['Trigo', 'Maíz', 'Avena', 'Hotcakes', 'Pan', 'Tortilla']
            },
            'limpieza': {
                'hogar': ['Detergente', 'Jabón Polvo', 'Suavizante', 'Cloro', 'Desinfectante', 'Limpiador'],
                'personal': ['Jabón Barra', 'Shampoo', 'Pasta Dental', 'Desodorante', 'Crema', 'Papel Higiénico']
            },
            'panaderia': {
                'pan': ['Blanco', 'Integral', 'Tostado', 'Bolillo', 'Telera', 'Baguette'],
                'dulces': ['Concha', 'Cuernito', 'Dona', 'Muffin', 'Pay', 'Roles']
            }
        }
        
        self.tamaños = {
            'bebidas': ['250ml', '355ml', '500ml', '600ml', '1L', '1.5L', '2L', '3L'],
            'snacks': ['25g', '35g', '45g', '62g', '85g', '120g', '150g', '200g', '300g'],
            'lacteos': ['125g', '150g', '200g', '250ml', '500ml', '1L', '2L'],
            'frutas': ['por kg', 'por pieza', '1kg', '2kg', '500g'],
            'verduras': ['por kg', 'por pieza', '1kg', '500g', 'manojo'],
            'carnes': ['por kg', '250g', '500g', '1kg', '2kg'],
            'abarrotes': ['1kg', '500g', '250g', '2kg', '5kg', '200ml', '500ml', '1L'],
            'limpieza': ['500ml', '1L', '2L', '3L', '4L', '200g', '500g', '1kg', '4 piezas', '6 piezas'],
            'panaderia': ['pieza', '6 piezas', '12 piezas', '500g', '1kg', 'grande', 'mediano']
        }
        
        self.rangos_precio = {
            'bebidas': (8, 45),
            'snacks': (5, 60),
            'lacteos': (12, 80),
            'frutas': (15, 100),
            'verduras': (8, 50),
            'carnes': (25, 250),
            'abarrotes': (6, 120),
            'limpieza': (10, 150),
            'panaderia': (3, 80),
            'dulceria': (2, 50)
        }

    def generar_productos_masivos(self, cantidad: int = 1200) -> List[Dict]:
        """Generar cantidad específica de productos únicos y realistas"""
        productos_generados = []
        id_counter = 1
        
        # Distribución por categorías
        distribucion = {
            'bebidas': 200,
            'snacks': 250,
            'lacteos': 150,
            'frutas': 100,
            'verduras': 100,
            'carnes': 150,
            'abarrotes': 180,
            'limpieza': 90,
            'panaderia': 90,
            'dulceria': 80
        }
        
        for categoria, cantidad_cat in distribucion.items():
            if categoria not in self.productos_base:
                continue
                
            productos_cat = self.productos_base[categoria]
            marcas_cat = self.marcas_mexicanas.get(categoria, ['Genérica'])
            tamaños_cat = self.tamaños.get(categoria, ['unidad'])
            precio_min, precio_max = self.rangos_precio.get(categoria, (5, 100))
            
            productos_generados_cat = 0
            
            # Generar combinaciones únicas
            for subcategoria, tipos in productos_cat.items():
                for tipo in tipos:
                    for marca in marcas_cat:
                        for tamaño in tamaños_cat:
                            if productos_generados_cat >= cantidad_cat:
                                break
                                
                            # Crear variaciones realistas
                            variaciones = self._crear_variaciones(tipo, marca)
                            
                            for variacion in variaciones:
                                if productos_generados_cat >= cantidad_cat:
                                    break
                                
                                nombre = f"{variacion} {marca} {tamaño}"
                                precio = round(random.uniform(precio_min, precio_max), 2)
                                stock = random.randint(5, 150)
                                
                                producto = {
                                    'id': id_counter,
                                    'nombre': nombre,
                                    'categoria': categoria,
                                    'subcategoria': subcategoria,
                                    'precio': precio,
                                    'marca': marca,
                                    'stock': stock,
                                    'descripcion': f"{variacion} de marca {marca} en presentación {tamaño}"
                                }
                                
                                productos_generados.append(producto)
                                productos_generados_cat += 1
                                id_counter += 1
                        
                        if productos_generados_cat >= cantidad_cat:
                            break
                    if productos_generados_cat >= cantidad_cat:
                        break
                if productos_generados_cat >= cantidad_cat:
                    break
            
            print(f"✅ Generados {productos_generados_cat} productos para categoría: {categoria}")
        
        # Mezclar para diversidad
        random.shuffle(productos_generados)
        
        print(f"🎯 TOTAL PRODUCTOS GENERADOS: {len(productos_generados)}")
        return productos_generados
    
    def _crear_variaciones(self, tipo_base: str, marca: str) -> List[str]:
        """Crear variaciones realistas de un producto base"""
        variaciones = [tipo_base]
        
        # Variaciones por sabor/característica
        if 'Cola' in tipo_base:
            variaciones.extend([f'{tipo_base} Zero', f'{tipo_base} Light', f'{tipo_base} Sin Azúcar'])
        
        if any(sabor in tipo_base for sabor in ['Chocolate', 'Fresa', 'Vainilla']):
            variaciones.extend([f'{tipo_base} Light', f'{tipo_base} Sin Azúcar', f'{tipo_base} Orgánico'])
        
        if any(picante in tipo_base for picante in ['Chile', 'Jalapeño', 'Adobadas']):
            variaciones.extend([f'{tipo_base} Extra', f'{tipo_base} Mega', f'{tipo_base} Flamin Hot'])
        
        # Variaciones específicas por marca
        if marca == 'Sabritas' and 'Clásicas' in tipo_base:
            variaciones.extend(['Papas Clásicas', 'Papas Originales', 'Papas Tradicionales'])
        
        if marca == 'Coca-Cola':
            variaciones.extend(['Refresco Cola', 'Bebida Cola'])
        
        # Limitar variaciones para evitar explosión combinatoria
        return variaciones[:3]
    
    def generar_sinonimos_masivos(self, productos: List[Dict]) -> List[SinonimoRegistro]:
        """Generar 2000+ sinónimos inteligentes basados en productos + atributos"""
        print("🧠 Generando sinónimos masivos con atributos inteligentes...")
        
        # 1. Generar sinónimos básicos (método original)
        sinonimos_basicos = self._generar_sinonimos_basicos(productos)
        
        # 2. Generar sinónimos de atributos inteligentes
        generador_atributos = GeneradorAtributosInteligente()
        sinonimos_atributos = generador_atributos.generar_sinonimos_con_atributos(productos)
        
        # 3. Combinar ambos tipos
        todos_sinonimos = sinonimos_basicos + sinonimos_atributos
        
        # 4. Eliminar duplicados manteniendo el de mayor confianza
        sinonimos_unicos = {}
        for s in todos_sinonimos:
            key = (s.termino_normalizado, s.producto_id)
            if key not in sinonimos_unicos or s.confianza > sinonimos_unicos[key].confianza:
                sinonimos_unicos[key] = s
        
        sinonimos_finales = list(sinonimos_unicos.values())
        
        print(f"🎯 TOTAL SINÓNIMOS GENERADOS: {len(sinonimos_finales)}")
        print(f"   • Sinónimos básicos: {len(sinonimos_basicos)}")
        print(f"   • Sinónimos de atributos: {len(sinonimos_atributos)}")
        print(f"   • Únicos finales: {len(sinonimos_finales)}")
        
        return sinonimos_finales
    
    def _generar_sinonimos_basicos(self, productos: List[Dict]) -> List[SinonimoRegistro]:
        """Generar sinónimos básicos (método original)"""
        sinonimos = []
        
        # Diccionario de sinónimos comunes mexicanos
        sinonimos_comunes = {
            # Bebidas
            'coca': ['coca cola', 'refresco cola', 'bebida cola', 'cola'],
            'refresco': ['bebida', 'soda', 'gaseosa'],
            'jugo': ['néctar', 'bebida de fruta', 'agua de'],
            'agua': ['agua mineral', 'agua natural', 'hidratante'],
            
            # Snacks
            'papas': ['papitas', 'frituras', 'chips', 'sabritas'],
            'palomitas': ['pochoclos', 'rosetas', 'pop corn'],
            'cacahuates': ['maní', 'cacahuetes', 'nueces'],
            'galletas': ['cookies', 'crackers', 'galletitas'],
            
            # Lácteos  
            'leche': ['lácteo', 'bebida láctea'],
            'yogurt': ['yogur', 'yoghurt', 'lácteo probiótico'],
            'queso': ['lácteo', 'derivado lácteo'],
            
            # Descriptores
            'picante': ['picoso', 'enchilado', 'con chile'],
            'dulce': ['azucarado', 'endulzado', 'con azúcar'],
            'sin azucar': ['light', 'diet', 'zero', 'bajo en calorías'],
            'grande': ['familiar', 'mega', 'extra', 'jumbo'],
            'pequeño': ['mini', 'individual', 'personal'],
            
            # Marcas comunes
            'sabritas': ['papas', 'frituras', 'botanas'],
            'bimbo': ['pan', 'panadería', 'panificadora'],
            'lala': ['leche', 'lácteo', 'derivados lácteos'],
            'coca cola': ['coca', 'refresco', 'bebida cola'],
            
            # Categorías slang
            'botanas': ['snacks', 'frituras', 'papitas', 'botanitas'],
            'refrescos': ['sodas', 'bebidas', 'gaseosas'],
            'lacteos': ['derivados lácteos', 'productos lácteos'],
            'carnes': ['proteínas', 'productos cárnicos'],
            'limpieza': ['productos de limpieza', 'artículos de aseo']
        }
        
        for producto in productos:
            nombre = producto['nombre'].lower()
            categoria = producto['categoria']
            producto_id = producto['id']
            
            # 1. Sinónimos del nombre completo
            sinonimos.append(SinonimoRegistro(
                termino=nombre,
                termino_normalizado=self._normalizar(nombre),
                producto_id=producto_id,
                categoria=categoria,
                tipo='nombre_completo',
                confianza=1.0,
                frecuencia_uso=0
            ))
            
            # 2. Sinónimos por palabras clave
            palabras = nombre.split()
            for palabra in palabras:
                if len(palabra) > 2 and palabra not in ['de', 'en', 'con', 'sin', 'por']:
                    
                    # Sinónimo directo de la palabra
                    sinonimos.append(SinonimoRegistro(
                        termino=palabra,
                        termino_normalizado=self._normalizar(palabra),
                        producto_id=producto_id,
                        categoria=categoria,
                        tipo='palabra_clave',
                        confianza=0.8,
                        frecuencia_uso=0
                    ))
                    
                    # Buscar sinónimos comunes
                    if palabra in sinonimos_comunes:
                        for sinonimo in sinonimos_comunes[palabra]:
                            sinonimos.append(SinonimoRegistro(
                                termino=sinonimo,
                                termino_normalizado=self._normalizar(sinonimo),
                                producto_id=producto_id,
                                categoria=categoria,
                                tipo='sinonimo_comun',
                                confianza=0.7,
                                frecuencia_uso=0
                            ))
            
            # 3. Sinónimos por marca
            marca = producto.get('marca', '').lower()
            if marca and marca in sinonimos_comunes:
                for sinonimo in sinonimos_comunes[marca]:
                    sinonimos.append(SinonimoRegistro(
                        termino=sinonimo,
                        termino_normalizado=self._normalizar(sinonimo),
                        producto_id=producto_id,
                        categoria=categoria,
                        tipo='sinonimo_marca',
                        confianza=0.6,
                        frecuencia_uso=0
                    ))
            
            # 4. Sinónimos por categoría
            if categoria in sinonimos_comunes:
                for sinonimo in sinonimos_comunes[categoria]:
                    sinonimos.append(SinonimoRegistro(
                        termino=sinonimo,
                        termino_normalizado=self._normalizar(sinonimo),
                        producto_id=producto_id,
                        categoria=categoria,
                        tipo='sinonimo_categoria',
                        confianza=0.5,
                        frecuencia_uso=0
                    ))
            
            # 5. Sinónimos por atributos detectados
            if any(attr in nombre for attr in ['picante', 'dulce', 'light', 'grande', 'pequeño']):
                for atributo in ['picante', 'dulce', 'light', 'grande', 'pequeño']:
                    if atributo in nombre and atributo in sinonimos_comunes:
                        for sinonimo in sinonimos_comunes[atributo]:
                            sinonimos.append(SinonimoRegistro(
                                termino=sinonimo,
                                termino_normalizado=self._normalizar(sinonimo),
                                producto_id=producto_id,
                                categoria=categoria,
                                tipo='sinonimo_atributo',
                                confianza=0.6,
                                frecuencia_uso=0
                            ))
        
        # Eliminar duplicados manteniendo el de mayor confianza
        sinonimos_unicos = {}
        for s in sinonimos:
            key = (s.termino_normalizado, s.producto_id)
            if key not in sinonimos_unicos or s.confianza > sinonimos_unicos[key].confianza:
                sinonimos_unicos[key] = s
        
        sinonimos_finales = list(sinonimos_unicos.values())
        
        print(f"🎯 TOTAL SINÓNIMOS GENERADOS: {len(sinonimos_finales)}")
        return sinonimos_finales
    
    def _normalizar(self, texto: str) -> str:
        """Normalización básica de texto"""
        import unicodedata
        texto = texto.lower().strip()
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join(c for c in texto if not unicodedata.combining(c))
        return ' '.join(texto.split())


def poblar_base_datos_masiva():
    """Función principal para poblar la base de datos con 1000+ productos"""
    print("🚀 INICIANDO GENERACIÓN MASIVA DE DATOS")
    print("=" * 60)
    
    # 1. Crear generador
    generador = GeneradorDatosMasivos()
    print("✅ Generador de datos inicializado")
    
    # 2. Generar productos masivos
    print("\n📦 Generando 1000+ productos únicos...")
    productos = generador.generar_productos_masivos(1200)
    print(f"✅ {len(productos)} productos generados")
    
    # 3. Generar sinónimos masivos
    print(f"\n🔤 Generando 2000+ sinónimos...")
    sinonimos = generador.generar_sinonimos_masivos(productos)
    print(f"✅ {len(sinonimos)} sinónimos generados")
    
    # 4. Insertar en base de datos escalable
    print(f"\n💾 Insertando en base de datos escalable...")
    config_escalable = ConfiguracionEscalableLYNX()
    config_escalable._insertar_productos_masivos(productos)
    print("✅ Productos insertados en BD")
    
    # 5. Insertar sinónimos
    config_escalable.bd_escalable.gestor_sinonimos.agregar_sinonimos_masivos(sinonimos)
    print("✅ Sinónimos insertados en BD")
    
    # 6. Mostrar estadísticas finales
    print(f"\n📊 ESTADÍSTICAS FINALES:")
    stats = config_escalable.obtener_estadisticas()
    print(f"   • Productos totales: {stats['productos']['total']}")
    print(f"   • Sinónimos totales: {stats['sinonimos']['total']}")
    print(f"   • Categorías: {stats['categorias']['total']}")
    print(f"   • Cache ratio: {stats['sinonimos']['cache_ratio']:.2%}")
    
    # 7. Probar búsquedas
    print(f"\n🔍 PRUEBAS DE BÚSQUEDA:")
    consultas_prueba = ["coca cola", "papitas", "leche", "pan", "chocolate"]
    
    for consulta in consultas_prueba:
        resultados = config_escalable.buscar_productos_inteligente(consulta, limite=3)
        print(f"   '{consulta}': {len(resultados)} resultados")
        for i, r in enumerate(resultados[:2], 1):
            print(f"     {i}. {r['nombre']} - ${r['precio']} ({r['match_type']})")
    
    print(f"\n🎉 BASE DE DATOS MASIVA CREADA EXITOSAMENTE")
    print(f"   📁 Productos DB: productos_lynx_escalable.db")
    print(f"   📁 Sinónimos DB: sinonimos_lynx.db")
    
    return config_escalable


if __name__ == "__main__":
    config = poblar_base_datos_masiva()
