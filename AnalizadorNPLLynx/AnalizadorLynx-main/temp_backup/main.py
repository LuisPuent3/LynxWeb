# main.py - Buscador LYNX (Simulador Web Interface) - ESCALABLE
import json
import time
from datetime import datetime
from arquitectura_escalable import ConfiguracionEscalableLYNX
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
    """Muestra el banner del sistema escalable"""
    print(Colors.CYAN + Colors.BOLD + """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                   🦎 BUSCADOR LYNX 3.0 ESCALABLE             ║
    ║              Sistema Inteligente con 1000+ Productos          ║
    ║        Atributos Inteligentes + Sinónimos "Fuego/Hot"         ║
    ║                      🎯 VERSIÓN ACTUALIZADA                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """ + Colors.ENDC)
    
    print(Colors.GREEN + "🔍 Busca productos usando lenguaje natural + atributos inteligentes" + Colors.ENDC)
    print(Colors.BLUE + "💡 Ejemplos: 'papitas fuego', 'botana flaming hot', 'productos sin azucar'" + Colors.ENDC)
    print(Colors.WARNING + "� NUEVO: Sinónimos 'fuego', 'flaming hot' mapean a productos picantes" + Colors.ENDC)
    print()

def mostrar_estado_sistema(configuracion):
    """Muestra el estado del sistema escalable"""
    print(Colors.HEADER + "📊 ESTADO DEL SISTEMA ESCALABLE:" + Colors.ENDC)
    
    # Obtener estadísticas de la configuración escalable
    try:
        stats = configuracion.obtener_estadisticas()
        
        print(f"   🚀 Arquitectura: {Colors.GREEN}ESCALABLE{Colors.ENDC}")
        print(f"   📦 Productos disponibles: {Colors.CYAN}{stats['productos']['total']:,}{Colors.ENDC}")
        print(f"   🔤 Sinónimos inteligentes: {Colors.CYAN}{stats['sinonimos']['total']:,}{Colors.ENDC}")
        print(f"   📂 Categorías: {Colors.CYAN}{stats['categorias']['total']}{Colors.ENDC}")
        
        # Mostrar performance de cache
        if 'cache_ratio' in stats['sinonimos']:
            ratio = stats['sinonimos']['cache_ratio'] * 100
            print(f"   ⚡ Cache hits ratio: {Colors.GREEN}{ratio:.1f}%{Colors.ENDC}")
        
        print()
        
        # Mostrar distribución por categorías (top 5)
        print(Colors.HEADER + "📈 TOP CATEGORÍAS:" + Colors.ENDC)
        categorias_top = sorted(stats['productos']['por_categoria'], 
                               key=lambda x: x['productos'], reverse=True)[:5]
        for cat in categorias_top:
            print(f"   • {cat['categoria']}: {cat['productos']} productos")
        print()
            
    except Exception as e:
        print(f"   {Colors.WARNING}⚠️  Error obteniendo estadísticas: {e}{Colors.ENDC}")
        print(f"   🚀 Arquitectura: {Colors.GREEN}ESCALABLE (Modo básico){Colors.ENDC}")
        print()
    
    print(f"   ✅ Búsqueda por atributos: {Colors.GREEN}ACTIVA{Colors.ENDC}")
    print(f"   ✅ Corrección ortográfica: {Colors.GREEN}ACTIVA{Colors.ENDC}")
    print(f"   ✅ Motor recomendaciones: {Colors.GREEN}ACTIVO{Colors.ENDC}")
    print()

def mostrar_sugerencias_rapidas():
    """Muestra sugerencias rápidas con atributos inteligentes"""
    sugerencias = [
        ("🥤", "bebidas sin azucar", "Refrescos dietéticos y light - NUEVO"),
        ("🌶️", "productos picantes barato", "Snacks enchilados económicos - MEJORADO"),
        ("💰", "productos baratos", "Ofertas y promociones"),
        ("🍫", "chocolate", "Buscar por nombre de producto - NUEVO"),
        ("🥛", "leche deslactosada", "Lácteos sin lactosa"),
        ("🧂", "frituras saladas", "Botanas con sal"),
        ("🥤", "coca cola", "Refrescos de marca específica - MEJORADO"),
        ("🍟", "papitas sabritas", "Frituras crujientes"),
        ("🍭", "paleta dulce", "Dulces y postres con atributo - NUEVO")
    ]
    
    print(Colors.HEADER + "🚀 BÚSQUEDAS POPULARES CON ATRIBUTOS INTELIGENTES:" + Colors.ENDC)
    for i, (emoji, consulta, desc) in enumerate(sugerencias, 1):
        print(f"   {emoji} {Colors.CYAN}{consulta}{Colors.ENDC} - {desc}")
    print()
    print(Colors.WARNING + "💡 NUEVAS FUNCIONALIDADES:" + Colors.ENDC)
    print(Colors.BLUE + "🎯 Atributos complejos: 'sin azucar', 'productos picantes'" + Colors.ENDC)
    print(Colors.BLUE + "🔍 Búsqueda por nombre: 'chocolate', 'coca cola'" + Colors.ENDC)
    print(Colors.BLUE + "💰 Filtros combinados: 'picante barato', 'dulce grande'" + Colors.ENDC)
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
        
        if interpretacion.get('producto'):
            print(f"   🔍 Producto detectado: {Colors.CYAN}{interpretacion['producto']}{Colors.ENDC}")
        
        if interpretacion.get('categoria'):
            print(f"   📂 Categoría detectada: {Colors.CYAN}{interpretacion['categoria']}{Colors.ENDC}")
        
        if interpretacion.get('atributos'):
            atributos = interpretacion['atributos']
            print(f"   🏷️  Atributos: {Colors.GREEN}{', '.join(atributos)}{Colors.ENDC}")
        
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
                
                # Razones del match - Mapear las razones actuales (MEJORADO)
                if razones:
                    razones_texto = {
                        # Razones de atributos
                        'atributo_picante': '🌶️ Producto picante',
                        'atributo_sin_azucar': '🚫 Sin azúcar',
                        'atributo_dulce': '🍭 Producto dulce',
                        'atributo_salado': '🧂 Salado',
                        'atributo_barato': '💰 Precio económico',
                        'atributo_caro': '💎 Producto premium',
                        'atributo_grande': '📏 Tamaño grande',
                        'atributo_pequeño': '📏 Tamaño pequeño',
                        'atributo_sin_lactosa': '🥛 Sin lactosa',
                        'atributo_sin_gluten': '🌾 Sin gluten',
                        
                        # Razones de categoría
                        'categoria_correcta': '🎯 Categoría exacta',
                        'categoria_inferida_snacks': '🍟 Categoría: Snacks',
                        'categoria_inferida_bebidas': '🥤 Categoría: Bebidas',
                        'categoria_inferida_lacteos': '🥛 Categoría: Lácteos',
                        'categoria_inferida_dulceria': '🍭 Categoría: Dulces',
                        'busqueda_por_categoria': '📂 Búsqueda por categoría',
                        
                        # Razones de producto
                        'producto_exacto': '🎯 Producto exacto',
                        'producto_similar': '🔄 Producto similar',
                        'alta_similitud': '⭐ Alta similitud',
                        'buena_similitud': '👍 Buena similitud',
                        
                        # Razones de precio
                        'precio_en_rango': '💰 Precio ideal',
                        'precio_cercano': '💰 Precio similar',
                        'precio_economico': '💸 Precio económico',
                        
                        # Razones de búsqueda
                        'busqueda_inteligente': '🧠 Búsqueda inteligente',
                        'busqueda_combinada': '🔍 Búsqueda combinada',
                        'busqueda_basica': '🔍 Búsqueda básica',
                        'atributos_coinciden': '🏷️ Atributos coinciden',
                        
                        # Razones de fallback
                        'producto_popular': '📈 Producto popular',
                        'recomendacion_general': '💡 Recomendación general',
                        'categoria_relacionada': '📂 Categoría relacionada',
                        
                        # Razones legacy (mantener compatibilidad)
                        'categoria_correcta': '🎯 Categoría exacta',
                        'precio_en_rango': '💰 Precio ideal',
                        'precio_cercano': '💰 Precio similar',
                        'atributos_coinciden': '🏷️ Atributos coinciden',
                        'alta_similitud': '⭐ Alta similitud',
                        'buena_similitud': '👍 Buena similitud',
                        'producto_similar': '🔄 Producto similar',
                        'producto_exacto': '🎯 Producto exacto',
                        'atributo_dulce': '🍭 Producto dulce',
                        'atributo_sin_azucar': '🚫 Sin azúcar',
                        'atributo_picante': '🌶️ Producto picante',
                        'busqueda_inteligente': '🧠 Búsqueda inteligente',
                        'precio_economico': '💰 Precio económico'
                    }
                    
                    print("│ 🎯 Por qué coincide:")
                    for razon in razones[:3]:  # Máximo 3 razones
                        texto_razon = razones_texto.get(razon, razon)
                        print(f"│   • {texto_razon}")
                
                print("└─────────────────────────────────────────────────────────────┘")
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
        import traceback
        traceback.print_exc()
        print()

def main():
    """Buscador LYNX - Interfaz principal ESCALABLE"""
    
    # Inicializar sistema escalable
    try:
        mostrar_banner()
        print(Colors.BLUE + "🚀 Iniciando sistema LYNX ESCALABLE..." + Colors.ENDC)
        print(Colors.CYAN + "   • Cargando arquitectura escalable..." + Colors.ENDC)
        print(Colors.CYAN + "   • Inicializando 1000+ productos..." + Colors.ENDC)
        print(Colors.CYAN + "   • Activando atributos inteligentes..." + Colors.ENDC)
        
        configuracion = ConfiguracionEscalableLYNX()
        analizador = AnalizadorLexicoLYNX(configuracion)
        
        print(Colors.GREEN + "✅ Sistema ESCALABLE iniciado correctamente" + Colors.ENDC)
        print()
        
        # Mostrar información específica de escalabilidad
        try:
            stats = configuracion.obtener_estadisticas()
            print(Colors.HEADER + "🎉 FUNCIONALIDADES ESCALABLES ACTIVAS:" + Colors.ENDC)
            print(f"   🔍 Búsqueda por atributos (picante, dulce, salado)")
            print(f"   💰 Filtrado por precio (barato, caro)")
            print(f"   📏 Detección de tamaño (grande, pequeño)")
            print(f"   🧠 {stats['sinonimos']['total']:,} sinónimos inteligentes")
            print(f"   🔍 Búsqueda por nombre de producto")
            print(f"   🏷️  Atributos complejos ('sin azucar', 'productos picantes')")
            print()
        except Exception as e:
            print(Colors.HEADER + "🎉 FUNCIONALIDADES ESCALABLES ACTIVAS:" + Colors.ENDC)
            print(f"   🔍 Búsqueda por atributos (picante, dulce, salado)")
            print(f"   💰 Filtrado por precio (barato, caro)")
            print(f"   📏 Detección de tamaño (grande, pequeño)")
            print(f"   🧠 Sinónimos inteligentes")
            print(f"   🔍 Búsqueda por nombre de producto")
            print(f"   🏷️  Atributos complejos ('sin azucar', 'productos picantes')")
            print()
        
        mostrar_estado_sistema(configuracion)
        mostrar_sugerencias_rapidas()
        
    except Exception as e:
        print(Colors.FAIL + f"❌ Error inicializando sistema: {e}" + Colors.ENDC)
        import traceback
        traceback.print_exc()
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
                # Modo test con consultas predefinidas - ESCALABLE ACTUALIZADO
                consultas_test = [
                    "bebidas sin azucar",     # Test atributo compuesto NUEVO
                    "productos picantes barato",  # Test combinación MEJORADO
                    "chocolate",              # Test búsqueda por nombre NUEVO
                    "coca cola",              # Test producto específico
                    "paleta dulce",           # Test atributo dulce NUEVO
                    "papitas sabritas",       # Test marca + producto
                    "leche deslactosada",     # Test atributo salud
                    "votana brata picabte"    # Test corrección ortográfica
                ]
                
                print(Colors.HEADER + "🧪 MODO TEST - Ejecutando consultas actualizadas:" + Colors.ENDC)
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
            import traceback
            traceback.print_exc()
            print()
            continue

if __name__ == "__main__":
    main()
