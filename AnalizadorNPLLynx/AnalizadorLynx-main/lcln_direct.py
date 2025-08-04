#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script directo para ejecutar tu sistema LCLN original desde Node.js
"""

import sys
import json
from sistema_lcln_simple import SistemaLCLNSimplificado

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Consulta requerida"}))
        sys.exit(1)
    
    consulta = sys.argv[1]
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    try:
        # Usar tu sistema LCLN original
        sistema = SistemaLCLNSimplificado()
        productos = sistema.buscar_productos(consulta, limite)
        
        # Formato de respuesta compatible
        resultado = {
            "success": True,
            "query": consulta,
            "original_query": consulta,
            "products_found": len(productos),
            "user_message": f"LCLN directo: {len(productos)} productos encontrados",
            "message": f"LCLN directo: {len(productos)} productos encontrados",
            "recommendations": productos,
            "products": productos,  # Campo adicional para compatibilidad frontend
            "interpretation": {},
            "metadata": {
                "sistema": "LCLN Original Directo",
                "analizador_lexico": True,
                "analisis_contextual": True,
                "bnf_grammar": True,
                "semantic_categorization": True
            },
            "processing_time_ms": 0
        }
        
        print(json.dumps(resultado))
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "success": False,
            "consulta": consulta
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    main()
