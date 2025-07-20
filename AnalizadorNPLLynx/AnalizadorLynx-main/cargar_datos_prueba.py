#!/usr/bin/env python3
"""
Script para cargar datos de prueba en el sistema LYNX NLP
Basado en los productos del archivo poblar_bd_lynxshop.sql
"""

import sys
from pathlib import Path
import sqlite3
import json

# Agregar directorio padre al path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

from arquitectura_escalable import BaseDatosEscalable

def cargar_productos_prueba():
    """Carga productos de prueba basados en el archivo SQL"""
    
    productos_prueba = [
        # Bebidas (categoria = 'bebidas')
        {'id': 1, 'nombre': 'coca cola 600ml', 'precio': 18.50, 'stock': 45, 'categoria': 'bebidas'},
        {'id': 2, 'nombre': 'pepsi 600ml', 'precio': 17.00, 'stock': 38, 'categoria': 'bebidas'},
        {'id': 3, 'nombre': 'sprite 600ml', 'precio': 17.50, 'stock': 42, 'categoria': 'bebidas'},
        {'id': 4, 'nombre': 'fanta naranja 600ml', 'precio': 17.50, 'stock': 35, 'categoria': 'bebidas'},
        {'id': 5, 'nombre': 'agua bonafont 500ml', 'precio': 12.00, 'stock': 65, 'categoria': 'bebidas'},
        {'id': 6, 'nombre': 'jumex durazno 500ml', 'precio': 14.50, 'stock': 28, 'categoria': 'bebidas'},
        {'id': 7, 'nombre': 'boing mango 500ml', 'precio': 13.00, 'stock': 32, 'categoria': 'bebidas'},
        {'id': 8, 'nombre': 'electrolit naranja 625ml', 'precio': 22.00, 'stock': 15, 'categoria': 'bebidas'},
        {'id': 9, 'nombre': 'cafe americano 350ml', 'precio': 25.00, 'stock': 20, 'categoria': 'bebidas'},
        {'id': 10, 'nombre': 'te helado fuze tea 450ml', 'precio': 16.50, 'stock': 25, 'categoria': 'bebidas'},
        
        # Snacks (categoria = 'snacks')
        {'id': 11, 'nombre': 'sabritas clasicas 45g', 'precio': 15.50, 'stock': 55, 'categoria': 'snacks'},
        {'id': 12, 'nombre': 'doritos nacho 62g', 'precio': 18.00, 'stock': 48, 'categoria': 'snacks'},
        {'id': 13, 'nombre': 'cheetos torciditos 35g', 'precio': 14.00, 'stock': 62, 'categoria': 'snacks'},
        {'id': 14, 'nombre': 'ruffles queso 45g', 'precio': 16.50, 'stock': 40, 'categoria': 'snacks'},
        {'id': 15, 'nombre': 'takis fuego 62g', 'precio': 17.50, 'stock': 72, 'categoria': 'snacks'},
        {'id': 16, 'nombre': 'galletas marias gamesa 171g', 'precio': 22.00, 'stock': 25, 'categoria': 'snacks'},
        {'id': 17, 'nombre': 'chokis original 128g', 'precio': 28.50, 'stock': 18, 'categoria': 'snacks'},
        {'id': 18, 'nombre': 'emperador chocolate 45g', 'precio': 12.50, 'stock': 45, 'categoria': 'snacks'},
        {'id': 19, 'nombre': 'palomitas act ii mantequilla 85g', 'precio': 19.50, 'stock': 30, 'categoria': 'snacks'},
        {'id': 20, 'nombre': 'cacahuates japoneses 40g', 'precio': 13.00, 'stock': 38, 'categoria': 'snacks'},
        
        # Lácteos (categoria = 'lacteos')
        {'id': 21, 'nombre': 'leche lala entera 1l', 'precio': 24.50, 'stock': 35, 'categoria': 'lacteos'},
        {'id': 22, 'nombre': 'yogurt danone fresa 125g', 'precio': 11.50, 'stock': 42, 'categoria': 'lacteos'},
        {'id': 23, 'nombre': 'queso oaxaca philadelphia 150g', 'precio': 32.00, 'stock': 20, 'categoria': 'lacteos'},
        {'id': 24, 'nombre': 'leche deslactosada lactaid 1l', 'precio': 28.00, 'stock': 15, 'categoria': 'lacteos'},
        {'id': 25, 'nombre': 'yogurt griego chobani 150g', 'precio': 19.50, 'stock': 25, 'categoria': 'lacteos'},
        
        # Frutas (categoria = 'frutas')
        {'id': 26, 'nombre': 'manzana roja por kg', 'precio': 45.00, 'stock': 25, 'categoria': 'frutas'},
        {'id': 27, 'nombre': 'platano tabasco por kg', 'precio': 22.00, 'stock': 40, 'categoria': 'frutas'},
        {'id': 28, 'nombre': 'naranja valencia por kg', 'precio': 18.50, 'stock': 35, 'categoria': 'frutas'},
        {'id': 29, 'nombre': 'uvas rojas por kg', 'precio': 65.00, 'stock': 12, 'categoria': 'frutas'},
        {'id': 30, 'nombre': 'pera anjou por kg', 'precio': 52.00, 'stock': 18, 'categoria': 'frutas'},
        
        # Verduras (categoria = 'verduras')
        {'id': 31, 'nombre': 'zanahoria por kg', 'precio': 16.00, 'stock': 30, 'categoria': 'verduras'},
        {'id': 32, 'nombre': 'lechuga romana pieza', 'precio': 12.00, 'stock': 25, 'categoria': 'verduras'},
        {'id': 33, 'nombre': 'tomate saladette por kg', 'precio': 24.00, 'stock': 28, 'categoria': 'verduras'},
        {'id': 34, 'nombre': 'cebolla blanca por kg', 'precio': 19.00, 'stock': 35, 'categoria': 'verduras'},
        {'id': 35, 'nombre': 'papa blanca por kg', 'precio': 21.00, 'stock': 45, 'categoria': 'verduras'},
        
        # Panadería (categoria = 'panaderia')
        {'id': 36, 'nombre': 'pan blanco bimbo grande', 'precio': 32.00, 'stock': 22, 'categoria': 'panaderia'},
        {'id': 37, 'nombre': 'dona glaseada bimbo', 'precio': 8.50, 'stock': 48, 'categoria': 'panaderia'},
        {'id': 38, 'nombre': 'muffin chocolate chips 120g', 'precio': 15.00, 'stock': 32, 'categoria': 'panaderia'},
        {'id': 39, 'nombre': 'pan tostado bimbo 380g', 'precio': 28.50, 'stock': 18, 'categoria': 'panaderia'},
        
        # Dulcería (categoria = 'dulceria')
        {'id': 40, 'nombre': 'chocolate carlos v 30g', 'precio': 12.00, 'stock': 85, 'categoria': 'dulceria'},
        {'id': 41, 'nombre': 'paleta payaso 25g', 'precio': 8.50, 'stock': 95, 'categoria': 'dulceria'},
        {'id': 42, 'nombre': 'chicles trident menta 12 piezas', 'precio': 15.50, 'stock': 42, 'categoria': 'dulceria'},
        {'id': 43, 'nombre': 'mazapan de la rosa 28g', 'precio': 6.50, 'stock': 78, 'categoria': 'dulceria'},
        {'id': 44, 'nombre': 'gomitas panditas 85g', 'precio': 16.50, 'stock': 55, 'categoria': 'dulceria'}
    ]
    
    return productos_prueba

def cargar_sinonimos_prueba():
    """Carga sinónimos de prueba para mejorar las búsquedas"""
    
    sinonimos_prueba = {
        # Bebidas
        'refresco': ['coca cola', 'pepsi', 'sprite', 'fanta'],
        'cola': ['coca cola', 'pepsi'],
        'gaseosa': ['coca cola', 'pepsi', 'sprite', 'fanta'],
        'soda': ['coca cola', 'pepsi', 'sprite', 'fanta'],
        'agua': ['agua bonafont'],
        'jugo': ['jumex durazno', 'boing mango'],
        'bebida': ['coca cola', 'pepsi', 'sprite', 'agua', 'jugo'],
        
        # Snacks
        'papas': ['sabritas clasicas', 'doritos nacho', 'ruffles queso'],
        'frituras': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'takis'],
        'botana': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'takis', 'cacahuates'],
        'snack': ['sabritas', 'doritos', 'cheetos', 'ruffles', 'takis'],
        'galleta': ['galletas marias', 'chokis', 'emperador'],
        'dulce': ['emperador', 'chocolate carlos v', 'mazapan'],
        
        # Lácteos
        'leche': ['leche lala', 'leche deslactosada'],
        'yogur': ['yogurt danone', 'yogurt griego'],
        'yogurt': ['yogurt danone', 'yogurt griego'],
        'queso': ['queso oaxaca'],
        'lacteo': ['leche', 'yogurt', 'queso'],
        
        # Frutas
        'fruta': ['manzana', 'platano', 'naranja', 'uvas', 'pera'],
        'manzana': ['manzana roja'],
        'banana': ['platano tabasco'],
        'platano': ['platano tabasco'],
        'uva': ['uvas rojas'],
        
        # Precios/Atributos
        'barato': ['economico', 'bajo precio'],
        'barata': ['economica', 'bajo precio'],
        'economico': ['barato', 'bajo precio'],
        'caro': ['costoso', 'alto precio'],
        'picante': ['fuego', 'chile', 'hot'],
        'dulce': ['azucar', 'endulzado'],
        'sin azucar': ['light', 'diet', 'zero'],
        
        # Correcciones ortográficas comunes
        'koka': ['coca'],
        'kola': ['cola'],
        'chetos': ['cheetos'],
        'cheetos': ['cheetos torciditos'],
        'dorrito': ['doritos'],
        'dorito': ['doritos'],
        'sabritas': ['sabritas clasicas'],
        'votana': ['botana'],
        'brata': ['barata'],
        'varata': ['barata'],
        'picabte': ['picante'],
        'asucar': ['azucar'],
    }
    
    return sinonimos_prueba

def main():
    """Función principal para cargar todos los datos"""
    
    print("🚀 Iniciando carga de datos de prueba para LYNX NLP...")
    
    try:        # Crear instancia de la configuración escalable
        from arquitectura_escalable import ConfiguracionEscalableLYNX
        
        # Cargar productos
        productos = cargar_productos_prueba()
        print(f"📦 Cargando {len(productos)} productos...")
          # Crear configuración escalable que contiene el método correcto
        from arquitectura_escalable import ConfiguracionEscalableLYNX
        config_escalable = ConfiguracionEscalableLYNX()
        
        # Insertar productos usando el método correcto
        print("📦 Insertando productos en masa...")
        config_escalable._insertar_productos_masivos(productos)
          # Cargar sinónimos (por ahora omitimos esto)
        print(f"📝 Sinónimos omitidos por ahora (se generaron automáticamente)")
        
        # Los sinónimos se generan automáticamente durante la inserción
        # No necesitamos cargar manualmente por ahora
          # Recrear índices
        config_escalable.bd_escalable._crear_indices()
          # Verificar carga
        stats = config_escalable.obtener_estadisticas()
        
        print("\n✅ CARGA COMPLETADA!")
        print(f"📊 Estadísticas finales:")
        print(f"   • Productos cargados: {stats['productos']['total']}")
        print(f"   • Sinónimos cargados: {stats['sinonimos']['total']}")
        
        # Mostrar categorías de forma segura
        try:
            categorias = stats.get('productos', {}).get('categorias', [])
            print(f"   • Categorías disponibles: {len(categorias)}")
            if categorias:
                print(f"   • Categorías: {', '.join(categorias[:5])}{'...' if len(categorias) > 5 else ''}")
        except Exception as e:
            print(f"   • Categorías: (error al mostrar: {e})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la carga: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Sistema LYNX NLP listo para usar!")
        print("   • Reinicia el servidor FastAPI para ver los cambios")
        print("   • Usa: python main.py en la carpeta api/")
    else:
        print("\n💥 Falló la carga de datos")
        sys.exit(1)
