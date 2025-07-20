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
        import traceback
        traceback.print_exc()
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
            import traceback
            traceback.print_exc()
            print()
            continue

if __name__ == "__main__":
    main()
