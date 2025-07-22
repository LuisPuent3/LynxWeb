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
        ('botanas', 'Snacks', 'categoria', 0.9),
        ('dulces', 'Golosinas', 'categoria', 0.9),
        
        # Productos específicos
        ('coca', 'coca cola', 'producto', 0.9),
        ('coca-cola', 'coca cola', 'producto', 1.0),
        ('doritos', 'doritos dinamita', 'producto', 0.9),
        ('cheetos', 'cheetos mix', 'producto', 0.9),
        ('chetoos', 'cheetos mix', 'producto', 0.8),  # Error común
        ('crujitos', 'crujitos fuego', 'producto', 0.9),
          # *** ATRIBUTOS CRÍTICOS - Sin azúcar ***
        ('sin azucar', 'sin azucar', 'atributo', 1.0),
        ('sin azúcar', 'sin azucar', 'atributo', 1.0),
        ('light', 'sin azucar', 'atributo', 0.9),
        ('zero', 'sin azucar', 'atributo', 0.9),
        ('diet', 'sin azucar', 'atributo', 0.9),
        ('sin', 'sin azucar', 'atributo', 0.7),  # Para "bebidas sin..."
        
        # *** PRODUCTOS ESPECÍFICOS GOLOSINAS ***
        ('panditas', 'gomitas panditas', 'producto', 1.0),
        ('gomitas', 'gomitas panditas', 'producto', 0.9),
        ('ositos', 'gomitas panditas', 'producto', 0.8),
        ('gomas', 'gomitas panditas', 'producto', 0.8),
        ('dulcigomas', 'dulcigomas', 'producto', 1.0),
        ('emperador', 'emperador senzo', 'producto', 0.9),
        ('senzo', 'emperador senzo', 'producto', 0.9),
        
        # Atributos de sabor - Picante
        ('picante', 'picante', 'atributo', 1.0),
        ('picantes', 'picante', 'atributo', 1.0),
        ('fuego', 'picante', 'atributo', 0.9),
        ('hot', 'picante', 'atributo', 0.9),
        ('chile', 'picante', 'atributo', 0.8),
        ('adobadas', 'picante', 'atributo', 0.8),
        ('flamin', 'picante', 'atributo', 0.9),
        ('dinamita', 'picante', 'atributo', 0.9),
        
        # Atributos de sabor - Dulce/No picante
        ('dulce', 'dulce', 'atributo', 1.0),
        ('dulces', 'dulce', 'atributo', 1.0),
        ('suave', 'dulce', 'atributo', 0.7),
        ('sin picante', 'dulce', 'atributo', 0.8),
        ('no picante', 'dulce', 'atributo', 0.8),
        
        # Filtros de precio
        ('barato', 'barato', 'atributo', 1.0),
        ('baratas', 'barato', 'atributo', 1.0),
        ('economico', 'barato', 'atributo', 1.0),
        ('caro', 'caro', 'atributo', 1.0),
        ('picantes', 'picante', 'atributo', 1.0),
        ('fuego', 'picante', 'atributo', 0.9),
        ('hot', 'picante', 'atributo', 0.9),
        ('chile', 'picante', 'atributo', 0.8),
        ('adobadas', 'picante', 'atributo', 0.8),
        ('flamin', 'picante', 'atributo', 0.9),
        ('dinamita', 'picante', 'atributo', 0.9),
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
    
    # Mostrar sinónimos de 'snack' y 'picante' para verificación
    print("\n🔎 Sinónimos actuales de 'snack':")
    cursor.execute("SELECT termino, categoria, tipo, confianza FROM sinonimos WHERE termino LIKE '%snack%' AND activo = 1")
    for row in cursor.fetchall():
        print(f"  - {row}")
    print("\n🔎 Sinónimos actuales de 'picante':")
    cursor.execute("SELECT termino, categoria, tipo, confianza FROM sinonimos WHERE termino LIKE '%picante%' AND activo = 1")
    for row in cursor.fetchall():
        print(f"  - {row}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_y_corregir_sinonimos()
