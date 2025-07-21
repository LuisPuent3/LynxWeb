#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

def add_missing_synonyms():
    """Add missing synonyms for negation handling"""
    conn = sqlite3.connect('api/sinonimos_lynx.db')
    cursor = conn.cursor()
    
    # Define the missing synonyms for negation
    nuevos_sinonimos = [
        ('sin picante', 'dulce', 'atributo', 0.9),
        ('no picante', 'dulce', 'atributo', 0.8),
        ('sin chile', 'dulce', 'atributo', 0.8),
        ('no chile', 'dulce', 'atributo', 0.8),
    ]
    
    print("Adding missing synonyms for negation handling...")
    for origen, destino, tipo, confianza in nuevos_sinonimos:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO sinonimos (origen, destino, tipo, confianza, activo)
                VALUES (?, ?, ?, ?, 1)
            ''', (origen, destino, tipo, confianza))
            print(f"  ✅ Added: '{origen}' → '{destino}' ({tipo}, {confianza})")
        except Exception as e:
            print(f"  ❌ Error adding '{origen}': {e}")
    
    conn.commit()
    
    # Verificar que se agregaron
    print("\nVerifying added synonyms:")
    results = cursor.execute('''
        SELECT * FROM sinonimos 
        WHERE origen LIKE "%sin picante%" OR destino LIKE "%dulce%" 
        OR origen LIKE "%no picante%"
        AND activo = 1
    ''').fetchall()
    
    for r in results:
        print(f"  {r}")
    
    total_count = cursor.execute('SELECT COUNT(*) FROM sinonimos WHERE activo = 1').fetchone()[0]
    print(f"\nTotal active synonyms: {total_count}")
    
    conn.close()

if __name__ == "__main__":
    add_missing_synonyms()
