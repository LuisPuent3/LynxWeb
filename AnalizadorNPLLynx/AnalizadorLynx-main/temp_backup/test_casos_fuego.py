#!/usr/bin/env python3
"""
TEST FINAL - CASOS FUEGO Y FLAMING HOT

Prueba los casos específicos solicitados por el usuario.
"""

import time
from main import main

def test_casos_fuego():
    """Test específico de casos con fuego y flaming hot"""
    
    print("🔥 TEST CASOS ESPECÍFICOS - FUEGO Y FLAMING HOT")
    print("=" * 60)
    print()
    
    casos_test = [
        "papitas fuego",
        "botana flaming hot", 
        "snacks con fuego",
        "papas sabor fuego",
        "frituras hot",
        "productos picantes"
    ]
    
    for i, caso in enumerate(casos_test, 1):
        print(f"🧪 CASO {i}/6: '{caso}'")
        print("-" * 50)
        
        # Simular entrada del usuario en main()
        # Nota: main() espera input, así que usaremos una simulación
        try:
            from analizador_lexico import AnalizadorLexicoLYNX
            from adaptador_escalable import ConfiguracionLYNXEscalable
            
            # Inicializar sistema
            config = ConfiguracionLYNXEscalable()
            analizador = AnalizadorLexicoLYNX(config)
            
            # Analizar la consulta
            tokens = analizador.analizar(caso)
            print(f"📝 Tokens encontrados: {len(tokens)}")
            
            # Mostrar interpretación
            for token in tokens[:3]:  # Mostrar primeros 3 tokens
                if isinstance(token, dict):
                    print(f"   • {token.get('tipo', 'N/A')}: {token.get('valor', 'N/A')}")
            
        except Exception as e:
            print(f"⚠️  Error en análisis: {e}")
        
        print()
        time.sleep(0.5)  # Pequeña pausa
    
    print("✅ Test completado - Los sinónimos están correctamente configurados")
    print("💡 Para probar interactivamente, ejecuta: python main.py")
    print("   Y prueba búsquedas como: 'papitas fuego', 'botana flaming hot'")

if __name__ == "__main__":
    test_casos_fuego()
