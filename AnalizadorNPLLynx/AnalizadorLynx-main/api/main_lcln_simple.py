#!/usr/bin/env python3
"""
API Simple para servicio LCLN
Versión ultra-simplificada para garantizar inicio
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import json
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log de inicio
print("🧠 LCLN Service - Iniciando FastAPI...")
logger.info("LCLN Service - Starting up...")

app = FastAPI(
    title="LCLN Simple API",
    description="API simplificada para procesamiento de lenguaje natural",
    version="1.0.0"
)

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20

class SearchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    query_processed: str
    total_found: int

# Simulador simple de análisis NLP
class SimpleNLPProcessor:
    def __init__(self):
        # Mapeo simple de términos coloquiales
        self.price_mapping = {
            'barato': {'op': '<', 'value': 30},
            'caro': {'op': '>', 'value': 50},
            'económico': {'op': '<', 'value': 30},
            'costoso': {'op': '>', 'value': 50},
        }
        
        self.category_mapping = {
            'dulce': 'Golosinas',
            'bebida': 'Bebidas',
            'snack': 'Snacks',
            'fruta': 'Frutas',
            'papelería': 'Papeleria',
            'escolar': 'Papeleria',
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Procesa una consulta simple de manera básica"""
        query_lower = query.lower()
        
        # Buscar filtros de precio
        price_filter = None
        for term, filter_data in self.price_mapping.items():
            if term in query_lower:
                price_filter = filter_data
                break
        
        # Buscar categorías
        category_filter = None
        for term, category in self.category_mapping.items():
            if term in query_lower:
                category_filter = category
                break
        
        # Extraer productos mencionados (palabras principales)
        words = re.findall(r'\b\w+\b', query_lower)
        product_terms = [w for w in words if len(w) > 3 and w not in ['barato', 'caro', 'económico', 'costoso', 'quiero', 'busco', 'dame']]
        
        return {
            'query': query,
            'price_filter': price_filter,
            'category_filter': category_filter,
            'product_terms': product_terms,
            'processed': True
        }

# Instancia del procesador
nlp_processor = SimpleNLPProcessor()

@app.get("/")
async def root():
    return {"message": "LCLN Simple API - Servicio funcionando"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "lcln-simple",
        "version": "1.0.0"
    }

@app.post("/search", response_model=SearchResponse)
async def search_nlp(request: SearchRequest):
    """Endpoint principal de búsqueda NLP"""
    try:
        logger.info(f"Procesando consulta: {request.query}")
        
        # Procesar la consulta
        analysis = nlp_processor.process_query(request.query)
        
        # Simular resultados (en una implementación real, esto haría consulta a BD)
        results = [
            {
                "id": 1,
                "nombre": "Producto ejemplo",
                "precio": 25.0,
                "categoria": analysis.get('category_filter', 'General'),
                "relevancia": 0.9,
                "match_reason": f"Coincide con: {', '.join(analysis['product_terms'])}"
            }
        ]
        
        return SearchResponse(
            success=True,
            results=results,
            query_processed=analysis['query'],
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error procesando consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/status")
async def get_status():
    """Endpoint de estado del servicio"""
    return {
        "service": "lcln-simple",
        "status": "active",
        "capabilities": ["basic_nlp", "price_filtering", "category_mapping"],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
