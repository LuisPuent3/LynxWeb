# main.py - Buscador LYNX (Simulador Web Interface)
import json
import time
from datetime import datetime
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def mostrar_banner():
    """Muestra el banner del sistema"""
    print(Colors.CYAN + Colors.BOLD + """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                     🦎 BUSCADOR LYNX 2.0                     ║
    ║                Sistema Inteligente de Productos               ║
    ║              Con Corrección Ortográfica y IA                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """ + Colors.ENDC)
    
    print(Colors.GREEN + "🔍 Busca productos usando lenguaje natural" + Colors.ENDC)
    print(Colors.BLUE + "💡 Ejemplos: 'votana brata picabte', 'bebidas sin azucar', 'coca cola barata'" + Colors.ENDC)
    print()

def mostrar_estado_sistema(configuracion):
    """Muestra el estado del sistema"""
    bd = configuracion.base_datos
    print(Colors.HEADER + "📊 ESTADO DEL SISTEMA:" + Colors.ENDC)
    print(f"   ✅ Productos simples: {Colors.CYAN}{len(bd.get('productos_simples', []))}{Colors.ENDC}")
    print(f"   ✅ Productos multi-palabra: {Colors.CYAN}{len(bd.get('productos_multi', []))}{Colors.ENDC}")
    print(f"   ✅ Categorías: {Colors.CYAN}{len(bd.get('categorias', []))}{Colors.ENDC}")
    print(f"   ✅ Corrección ortográfica: {Colors.GREEN}ACTIVA{Colors.ENDC}")
    print(f"   ✅ Motor recomendaciones: {Colors.GREEN}ACTIVO{Colors.ENDC}")
    print()

def mostrar_sugerencias_rapidas():
    """Muestra sugerencias rápidas como en una página web"""
    sugerencias = [
        ("🥤", "bebidas sin azucar", "Refrescos dietéticos"),
        ("🍿", "botana barata", "Snacks económicos"),
        ("🥛", "leche deslactosada", "Lácteos sin lactosa"),
        ("🌶️", "productos picantes", "Comida con chile"),
        ("💰", "menos de 25 pesos", "Productos económicos"),
        ("🧀", "queso oaxaca", "Lácteos frescos")
    ]
    
    print(Colors.HEADER + "🚀 BÚSQUEDAS POPULARES:" + Colors.ENDC)
    for i, (emoji, consulta, desc) in enumerate(sugerencias, 1):
        print(f"   {emoji} {Colors.CYAN}{consulta}{Colors.ENDC} - {desc}")
    print()
    print(Colors.WARNING + "💡 Tip: Escribe como hablas naturalmente, el sistema corrige errores automáticamente" + Colors.ENDC)
    print()

def procesar_busqueda_web_style(consulta, analizador):
    """Procesa búsqueda simulando interfaz web"""
    
    # Header de búsqueda
    print("=" * 80)
    print(f"🔍 {Colors.BOLD}BÚSQUEDA:{Colors.ENDC} {Colors.CYAN}'{consulta}'{Colors.ENDC}")
    print("=" * 80)
    
    # Mostrar spinner simulado
    print("🔄 Procesando", end="", flush=True)
    for i in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print(" ✓")
    print()
    
    start_time = datetime.now()
    
    try:
        # Análisis con corrección ortográfica
        resultado_completo_json = analizador.generar_json_resultado_completo(consulta)
        resultado = json.loads(resultado_completo_json)
        
        end_time = datetime.now()
        tiempo_ms = (end_time - start_time).total_seconds() * 1000
        
        # Mostrar correcciones si las hay (como Google)
        correcciones = resultado.get('corrections', {})
        if correcciones.get('applied'):
            print(Colors.WARNING + "🔧 ¿QUISISTE DECIR?" + Colors.ENDC)
            consulta_corregida = correcciones.get('corrected_query', consulta)
            print(f"   {Colors.GREEN}{consulta_corregida}{Colors.ENDC}")
            
            cambios = correcciones.get('changes', [])
            for cambio in cambios:
                confianza = int(cambio['confidence'] * 100)
                print(f"   • '{cambio['from']}' → '{cambio['to']}' ({confianza}% confianza)")
            print()
        
        # Mostrar interpretación del sistema
        interpretacion = resultado.get('interpretation', {})
        print(Colors.HEADER + "🧠 INTERPRETACIÓN DEL SISTEMA:" + Colors.ENDC)
        
        if interpretacion.get('categoria'):
            print(f"   📂 Categoría detectada: {Colors.CYAN}{interpretacion['categoria']}{Colors.ENDC}")
        
        # Filtros aplicados
        filtros = interpretacion.get('filtros', {})
        if filtros:
            print(f"   🔧 Filtros aplicados:")
            
            if filtros.get('precio'):
                precio_info = filtros['precio']
                if 'max' in precio_info:
                    print(f"      💰 Precio máximo: ${precio_info['max']}")
                if 'min' in precio_info:
                    print(f"      💰 Precio mínimo: ${precio_info['min']}")
                if precio_info.get('tendency') == 'low':
                    print(f"      📉 Tendencia: Productos económicos")
            
            if filtros.get('atributos'):
                for attr in filtros['atributos']:
                    if isinstance(attr, dict):
                        mod = attr.get('modificador', 'con')
                        atr = attr.get('atributo', '')
                        emoji = "❌" if mod == 'sin' else "✅"
                        print(f"      {emoji} {mod.title()} {atr}")
        print()
        
        # Mostrar recomendaciones como resultados de búsqueda
        recomendaciones = resultado.get('recommendations', [])
        if recomendaciones:
            print(Colors.GREEN + Colors.BOLD + f"🛍️  PRODUCTOS ENCONTRADOS ({len(recomendaciones)} resultados):" + Colors.ENDC)
            print()
            
            for i, rec in enumerate(recomendaciones, 1):
                nombre = rec.get('name', 'Producto')
                precio = rec.get('price', 0)
                categoria = rec.get('category', 'General')
                score = rec.get('match_score', 0)
                razones = rec.get('match_reasons', [])
                disponible = rec.get('available', True)
                
                # Card del producto (simulando interfaz web)
                print(f"┌─── {Colors.BOLD}PRODUCTO #{i}{Colors.ENDC} ─────────────────────────────────────┐")
                print(f"│ 📦 {Colors.CYAN}{nombre}{Colors.ENDC}")
                print(f"│ 📂 Categoría: {categoria}")
                print(f"│ 💰 Precio: {Colors.GREEN}${precio:.2f}{Colors.ENDC}")
                print(f"│ ⭐ Match: {score * 100:.0f}%")
                
                # Estado de disponibilidad
                if disponible:
                    print(f"│ ✅ {Colors.GREEN}DISPONIBLE{Colors.ENDC}")
                else:
                    print(f"│ ❌ {Colors.FAIL}AGOTADO{Colors.ENDC}")
                
                # Razones del match
                if razones:
                    razones_texto = {
                        'categoria_correcta': '🎯 Categoría exacta',
                        'precio_en_rango': '💰 Precio ideal',
                        'precio_cercano': '💰 Precio similar',
                        'atributos_coinciden': '🏷️ Atributos coinciden',
                        'alta_similitud': '⭐ Alta similitud',
                        'buena_similitud': '👍 Buena similitud',
                        'producto_similar': '🔄 Producto similar'
                    }
                    
                    print("│ 🎯 Por qué coincide:")
                    for razon in razones[:3]:  # Máximo 3 razones
                        texto_razon = razones_texto.get(razon, razon)
                        print(f"│   • {texto_razon}")
                
                print("└─────────────────────────────────────────────────────────┘")
                print()
        
        else:
            print(Colors.WARNING + "❌ No se encontraron productos que coincidan exactamente" + Colors.ENDC)
            print(Colors.BLUE + "💡 Prueba con:")
            print("   • Términos más generales ('bebidas' en lugar de marca específica)")
            print("   • Revisar ortografía")
            print("   • Usar sinónimos ('refresco' en lugar de 'bebida')")
            print()
        
        # Consulta SQL generada (para desarrolladores)
        sql = resultado.get('sql_query', '')
        if sql and len(sql) < 200:  # Solo mostrar si no es muy larga
            print(Colors.HEADER + "🗃️  CONSULTA GENERADA:" + Colors.ENDC)
            print(f"   {Colors.CYAN}{sql}{Colors.ENDC}")
            print()
        
        # Mensaje del sistema
        mensaje = resultado.get('user_message', '')
        if mensaje:
            print(Colors.BLUE + f"💬 {mensaje}" + Colors.ENDC)
            print()
        
        # Footer con estadísticas
        print("─" * 80)
        print(f"⏱️  Procesado en {tiempo_ms:.1f}ms | "
              f"🎯 {len(recomendaciones)} productos encontrados | "
              f"🔧 Corrección: {'Sí' if correcciones.get('applied') else 'No'}")
        print()
        
    except Exception as e:
        print(Colors.FAIL + f"❌ Error procesando búsqueda: {e}" + Colors.ENDC)
        print(Colors.WARNING + "💡 Intenta con una consulta más simple" + Colors.ENDC)
        print()

def main():
    """Buscador LYNX - Interfaz principal"""
    
    # Inicializar sistema
    try:
        mostrar_banner()
        print(Colors.BLUE + "🚀 Iniciando sistema LYNX..." + Colors.ENDC)
        
        configuracion = ConfiguracionLYNX()
        analizador = AnalizadorLexicoLYNX(configuracion)
        
        print(Colors.GREEN + "✅ Sistema iniciado correctamente" + Colors.ENDC)
        print()
        
        mostrar_estado_sistema(configuracion)
        mostrar_sugerencias_rapidas()
        
    except Exception as e:
        print(Colors.FAIL + f"❌ Error inicializando sistema: {e}" + Colors.ENDC)
        return
    
    # Loop principal del buscador
    historial = []
    
    while True:
        try:
            # Input principal (simulando barra de búsqueda web)
            print(Colors.BOLD + "┌─────────────────────────────────────────────────────────────────────────┐" + Colors.ENDC)
            consulta = input(Colors.BOLD + "│ 🔍 ¿Qué producto estás buscando? │ " + Colors.ENDC).strip()
            print(Colors.BOLD + "└─────────────────────────────────────────────────────────────────────────┘" + Colors.ENDC)
            print()
            
            # Comandos especiales (simulando URLs/rutas)
            if not consulta:
                continue
            elif consulta.lower() in ['/salir', 'salir', 'exit', 'quit']:
                print(Colors.GREEN + "👋 ¡Gracias por usar LYNX! Hasta luego" + Colors.ENDC)
                break
            elif consulta.lower() in ['/ayuda', 'ayuda', 'help', '?']:
                mostrar_sugerencias_rapidas()
                continue
            elif consulta.lower() in ['/estado', 'estado', 'status']:
                mostrar_estado_sistema(configuracion)
                continue
            elif consulta.lower() in ['/historial', 'historial']:
                if historial:
                    print(Colors.HEADER + "📈 HISTORIAL DE BÚSQUEDAS:" + Colors.ENDC)
                    for i, h in enumerate(historial[-5:], 1):  # Últimas 5
                        print(f"   {i}. {h}")
                    print()
                else:
                    print(Colors.WARNING + "📭 Sin búsquedas previas" + Colors.ENDC)
                    print()
                continue
            elif consulta.lower().startswith('/test'):
                # Modo test con consultas predefinidas
                consultas_test = [
                    "votana brata picabte",
                    "coca cola sin asucar",
                    "bebidas baratas",
                    "leche deslactosada",
                    "productos picantes menor a 30"
                ]
                
                print(Colors.HEADER + "🧪 MODO TEST - Ejecutando consultas predefinidas:" + Colors.ENDC)
                print()
                
                for consulta_test in consultas_test:
                    print(Colors.CYAN + f"▶️  Probando: {consulta_test}" + Colors.ENDC)
                    procesar_busqueda_web_style(consulta_test, analizador)
                    time.sleep(1)  # Pausa entre tests
                
                continue
            
            # Agregar al historial
            historial.append(consulta)
            if len(historial) > 50:  # Mantener máximo 50 búsquedas
                historial.pop(0)
            
            # Procesar búsqueda principal
            procesar_busqueda_web_style(consulta, analizador)
            
        except KeyboardInterrupt:
            print()
            print(Colors.GREEN + "👋 ¡Gracias por usar LYNX! Hasta luego" + Colors.ENDC)
            break
        except Exception as e:
            print(Colors.FAIL + f"❌ Error inesperado: {e}" + Colors.ENDC)
            print(Colors.WARNING + "💡 El sistema sigue funcionando, intenta otra búsqueda" + Colors.ENDC)
            print()
            continue

if __name__ == "__main__":
    main()
            
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
    
    # Análisis léxico con corrección
    start_time = datetime.now()
    resultado_completo = analizador.analizar_con_correccion(consulta)
    tokens = resultado_completo['tokens']
    correcciones = resultado_completo['correcciones']
    end_time = datetime.now()
    
    # Mostrar correcciones si las hay
    if correcciones.get('applied'):
        print("🔧 CORRECCIONES APLICADAS:")
        for correccion in correcciones.get('changes', []):
            print(f"   '{correccion['from']}' → '{correccion['to']}' (confianza: {correccion['confidence']})")
        print(f"   Consulta corregida: '{correcciones['corrected_query']}'")
        print()
    
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
    
    # Generar respuesta completa
    try:
        resultado_json = analizador.generar_json_resultado_completo(consulta)
        resultado = json.loads(resultado_json)
        
        print("\n💡 INTERPRETACIÓN:")
        interpretacion = resultado.get('interpretation', {})
        
        # Mostrar productos identificados
        if interpretacion.get('productos'):
            productos = interpretacion['productos']
            print(f"   📦 Productos: {', '.join([p['nombre'] for p in productos])}")
        
        # Mostrar categorías
        if interpretacion.get('categoria'):
            print(f"   📂 Categoría: {interpretacion['categoria']}")
        
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
                if isinstance(attr, dict):
                    modificador = attr.get('modificador', 'con')
                    atributo = attr.get('atributo', '')
                    print(f"   🏷️  {modificador.title()} {atributo}")
                else:
                    print(f"   🏷️  {attr}")
        
        # Mostrar recomendaciones si las hay
        recomendaciones = resultado.get('recommendations', [])
        if recomendaciones:
            print(f"\n💡 RECOMENDACIONES ({len(recomendaciones)}):")
            for i, rec in enumerate(recomendaciones, 1):
                score = rec.get('match_score', 0)
                precio = rec.get('price', 0)
                razones = ', '.join(rec.get('match_reasons', []))
                print(f"   {i}. {rec['name']} - ${precio:.2f}")
                print(f"      Score: {score} | Razones: {razones}")
        
        # Mostrar consulta SQL generada
        sql = resultado.get('sql_query', '')
        if sql:
            print(f"\n🗃️  CONSULTA SQL:")
            print(f"   {sql}")
        
        # Mostrar mensaje del sistema
        mensaje = resultado.get('user_message', '')
        if mensaje:
            print(f"\n💬 MENSAJE: {mensaje}")
        
        # Mostrar tiempo de procesamiento
        tiempo = (end_time - start_time).total_seconds() * 1000
        print(f"\n⏱️  Procesado en {tiempo:.2f}ms")
        
    except Exception as e:
        print(f"❌ Error al procesar resultado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
