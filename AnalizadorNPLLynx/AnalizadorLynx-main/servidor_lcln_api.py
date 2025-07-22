#!/usr/bin/env python3
"""
Servidor FastAPI para Sistema LCLN - Integración con Frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from sistema_lcln_simple import SistemaLCLNSimplificado
from sistema_lcln_mejorado import sistema_lcln_mejorado

# Inicializar sistema LCLN original (el que ya funcionaba)
sistema_lcln = SistemaLCLNSimplificado()

# Sistema mejorado como PLUS opcional (solo para análisis adicional)
sistema_lcln_plus = sistema_lcln_mejorado

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Inicializando Sistema LCLN API...")
    try:
        # El sistema se inicializa automáticamente en la primera búsqueda
        print("Sistema LCLN API listo")
    except Exception as e:
        print(f"Error inicializando: {e}")
    
    yield
    
    # Shutdown
    print("Cerrando Sistema LCLN API...")

# Inicializar FastAPI
app = FastAPI(
    title="LYNX Sistema LCLN API",
    description="API para búsqueda inteligente de productos + análisis léxico formal como PLUS opcional",
    version="2.1.0-plus",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Inicializar sistema LCLN (movido arriba)
# sistema_lcln = SistemaLCLNSimplificado()

# Modelos Pydantic
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20

class SearchResponse(BaseModel):
    success: bool
    processing_time_ms: float
    original_query: str
    products_found: int
    user_message: str
    recommendations: List[Dict[str, Any]]
    interpretation: Dict[str, Any]
    corrections: Dict[str, Any]
    metadata: Dict[str, Any]

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "LYNX Sistema LCLN API",
        "version": "2.1.0-plus",
        "status": "active",
        "sistema_principal": "Sistema LCLN original que ya funcionaba perfectamente",
        "plus_agregado": {
            "analisis_lexico_formal": "AFD + BNF + RD1-RD4 como información adicional",
            "nota": "El PLUS no afecta el funcionamiento principal"
        },
        "endpoints": {
            "search": "/search (sistema principal - compatible con frontend)",
            "analisis_lexico_plus": "/analisis-lexico-plus?query=... (PLUS opcional)",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check para verificar que el sistema está funcionando"""
    try:
        # Verificar que el sistema puede acceder a la base de datos
        sistema_lcln._actualizar_cache_dinamico()
        
        return {
            "status": "healthy",
            "system": "lcln_original_plus",
            "version": "2.1.0-plus",
            "database": "mysql_connected",
            "cache_products": len(sistema_lcln._cache_productos),
            "cache_synonyms": len(sistema_lcln._cache_sinonimos),
            "timestamp": sistema_lcln._cache_timestamp.isoformat() if sistema_lcln._cache_timestamp else None,
            "sistema_principal": "funcionando_perfectamente",
            "plus_opcional": {
                "analisis_lexico_disponible": True,
                "modo_activo": sistema_lcln_plus.modo_analisis_formal
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "system": "lcln"
            }
        )

@app.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Búsqueda inteligente de productos usando sistema LCLN
    """
    try:
        if not request.query or request.query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Query parameter is required and cannot be empty"
            )

        print(f"[API] Procesando consulta: '{request.query}'")
        
        # Ejecutar búsqueda usando el sistema LCLN ORIGINAL que ya funcionaba
        resultado = sistema_lcln.buscar_productos_inteligente(
            request.query,
            request.limit
        )
        
        # ➕ PLUS OPCIONAL: Agregar análisis léxico formal como información adicional
        try:
            resultado_plus = sistema_lcln_plus.obtener_analisis_completo_formal(request.query)
            # Agregar datos del analizador léxico como metadatos adicionales
            resultado['metadata']['analisis_lexico_plus'] = {
                'conformidad_lcln': resultado_plus['resumen_ejecutivo']['conformidad_lcln'],
                'tokens_formales': resultado_plus['resumen_ejecutivo']['tokens_formales_count'],
                'precision_tokens': resultado_plus.get('fase_afd_lexico', {}).get('estadisticas', {}).get('precision_reconocimiento', 0)
            }
        except Exception as e:
            # Si falla el análisis plus, no afecta la funcionalidad principal
            resultado['metadata']['analisis_lexico_plus'] = {'error': str(e)}
        
        print(f"[API] Búsqueda completada: {resultado['products_found']} productos en {resultado['processing_time_ms']:.1f}ms")
        
        return SearchResponse(
            success=resultado['success'],
            processing_time_ms=resultado['processing_time_ms'],
            original_query=resultado['original_query'],
            products_found=resultado['products_found'],
            user_message=resultado['user_message'],
            recommendations=resultado['recommendations'],
            interpretation=resultado['interpretation'],
            corrections=resultado['corrections'],
            metadata=resultado['metadata']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error en búsqueda: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "system": "lcln"
            }
        )

@app.get("/analisis-lexico-plus")
async def analisis_lexico_plus(query: str):
    """
    ➕ ENDPOINT PLUS - Solo análisis léxico formal adicional
    NO interfiere con el sistema principal que ya funciona
    """
    try:
        if not query or query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Query parameter is required"
            )

        print(f"[PLUS] Analizando léxicamente: '{query}'")
        
        # Solo el análisis léxico formal, sin afectar el sistema principal
        resultado_plus = sistema_lcln_plus.obtener_analisis_completo_formal(query)
        
        return {
            "success": True,
            "query": query,
            "analisis_lexico": {
                "conformidad_lcln": resultado_plus['resumen_ejecutivo']['conformidad_lcln'],
                "tokens_formales_count": resultado_plus['resumen_ejecutivo']['tokens_formales_count'],
                "afd_lexico": resultado_plus.get('fase_afd_lexico', {}),
                "analisis_sintactico": resultado_plus.get('fase_analisis_sintactico', {}),
                "validacion_gramatical": resultado_plus.get('validacion_gramatical', {})
            },
            "nota": "Este es un análisis PLUS que no afecta el sistema principal"
        }
        
    except Exception as e:
        print(f"[PLUS] Error en análisis léxico plus: {e}")
        return {
            "success": False,
            "error": str(e),
            "nota": "Error en análisis PLUS - el sistema principal sigue funcionando normal"
        }

@app.get("/toggle-plus/{mode}")
async def toggle_plus_analysis(mode: bool):
    """Activar/desactivar el análisis PLUS (no afecta sistema principal)"""
    try:
        sistema_lcln_plus.modo_analisis_formal = mode
        return {
            "success": True,
            "modo_plus": sistema_lcln_plus.modo_analisis_formal,
            "mensaje": f"Análisis PLUS {'activado' if mode else 'desactivado'}",
            "nota": "Esto no afecta el funcionamiento del sistema principal"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/cache-stats")
async def cache_statistics():
    """Obtener estadísticas del cache"""
    try:
        sistema_lcln._actualizar_cache_dinamico()
        
        return {
            "cache_timestamp": sistema_lcln._cache_timestamp.isoformat() if sistema_lcln._cache_timestamp else None,
            "products_count": len(sistema_lcln._cache_productos),
            "categories_count": len(sistema_lcln._cache_categorias),
            "synonyms_count": len(sistema_lcln._cache_sinonimos),
            "cache_duration_minutes": sistema_lcln._cache_duration.total_seconds() / 60,
            "categories": list(sistema_lcln._cache_categorias.keys()),
            "sample_products": list(sistema_lcln._cache_productos.keys())[:5]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )

if __name__ == "__main__":
    print("=== INICIANDO SERVIDOR LCLN API (Sistema Original + PLUS) ===")
    print("Puerto: 8004")
    print("")
    print("✅ SISTEMA PRINCIPAL: El que ya funcionaba perfectamente")
    print("  - Endpoint: POST /search")
    print("  - Compatible 100% con tu frontend")
    print("  - Misma funcionalidad de siempre")
    print("")
    print("➕ PLUS AGREGADO: Análisis léxico formal")
    print("  - Endpoint: GET /analisis-lexico-plus?query=...")
    print("  - AFD + Análisis sintáctico + Validación")
    print("  - NO interfiere con el sistema principal")
    print("")
    print(f"PLUS activo: {'SÍ' if sistema_lcln_plus.modo_analisis_formal else 'NO'}")
    print("===========================================================")
    
    uvicorn.run(
        "servidor_lcln_api:app",
        host="127.0.0.1",
        port=8004,
        reload=False,
        log_level="info"
    )
