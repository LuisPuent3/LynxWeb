#!/usr/bin/env python
import os
import time
import pickle
import numpy as np
import pandas as pd
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('recommender-etl')

# Configuración de conexión a MySQL con valores fijos
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = '12345678'  # Contraseña fija según .env
DB_NAME = 'lynxshop'

# Directorio para guardar modelo
MODEL_DIR = os.environ.get('MODEL_DIR', './data')
os.makedirs(MODEL_DIR, exist_ok=True)

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
        logger.info("Conexión a MySQL establecida correctamente")
        return connection
    except Exception as e:
        logger.error(f"Error al conectar a MySQL: {str(e)}")
        raise

def fetch_product_data():
    """Extrae datos de productos y categorías para crear el corpus"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Consulta SQL para obtener productos con su categoría
            query = """
            SELECT p.id_producto, CONCAT_WS(' ', p.nombre, c.nombre) AS texto
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id_categoria
            """
            cursor.execute(query)
            products = cursor.fetchall()
            
            logger.info(f"Se extrajeron {len(products)} productos con sus categorías")
            return products
    except Exception as e:
        logger.error(f"Error al extraer datos de productos: {str(e)}")
        raise
    finally:
        if connection:
            connection.close()

def train_tfidf_model(products):
    """Entrena modelo TF-IDF con los datos de productos"""
    try:
        # Convertir a DataFrame para facilitar manipulación
        df = pd.DataFrame(products)
        
        # Crear y entrenar vectorizador TF-IDF
        tfidf_vectorizer = TfidfVectorizer(
            min_df=1,              # Reducido de 2 a 1 para muestras pequeñas
            max_df=1.0,            # Aumentado de 0.95 a 1.0 para muestras pequeñas
            max_features=5000,     # Máximo número de características
            stop_words=None,       # Desactivar stop_words para muestras pequeñas
            ngram_range=(1, 1)     # Reducido a solo unigramas para simplificar
        )
        
        # Ajustar y transformar los textos
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['texto'])
        
        # Calcular matriz de similitud coseno
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Crear diccionario de mapeo de índices a ID de productos
        indices = pd.Series(df.index, index=df['id_producto']).to_dict()
        
        # Crear modelo para guardar
        model = {
            'tfidf_vectorizer': tfidf_vectorizer,
            'tfidf_matrix': tfidf_matrix,
            'cosine_sim': cosine_sim,
            'indices': indices,
            'product_ids': df['id_producto'].tolist()
        }
        
        logger.info(f"Modelo TF-IDF entrenado con éxito: {tfidf_matrix.shape[0]} productos, {tfidf_matrix.shape[1]} características")
        return model
    except Exception as e:
        logger.error(f"Error al entrenar modelo TF-IDF: {str(e)}")
        raise

def save_model(model, filepath):
    """Guarda el modelo entrenado en disco"""
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Modelo guardado correctamente en {filepath}")
    except Exception as e:
        logger.error(f"Error al guardar modelo: {str(e)}")
        raise

def main():
    """Función principal del ETL"""
    start_time = time.time()
    logger.info("Iniciando proceso ETL para entrenamiento del modelo de recomendación")
    
    try:
        # Extraer datos
        products = fetch_product_data()
        
        # Entrenar modelo
        model = train_tfidf_model(products)
        
        # Guardar modelo
        model_path = os.path.join(MODEL_DIR, 'model.pkl')
        save_model(model, model_path)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Proceso ETL completado exitosamente en {elapsed_time:.2f} segundos")
    except Exception as e:
        logger.error(f"Error en proceso ETL: {str(e)}")
        raise

if __name__ == "__main__":
    main() 