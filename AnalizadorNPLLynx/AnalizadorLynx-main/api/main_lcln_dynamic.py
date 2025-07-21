#!/usr/bin/env python3
"""
API LYNX NLP LCLN - FastAPI con Sistema Dinámico
Integra el Sistema LCLN con la API existente para máxima compatibilidad
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
from sistema_lcln_simple import SistemaLCLNSimplificado

# Inicializar FastAPI
app = FastAPI(
    title="LYNX LCLN Dynamic NLP API",
    description="Sistema LCLN dinámico con productos reales MySQL + imágenes",
    version="6.0.0-lcln-dynamic",
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

class BatchQueryRequest(BaseModel):
    queries: list[str]

# Instancia del sistema LCLN
sistema_lcln = SistemaLCLNSimplificado()

@app.get("/")
def root():
    return {
        "message": "LYNX LCLN Dynamic NLP API",
        "version": "6.0.0-lcln-dynamic", 
        "features": [
            "Sistema LCLN completo según documentación técnica",
            "Cache dinámico que se actualiza automáticamente",
            "Soporte completo para nuevas categorías/productos",
            "Imágenes incluidas en respuestas",
            "5 estrategias de búsqueda inteligente"
        ],
        "products_source": "mysql_lynxshop_dynamic_cache",
        "status": "active"
    }

@app.get("/api/health")
def health_check():
    """Health check con estadísticas dinámicas"""
    try:
        # Forzar actualización del cache para estadísticas actuales
        sistema_lcln._actualizar_cache_dinamico()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "6.0.0-lcln-dynamic",
            "components": {
                "database": "mysql_dynamic_cache",
                "products": f"{len(sistema_lcln._cache_productos)} productos con imágenes",
                "categories": f"{len(sistema_lcln._cache_categorias)} categorías dinámicas",
                "cache_updated": sistema_lcln._cache_timestamp.isoformat() if sistema_lcln._cache_timestamp else "never",
                "mode": "lcln_dynamic_adaptive"
            },
            "features": {
                "adaptive_to_new_products": True,
                "adaptive_to_new_categories": True,
                "images_included": True,
                "cache_auto_refresh": True,
                "multiple_search_strategies": 5
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/api/nlp/analyze")
def analyze_lcln_dynamic(request: QueryRequest):
    """
    Endpoint principal - Análisis NLP con Sistema LCLN Dinámico
    Se adapta automáticamente cuando el admin agrega productos/categorías
    """
    try:
        # Usar el sistema LCLN dinámico
        resultado = sistema_lcln.buscar_productos_inteligente(
            consulta=request.query,
            limit=20
        )
        
        if not resultado['success']:
            raise HTTPException(status_code=500, detail="Error en Sistema LCLN")
        
        # Preparar respuesta compatible con frontend existente
        return {
            "success": True,
            "processing_time_ms": resultado['processing_time_ms'],
            "original_query": request.query,
            "corrections": {
                "applied": False,  # TODO: Implementar correcciones en versión futura
                "original_query": request.query
            },
            "interpretation": {
                "type": resultado['interpretation']['tipo'],
                "termino_busqueda": resultado['interpretation']['termino_busqueda'],
                "categoria": resultado['interpretation']['categoria'],
                "estrategia_usada": resultado['interpretation']['estrategia_usada']
            },
            "recommendations": resultado['recommendations'],
            "user_message": resultado['user_message'],
            "metadata": {
                "products_found": resultado['products_found'],
                "has_corrections": False,
                "source": "lcln_dynamic_mysql",
                "productos_comprables": True,
                "database_real": True,
                "imagenes_incluidas": True,
                "adaptativo": True,
                "cache_timestamp": resultado['metadata']['cache_timestamp']
            },
            "sql_query": f"Dynamic LCLN Query - Strategy: {resultado['interpretation']['estrategia_usada']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis LCLN: {str(e)}")

@app.post("/api/nlp/batch")
def analyze_batch_lcln(request: BatchQueryRequest):
    """
    Análisis en lote para múltiples consultas
    """
    try:
        resultados = []
        
        for query in request.queries:
            resultado_individual = sistema_lcln.buscar_productos_inteligente(
                consulta=query,
                limit=10  # Menos productos por consulta en batch
            )
            
            resultados.append({
                "query": query,
                "success": resultado_individual['success'],
                "products_found": resultado_individual['products_found'],
                "products": resultado_individual['recommendations'][:5],  # Solo top 5
                "strategy": resultado_individual['interpretation']['estrategia_usada']
            })
        
        return {
            "success": True,
            "total_queries": len(request.queries),
            "results": resultados,
            "processing_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis batch: {str(e)}")

@app.get("/api/stats")
def get_stats():
    """
    Estadísticas detalladas del sistema
    """
    try:
        # Actualizar cache para estadísticas frescas
        sistema_lcln._actualizar_cache_dinamico()
        
        # Análisis por categorías
        productos_por_categoria = {}
        precios_por_categoria = {}
        
        for producto in sistema_lcln._cache_productos.values():
            categoria = producto['categoria']
            
            # Contar productos por categoría
            if categoria not in productos_por_categoria:
                productos_por_categoria[categoria] = 0
            productos_por_categoria[categoria] += 1
            
            # Precios por categoría
            if categoria not in precios_por_categoria:
                precios_por_categoria[categoria] = []
            precios_por_categoria[categoria].append(producto['precio'])
        
        # Calcular estadísticas de precios
        estadisticas_precios = {}
        for categoria, precios in precios_por_categoria.items():
            estadisticas_precios[categoria] = {
                "min": min(precios),
                "max": max(precios),
                "promedio": sum(precios) / len(precios)
            }
        
        return {
            "sistema": "LCLN Dynamic",
            "timestamp": datetime.now().isoformat(),
            "cache_actualizado": sistema_lcln._cache_timestamp.isoformat(),
            "totales": {
                "productos": len(sistema_lcln._cache_productos),
                "categorias": len(sistema_lcln._cache_categorias),
                "con_imagenes": sum(1 for p in sistema_lcln._cache_productos.values() if p['imagen'] != 'default.jpg')
            },
            "productos_por_categoria": productos_por_categoria,
            "estadisticas_precios": estadisticas_precios,
            "categorias_disponibles": list(sistema_lcln._cache_categorias.keys()),
            "adaptabilidad": {
                "se_actualiza_automaticamente": True,
                "detecta_nuevas_categorias": True,
                "detecta_nuevos_productos": True,
                "mantiene_imagenes": True
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/force-cache-refresh")
def force_cache_refresh():
    """
    Forzar actualización del cache (útil después de que admin agrega productos)
    """
    try:
        # Resetear timestamp para forzar actualización
        sistema_lcln._cache_timestamp = None
        sistema_lcln._actualizar_cache_dinamico()
        
        return {
            "success": True,
            "message": "Cache actualizado exitosamente",
            "timestamp": sistema_lcln._cache_timestamp.isoformat(),
            "productos_cargados": len(sistema_lcln._cache_productos),
            "categorias_cargadas": len(sistema_lcln._cache_categorias)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando LYNX LCLN Dynamic NLP API...")
    print("📦 Sistema adaptativo para productos dinámicos")
    print("🖼️ Imágenes incluidas automáticamente")
    print("🔄 Cache que se actualiza cada 5 minutos")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8004,  # Puerto diferente para no conflicto
        log_level="info"
    )
