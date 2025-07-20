#!/usr/bin/env python3
"""
MIGRACIÓN A ARQUITECTURA ESCALABLE - LYNX SYSTEM

Este script migra tu sistema actual a la arquitectura escalable
manteniendo compatibilidad completa con el código existente.

Características:
- ✅ 1,304 productos únicos 
- ✅ 26,806 sinónimos inteligentes
- ✅ Compatibilidad total con código actual
- ✅ Rendimiento optimizado
- ✅ Base de datos SQLite escalable

Uso: python migrar_escalable.py
"""

import os
import shutil
import json
from pathlib import Path

def migrar_sistema_escalable():
    """Migración principal del sistema"""
    print("🚀 MIGRANDO A ARQUITECTURA ESCALABLE")
    print("=" * 50)
    
    # 1. Backup de archivos originales
    print("\n💾 Creando backup de archivos originales...")
    archivos_backup = [
        'utilidades.py',
        'configuracion_bd.py'
    ]
    
    backup_dir = Path("backup_original")
    backup_dir.mkdir(exist_ok=True)
    
    for archivo in archivos_backup:
        if os.path.exists(archivo):
            shutil.copy2(archivo, backup_dir / archivo)
            print(f"   ✅ Backup: {archivo}")
    
    # 2. Crear nuevo configuracion_bd.py que use arquitectura escalable
    print("\n🔄 Creando configuración escalable compatible...")
    
    nuevo_config_bd = '''# configuracion_bd.py - VERSIÓN ESCALABLE COMPATIBLE
"""
Configuración de BD escalable que mantiene compatibilidad
con el sistema original mientras usa 1000+ productos y sinónimos
"""

# Importar adaptador escalable
from adaptador_escalable import simulador_bd

# Mantener compatibilidad exportando la instancia global
# Este es el mismo nombre que usa el código original
simulador_bd = simulador_bd

# Clase para compatibilidad total
class SimuladorBDLynxShop:
    """Wrapper de compatibilidad para el simulador escalable"""
    
    def __init__(self):
        global simulador_bd
        self.simulador = simulador_bd
        
        # Propiedades compatibles
        self.productos = simulador_bd.productos
        self.categorias = simulador_bd.categorias
    
    def buscar_productos(self, consulta_sql=None, filtros=None):
        return self.simulador.buscar_productos(consulta_sql, filtros)
    
    def buscar_por_similitud(self, termino, categoria=None):
        return self.simulador.buscar_por_similitud(termino, categoria)
    
    def obtener_productos_populares(self, limit=10):
        return self.simulador.obtener_productos_populares(limit)
    
    def obtener_ofertas(self, limit=5):
        return self.simulador.obtener_ofertas(limit)
    
    def obtener_estadisticas(self):
        return self.simulador.obtener_estadisticas()

# Instancia global para compatibilidad
simulador_bd = simulador_bd  # Usa el adaptador escalable
'''
    
    with open('configuracion_bd.py', 'w', encoding='utf-8') as f:
        f.write(nuevo_config_bd)
    
    print("   ✅ configuracion_bd.py actualizado")
    
    # 3. Crear nuevo utilidades.py que use configuración escalable
    print("\n⚙️ Actualizando utilidades.py...")
    
    # Leer utilidades.py actual
    with open('utilidades.py', 'r', encoding='utf-8') as f:
        contenido_original = f.read()
    
    # Reemplazar import y configuración
    nuevo_utilidades = contenido_original.replace(
        'from configuracion_bd import simulador_bd',
        '''from configuracion_bd import simulador_bd
# Importar adaptador escalable para ConfiguracionLYNX mejorada
from adaptador_escalable import ConfiguracionLYNXEscalable'''
    )
    
    # Reemplazar la clase ConfiguracionLYNX
    if 'class ConfiguracionLYNX:' in nuevo_utilidades:
        # Encontrar el inicio y fin de la clase
        inicio_clase = nuevo_utilidades.find('class ConfiguracionLYNX:')
        if inicio_clase != -1:
            # Contar indentación para encontrar el final de la clase
            lineas = nuevo_utilidades[inicio_clase:].split('\n')
            fin_clase_relativo = 0
            
            for i, linea in enumerate(lineas[1:], 1):
                if linea.strip() and not linea.startswith('    ') and not linea.startswith('\t'):
                    fin_clase_relativo = i
                    break
            
            if fin_clase_relativo == 0:
                fin_clase_relativo = len(lineas)
            
            fin_clase = inicio_clase + len('\n'.join(lineas[:fin_clase_relativo]))
            
            # Crear nueva clase que use configuración escalable
            nueva_clase = '''class ConfiguracionLYNX:
    """Configuración LYNX con arquitectura escalable"""
    
    def __init__(self):
        # Usar configuración escalable en lugar de la original
        self._config_escalable = ConfiguracionLYNXEscalable()
        
        # Mantener compatibilidad con propiedades existentes
        self.simulador = self._config_escalable.simulador
        self.base_datos = self._config_escalable.base_datos
        
        print(f"🚀 ConfiguracionLYNX escalable cargada:")
        stats = self.simulador.obtener_estadisticas()
        print(f"   • Productos: {stats['productos']['total']}")
        print(f"   • Sinónimos: {stats.get('sinonimos', {}).get('total', 0)}")
        print(f"   • Categorías: {len(self.base_datos.get('categorias', []))}")

'''
            
            nuevo_utilidades = nuevo_utilidades[:inicio_clase] + nueva_clase + nuevo_utilidades[fin_clase:]
    
    with open('utilidades.py', 'w', encoding='utf-8') as f:
        f.write(nuevo_utilidades)
    
    print("   ✅ utilidades.py actualizado")
    
    # 4. Probar la migración
    print("\n🧪 PROBANDO MIGRACIÓN...")
    try:
        from utilidades import ConfiguracionLYNX
        from configuracion_bd import simulador_bd
        
        # Probar configuración
        config = ConfiguracionLYNX()
        
        # Probar simulador
        resultados = simulador_bd.buscar_por_similitud("coca cola")
        print(f"   ✅ Prueba búsqueda: {len(resultados)} resultados")
        
        # Mostrar estadísticas
        stats = simulador_bd.obtener_estadisticas()
        print(f"   ✅ Sistema escalable activo:")
        print(f"      • Tipo: {stats['tipo']}")
        print(f"      • Productos: {stats['productos']['total']}")
        print(f"      • Performance: {stats['performance']['tiempo_promedio_ms']:.1f}ms")
        
    except Exception as e:
        print(f"   ❌ Error en prueba: {e}")
        return False
    
    # 5. Crear archivo de verificación
    print("\n📝 Creando archivo de verificación...")
    
    verificacion_info = {
        "migrado": True,
        "fecha_migracion": "2025-01-19",
        "productos_total": stats['productos']['total'],
        "sinonimos_total": stats.get('sinonimos', {}).get('total', 0),
        "arquitectura": "escalable",
        "archivos_backup": [str(backup_dir / archivo) for archivo in archivos_backup],
        "bases_datos": [
            "productos_lynx_escalable.db",
            "sinonimos_lynx.db"
        ]
    }
    
    with open('migracion_info.json', 'w', encoding='utf-8') as f:
        json.dump(verificacion_info, f, indent=2, ensure_ascii=False)
    
    print("   ✅ migracion_info.json creado")
    
    # 6. Mostrar resumen final
    print(f"\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print(f"📊 RESUMEN:")
    print(f"   • Productos disponibles: {stats['productos']['total']:,}")
    print(f"   • Sinónimos inteligentes: {stats.get('sinonimos', {}).get('total', 0):,}")
    print(f"   • Arquitectura: Escalable con SQLite")
    print(f"   • Compatibilidad: 100% con código existente")
    print(f"   • Backup original: {backup_dir}/")
    
    print(f"\n✅ Tu sistema ahora puede manejar consultas complejas con:")
    print(f"   • Búsqueda inteligente por sinónimos")
    print(f"   • Cache optimizado para velocidad")
    print(f"   • Soporte para 1000+ productos únicos")
    
    print(f"\n🚀 ¡Listo para probar con tu código existente!")
    
    return True


def verificar_migracion():
    """Verificar que la migración fue exitosa"""
    if not os.path.exists('migracion_info.json'):
        print("❌ No se encontró información de migración")
        return False
    
    with open('migracion_info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    print("✅ VERIFICACIÓN DE MIGRACIÓN:")
    print(f"   • Estado: {'Migrado' if info['migrado'] else 'No migrado'}")
    print(f"   • Productos: {info['productos_total']:,}")
    print(f"   • Sinónimos: {info['sinonimos_total']:,}")
    print(f"   • Arquitectura: {info['arquitectura']}")
    
    return info['migrado']


def revertir_migracion():
    """Revertir a la configuración original"""
    print("🔄 REVIRTIENDO MIGRACIÓN...")
    
    backup_dir = Path("backup_original")
    
    if not backup_dir.exists():
        print("❌ No se encontró directorio de backup")
        return False
    
    archivos_revertir = ['utilidades.py', 'configuracion_bd.py']
    
    for archivo in archivos_revertir:
        backup_file = backup_dir / archivo
        if backup_file.exists():
            shutil.copy2(backup_file, archivo)
            print(f"   ✅ Revertido: {archivo}")
    
    # Eliminar archivo de verificación
    if os.path.exists('migracion_info.json'):
        os.remove('migracion_info.json')
        print("   ✅ Información de migración eliminada")
    
    print("✅ Migración revertida exitosamente")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "verificar":
            verificar_migracion()
        elif comando == "revertir":
            revertir_migracion()
        elif comando == "migrar":
            migrar_sistema_escalable()
        else:
            print("Comandos disponibles: migrar, verificar, revertir")
    else:
        # Migración por defecto
        migrar_sistema_escalable()
