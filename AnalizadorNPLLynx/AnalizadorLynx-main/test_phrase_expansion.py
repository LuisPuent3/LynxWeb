#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sistema_lcln_mejorado_limpio import sistema_lcln_mejorado
import json

def test_phrase_expansion():
    """Test how phrase expansion works for compound terms"""
    sistema = sistema_lcln_mejorado
    
    # Force cache initialization first
    print("🔄 Initializing cache...")
    sistema._actualizar_cache_dinamico()
    
    # Test direct lookup of "sin picante" in cache
    cache_key = "sin picante"
    print(f"Looking for '{cache_key}' in synonym cache...")
    
    if hasattr(sistema, '_cache_sinonimos') and cache_key in sistema._cache_sinonimos:
        print(f"✅ Found in cache: {sistema._cache_sinonimos[cache_key]}")
    else:
        print("❌ Not found in cache. Checking cache keys...")
        if hasattr(sistema, '_cache_sinonimos'):
            matching_keys = [k for k in sistema._cache_sinonimos.keys() if 'sin' in k and 'picante' in k]
            print(f"Matching keys: {matching_keys}")
        else:
            print("Cache not initialized")
      # Test the expansion phase specifically
    print("\nTesting _fase_expansion_sinonimos for 'snack sin picante'...")
    try:
        expansion = sistema._fase_expansion_sinonimos("snack sin picante")
        print(f"Expansion result: {json.dumps(expansion, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error in expansion: {e}")

if __name__ == "__main__":
    test_phrase_expansion()
