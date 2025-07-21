#!/usr/bin/env python3
"""
API LYNX NLP Híbrido - FastAPI
- Productos reales de MySQL LynxShop (comprables)
- Sinónimos y configuraciones de SQLite (análisis NLP)
"""

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from datetime import datetime
from configurador_hibrido import ConfiguradorHibridoLYNX

# Inicializar FastAPI
app = FastAPI(
    title="LYNX Hybrid NLP API",
    description="NLP con productos reales MySQL + sinónimos SQLite",
    version="5.0.0-hybrid",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class QueryRequest(BaseModel):
    query: str

# Instancia del configurador híbrido
configurador = ConfiguradorHibridoLYNX()

@app.get("/")
def root():
    return {
        "message": "LYNX Hybrid NLP API",
        "version": "5.0.0-hybrid",
        "products_source": "mysql_lynxshop_real_purchasable",
        "nlp_source": "sqlite_synonyms_and_configs",
        "status": "active"
    }

@app.get("/api/health")
def health_check():
    """Health check con estadísticas híbridas"""
    try:
        stats = configurador.obtener_estadisticas()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "5.0.0-hybrid",
            "components": {
                "database": "hybrid_mysql_sqlite",
                "products": f"{stats['productos_reales_mysql']} productos comprables (MySQL)",
                "categories": f"{stats['categorias_mysql']} categorías reales (MySQL)",
                "synonyms": f"{stats['sinonimos_nlp_sqlite']} sinónimos NLP (SQLite)",
                "mode": stats['modo']
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/api/nlp/analyze")
def analyze_hybrid_nlp(request: QueryRequest):
    """
    Análisis NLP híbrido:
    - Sinónimos y análisis: SQLite
    - Productos reales: MySQL (comprables en el flujo normal)
    """
    try:
        # Usar el configurador híbrido
        resultado = configurador.buscar_productos_hibrido(
            consulta=request.query,
            limit=20
        )
        
        if not resultado['success']:
            raise HTTPException(status_code=500, detail="Error en búsqueda híbrida")
        
        # Preparar respuesta en formato esperado por el frontend
        return {
            "success": True,
            "processing_time_ms": resultado['processing_time_ms'],
            "original_query": request.query,
            
            # Información del análisis
            "corrections": {"applied": False},
            "interpretation": {
                "type": "hybrid_mysql_sqlite_search",
                "termino_busqueda": resultado['analysis']['termino_busqueda'],
                "categoria": resultado['analysis']['categoria'],
                "precio_max": resultado['analysis']['precio_max'],
                "precio_min": resultado['analysis']['precio_min'],
                "sinonimos_usados": resultado['analysis']['sinonimos_encontrados']
            },
            
            # Consulta SQL (informativa)
            "sql_query": "MySQL: productos JOIN categorias + SQLite: sinonimos",
            
            # Productos REALES y COMPRABLES
            "recommendations": resultado['products'],
            
            # Mensaje para el usuario
            "user_message": resultado['user_message'],
            
            # Metadatos
            "metadata": {
                "products_found": resultado['products_found'],
                "has_corrections": False,
                "source": "hybrid_mysql_sqlite",
                "productos_comprables": True,  # IMPORTANTE: estos productos SÍ se pueden comprar
                "database_real": True
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "processing_time_ms": 0,
            "original_query": request.query,
            "error": str(e),
            "recommendations": [],
            "user_message": "Error procesando consulta",
            "metadata": {"error": True}
        }

@app.get("/api/stats")
def get_stats():
    """Obtener estadísticas del sistema híbrido"""
    return configurador.obtener_estadisticas()

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando LYNX Hybrid NLP API...")
    print("📦 Productos: MySQL LynxShop (comprables)")
    print("🔍 Sinónimos: SQLite (análisis NLP)")
    uvicorn.run(app, host="0.0.0.0", port=8003)
