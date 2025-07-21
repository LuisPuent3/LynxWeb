"""
API SIMPLE LCLN CON PRIORIDADES
Versión simplificada que funciona sin errores
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import mysql.connector
from datetime import datetime
import uvicorn
import traceback

app = FastAPI(title="LCLN API Simple", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config MySQL
mysql_config = {
    'host': 'localhost',
    'database': 'lynxshop',
    'user': 'root',
    'password': '12345678',
    'charset': 'utf8mb4'
}

class ConsultaNLP(BaseModel):
    query: str
    limit: Optional[int] = 20

class SinonimoCreate(BaseModel):
    producto_id: int
    sinonimo: str
    fuente: str = "admin"

@app.get("/")
async def root():
    return {
        "service": "LCLN API Simple",
        "version": "1.0",
        "status": "active"
    }

@app.get("/api/health")
async def health():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM producto_sinonimos WHERE activo = 1")
        total_sinonimos = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "productos": total_productos,
            "sinonimos": total_sinonimos,
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.post("/api/nlp/analyze")
async def buscar(consulta: ConsultaNLP):
    try:
        inicio = datetime.now()
        query = consulta.query.lower().strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Consulta vacía")
        
        # Buscar productos por sinónimos específicos (PRIORIDAD 1)
        productos_especificos = buscar_por_sinonimos(query)
        
        if productos_especificos:
            return formatear_respuesta(productos_especificos, consulta, inicio, "sinonimos_especificos")
        
        # Buscar por atributos (PRIORIDAD 2)
        if "sin" in query:
            productos_sin = buscar_sin_atributos(query)
            if productos_sin:
                return formatear_respuesta(productos_sin, consulta, inicio, "sin_atributos")
        
        # Buscar por categoría (PRIORIDAD 3)
        productos_categoria = buscar_por_categoria(query)
        if productos_categoria:
            return formatear_respuesta(productos_categoria, consulta, inicio, "categoria")
        
        # Fallback: búsqueda general
        productos_general = buscar_general(query)
        return formatear_respuesta(productos_general, consulta, inicio, "fallback")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_query": consulta.query,
            "recommendations": [],
            "products_found": 0
        }

def buscar_por_sinonimos(query):
    """Buscar productos específicos por sinónimos"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT DISTINCT p.*, c.nombre as categoria, ps.sinonimo
            FROM productos p
            INNER JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE ps.sinonimo LIKE %s AND ps.activo = 1
            ORDER BY ps.popularidad DESC
        """, [f"%{query}%"])
        
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            producto = {
                'id': row['id_producto'],
                'nombre': row['nombre'],
                'precio': float(row['precio']),
                'categoria': row['categoria'],
                'imagen': row['imagen'] or 'default.jpg',
                'cantidad': row['cantidad'],
                'available': row['cantidad'] > 0,
                'match_score': 0.95,
                'match_type': 'sinonimo_especifico',
                'sinonimo_usado': row['sinonimo']
            }
            productos.append(producto)
        
        return productos
        
    except Exception as e:
        print(f"Error buscando sinónimos: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def buscar_sin_atributos(query):
    """Buscar productos SIN ciertos atributos"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        atributo = None
        if "sin azucar" in query or "sin azúcar" in query:
            atributo = "azucar"
        elif "sin picante" in query:
            atributo = "picante"
        
        if not atributo:
            return []
        
        cursor.execute("""
            SELECT DISTINCT p.*, c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            LEFT JOIN producto_atributos pa ON p.id_producto = pa.producto_id AND pa.atributo = %s
            WHERE pa.valor = FALSE OR pa.valor IS NULL
            ORDER BY p.precio ASC
            LIMIT 10
        """, [atributo])
        
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            producto = {
                'id': row['id_producto'],
                'nombre': row['nombre'],
                'precio': float(row['precio']),
                'categoria': row['categoria'],
                'imagen': row['imagen'] or 'default.jpg',
                'cantidad': row['cantidad'],
                'available': row['cantidad'] > 0,
                'match_score': 0.85,
                'match_type': 'sin_atributo',
                'atributo_filtrado': atributo
            }
            productos.append(producto)
        
        return productos
        
    except Exception as e:
        print(f"Error buscando sin atributos: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def buscar_por_categoria(query):
    """Buscar por categoría"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        categoria = None
        if "bebida" in query or "refresco" in query:
            categoria = "bebidas"
        elif "botana" in query or "snack" in query:
            categoria = "snacks"
        elif "fruta" in query:
            categoria = "frutas"
        
        if not categoria:
            return []
        
        cursor.execute("""
            SELECT p.*, c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE LOWER(c.nombre) LIKE %s
            ORDER BY p.precio ASC
            LIMIT 10
        """, [f"%{categoria}%"])
        
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            producto = {
                'id': row['id_producto'],
                'nombre': row['nombre'],
                'precio': float(row['precio']),
                'categoria': row['categoria'],
                'imagen': row['imagen'] or 'default.jpg',
                'cantidad': row['cantidad'],
                'available': row['cantidad'] > 0,
                'match_score': 0.7,
                'match_type': 'categoria',
                'categoria_buscada': categoria
            }
            productos.append(producto)
        
        return productos
        
    except Exception as e:
        print(f"Error buscando categoría: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def buscar_general(query):
    """Búsqueda general de fallback"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.*, c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE LOWER(p.nombre) LIKE %s
            ORDER BY p.precio ASC
            LIMIT 10
        """, [f"%{query}%"])
        
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            producto = {
                'id': row['id_producto'],
                'nombre': row['nombre'],
                'precio': float(row['precio']),
                'categoria': row['categoria'],
                'imagen': row['imagen'] or 'default.jpg',
                'cantidad': row['cantidad'],
                'available': row['cantidad'] > 0,
                'match_score': 0.4,
                'match_type': 'general',
            }
            productos.append(producto)
        
        return productos
        
    except Exception as e:
        print(f"Error búsqueda general: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def formatear_respuesta(productos, consulta, inicio, estrategia):
    """Formatear respuesta para el frontend"""
    tiempo_ms = (datetime.now() - inicio).total_seconds() * 1000
    
    return {
        'success': True,
        'processing_time_ms': round(tiempo_ms, 2),
        'original_query': consulta.query,
        'recommendations': productos[:consulta.limit],
        'products_found': len(productos),
        'strategy_used': estrategia,
        'user_message': f"Encontrados {len(productos)} productos usando {estrategia}",
        'timestamp': datetime.now().isoformat()
    }

# ================================================
# ENDPOINTS DE ADMIN PARA SINÓNIMOS
# ================================================

@app.get("/api/admin/sinonimos/producto/{producto_id}")
async def obtener_sinonimos_producto(producto_id: int):
    """Obtener sinónimos de un producto"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM producto_sinonimos 
            WHERE producto_id = %s AND activo = 1
            ORDER BY popularidad DESC
        """, [producto_id])
        
        sinonimos = cursor.fetchall()
        return sinonimos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.post("/api/admin/sinonimos/")
async def crear_sinonimo(sinonimo: SinonimoCreate):
    """Crear nuevo sinónimo"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Verificar que el producto existe
        cursor.execute("SELECT nombre FROM productos WHERE id_producto = %s", [sinonimo.producto_id])
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Verificar que el sinónimo no existe
        cursor.execute(
            "SELECT id FROM producto_sinonimos WHERE producto_id = %s AND sinonimo = %s",
            [sinonimo.producto_id, sinonimo.sinonimo.lower()]
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Sinónimo ya existe")
        
        # Insertar sinónimo
        cursor.execute("""
            INSERT INTO producto_sinonimos (producto_id, sinonimo, popularidad, activo)
            VALUES (%s, %s, 0, 1)
        """, [sinonimo.producto_id, sinonimo.sinonimo.lower()])
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Sinónimo creado correctamente",
            "id": cursor.lastrowid
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.delete("/api/admin/sinonimos/{sinonimo_id}")
async def eliminar_sinonimo(sinonimo_id: int):
    """Eliminar sinónimo"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE producto_sinonimos SET activo = 0 WHERE id = %s",
            [sinonimo_id]
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sinónimo no encontrado")
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Sinónimo eliminado correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Iniciando LCLN API Simple en puerto 8004...")
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")