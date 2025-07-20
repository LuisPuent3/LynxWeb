# main.py - Buscador LYNX 3.0 ESCALABLE
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
    print(Colors.WARNING + "🔥 NUEVO: Sinónimos 'fuego', 'flaming hot' mapean a productos picantes" + Colors.ENDC)
    print()

def mostrar_estado_sistema(configuracion):
    """Muestra el estado del sistema escalable"""
    print(Colors.HEADER + "📊 ESTADO DEL SISTEMA ESCALABLE:" + Colors.ENDC)
    
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

def mostrar_sugerencias():
    """Muestra sugerencias de búsqueda mejoradas"""
    print(Colors.HEADER + "💡 SUGERENCIAS DE BÚSQUEDA INTELIGENTE:" + Colors.ENDC)
    print()
    
    sugerencias = [
        ("🔥 Productos picantes:", ["papitas fuego", "botana flaming hot", "snacks hot", "productos picantes"]),
        ("🥤 Bebidas dietéticas:", ["bebidas sin azucar", "coca zero", "agua sin gas", "refrescos light"]),
        ("💰 Filtros de precio:", ["botana mayor a 50", "productos baratos", "bebidas caras", "snacks economicos"]),
        ("🍫 Por sabor:", ["chocolate dulce", "papas saladas", "galletas sin gluten", "yogurt natural"]),
        ("📏 Por tamaño:", ["coca familiar", "papas individuales", "agua grande", "snacks mini"]),
        ("🏷️  Por marca:", ["sabritas picantes", "coca cola zero", "productos bimbo", "agua ciel"])
    ]
    
    for categoria, ejemplos in sugerencias:
        print(f"{Colors.BLUE}{categoria}{Colors.ENDC}")
        for ejemplo in ejemplos:
            print(f"   • {Colors.CYAN}'{ejemplo}'{Colors.ENDC}")
        print()

def procesar_busqueda(consulta, configuracion, analizador):
    """Procesa una búsqueda usando el sistema escalable"""
    inicio = time.time()
    
    print(f"{Colors.HEADER}🔍 PROCESANDO: '{consulta}'{Colors.ENDC}")
    print("-" * 60)
    
    try:
        # 1. Análisis léxico
        print(f"{Colors.BLUE}1. Análisis léxico...{Colors.ENDC}")
        tokens = analizador.analizar(consulta)
        print(f"   ✅ Tokens procesados: {len(tokens)}")
        
        # Mostrar algunos tokens para debug
        for i, token in enumerate(tokens[:3]):
            if isinstance(token, dict):
                tipo = token.get('tipo', 'N/A')
                valor = token.get('valor', 'N/A')
                print(f"      Token {i+1}: {tipo} = '{valor}'")
        
        # 2. Búsqueda inteligente
        print(f"{Colors.BLUE}2. Búsqueda inteligente...{Colors.ENDC}")
        resultados = configuracion.buscar_productos_inteligente(consulta, limite=10)
        
        tiempo_total = (time.time() - inicio) * 1000
        
        # 3. Mostrar resultados
        print(f"{Colors.GREEN}3. Resultados encontrados: {len(resultados)}{Colors.ENDC}")
        print(f"   ⏱️ Tiempo total: {tiempo_total:.1f}ms")
        print()
        
        if resultados:
            print(f"{Colors.HEADER}🛍️  PRODUCTOS ENCONTRADOS:{Colors.ENDC}")
            print()
            
            for i, producto in enumerate(resultados, 1):
                nombre = producto['nombre']
                precio = producto.get('precio', 0)
                categoria = producto.get('categoria', 'N/A')
                match_type = producto.get('match_type', 'N/A')
                match_score = producto.get('match_score', 0) * 100
                
                print(f"{Colors.CYAN}{i:2d}. {nombre}{Colors.ENDC}")
                print(f"     💰 ${precio:.2f} | 📂 {categoria} | 🎯 {match_type} ({match_score:.0f}%)")
                
                if i % 5 == 0 and i < len(resultados):
                    input(f"\n{Colors.WARNING}Presiona Enter para ver más resultados...{Colors.ENDC}")
                    print()
            
        else:
            print(f"{Colors.FAIL}❌ No se encontraron productos para '{consulta}'{Colors.ENDC}")
            print(f"{Colors.WARNING}💡 Prueba términos más generales como 'papitas', 'coca', 'chocolate'{Colors.ENDC}")
        
        print()
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error en búsqueda: {e}{Colors.ENDC}")
        print(f"{Colors.WARNING}💡 Intenta reiniciar el sistema o usa términos más simples{Colors.ENDC}")
        print()

def mostrar_menu_opciones():
    """Muestra el menú de opciones"""
    print(Colors.HEADER + "⚙️  OPCIONES DISPONIBLES:" + Colors.ENDC)
    print(f"   {Colors.CYAN}help{Colors.ENDC} - Mostrar sugerencias de búsqueda")
    print(f"   {Colors.CYAN}stats{Colors.ENDC} - Mostrar estadísticas del sistema")
    print(f"   {Colors.CYAN}test{Colors.ENDC} - Ejecutar casos de prueba")
    print(f"   {Colors.CYAN}exit{Colors.ENDC} - Salir del sistema")
    print()

def ejecutar_casos_prueba(configuracion):
    """Ejecuta casos de prueba predefinidos"""
    print(f"{Colors.HEADER}🧪 EJECUTANDO CASOS DE PRUEBA:{Colors.ENDC}")
    print()
    
    casos_prueba = [
        "papitas fuego",
        "botana flaming hot", 
        "coca zero",
        "productos picantes",
        "bebidas sin azucar",
        "snacks baratos"
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"{Colors.BLUE}Caso {i}: '{caso}'{Colors.ENDC}")
        resultados = configuracion.buscar_productos_inteligente(caso, limite=3)
        
        if resultados:
            print(f"   ✅ {len(resultados)} productos encontrados")
            for j, r in enumerate(resultados[:2], 1):
                print(f"      {j}. {r['nombre'][:40]}... - ${r['precio']}")
        else:
            print("   ❌ Sin resultados")
        print()

def main():
    """Función principal del sistema LYNX 3.0 Escalable"""
    try:
        # Inicializar sistema escalable
        print(f"{Colors.GREEN}🚀 Iniciando LYNX 3.0 Escalable...{Colors.ENDC}")
        configuracion = ConfiguracionEscalableLYNX()
        analizador = AnalizadorLexicoLYNX(configuracion)
        
        # Mostrar interfaz
        mostrar_banner()
        mostrar_estado_sistema(configuracion)
        mostrar_sugerencias()
        mostrar_menu_opciones()
        
        print(f"{Colors.GREEN}✅ Sistema iniciado correctamente{Colors.ENDC}")
        print(f"{Colors.WARNING}Escribe tu búsqueda o 'help' para ver opciones{Colors.ENDC}")
        print("=" * 60)
        
        # Loop principal
        while True:
            try:
                consulta = input(f"\n{Colors.BOLD}🔍 LYNX > {Colors.ENDC}").strip()
                
                if not consulta:
                    continue
                    
                consulta_lower = consulta.lower()
                
                # Comandos especiales
                if consulta_lower in ['exit', 'quit', 'salir']:
                    print(f"{Colors.GREEN}👋 ¡Gracias por usar LYNX 3.0 Escalable!{Colors.ENDC}")
                    break
                    
                elif consulta_lower == 'help':
                    mostrar_sugerencias()
                    
                elif consulta_lower == 'stats':
                    mostrar_estado_sistema(configuracion)
                    
                elif consulta_lower == 'test':
                    ejecutar_casos_prueba(configuracion)
                    
                else:
                    # Procesar búsqueda
                    procesar_busqueda(consulta, configuracion, analizador)
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}⚠️ Interrupción detectada{Colors.ENDC}")
                confirmacion = input(f"{Colors.WARNING}¿Deseas salir? (s/n): {Colors.ENDC}")
                if confirmacion.lower() in ['s', 'si', 'yes', 'y']:
                    break
                    
            except Exception as e:
                print(f"{Colors.FAIL}❌ Error inesperado: {e}{Colors.ENDC}")
                print(f"{Colors.WARNING}💡 El sistema continuará funcionando...{Colors.ENDC}")
                
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error crítico al inicializar LYNX: {e}{Colors.ENDC}")
        print(f"{Colors.WARNING}💡 Verifica que todos los archivos estén presentes{Colors.ENDC}")
        
    finally:
        print(f"\n{Colors.CYAN}🦎 LYNX 3.0 Escalable - Sesión terminada{Colors.ENDC}")
        print(f"{Colors.GREEN}   Tiempo de sesión: {datetime.now().strftime('%H:%M:%S')}{Colors.ENDC}")

if __name__ == "__main__":
    main()
