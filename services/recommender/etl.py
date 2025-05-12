import os
import mysql.connector
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz
import joblib
import numpy as np

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Establece conexión con la base de datos MySQL."""
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'mysql'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE', 'lynxshop')
    )

def fetch_corpus_data():
    """Obtiene el corpus de texto para entrenar el TF-IDF."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        p.id_producto,
        CONCAT_WS(' ', p.nombre, c.nombre, IFNULL(c.descripcion,'')) AS text
    FROM Productos p
    JOIN Categorias c USING(id_categoria)
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {row['id_producto']: row['text'] for row in results}

def fetch_user_history():
    """Obtiene el historial de interacciones de usuarios con productos."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        dp.id_producto,
        pe.id_usuario,
        SUM(dp.cantidad) AS interactions
    FROM DetallePedido dp
    JOIN Pedidos pe USING(id_pedido)
    GROUP BY pe.id_usuario, dp.id_producto
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def train_and_save_model():
    """Entrena el modelo TF-IDF y guarda los resultados."""
    # Obtener datos
    corpus_data = fetch_corpus_data()
    product_ids = list(corpus_data.keys())
    texts = list(corpus_data.values())
    
    # Entrenar TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    # Transformar corpus
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Crear directorio si no existe
    os.makedirs('data/model', exist_ok=True)
    
    # Guardar modelo y matriz
    joblib.dump(vectorizer, 'data/model/tfidf_vectorizer.pkl')
    save_npz('data/model/tfidf_matrix.npz', tfidf_matrix)
    
    # Guardar mapeo de IDs
    np.save('data/model/product_ids.npy', np.array(product_ids))
    
    print(f"Modelo entrenado y guardado. Dimensiones de la matriz: {tfidf_matrix.shape}")
    print(f"Vocabulario: {len(vectorizer.vocabulary_)} términos")

if __name__ == "__main__":
    train_and_save_model() 