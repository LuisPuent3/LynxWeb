#!/usr/bin/env python3
"""
FastAPI Microservice for LYNX Natural Language Processing
Sistema LCLN (Lenguaje de Consulta en Lenguaje Natural) v3.0
"""

import sys
import os
from pathlib import Path

# Agregar el directorio padre al path para importar módulos LYNX
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import time
import json
import logging
from datetime import datetime

# Importar módulos LYNX
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="LYNX LCLN Microservice",
    description="Sistema de Procesamiento de Lenguaje Natural para búsquedas de productos",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class QueryRequest(BaseModel):
    query: str = Field(..., description="Consulta en lenguaje natural", example="bebidas sin azucar baratas")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Opciones adicionales")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto del usuario")

class QueryOptions(BaseModel):
    enable_correction: bool = Field(True, description="Habilitar corrección ortográfica")
    enable_recommendations: bool = Field(True, description="Habilitar recomendaciones")
    max_recommendations: int = Field(10, description="Número máximo de recomendaciones")
    enable_sql_generation: bool = Field(True, description="Generar consulta SQL")

class CorrectionInfo(BaseModel):
    applied: bool
    changes: List[Dict[str, Any]]
    corrected_query: str
    confidence_average: float

class Interpretation(BaseModel):
    type: str
    producto: Optional[str]
    categoria: Optional[str]
    atributos: List[str]
    filtros: Dict[str, Any]

class ProductRecommendation(BaseModel):
    name: str
    category: str
    price: float
    match_score: float
    match_reasons: List[str]
    available: bool

class QueryResponse(BaseModel):
    success: bool
    processing_time_ms: float
    original_query: str
    corrections: Optional[CorrectionInfo]
    interpretation: Interpretation
    sql_query: Optional[str]
    recommendations: List[ProductRecommendation]
    user_message: str
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

class StatsResponse(BaseModel):
    total_products: int
    total_synonyms: int
    categories: List[str]
    system_uptime: float
    last_query_time: Optional[str]

# Variables globales del sistema
sistema_inicializado = False
configuracion = None
analizador = None
inicio_sistema = time.time()
ultima_consulta = None

@app.on_event("startup")
async def startup_event():
    """Inicializar sistema al arrancar"""
    global sistema_inicializado, configuracion, analizador
    
    try:
        logger.info("🚀 Inicializando LYNX LCLN Microservice...")
        
        configuracion = ConfiguracionLYNX()
        analizador = AnalizadorLexicoLYNX(configuracion)
        
        sistema_inicializado = True
        logger.info("✅ Sistema LYNX inicializado correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando sistema: {e}")
        sistema_inicializado = False

@app.get("/", response_class=JSONResponse)
async def root():
    """Endpoint raíz con información básica"""
    return {
        "service": "LYNX LCLN Microservice",
        "version": "3.0.0",
        "status": "running" if sistema_inicializado else "initializing",
        "endpoints": {
            "health": "/api/health",
            "analyze": "/api/nlp/analyze",
            "stats": "/api/stats",
            "docs": "/api/docs"
        }
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check del microservicio"""
    components = {}
    
    try:
        if configuracion:
            stats = configuracion.obtener_estadisticas()
            components["database"] = "healthy"
            components["products"] = f"{stats['productos']['total']} loaded"
            components["synonyms"] = f"{stats.get('sinonimos', {}).get('total', 0)} loaded"
        else:
            components["database"] = "not_initialized"
            
        if analizador:
            components["nlp_engine"] = "healthy"
        else:
            components["nlp_engine"] = "not_initialized"
            
    except Exception as e:
        components["error"] = str(e)
    
    status = "healthy" if sistema_inicializado else "unhealthy"
    
    return HealthResponse(
        status=status,
        timestamp=datetime.now().isoformat(),
        version="3.0.0",
        components=components
    )

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Estadísticas del sistema"""
    if not sistema_inicializado:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    try:
        stats = configuracion.obtener_estadisticas()
        
        return StatsResponse(
            total_products=stats['productos']['total'],
            total_synonyms=stats.get('sinonimos', {}).get('total', 0),
            categories=list(configuracion.base_datos.get('categorias', [])),
            system_uptime=time.time() - inicio_sistema,
            last_query_time=ultima_consulta
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/api/nlp/analyze", response_model=QueryResponse)
async def analyze_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Endpoint principal para análisis de consultas en lenguaje natural
    """
    global ultima_consulta
    
    if not sistema_inicializado:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    start_time = time.time()
    ultima_consulta = datetime.now().isoformat()
    
    try:
        # Procesar consulta
        resultado_json = analizador.generar_json_resultado_completo(request.query)
        resultado = json.loads(resultado_json)
        
        # Extraer información
        interpretacion = resultado.get('interpretation', {})
        recomendaciones = resultado.get('recommendations', [])
        correcciones_raw = resultado.get('corrections', {})
        sql_query = resultado.get('sql_query', '')
        user_message = resultado.get('user_message', '')
        
        # Formatear correcciones
        corrections = None
        if correcciones_raw.get('applied', False):
            corrections = CorrectionInfo(
                applied=True,
                changes=correcciones_raw.get('changes', []),
                corrected_query=correcciones_raw.get('corrected_query', request.query),
                confidence_average=correcciones_raw.get('confidence_average', 0.0)
            )
        
        # Formatear interpretación
        interpretation = Interpretation(
            type="product_search",  # Tipo por defecto
            producto=interpretacion.get('producto'),
            categoria=interpretacion.get('categoria'),
            atributos=interpretacion.get('atributos', []),
            filtros=interpretacion.get('filtros', {})
        )
        
        # Formatear recomendaciones
        recommendations = []
        for rec in recomendaciones:
            recommendations.append(ProductRecommendation(
                name=rec.get('name', ''),
                category=rec.get('category', ''),
                price=rec.get('price', 0.0),
                match_score=rec.get('match_score', 0.0),
                match_reasons=rec.get('match_reasons', []),
                available=rec.get('available', True)
            ))
        
        processing_time = (time.time() - start_time) * 1000
        
        # Crear respuesta
        response = QueryResponse(
            success=True,
            processing_time_ms=processing_time,
            original_query=request.query,
            corrections=corrections,
            interpretation=interpretation,
            sql_query=sql_query if request.options.get('enable_sql_generation', True) else None,
            recommendations=recommendations,
            user_message=user_message,
            metadata={
                "products_found": len(recommendations),
                "has_corrections": corrections is not None,
                "context": request.context
            }
        )
        
        # Log de la consulta (background task)
        background_tasks.add_task(log_query, request.query, processing_time, len(recommendations))
        
        return response
        
    except Exception as e:
        logger.error(f"Error procesando consulta '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

@app.post("/api/nlp/batch")
async def analyze_batch(queries: List[str]):
    """Procesar múltiples consultas en batch"""
    if not sistema_inicializado:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    results = []
    for query in queries[:10]:  # Límite de 10 consultas por batch
        try:
            request = QueryRequest(query=query)
            result = await analyze_query(request, BackgroundTasks())
            results.append(result)
        except Exception as e:
            results.append({"query": query, "error": str(e), "success": False})
    
    return {"results": results, "processed": len(results)}

def log_query(query: str, processing_time: float, results_count: int):
    """Background task para logging de consultas"""
    logger.info(f"Query processed: '{query}' | {processing_time:.1f}ms | {results_count} results")

# Endpoint para desarrollo/debug (solo en dev)
@app.get("/api/debug/products")
async def debug_products():
    """Endpoint de debug para listar productos (solo desarrollo)"""
    if not sistema_inicializado:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    try:
        stats = configuracion.obtener_estadisticas()
        productos_muestra = configuracion.base_datos.get('productos_completos', [])[:10]
        
        return {
            "total_products": stats['productos']['total'],
            "sample_products": productos_muestra,
            "categories": list(configuracion.base_datos.get('categorias', []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
