#!/usr/bin/env python
import os
import pickle
import logging
from typing import Dict, List, Optional, Union

import pandas as pd
import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('recommender-api')

# Configuración de conexión a MySQL con valores fijos
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = '12345678'  # Contraseña fija según .env
DB_NAME = 'lynxshop'

# Directorio del modelo
MODEL_DIR = os.environ.get('MODEL_DIR', './data')
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')

# Inicializar FastAPI
app = FastAPI(
    title="LynxShop Recommender API",
    description="API para recomendaciones personalizadas de productos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Recommendation(BaseModel):
    id_producto: int
    score: float

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]

# Cargar modelo al iniciar
model = None

@app.on_event("startup")
async def load_model():
    """Carga el modelo TF-IDF al iniciar la aplicación"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Modelo cargado correctamente desde {MODEL_PATH}")
        else:
            logger.warning(f"Archivo de modelo no encontrado en {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error al cargar el modelo: {str(e)}")
        model = None

def get_db_connection():
    """Establece conexión con la base de datos MySQL"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        logger.error(f"Error al conectar a MySQL: {str(e)}")
        raise

def get_user_history(user_id: int, limit: int = 20) -> List[int]:
    """Obtiene los últimos productos comprados por el usuario"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
            SELECT dp.id_producto 
            FROM DetallePedido dp
            JOIN Pedidos p ON dp.id_pedido = p.id_pedido
            WHERE p.id_usuario = %s
            ORDER BY p.fecha DESC
            LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
            results = cursor.fetchall()
            
            # Extraer solo los IDs de productos
            product_ids = [row['id_producto'] for row in results]
            logger.info(f"Historial del usuario {user_id}: {len(product_ids)} productos")
            return product_ids
    except Exception as e:
        logger.error(f"Error al obtener historial de usuario {user_id}: {str(e)}")
        return []
    finally:
        if connection:
            connection.close()

def get_popular_products(limit: int = 10) -> List[Dict[str, Union[int, float]]]:
    """Obtiene los productos más populares (más vendidos)"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
            SELECT dp.id_producto, SUM(dp.cantidad) as total_vendido
            FROM DetallePedido dp
            GROUP BY dp.id_producto
            ORDER BY total_vendido DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            # Convertir a formato de recomendaciones
            recommendations = [
                {"id_producto": row['id_producto'], "score": 1.0 - (i * 0.05)}  # Score decreciente
                for i, row in enumerate(results)
            ]
            logger.info(f"Productos populares obtenidos: {len(recommendations)}")
            return recommendations
    except Exception as e:
        logger.error(f"Error al obtener productos populares: {str(e)}")
        return []
    finally:
        if connection:
            connection.close()

def get_recommendations_by_history(product_ids: List[int], limit: int = 10) -> List[Dict[str, Union[int, float]]]:
    """Genera recomendaciones basadas en el historial de productos"""
    global model
    
    if not model or len(product_ids) == 0:
        return []
    
    try:
        # Obtener índices de productos en la matriz TF-IDF
        product_indices = [model['indices'].get(pid) for pid in product_ids if pid in model['indices']]
        
        # Filtrar índices no encontrados
        product_indices = [idx for idx in product_indices if idx is not None]
        
        if not product_indices:
            return []
        
        # Calcular similitud promedio para cada producto del historial
        sim_scores = model['cosine_sim'][product_indices].mean(axis=0)
        
        # Ordenar por similitud y obtener top N
        sim_scores_with_indices = list(enumerate(sim_scores))
        sim_scores_with_indices.sort(key=lambda x: x[1], reverse=True)
        
        # Filtrar productos que ya están en el historial
        filtered_scores = [item for item in sim_scores_with_indices 
                          if model['product_ids'][item[0]] not in product_ids]
        
        # Tomar top N
        top_similar = filtered_scores[:limit]
        
        # Convertir a formato de respuesta
        recommendations = [
            {
                "id_producto": model['product_ids'][idx], 
                "score": float(score)
            } 
            for idx, score in top_similar
        ]
        
        logger.info(f"Generadas {len(recommendations)} recomendaciones basadas en historial")
        return recommendations
    except Exception as e:
        logger.error(f"Error al generar recomendaciones por historial: {str(e)}")
        return []

@app.get("/predict/{user_id}", response_model=RecommendationResponse)
async def predict(user_id: int, limit: int = 10):
    """
    Genera recomendaciones personalizadas para un usuario.
    
    - Si el usuario tiene historial, recomienda productos similares.
    - Si no tiene historial, devuelve los productos más populares.
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de recomendaciones (default: 10)
    
    Returns:
        Lista de recomendaciones con id_producto y score
    """
    global model
    
    # Verificar que el modelo esté cargado
    if model is None:
        try:
            await load_model()
            if model is None:
                logger.error("No se pudo cargar el modelo de recomendaciones")
                raise HTTPException(status_code=500, detail="Modelo de recomendaciones no disponible")
        except Exception as e:
            logger.error(f"Error al cargar modelo en endpoint predict: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al cargar modelo: {str(e)}")
    
    try:
        # Obtener historial del usuario
        user_history = get_user_history(user_id)
        
        # Si el usuario tiene historial, generar recomendaciones personalizadas
        if user_history:
            recommendations = get_recommendations_by_history(user_history, limit)
            if recommendations:
                return RecommendationResponse(recommendations=recommendations)
        
        # Si no tiene historial o no se generaron recomendaciones, usar productos populares
        popular_recommendations = get_popular_products(limit)
        return RecommendationResponse(recommendations=popular_recommendations)
    
    except Exception as e:
        logger.error(f"Error al generar predicciones para usuario {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar recomendaciones: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servicio"""
    return {"status": "ok", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 