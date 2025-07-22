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

# Inicializar sistema LCLN
sistema_lcln = SistemaLCLNSimplificado()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Inicializando Sistema LCLN API...")
    try:
        # El sistema se inicializa automáticamente en la primera búsqueda
        print("✅ Sistema LCLN API listo")
    except Exception as e:
        print(f"❌ Error inicializando: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando Sistema LCLN API...")

# Inicializar FastAPI
app = FastAPI(
    title="LYNX Sistema LCLN API",
    description="API para búsqueda inteligente de productos usando análisis semántico",
    version="2.0.0",
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
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "search": "/search",
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
            "system": "lcln",
            "version": "2.0.0",
            "database": "mysql_connected",
            "cache_products": len(sistema_lcln._cache_productos),
            "cache_synonyms": len(sistema_lcln._cache_sinonimos),
            "timestamp": sistema_lcln._cache_timestamp.isoformat() if sistema_lcln._cache_timestamp else None
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

        print(f"🔍 [API] Procesando consulta: '{request.query}'")
        
        # Ejecutar búsqueda usando el sistema LCLN
        resultado = sistema_lcln.buscar_productos_inteligente(
            request.query,
            request.limit
        )
        
        print(f"✅ [API] Búsqueda completada: {resultado['products_found']} productos en {resultado['processing_time_ms']:.1f}ms")
        
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
        print(f"❌ [API] Error en búsqueda: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "system": "lcln"
            }
        )

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
    print("🌟 Iniciando Servidor LCLN API en puerto 8004...")
    uvicorn.run(
        "servidor_lcln_api:app",
        host="127.0.0.1",
        port=8004,
        reload=False,
        log_level="info"
    )
