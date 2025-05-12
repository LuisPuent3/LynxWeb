import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv
import numpy as np
from scipy.sparse import load_npz
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="LynxShop Recommender Service")

# Modelos Pydantic
class Recommendation(BaseModel):
    product_id: int
    score: float

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]

# Variables globales para el modelo
vectorizer = None
tfidf_matrix = None
product_ids = None

def get_db_connection():
    """Establece conexión con la base de datos MySQL."""
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'mysql'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE', 'lynxshop')
    )

@app.on_event("startup")
async def startup_event():
    """Carga el modelo al iniciar la aplicación."""
    global vectorizer, tfidf_matrix, product_ids
    
    try:
        vectorizer = joblib.load('data/model/tfidf_vectorizer.pkl')
        tfidf_matrix = load_npz('data/model/tfidf_matrix.npz')
        product_ids = np.load('data/model/product_ids.npy')
        print("Modelo cargado exitosamente")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        raise

def get_user_recent_products(user_id: int, limit: int = 20) -> List[int]:
    """Obtiene los productos más recientes del usuario."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT dp.id_producto
    FROM Pedidos pe
    JOIN DetallePedido dp USING(id_pedido)
    WHERE pe.id_usuario = %s
    ORDER BY pe.fecha DESC
    LIMIT %s
    """
    
    cursor.execute(query, (user_id, limit))
    products = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return products

def get_popular_products(limit: int = 10) -> List[Dict]:
    """Obtiene los productos más populares basado en ventas totales."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT dp.id_producto, SUM(dp.cantidad) as total
    FROM DetallePedido dp
    GROUP BY dp.id_producto
    ORDER BY total DESC
    LIMIT %s
    """
    
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def get_user_profile(user_id: int) -> np.ndarray:
    """Calcula el perfil del usuario basado en sus productos recientes."""
    recent_products = get_user_recent_products(user_id)
    
    if not recent_products:
        return None
    
    # Obtener índices de los productos en la matriz TF-IDF
    product_indices = [np.where(product_ids == pid)[0][0] for pid in recent_products]
    
    # Calcular el vector promedio de los productos recientes
    user_profile = tfidf_matrix[product_indices].mean(axis=0)
    
    return user_profile

@app.get("/predict/{user_id}", response_model=RecommendationResponse)
async def predict(user_id: int):
    """Genera recomendaciones para un usuario."""
    # Obtener perfil del usuario
    user_profile = get_user_profile(user_id)
    
    if user_profile is None:
        # Fallback a productos populares
        popular_products = get_popular_products()
        recommendations = [
            Recommendation(
                product_id=row['id_producto'],
                score=1.0  # Score máximo para productos populares
            )
            for row in popular_products
        ]
    else:
        # Calcular similitud coseno
        similarities = cosine_similarity(user_profile, tfidf_matrix).flatten()
        
        # Obtener productos ya comprados por el usuario
        purchased_products = set(get_user_recent_products(user_id, limit=1000))
        
        # Crear lista de (product_id, score) excluyendo productos ya comprados
        product_scores = [
            (int(product_ids[i]), float(similarities[i]))
            for i in range(len(product_ids))
            if product_ids[i] not in purchased_products
        ]
        
        # Ordenar por score y tomar top 10
        recommendations = [
            Recommendation(product_id=pid, score=score)
            for pid, score in sorted(product_scores, key=lambda x: x[1], reverse=True)[:10]
        ]
    
    return RecommendationResponse(recommendations=recommendations)

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servicio."""
    return {"status": "healthy", "model_loaded": vectorizer is not None} 