#!/usr/bin/env python3
"""
Endpoint MySQL para API LYNX NLP
Utiliza directamente la base de datos MySQL real
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
from adaptador_mysql import AdaptadorMySQLLYNX, obtener_stats_mysql

# Inicializar FastAPI
app = FastAPI(
    title="LYNX MySQL NLP Microservice",
    description="Sistema NLP conectado directamente a MySQL LynxShop",
    version="4.0.0-mysql",
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

class NLPResponse(BaseModel):
    success: bool
    processing_time_ms: float
    original_query: str
    recommendations: list
    user_message: str
    metadata: dict

# Instancia del adaptador
adaptador = AdaptadorMySQLLYNX()

@app.get("/")
def root():
    return {
        "message": "LYNX NLP MySQL Microservice",
        "version": "4.0.0-mysql",
        "database": "mysql_lynxshop_real",
        "status": "active"
    }

@app.get("/api/health")
def health_check():
    """Health check con estadísticas MySQL reales"""
    try:
        stats = obtener_stats_mysql()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "4.0.0-mysql",
            "components": {
                "database": "mysql_healthy",
                "products": f"{stats['productos_mysql']} productos reales",
                "categories": f"{stats['categorias_mysql']} categorías reales",
                "source": stats['source']
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/api/nlp/analyze")
def analyze_nlp_mysql(request: QueryRequest):
    """Análisis NLP usando MySQL directo"""
    inicio = time.time()
    
    try:
        consulta = request.query.lower().strip()
        
        # Análisis básico de la consulta
        filtros = {}
        
        # Detectar categorías
        categorias_map = {
            'bebidas': ['bebida', 'refresco', 'agua', 'jugo', 'cola'],
            'snacks': ['botana', 'papas', 'galletas'],
            'golosinas': ['dulce', 'chocolate', 'paleta'],
            'frutas': ['fruta', 'fresco'],
            'papeleria': ['utiles', 'boligrafo', 'cuaderno']
        }
        
        categoria_detectada = None
        for categoria, sinonimos in categorias_map.items():
            if any(sin in consulta for sin in sinonimos + [categoria]):
                categoria_detectada = categoria
                break
          # Detectar filtros de precio
        precio_max = None
        if 'barato' in consulta or 'economico' in consulta or 'baratas' in consulta:
            precio_max = 20.0
        elif 'caro' in consulta or 'costoso' in consulta:
            precio_max = None  # No filtrar por precio alto        # Extraer términos de búsqueda (remover palabras de filtro)
        palabras_filtro = {'barato', 'baratas', 'economico', 'caro', 'costoso', 'sin', 'con', 'bebidas', 'snacks', 'golosinas'}
        terminos_busqueda = [p for p in consulta.split() if p not in palabras_filtro and len(p) > 2]
        termino_busqueda = ' '.join(terminos_busqueda) if terminos_busqueda else ''
        
        # Buscar en MySQL - primero por término específico
        productos = adaptador.buscar_productos(
            consulta=termino_busqueda,
            categoria=None,  # No filtrar por categoría inicialmente
            precio_max=precio_max
        )
        
        # Si no hay resultados específicos, buscar por categoría
        if not productos and categoria_detectada:
            productos = adaptador.buscar_productos(
                consulta='',
                categoria=categoria_detectada,
                precio_max=precio_max
            )
        
        tiempo_proceso = (time.time() - inicio) * 1000
        
        # Preparar respuesta
        mensaje = f"Se encontraron {len(productos)} productos"
        if categoria_detectada:
            mensaje += f" en {categoria_detectada}"
        if precio_max:
            mensaje += f" hasta ${precio_max}"
        
        return {
            "success": True,
            "processing_time_ms": tiempo_proceso,
            "original_query": request.query,
            "corrections": {"applied": False},
            "interpretation": {
                "type": "mysql_direct_search",
                "categoria": categoria_detectada,
                "precio_max": precio_max,
                "terminos": terminos_busqueda
            },
            "sql_query": f"MySQL: productos JOIN categorias WHERE cantidad > 0",
            "recommendations": productos,
            "user_message": mensaje,
            "metadata": {
                "products_found": len(productos),
                "has_corrections": False,
                "source": "mysql_lynxshop_real"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "processing_time_ms": (time.time() - inicio) * 1000,
            "original_query": request.query,
            "error": str(e),
            "recommendations": [],
            "user_message": "Error procesando consulta",
            "metadata": {"error": True}
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
