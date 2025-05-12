import pytest
from fastapi.testclient import TestClient
from main import app
import numpy as np
from scipy.sparse import csr_matrix
import joblib
import os

# Crear directorio de datos de prueba
os.makedirs('data/model', exist_ok=True)

# Mock del modelo para pruebas
@pytest.fixture(autouse=True)
def mock_model():
    # Crear vectorizador mock
    vectorizer = joblib.dump({}, 'data/model/tfidf_vectorizer.pkl')
    
    # Crear matriz TF-IDF mock (10 productos, 5 features)
    mock_matrix = csr_matrix(np.random.rand(10, 5))
    mock_matrix.save_npz('data/model/tfidf_matrix.npz')
    
    # Crear array de IDs mock
    np.save('data/model/product_ids.npy', np.array(range(1, 11)))
    
    yield
    
    # Limpiar archivos mock
    os.remove('data/model/tfidf_vectorizer.pkl')
    os.remove('data/model/tfidf_matrix.npz')
    os.remove('data/model/product_ids.npy')

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Test del endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "model_loaded": True}

def test_predict_endpoint(client):
    """Test del endpoint de predicción."""
    response = client.get("/predict/1")
    assert response.status_code == 200
    
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) <= 10
    
    for rec in data["recommendations"]:
        assert "product_id" in rec
        assert "score" in rec
        assert 0 <= rec["score"] <= 1

def test_predict_invalid_user(client):
    """Test con ID de usuario inválido."""
    response = client.get("/predict/-1")
    assert response.status_code == 200  # Debería devolver productos populares
    assert "recommendations" in response.json() 