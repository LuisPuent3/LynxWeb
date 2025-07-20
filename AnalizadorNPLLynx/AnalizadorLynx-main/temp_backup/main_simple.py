# main_simple.py - Buscador simple LYNX
import json
from datetime import datetime
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

def main():
    """Sistema de búsqueda LYNX - Buscador de productos en lenguaje natural"""
    print("=== BUSCADOR LYNX ===")
    print("Busca productos usando lenguaje natural")
    print("Ejemplos: 'botana barata', 'bebidas sin azúcar', 'productos menos de 50 pesos'")
    print()
    
    # Inicializar configuración y analizador
    print("Iniciando sistema...")
    configuracion = ConfiguracionLYNX()
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✓ Sistema listo para búsquedas")
    print()
    
    # Mostrar comandos disponibles
    mostrar_ayuda()
    
    # Bucle principal de búsqueda
    while True:
        try:
            consulta = input("\n🔍 Buscar: ").strip()
            
            # Verificar comandos especiales
            if not consulta:
                continue
            elif consulta.lower() in ['salir', 'quit', 'exit']:
                print("¡Hasta luego!")
                break
            elif consulta.lower() in ['ayuda', 'help', '?']:
                mostrar_ayuda()
                continue
            elif consulta.lower() == 'ejemplos':
                mostrar_ejemplos()
                continue
            elif consulta.lower() == 'estadisticas':
                mostrar_estadisticas(configuracion)
                continue
            elif consulta.lower().startswith('agregar'):
                manejar_agregar_termino(consulta, configuracion, analizador)
                continue
            
            # Procesar búsqueda
            procesar_busqueda(consulta, analizador)
            
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

def mostrar_ayuda():
    """Muestra la ayuda del sistema"""
    print("📚 COMANDOS DISPONIBLES:")
    print("  • ayuda, help, ?     - Muestra esta ayuda")
    print("  • ejemplos           - Muestra ejemplos de búsquedas")
    print("  • estadisticas       - Muestra estadísticas del sistema")
    print("  • agregar <tipo> <término> - Agrega un nuevo término")
    print("  • salir, quit, exit  - Sale del buscador")
    print()
    print("💡 TIPOS DE BÚSQUEDA:")
    print("  • Productos: 'coca cola', 'galletas', 'leche'")
    print("  • Categorías: 'bebidas', 'botanas', 'lácteos'")
    print("  • Filtros de precio: 'barato', 'caro', 'menor a 20'")
    print("  • Atributos: 'sin azúcar', 'con chile', 'integral'")

def mostrar_ejemplos():
    """Muestra ejemplos de búsquedas"""
    ejemplos = [
        ("botana barata", "Busca snacks económicos (precio < 50)"),
        ("bebidas sin azúcar", "Busca bebidas que no contengan azúcar"),
        ("productos menos de 30", "Busca productos con precio menor a 30"),
        ("coca cola grande", "Busca Coca Cola de tamaño grande"),
        ("categoría frutas", "Busca en la categoría de frutas"),
        ("leche deslactosada", "Busca leche sin lactosa"),
        ("galletas con chocolate", "Busca galletas que contengan chocolate"),
        ("productos entre 10 y 50", "Busca productos en ese rango de precio")
    ]
    
    print("📝 EJEMPLOS DE BÚSQUEDA:")
    for i, (consulta, descripcion) in enumerate(ejemplos, 1):
        print(f"  {i:2d}. '{consulta}' → {descripcion}")

def mostrar_estadisticas(configuracion):
    """Muestra estadísticas del sistema"""
    bd = configuracion.base_datos
    print("📊 ESTADÍSTICAS DEL SISTEMA:")
    print(f"  • Productos simples: {len(bd.get('productos_simples', []))}")
    print(f"  • Productos multi-palabra: {len(bd.get('productos_multi', []))}")
    print(f"  • Productos completos: {len(bd.get('productos_completos', []))}")
    print(f"  • Categorías: {len(bd.get('categorias', []))}")
    print(f"  • Atributos: {len(bd.get('atributos', []))}")
    print(f"  • Modificadores: {len(bd.get('modificadores', []))}")
    print(f"  • Unidades: {len(bd.get('unidades', []))}")

def manejar_agregar_termino(consulta, configuracion, analizador):
    """Maneja la adición de nuevos términos"""
    try:
        partes = consulta.split(' ', 2)
        if len(partes) < 3:
            print("❌ Formato: agregar <tipo> <término>")
            print("   Tipos disponibles: producto, categoria, atributo, modificador")
            return
        
        _, tipo, termino = partes
        tipo = tipo.lower()
        termino = termino.lower()
        
        tipo_map = {
            'producto': 'productos_simples',
            'categoria': 'categorias', 
            'atributo': 'atributos',
            'modificador': 'modificadores'
        }
        
        if tipo not in tipo_map:
            print(f"❌ Tipo '{tipo}' no válido. Tipos: {', '.join(tipo_map.keys())}")
            return
            
        categoria_bd = tipo_map[tipo]
        if configuracion.agregar_termino(categoria_bd, termino):
            print(f"✓ '{termino}' agregado como {tipo}")
            configuracion.guardar_configuracion()
            # Reinicializar analizador con nueva configuración
            analizador.__init__(configuracion)
        else:
            print(f"⚠️ '{termino}' ya existe en {tipo}")
            
    except Exception as e:
        print(f"❌ Error al agregar término: {e}")

def procesar_busqueda(consulta, analizador):
    """Procesa una búsqueda y muestra los resultados"""
    print(f"\n🔍 Procesando: '{consulta}'")
    print("─" * 50)
    
    # Análisis léxico
    start_time = datetime.now()
    tokens = analizador.analizar(consulta)
    end_time = datetime.now()
    
    # Mostrar tokens encontrados
    print("🏷️  TOKENS IDENTIFICADOS:")
    if not tokens:
        print("   ❌ No se encontraron tokens válidos")
        return
    
    for i, token in enumerate(tokens, 1):
        tipo = token['tipo']
        valor = token['valor']
        
        # Mostrar información adicional para tokens especiales
        if 'interpretacion' in token:
            interp = token['interpretacion']
            print(f"   {i}. {tipo}: '{valor}' → {interp}")
        else:
            print(f"   {i}. {tipo}: '{valor}'")
    
    # Generar consulta SQL
    try:
        resultado_json = analizador.generar_json_resultado(consulta)
        resultado = json.loads(resultado_json)
        
        print("\n💡 INTERPRETACIÓN:")
        interpretacion = resultado.get('interpretacion', {})
        
        # Mostrar productos identificados
        if interpretacion.get('productos'):
            productos = interpretacion['productos']
            print(f"   📦 Productos: {', '.join([p['nombre'] for p in productos])}")
        
        # Mostrar categorías
        if interpretacion.get('categorias'):
            print(f"   📂 Categorías: {', '.join(interpretacion['categorias'])}")
        
        # Mostrar filtros
        filtros = interpretacion.get('filtros', {})
        if filtros.get('precio'):
            precio = filtros['precio']
            if 'max' in precio:
                print(f"   💰 Precio máximo: ${precio['max']}")
            if 'min' in precio:
                print(f"   💰 Precio mínimo: ${precio['min']}")
            if 'exacto' in precio:
                print(f"   💰 Precio exacto: ${precio['exacto']}")
        
        if filtros.get('atributos'):
            for attr in filtros['atributos']:
                print(f"   🏷️  {attr['modificador'].title()} {attr['atributo']}")
        
        # Mostrar consulta SQL generada
        sql = resultado.get('sql_sugerido', '')
        if sql:
            print(f"\n🗃️  CONSULTA SQL:")
            print(f"   {sql}")
        
        # Mostrar tiempo de procesamiento
        tiempo = (end_time - start_time).total_seconds() * 1000
        print(f"\n⏱️  Procesado en {tiempo:.2f}ms")
        
    except Exception as e:
        print(f"❌ Error al procesar resultado: {e}")

if __name__ == "__main__":
    main()
