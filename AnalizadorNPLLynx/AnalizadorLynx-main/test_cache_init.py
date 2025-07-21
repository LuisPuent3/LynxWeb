#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_mejorado_limpio import sistema_lcln_mejorado
import sqlite3

def test_cache_initialization():
    """Test if the cache is being initialized correctly"""
    sistema = sistema_lcln_mejorado
    
    # Force cache update
    print("🔄 Forcing cache update...")
    sistema._actualizar_cache_dinamico()
    
    # Check if cache has compound terms
    print("\n🔍 Checking cache for compound terms...")
    compound_terms = []
    if hasattr(sistema, '_cache_sinonimos'):
        for key in sistema._cache_sinonimos.keys():
            if ' ' in key:  # Contains space (compound term)
                compound_terms.append(key)
    
    print(f"Found {len(compound_terms)} compound terms in cache:")
    for term in compound_terms[:10]:  # Show first 10
        print(f"  - '{term}': {sistema._cache_sinonimos[term]}")
    
    # Specifically check for sin picante
    if 'sin picante' in sistema._cache_sinonimos:
        print(f"\n✅ 'sin picante' found: {sistema._cache_sinonimos['sin picante']}")
    else:
        print("\n❌ 'sin picante' not found in cache")
        
        # Check the database directly
        print("\n🔍 Checking database directly...")
        conn = sqlite3.connect('api/sinonimos_lynx.db')
        cursor = conn.cursor()
        
        results = cursor.execute('''
            SELECT termino, categoria, tipo, confianza, activo
            FROM sinonimos 
            WHERE termino = 'sin picante' AND activo = 1
        ''').fetchall()
        
        print(f"Database results for 'sin picante': {results}")
        conn.close()

if __name__ == "__main__":
    test_cache_initialization()
