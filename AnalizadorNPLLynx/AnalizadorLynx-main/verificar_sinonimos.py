#!/usr/bin/env python3
"""
Verificador y corrector de sinónimos LYNX
"""

import sqlite3
from pathlib import Path

def verificar_y_corregir_sinonimos():
    db_path = Path("api/sinonimos_lynx.db")
    if not db_path.exists():
        print("❌ No se encontró la base de datos de sinónimos")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 Verificando sinónimos actuales...")
    
    # Ver todos los sinónimos
    cursor.execute("SELECT termino, categoria, tipo, confianza FROM sinonimos WHERE activo = 1")
    sinonimos = cursor.fetchall()
    
    print(f"📊 Total sinónimos activos: {len(sinonimos)}")
    
    # Agrupar por tipo
    por_tipo = {}
    for termino, categoria, tipo, confianza in sinonimos:
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append((termino, categoria, confianza))
    
    for tipo, items in por_tipo.items():
        print(f"\n{tipo.upper()}:")
        for termino, categoria, confianza in items[:5]:
            print(f"  - {termino} → {categoria} (confianza: {confianza})")
        if len(items) > 5:
            print(f"  ... y {len(items) - 5} más")
    
    # Verificar problema específico de "snacks"
    print(f"\n🔍 Verificando mapeo de 'snacks':")
    cursor.execute("SELECT * FROM sinonimos WHERE termino LIKE '%snack%'")
    snacks_results = cursor.fetchall()
    for result in snacks_results:
        print(f"  - {result}")
    
    # Agregar sinónimos mejorados si es necesario
    print(f"\n🔧 Agregando sinónimos mejorados...")
    
    nuevos_sinonimos = [
        # Categorías específicas
        ('snacks', 'Snacks', 'categoria', 1.0),
        ('golosinas', 'Golosinas', 'categoria', 1.0),
        ('bebidas', 'Bebidas', 'categoria', 1.0),
        ('frutas', 'Frutas', 'categoria', 1.0),
        ('papeleria', 'Papelería', 'categoria', 1.0),
        
        # Productos específicos
        ('coca', 'coca cola', 'producto', 0.9),
        ('coca-cola', 'coca cola', 'producto', 1.0),
        ('doritos', 'doritos dinamita', 'producto', 0.9),
        ('cheetos', 'cheetos mix', 'producto', 0.9),
        
        # Filtros de precio
        ('barato', '', 'filtro_precio', 1.0),
        ('baratas', '', 'filtro_precio', 1.0),
        ('economico', '', 'filtro_precio', 1.0),
        ('caro', '', 'filtro_precio', 1.0),
    ]
      for termino, categoria, tipo, confianza in nuevos_sinonimos:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO sinonimos 
                (termino, termino_normalizado, producto_id, categoria, tipo, confianza, activo) 
                VALUES (?, ?, 0, ?, ?, ?, 1)
            """, (termino, termino.lower(), categoria, tipo, confianza))
            print(f"✅ Agregado: {termino} → {categoria} ({tipo})")
        except Exception as e:
            print(f"❌ Error insertando {termino}: {e}")
    
    conn.commit()
    
    # Verificar después de los cambios
    cursor.execute("SELECT COUNT(*) FROM sinonimos WHERE activo = 1")
    total_final = cursor.fetchone()[0]
    print(f"✅ Total sinónimos después de actualización: {total_final}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_y_corregir_sinonimos()
