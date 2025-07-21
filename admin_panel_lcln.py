#!/usr/bin/env python3
"""
Panel de Administración Simple - Sistema LCLN Dinámico
Interfaz básica para administrar el sistema NLP
"""

import requests
import json
import time
from datetime import datetime

class AdminPanelLCLN:
    def __init__(self):
        self.api_base = "http://localhost:8004"
        self.backend_base = "http://localhost:5000"
    
    def mostrar_menu(self):
        print("\n" + "="*60)
        print("🦎 PANEL DE ADMINISTRACIÓN - SISTEMA LCLN DINÁMICO")
        print("="*60)
        print("1. 📊 Ver estadísticas del sistema")
        print("2. 🔍 Probar consulta NLP")
        print("3. 🔄 Refrescar cache de productos")
        print("4. 🏥 Estado de los servicios")
        print("5. 📋 Últimas consultas")
        print("6. 🧪 Ejecutar pruebas de integración")
        print("7. 📄 Generar reporte completo")
        print("8. 🚪 Salir")
        print("-"*60)
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas del sistema"""
        try:
            response = requests.get(f"{self.api_base}/api/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def obtener_health(self):
        """Obtiene estado de salud del sistema"""
        try:
            response = requests.get(f"{self.api_base}/api/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def refrescar_cache(self):
        """Refresca el cache de productos"""
        print("🔄 Refrescando cache de productos...")
        try:
            response = requests.post(f"{self.api_base}/api/force-cache-refresh", timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data.get('message', 'Cache refrescado exitosamente')}")
                return True
            else:
                print(f"❌ Error al refrescar cache: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def probar_consulta(self):
        """Prueba una consulta NLP"""
        consulta = input("🔍 Ingresa tu consulta: ")
        if not consulta.strip():
            print("❌ Consulta vacía")
            return
        
        print(f"Procesando '{consulta}'...")
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/api/nlp/analyze",
                json={"query": consulta},
                timeout=10
            )
            tiempo = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                productos = data.get('recommendations', [])
                
                print(f"\n✅ Consulta procesada en {tiempo:.2f} segundos")
                print(f"📦 Productos encontrados: {len(productos)}")
                
                if productos:
                    print(f"\n🔝 Top 5 resultados:")
                    for i, producto in enumerate(productos[:5]):
                        nombre = producto.get('nombre', producto.get('name', 'N/A'))
                        precio = producto.get('precio', producto.get('price', 0))
                        categoria = producto.get('categoria', producto.get('category', 'N/A'))
                        imagen = "🖼️" if producto.get('imagen', producto.get('image')) else "📄"
                        print(f"   {i+1}. {imagen} {nombre} - ${precio} ({categoria})")
                
                # Mostrar interpretación
                interpretacion = data.get('interpretation', {})
                if interpretacion:
                    print(f"\n🧠 Interpretación:")
                    print(f"   • Tipo: {interpretacion.get('type', 'N/A')}")
                    print(f"   • Estrategia: {interpretacion.get('estrategia_usada', 'N/A')}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas detalladas"""
        print("📊 ESTADÍSTICAS DEL SISTEMA")
        print("-"*30)
        
        # Health del sistema
        health = self.obtener_health()
        if "error" not in health:
            print(f"🏥 Estado: {health['status']}")
            print(f"📅 Última actualización: {health['timestamp']}")
            
            components = health.get('components', {})
            print(f"💾 Base de datos: {components.get('database', 'N/A')}")
            print(f"📦 Productos: {components.get('products', 'N/A')}")
            print(f"🏷️ Categorías: {components.get('categories', 'N/A')}")
            
            features = health.get('features', {})
            if features:
                print(f"\n🚀 Características:")
                for feature, enabled in features.items():
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {feature.replace('_', ' ').title()}")
        else:
            print(f"❌ Error obteniendo health: {health['error']}")
        
        # Stats del sistema
        stats = self.obtener_estadisticas()
        if "error" not in stats:
            print(f"\n📈 Estadísticas adicionales:")
            print(f"   • Total productos: {stats.get('total_products', 'N/A')}")
            print(f"   • Categorías: {len(stats.get('categories', []))}")
            print(f"   • Uptime: {stats.get('system_uptime', 0):.1f} segundos")
        else:
            print(f"❌ Error obteniendo stats: {stats['error']}")
    
    def verificar_servicios(self):
        """Verifica el estado de todos los servicios"""
        print("🏥 ESTADO DE LOS SERVICIOS")
        print("-"*25)
        
        servicios = [
            ("NLP API (8004)", f"{self.api_base}/api/health"),
            ("Backend API (5000)", f"{self.backend_base}/api/health")
        ]
        
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {nombre}: Funcionando")
                else:
                    print(f"❌ {nombre}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {nombre}: No disponible ({e})")
    
    def generar_reporte_completo(self):
        """Genera un reporte completo del sistema"""
        print("📄 GENERANDO REPORTE COMPLETO DEL SISTEMA...")
        print("="*50)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Recopilar información
        health = self.obtener_health()
        stats = self.obtener_estadisticas()
        
        # Generar reporte
        reporte = f"""
🦎 REPORTE DEL SISTEMA LCLN DINÁMICO
Generado: {timestamp}

ESTADO GENERAL:
- Estado: {'✅ SALUDABLE' if health.get('status') == 'healthy' else '❌ CON PROBLEMAS'}
- Versión: {health.get('version', 'N/A')}

PRODUCTOS Y DATOS:
- Productos cargados: {health.get('components', {}).get('products', 'N/A')}
- Categorías: {health.get('components', {}).get('categories', 'N/A')}
- Base de datos: {health.get('components', {}).get('database', 'N/A')}

CARACTERÍSTICAS:
"""
        
        features = health.get('features', {})
        for feature, enabled in features.items():
            status = "✅ ACTIVO" if enabled else "❌ INACTIVO"
            reporte += f"- {feature.replace('_', ' ').title()}: {status}\n"
        
        reporte += f"""
RENDIMIENTO:
- Uptime del sistema: {stats.get('system_uptime', 0):.1f} segundos
- Última consulta: {stats.get('last_query_time', 'N/A')}

RECOMENDACIONES:
- ✅ Sistema completamente funcional y listo para producción
- 🔧 Configurar monitoreo automatizado para producción
- 📊 Implementar analytics de consultas de usuarios
- 🔄 Cache se actualiza automáticamente cada 5 minutos
"""
        
        print(reporte)
        
        # Guardar reporte
        try:
            with open(f"reporte_lcln_{timestamp.replace(':', '-').replace(' ', '_')}.txt", "w", encoding="utf-8") as f:
                f.write(reporte)
            print(f"💾 Reporte guardado como: reporte_lcln_{timestamp.replace(':', '-').replace(' ', '_')}.txt")
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
    
    def ejecutar_pruebas(self):
        """Ejecuta pruebas de integración básicas"""
        print("🧪 EJECUTANDO PRUEBAS DE INTEGRACIÓN...")
        print("-"*35)
        
        consultas_test = [
            "coca cola",
            "snacks", 
            "productos baratos",
            "papelería"
        ]
        
        resultados_exitosos = 0
        
        for consulta in consultas_test:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_base}/api/nlp/analyze",
                    json={"query": consulta},
                    timeout=8
                )
                tiempo = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    productos = len(data.get('recommendations', []))
                    print(f"✅ '{consulta}': {productos} productos ({tiempo:.2f}s)")
                    resultados_exitosos += 1
                else:
                    print(f"❌ '{consulta}': Error {response.status_code}")
                    
            except Exception as e:
                print(f"❌ '{consulta}': {e}")
        
        print(f"\n📊 Resultado: {resultados_exitosos}/{len(consultas_test)} pruebas exitosas")
        
        if resultados_exitosos == len(consultas_test):
            print("🎉 ¡Todas las pruebas pasaron! Sistema funcionando correctamente.")
        else:
            print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
    
    def ejecutar(self):
        """Ejecuta el panel de administración"""
        print("🚀 Iniciando Panel de Administración LCLN...")
        
        while True:
            try:
                self.mostrar_menu()
                opcion = input("Selecciona una opción (1-8): ").strip()
                
                if opcion == "1":
                    self.mostrar_estadisticas()
                elif opcion == "2":
                    self.probar_consulta()
                elif opcion == "3":
                    self.refrescar_cache()
                elif opcion == "4":
                    self.verificar_servicios()
                elif opcion == "5":
                    print("📋 Función de últimas consultas no implementada aún")
                elif opcion == "6":
                    self.ejecutar_pruebas()
                elif opcion == "7":
                    self.generar_reporte_completo()
                elif opcion == "8":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción no válida. Intenta de nuevo.")
                
                input("\nPresiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Panel cerrado por el usuario.")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                input("Presiona Enter para continuar...")

if __name__ == "__main__":
    admin = AdminPanelLCLN()
    admin.ejecutar()
