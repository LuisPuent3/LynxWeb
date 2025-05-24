# LynxShop Recommender Service

Microservicio de recomendación basado en contenido para LynxShop, utilizando TF-IDF y similitud coseno para generar recomendaciones personalizadas.

## Características

- Recomendaciones basadas en contenido usando TF-IDF
- Perfil de usuario basado en productos recientes
- Fallback a productos populares para usuarios nuevos
- API REST con FastAPI
- Persistencia de modelo en disco
- Tests automatizados

## Requisitos

- Python 3.11+
- MySQL 8.0+
- Docker y Docker Compose

## Estructura del Proyecto

```
services/recommender/
├── data/
│   └── model/          # Directorio para modelos serializados
├── tests/              # Tests automatizados
├── etl.py             # Script de entrenamiento
├── main.py            # API FastAPI
├── requirements.txt   # Dependencias
└── Dockerfile        # Configuración Docker
```

## Configuración

1. Crear archivo `.env` en el directorio raíz:

```env
MYSQL_HOST=mysql
MYSQL_USER=root
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=lynxshop
```

2. Asegurarse que la base de datos `lynxshop` existe y tiene las tablas necesarias:

```sql
-- Ejemplo de consulta para verificar tablas
SHOW TABLES;
-- Deberían existir: Productos, Categorias, Pedidos, DetallePedido, Usuarios
```

## Uso

### Desarrollo Local

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Entrenar modelo:
```bash
python etl.py
```

3. Iniciar servidor:
```bash
uvicorn -m main:app --reload
```

### Docker

1. Construir imagen:
```bash
docker build -t lynxshop-recommender .
```

2. Ejecutar con Docker Compose:
```bash
docker-compose up
```

### Endpoints

- `GET /predict/{user_id}`: Obtiene recomendaciones para un usuario
  ```bash
  curl http://localhost:8000/predict/1
  ```
  Respuesta:
  ```json
  {
    "recommendations": [
      {"product_id": 123, "score": 0.85},
      {"product_id": 456, "score": 0.72},
      ...
    ]
  }
  ```

- `GET /health`: Verifica estado del servicio
  ```bash
  curl http://localhost:8000/health
  ```

## Tests

Ejecutar tests:
```bash
pytest tests/
```

## Mantenimiento

### Reentrenamiento del Modelo

Para actualizar el modelo con nuevos datos:

1. Detener el servicio
2. Ejecutar `python etl.py`
3. Reiniciar el servicio

### Monitoreo

- Verificar logs del contenedor:
```bash
docker logs recommender
```

- Endpoint de health check:
```bash
curl http://localhost:8000/health
```

## Notas de Implementación

- El modelo TF-IDF se entrena sobre el texto combinado de nombre, categoría y descripción de productos
- Se excluyen productos ya comprados por el usuario
- Para usuarios nuevos, se devuelven los productos más populares
- El perfil de usuario se calcula como el promedio de los vectores TF-IDF de sus productos recientes
- La similitud se calcula usando coseno entre el perfil del usuario y todos los productos 