#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

def check_synonyms():
    conn = sqlite3.connect('api/sinonimos_lynx.db')
    cursor = conn.cursor()
    
    # Buscar sinónimos relacionados con "sin picante" y "dulce"
    results = cursor.execute('''
        SELECT * FROM sinonimos 
        WHERE origen LIKE "%sin picante%" OR destino LIKE "%sin picante%" 
        OR origen LIKE "%dulce%" OR destino LIKE "%dulce%"
        OR origen LIKE "%no picante%" OR destino LIKE "%no picante%"
    ''').fetchall()
    
    print("Synonyms related to sin picante/dulce:")
    for r in results:
        print(f"  {r}")
    
    conn.close()

if __name__ == "__main__":
    check_synonyms()
