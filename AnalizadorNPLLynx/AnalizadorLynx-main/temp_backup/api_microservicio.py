# api_microservicio.py
"""
API REST para el microservicio LCLN (Lenguaje de Consulta en Lenguaje Natural)
Sistema de análisis léxico inteligente para LYNX
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import time
import json
from datetime import datetime

# Importar componentes del sistema
from utilidades import ConfiguracionLYNX
from analizador_lexico import AnalizadorLexicoLYNX

# Modelos Pydantic para la API
class QueryRequest(BaseModel):
    """Modelo de request para análisis de consulta"""
    query: str = Field(..., description="Consulta en lenguaje natural")
    options: Optional[Dict[str, Any]] = Field(
        default={
            "enable_correction": True,
            "enable_recommendations": True,
            "max_recommendations": 5
        },
        description="Opciones de procesamiento"
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Contexto adicional (user_id, location, etc.)"
    )

class CorrectionInfo(BaseModel):
    """Información de corrección ortográfica"""
    from_word: str = Field(alias="from")
    to: str
    confidence: float

class QueryResponse(BaseModel):
    """Modelo de respuesta para análisis de consulta"""
    success: bool
    processing_time_ms: float
    original_query: str
    corrections: Dict[str, Any]
    interpretation: Dict[str, Any]
    sql_query: str
    recommendations: List[Dict[str, Any]]
    user_message: str

# Inicializar FastAPI
app = FastAPI(
    title="LCLN Microservice",
    description="Lenguaje de Consulta en Lenguaje Natural - Sistema de Análisis Léxico para LYNX",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para el sistema
configuracion: Optional[ConfiguracionLYNX] = None
analizador: Optional[AnalizadorLexicoLYNX] = None

@app.on_event("startup")
async def startup_event():
    """Inicializa el sistema al arrancar el microservicio"""
    global configuracion, analizador
    
    print("🚀 Iniciando microservicio LCLN...")
    
    # Inicializar configuración
    configuracion = ConfiguracionLYNX()
    
    # Inicializar analizador
    analizador = AnalizadorLexicoLYNX(configuracion)
    
    print("✅ Sistema LCLN iniciado correctamente")
    print(f"📊 Base de datos cargada:")
    bd = configuracion.base_datos
    print(f"  • Productos simples: {len(bd.get('productos_simples', []))}")
    print(f"  • Productos multi-palabra: {len(bd.get('productos_multi', []))}")
    print(f"  • Categorías: {len(bd.get('categorias', []))}")

@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "LCLN Microservice",
        "version": "2.0.0",
        "description": "Lenguaje de Consulta en Lenguaje Natural",
        "status": "active",
        "endpoints": {
            "analyze": "/api/nlp/analyze",
            "health": "/api/health",
            "metrics": "/api/metrics",
            "docs": "/api/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """Endpoint de health check"""
    global configuracion, analizador
    
    status = "healthy" if (configuracion and analizador) else "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "configuracion": configuracion is not None,
            "analizador": analizador is not None
        }
    }

@app.get("/api/metrics")
async def get_metrics():
    """Endpoint de métricas básicas"""
    global configuracion
    
    if not configuracion:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    bd = configuracion.base_datos
    return {
        "database_stats": {
            "productos_simples": len(bd.get('productos_simples', [])),
            "productos_multi": len(bd.get('productos_multi', [])),
            "productos_completos": len(bd.get('productos_completos', [])),
            "categorias": len(bd.get('categorias', [])),
            "atributos": len(bd.get('atributos', [])),
            "modificadores": len(bd.get('modificadores', [])),
            "unidades": len(bd.get('unidades', []))
        },
        "system_info": {
            "corrections_enabled": True,
            "recommendations_enabled": True,
            "cache_enabled": False  # Por implementar
        }
    }

@app.post("/api/nlp/analyze", response_model=QueryResponse)
async def analyze_query(request: QueryRequest):
    """
    Endpoint principal para análisis de consultas en lenguaje natural
    """
    global analizador
    
    if not analizador:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    start_time = time.time()
    
    try:
        # Obtener opciones
        enable_correction = request.options.get("enable_correction", True)
        enable_recommendations = request.options.get("enable_recommendations", True)
        max_recommendations = request.options.get("max_recommendations", 5)
        
        # Procesar consulta
        if enable_correction:
            # Análisis con corrección ortográfica
            resultado_completo_json = analizador.generar_json_resultado_completo(request.query)
            resultado_completo = json.loads(resultado_completo_json)
        else:
            # Análisis básico sin corrección
            tokens = analizador.analizar(request.query)
            resultado_json = analizador.generar_json_resultado(request.query)
            resultado_basico = json.loads(resultado_json)
            
            # Adaptar formato para compatibilidad
            resultado_completo = {
                "success": True,
                "original_query": request.query,
                "corrections": {"applied": False, "changes": []},
                "interpretation": resultado_basico.get("interpretacion", {}),
                "sql_query": resultado_basico.get("sql_sugerido", ""),
                "recommendations": [],
                "user_message": "Análisis completado sin correcciones"
            }
        
        # Calcular tiempo de procesamiento
        processing_time = (time.time() - start_time) * 1000
        resultado_completo["processing_time_ms"] = round(processing_time, 2)
        
        # Limitar recomendaciones si es necesario
        if len(resultado_completo.get("recommendations", [])) > max_recommendations:
            resultado_completo["recommendations"] = resultado_completo["recommendations"][:max_recommendations]
        
        return QueryResponse(**resultado_completo)
        
    except Exception as e:
        # Log del error (en producción usar logging apropiado)
        print(f"❌ Error procesando consulta '{request.query}': {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Respuesta de error
        processing_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            success=False,
            processing_time_ms=round(processing_time, 2),
            original_query=request.query,
            corrections={"applied": False, "changes": []},
            interpretation={},
            sql_query="",
            recommendations=[],
            user_message=f"Error procesando consulta: {str(e)}"
        )

@app.post("/api/nlp/correct")
async def correct_text(text: str):
    """Endpoint específico para corrección ortográfica"""
    global analizador
    
    if not analizador:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    try:
        resultado = analizador.corrector_ortografico.corregir_consulta(text)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en corrección: {str(e)}")

@app.get("/api/vocabulary")
async def get_vocabulary():
    """Endpoint para obtener el vocabulario actual"""
    global analizador
    
    if not analizador:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    vocabulario = list(analizador.corrector_ortografico.vocabulario)
    return {
        "vocabulary": sorted(vocabulario),
        "count": len(vocabulario)
    }

@app.post("/api/vocabulary")
async def add_vocabulary(words: List[str]):
    """Endpoint para agregar palabras al vocabulario"""
    global analizador
    
    if not analizador:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    try:
        analizador.corrector_ortografico.agregar_al_vocabulario(words)
        return {
            "success": True,
            "message": f"Se agregaron {len(words)} palabras al vocabulario",
            "words_added": words
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando vocabulario: {str(e)}")

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Procesar request
    response = await call_next(request)
    
    # Log básico (en producción usar logging apropiado)
    process_time = time.time() - start_time
    print(f"📝 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando servidor LCLN Microservice...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
