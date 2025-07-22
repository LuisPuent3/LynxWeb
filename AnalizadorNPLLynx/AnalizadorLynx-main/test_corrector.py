#!/usr/bin/env python3
"""
Test script for the corrector
"""
from corrector_ortografico import CorrectorOrtografico

corrector = CorrectorOrtografico()

print("🔍 Testing critical case: 'votana barata picabte menor a 20'")
resultado = corrector.corregir_consulta("votana barata picabte menor a 20")

print(f"Applied: {resultado['applied']}")
print(f"Changes: {resultado['changes']}")
print(f"Corrected query: {resultado['corrected_query']}")

print("\n🧪 Testing individual words:")
words = ["votana", "picabte", "barata"]
for word in words:
    corrected, conf = corrector.corregir_palabra(word)
    print(f"  {word} -> {corrected} (confidence: {conf})")
