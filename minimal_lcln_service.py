#!/usr/bin/env python3
"""
Minimal LCLN Service for LynxWeb
Simple FastAPI service that provides basic NLP functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from datetime import datetime
import json

# Inicializar FastAPI
app = FastAPI(
    title="LYNX LCLN Minimal NLP API",
    description="Servicio NLP LCLN mínimo para LynxWeb",
    version="1.0.0-minimal",
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

@app.get("/")
def root():
    return {
        "message": "LYNX LCLN Minimal NLP API",
        "version": "1.0.0-minimal",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "lcln-minimal",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time()
    }

@app.post("/api/search")
def search_nlp(request: QueryRequest):
    """Búsqueda NLP básica"""
    try:
        query = request.query.strip().lower()
        
        # Respuesta básica de búsqueda
        response = {
            "query": request.query,
            "processed_query": query,
            "results": [],
            "suggestions": [],
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "message": "LCLN service running - basic response"
        }
        
        # Agregar algunas sugerencias básicas
        if len(query) > 2:
            response["suggestions"] = [
                f"{query} premium",
                f"{query} oferta",
                f"{query} recomendado"
            ]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/batch-search")
def batch_search_nlp(request: BatchQueryRequest):
    """Búsqueda por lotes"""
    try:
        results = []
        for query in request.queries:
            result = {
                "query": query,
                "processed_query": query.strip().lower(),
                "suggestions": [f"{query} premium"] if len(query) > 2 else [],
                "timestamp": datetime.now().isoformat()
            }
            results.append(result)
        
        return {
            "batch_results": results,
            "total_queries": len(request.queries),
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")

@app.get("/api/status")
def get_status():
    """Estado del servicio"""
    return {
        "service": "lcln-minimal",
        "status": "operational",
        "version": "1.0.0-minimal",
        "endpoints": [
            "/api/health",
            "/api/search",
            "/api/batch-search",
            "/api/status"
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🧠 Starting minimal LCLN service...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
