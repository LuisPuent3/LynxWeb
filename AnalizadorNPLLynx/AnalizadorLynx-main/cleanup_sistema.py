#!/usr/bin/env python3
"""
Script de limpieza para el sistema LCLN - Eliminación de archivos innecesarios
Mantiene solo los archivos esenciales para el funcionamiento del core del sistema
"""

import os
import shutil
from pathlib import Path

def limpiar_directorio():
    """
    Elimina archivos innecesarios del directorio del AnalizadorNPLLynx
    """
    base_dir = Path(__file__).parent
    
    # Archivos a eliminar (patrones)
    archivos_innecesarios = [
        # Archivos de test
        "test_*.py",
        "debug_*.py",
        
        # Versiones obsoletas del sistema LCLN
        "sistema_lcln_corregido.py",
        "sistema_lcln_dinamico.py",
        "sistema_lcln_dinamico_corregido.py", 
        "sistema_lcln_mejorado.py",
        "sistema_lcln_simple.backup.py",
        "sistema_lcln_simple.py",
        "sistema_lcln_simple_fixed.py",
        
        # Archivos de desarrollo temporal
        "check_*.py",
        "cleanup.py",
        "fix_*.py",
        "comparar_documentacion.py",
        "add_negation_synonyms.py",
        
        # Archivos de migración y configuración antigua
        "migracion_directa.py",
        "migrar_bd_real.py",
        "migrar_simple.py",
        "cargar_datos_prueba.py",
        "conectar_mysql.py",
        "configuracion_bd.py",
        "configurador_hibrido.py",
        "config_nlp_mysql.json",
        
        # Archivos específicos de verificación
        "verificar_sinonimos.py",
        "check_coca_products.py",
        "check_current_synonyms.py",
        "check_synonyms.py",
    ]
    
    # Directorios a eliminar
    directorios_innecesarios = [
        "temp_backup",
        "resultados",
        "diagramas_afd",
        "__pycache__",
    ]
    
    print("🧹 Iniciando limpieza del sistema LCLN...")
    print("=" * 60)
    
    archivos_eliminados = []
    directorios_eliminados = []
    
    # Eliminar archivos por patrón
    for patron in archivos_innecesarios:
        if "*" in patron:
            # Usar glob para patrones
            for archivo in base_dir.glob(patron):
                if archivo.is_file():
                    try:
                        archivo.unlink()
                        archivos_eliminados.append(str(archivo.name))
                        print(f"✅ Eliminado: {archivo.name}")
                    except Exception as e:
                        print(f"❌ Error eliminando {archivo.name}: {e}")
        else:
            # Archivo específico
            archivo_path = base_dir / patron
            if archivo_path.exists() and archivo_path.is_file():
                try:
                    archivo_path.unlink()
                    archivos_eliminados.append(patron)
                    print(f"✅ Eliminado: {patron}")
                except Exception as e:
                    print(f"❌ Error eliminando {patron}: {e}")
    
    # Eliminar directorios
    for directorio in directorios_innecesarios:
        dir_path = base_dir / directorio
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                directorios_eliminados.append(directorio)
                print(f"🗂️ Directorio eliminado: {directorio}")
            except Exception as e:
                print(f"❌ Error eliminando directorio {directorio}: {e}")
    
    # Limpiar directorio API
    api_dir = base_dir / "api"
    if api_dir.exists():
        print("\n🔧 Limpiando directorio API...")
        
        # Eliminar archivos innecesarios de API
        api_innecesarios = ["main.py", "main_hibrido.py", "main_mysql.py"]
        
        for archivo in api_innecesarios:
            archivo_path = api_dir / archivo
            if archivo_path.exists():
                try:
                    archivo_path.unlink()
                    archivos_eliminados.append(f"api/{archivo}")
                    print(f"✅ API - Eliminado: {archivo}")
                except Exception as e:
                    print(f"❌ Error eliminando API/{archivo}: {e}")
        
        # Limpiar __pycache__ en API
        pycache_api = api_dir / "__pycache__"
        if pycache_api.exists():
            try:
                shutil.rmtree(pycache_api)
                directorios_eliminados.append("api/__pycache__")
                print("🗂️ API - Directorio __pycache__ eliminado")
            except Exception as e:
                print(f"❌ Error eliminando API/__pycache__: {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LIMPIEZA:")
    print(f"   📄 Archivos eliminados: {len(archivos_eliminados)}")
    print(f"   🗂️ Directorios eliminados: {len(directorios_eliminados)}")
    
    if archivos_eliminados:
        print("\n📋 Archivos eliminados:")
        for archivo in sorted(archivos_eliminados):
            print(f"   • {archivo}")
    
    if directorios_eliminados:
        print("\n📋 Directorios eliminados:")
        for directorio in sorted(directorios_eliminados):
            print(f"   • {directorio}")

def mostrar_estructura_final():
    """
    Muestra la estructura final después de la limpieza
    """
    base_dir = Path(__file__).parent
    
    print("\n" + "=" * 60)
    print("📁 ESTRUCTURA FINAL - ARCHIVOS ESENCIALES:")
    print("=" * 60)
    
    # Archivos esenciales esperados
    archivos_esenciales = {
        # Core del sistema LCLN
        "sistema_lcln_mejorado_limpio.py": "🧠 Sistema LCLN principal",
        
        # Base de datos y adaptadores
        "productos_lynx_escalable.db": "💾 Base de datos productos",
        "sinonimos_lynx.db": "📖 Base de datos sinónimos",
        "adaptador_bd.py": "🔌 Adaptador base de datos",
        "adaptador_escalable.py": "📈 Adaptador escalable",
        "adaptador_mysql.py": "🐬 Adaptador MySQL",
        
        # AFDs y analizadores
        "afd_base.py": "🔤 Autómata base",
        "afd_moderno.py": "🆕 Autómata moderno",
        "afd_multipalabra.py": "📝 Autómata multipalabra",
        "afd_numeros.py": "🔢 Autómata números",
        "afd_operadores.py": "➕ Autómata operadores",
        "afd_palabras.py": "📚 Autómata palabras",
        "afd_unidades.py": "📏 Autómata unidades",
        "afd_visualizador_moderno.py": "👁️ Visualizador AFD",
        "analizador_lexico.py": "🔍 Analizador léxico",
        
        # Componentes del sistema
        "interpretador_semantico.py": "🎯 Interpretador semántico",
        "motor_recomendaciones.py": "🎲 Motor recomendaciones",
        "corrector_ortografico.py": "✏️ Corrector ortográfico",
        "utilidades.py": "🛠️ Utilidades generales",
        "arquitectura_escalable.py": "🏗️ Arquitectura escalable",
        
        # Configuración
        "main.py": "🚀 Punto de entrada principal",
        "requirements.txt": "📦 Dependencias",
        "README.md": "📋 Documentación",
        "Dockerfile": "🐳 Configuración Docker",
        "docker-compose.yml": "🐙 Docker Compose",
    }
    
    for archivo, descripcion in archivos_esenciales.items():
        archivo_path = base_dir / archivo
        estado = "✅" if archivo_path.exists() else "❌"
        print(f"{estado} {descripcion}: {archivo}")
    
    # Verificar directorio API
    print("\n🔧 DIRECTORIO API:")
    api_dir = base_dir / "api"
    if api_dir.exists():
        api_esenciales = {
            "main_lcln_dynamic.py": "🌐 API FastAPI principal",
            "config.py": "⚙️ Configuración API",
            "productos_lynx_escalable.db": "💾 DB productos (copia)",
            "sinonimos_lynx.db": "📖 DB sinónimos (copia)",
        }
        
        for archivo, descripcion in api_esenciales.items():
            archivo_path = api_dir / archivo
            estado = "✅" if archivo_path.exists() else "❌"
            print(f"  {estado} {descripcion}: api/{archivo}")
    else:
        print("  ❌ Directorio API no encontrado")

if __name__ == "__main__":
    print("🧹 SISTEMA DE LIMPIEZA LCLN")
    print("=" * 60)
    print("Este script eliminará archivos innecesarios del sistema LCLN")
    print("manteniendo solo los archivos esenciales para el funcionamiento.")
    print()
    
    respuesta = input("¿Proceder con la limpieza? (s/n): ").lower().strip()
    
    if respuesta == 's' or respuesta == 'si':
        limpiar_directorio()
        mostrar_estructura_final()
        
        print("\n" + "=" * 60)
        print("🎉 LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("✨ El sistema LCLN ha sido optimizado y limpiado.")
        print("🚀 Solo quedan los archivos esenciales para el funcionamiento.")
        print("📂 La estructura está lista para la nueva estrategia LCLN.")
        
    else:
        print("❌ Limpieza cancelada.")
