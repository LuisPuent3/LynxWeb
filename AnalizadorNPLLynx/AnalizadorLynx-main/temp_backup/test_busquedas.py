#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rápido para probar búsquedas específicas
"""

from adaptador_escalable import SimuladorBDLynxShopEscalable
from analizador_lexico import AnalizadorLexicoLYNX

def main():
    print("🧪 TEST RÁPIDO DE BÚSQUEDAS")
    print("="*50)
    
    # Inicializar sistema escalable
    try:
        simulador = SimuladorBDLynxShopEscalable(usar_escalable=True)
        stats = simulador.obtener_estadisticas()
        print(f"✅ Sistema escalable cargado: {stats.get('total_productos', 'N/A')} productos")
        print(f"📊 Estadísticas completas: {stats}")
        
        # Crear configuración usando el sistema escalable
        from adaptador_escalable import ConfiguracionLYNXEscalable
        configuracion = ConfiguracionLYNXEscalable()
        analizador = AnalizadorLexicoLYNX(configuracion)
        
        # Probar búsquedas específicas
        consultas = [
            "paleta dulce",
            "bebidas sin azucar", 
            "productos picantes barato",
            "chocolate",
            "coca cola"
        ]
        
        for consulta in consultas:
            print(f"\n🔍 PROBANDO: '{consulta}'")
            print("-" * 40)
            
            try:
                resultado = analizador.generar_json_resultado_completo(consulta)
                
                # Parsear el JSON result
                import json
                data = json.loads(resultado)
                
                print(f"✅ Consulta procesada")
                print(f"📊 Interpretación: {data.get('interpretation', {})}")
                
                recomendaciones = data.get('recommendations', [])
                print(f"🛍️  {len(recomendaciones)} recomendaciones:")
                
                for i, rec in enumerate(recomendaciones[:3], 1):
                    print(f"   {i}. {rec.get('name', 'N/A')} - ${rec.get('price', 'N/A')} ({rec.get('category', 'N/A')})")
                    print(f"      Score: {rec.get('match_score', 'N/A')}, Razones: {rec.get('match_reasons', [])}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
