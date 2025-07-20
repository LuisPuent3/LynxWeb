#!/usr/bin/env python3
"""
Script para limpiar archivos innecesarios del proyecto LYNX
"""
import os
import shutil
from pathlib import Path

def limpiar_proyecto():
    """Limpia archivos innecesarios"""
    
    archivos_innecesarios = [
        # Archivos de test
        "test_*.py",
        "debug_*.py",
        
        # Mains antiguos
        "main_*.py",
        "api_microservicio.py",
        
        # Archivos de desarrollo
        "explicacion_*.py",
        "diagrama_*.py",
        "generador_*.py",
        "flujo_*.py",
        "migrar_*.py",
        "temp_*.py",
        
        # Documentos de estado
        "ESTADO_PROYECTO.md",
        "README_NUEVO.md",
        "DOCUMENTACION_LYNX_3.0_COMPLETA.md",
        "migracion_info.json",
        
        # Directorios innecesarios
        "backup_original",
        "diagramas_explicativos",
        "diagramas",
        "diagramas_afd"
    ]
    
    base_path = Path(".")
    
    print("🧹 Limpiando archivos innecesarios...")
    
    for patron in archivos_innecesarios:
        if "*" in patron:
            # Usar glob para patrones
            for archivo in base_path.glob(patron):
                if archivo.is_file():
                    print(f"   🗑️  Eliminando archivo: {archivo}")
                    archivo.unlink()
                elif archivo.is_dir():
                    print(f"   📁 Eliminando directorio: {archivo}")
                    shutil.rmtree(archivo)
        else:
            # Archivo o directorio específico
            ruta = base_path / patron
            if ruta.exists():
                if ruta.is_file():
                    print(f"   🗑️  Eliminando archivo: {ruta}")
                    ruta.unlink()
                elif ruta.is_dir():
                    print(f"   📁 Eliminando directorio: {ruta}")
                    shutil.rmtree(ruta)
    
    print("✅ Limpieza completada")
    
    # Mostrar archivos core restantes
    print("\n📋 Archivos core mantenidos:")
    archivos_core = [
        "analizador_lexico.py",
        "utilidades.py", 
        "arquitectura_escalable.py",
        "adaptador_bd.py",
        "adaptador_escalable.py",
        "corrector_ortografico.py",
        "interpretador_semantico.py",
        "motor_recomendaciones.py",
        "configuracion_bd.py",
        "afd_*.py",
        "api/",
        "requirements.txt",
        "Dockerfile",
        "docker-compose-new.yml"
    ]
    
    for archivo in archivos_core:
        if "*" in archivo:
            encontrados = list(base_path.glob(archivo))
            for f in encontrados:
                print(f"   ✅ {f}")
        else:
            ruta = base_path / archivo
            if ruta.exists():
                print(f"   ✅ {ruta}")

if __name__ == "__main__":
    limpiar_proyecto()
