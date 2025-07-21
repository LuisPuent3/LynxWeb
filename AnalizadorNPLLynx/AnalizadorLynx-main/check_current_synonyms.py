#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

def check_current_synonyms():
    """Check current synonyms structure"""
    conn = sqlite3.connect('api/sinonimos_lynx.db')
    cursor = conn.cursor()
    
    print("=== Checking 'sin azucar' related synonyms ===")
    results = cursor.execute('''
        SELECT * FROM sinonimos 
        WHERE termino LIKE "%azucar%" OR termino_normalizado LIKE "%azucar%" 
        OR termino LIKE "%sin%" OR categoria LIKE "%azucar%"
        OR termino LIKE "%light%" OR termino LIKE "%zero%" OR termino LIKE "%diet%"
    ''').fetchall()
    
    for r in results:
        print(f"  {r}")
    
    print("\n=== Checking 'picante' related synonyms ===")
    results = cursor.execute('''
        SELECT * FROM sinonimos 
        WHERE termino LIKE "%picante%" OR termino_normalizado LIKE "%picante%" 
        OR categoria LIKE "%picante%"
    ''').fetchall()
    
    for r in results:
        print(f"  {r}")
    
    print("\n=== Checking 'dulce' related synonyms ===")
    results = cursor.execute('''
        SELECT * FROM sinonimos 
        WHERE termino LIKE "%dulce%" OR termino_normalizado LIKE "%dulce%" 
        OR categoria LIKE "%dulce%"
    ''').fetchall()
    
    for r in results:
        print(f"  {r}")
    
    conn.close()

if __name__ == "__main__":
    check_current_synonyms()
