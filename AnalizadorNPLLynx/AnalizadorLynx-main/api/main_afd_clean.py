#!/usr/bin/env python3
"""
API LCLN CON AFDs LIMPIA PARA WINDOWS (SIN EMOJIS)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import mysql.connector
from datetime import datetime
import uvicorn

app = FastAPI(title="LCLN API con AFDs", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class AnalizadorAFD:
    """Analizador AFD simplificado sin emojis"""
    
    def __init__(self):
        self.afd_palabras = {
            # Sinónimos exactos de productos (desde base de datos)
            'coca': 'PRODUCTO_SINONIMO',
            'coca-cola': 'PRODUCTO_SINONIMO',
            'coka': 'PRODUCTO_SINONIMO',
            'cokita': 'PRODUCTO_SINONIMO',
            'coquita': 'PRODUCTO_SINONIMO',
            'kola': 'PRODUCTO_SINONIMO',
            'doritos': 'PRODUCTO_SINONIMO',
            'dorito': 'PRODUCTO_SINONIMO',
            'cheetos': 'PRODUCTO_SINONIMO',
            'cheetos mix': 'PRODUCTO_SINONIMO',
            'chettos': 'PRODUCTO_SINONIMO',
            'chetos': 'PRODUCTO_SINONIMO',  # Variación común
            'crujitos': 'PRODUCTO_SINONIMO',
            'chocolate': 'PRODUCTO_SINONIMO',
            
            # Categorías
            'botana': 'CATEGORIA_GENERICA',
            'snack': 'CATEGORIA_GENERICA',
            'bebida': 'CATEGORIA_GENERICA',
            
            # Atributos
            'barato': 'ATRIBUTO_PRECIO',
            'barata': 'ATRIBUTO_PRECIO',
            'picante': 'ATRIBUTO_SABOR'
        }
    
    def tokenizar(self, consulta: str) -> List[Dict]:
        palabras = consulta.lower().split()
        tokens = []
        
        for palabra in palabras:
            if palabra in self.afd_palabras:
                tokens.append({
                    'tipo': self.afd_palabras[palabra],
                    'valor': palabra
                })
        
        return tokens
    
    def interpretar(self, tokens: List[Dict]) -> Dict:
        interpretacion = {
            'producto_sinonimo': None,
            'categoria': None,
            'filtro_precio': False
        }
        
        for token in tokens:
            if token['tipo'] == 'PRODUCTO_SINONIMO':
                interpretacion['producto_sinonimo'] = token['valor']
            elif token['tipo'] == 'CATEGORIA_GENERICA':
                interpretacion['categoria'] = token['valor']
            elif token['tipo'] == 'ATRIBUTO_PRECIO':
                interpretacion['filtro_precio'] = True
        
        return interpretacion

analizador = AnalizadorAFD()

@app.get("/")
async def root():
    return {"service": "LCLN API con AFDs", "version": "2.0", "status": "active"}

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
            "version": "afd_clean",
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
        
        print(f"PROCESANDO CON AFDs: '{query}'")
        
        # FASE 1: Tokenización AFD
        tokens = analizador.tokenizar(query)
        print(f"Tokens encontrados: {tokens}")
        
        # FASE 2: Interpretación contextual
        interpretacion = analizador.interpretar(tokens)
        print(f"Interpretación: {interpretacion}")
        
        # FASE 3: Búsqueda inteligente
        productos = buscar_productos_afd(interpretacion)
        
        tiempo_ms = (datetime.now() - inicio).total_seconds() * 1000
        
        return {
            'success': True,
            'processing_time_ms': round(tiempo_ms, 2),
            'original_query': consulta.query,
            'corrections': {'applied': False},
            'interpretation': {
                'type': 'afd_clean',
                'tokens': tokens,
                'interpretacion': interpretacion
            },
            'recommendations': productos,
            'products_found': len(productos),
            'user_message': f"AFD encontró {len(productos)} productos inteligentes",
            'metadata': {
                'source': 'afd_clean_system',
                'has_synonyms': bool(interpretacion['producto_sinonimo']),
                'cache_timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"Error en AFD: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_query": consulta.query,
            "recommendations": [],
            "products_found": 0
        }

def buscar_productos_afd(interpretacion: Dict) -> List[Dict]:
    productos = []
    
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        # PRIORIDAD 1: Sinónimo específico
        if interpretacion['producto_sinonimo']:
            sinonimo = interpretacion['producto_sinonimo']
            print(f"Buscando por sinónimo: {sinonimo}")
            
            cursor.execute("""
                SELECT DISTINCT p.*, c.nombre as categoria, ps.sinonimo, ps.popularidad
                FROM productos p
                INNER JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id
                INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE ps.sinonimo = %s AND ps.activo = 1 AND p.cantidad > 0
                ORDER BY ps.popularidad DESC, p.precio ASC
                LIMIT 5
            """, [sinonimo])
            
            resultados = cursor.fetchall()
            print(f"Productos por sinónimo: {len(resultados)}")
            
            for row in resultados:
                producto = {
                    'id': row['id_producto'],
                    'id_producto': row['id_producto'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'price': float(row['precio']),
                    'categoria': row['categoria'],
                    'category': row['categoria'].lower(),
                    'id_categoria': row['id_categoria'],
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.95,
                    'match_reasons': ['afd_sinonimo_exacto'],
                    'source': 'afd_clean',
                    'sinonimo_usado': row['sinonimo']
                }
                productos.append(producto)
        
        # PRIORIDAD 2: Categoría + filtro precio
        if len(productos) < 10 and interpretacion['categoria']:
            categoria = interpretacion['categoria']
            print(f"Buscando por categoría: {categoria}")
            
            # Mapeo categoría
            mapeo = {'botana': 'snacks', 'bebida': 'bebidas'}
            categoria_real = mapeo.get(categoria, categoria)
            
            query_cat = """
                SELECT p.*, c.nombre as categoria
                FROM productos p
                INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE LOWER(c.nombre) = %s AND p.cantidad > 0
            """
            
            params = [categoria_real.lower()]
            
            if interpretacion['filtro_precio']:
                query_cat += " AND p.precio <= 20"
            
            query_cat += " ORDER BY p.precio ASC LIMIT 8"
            
            cursor.execute(query_cat, params)
            resultados_cat = cursor.fetchall()
            
            for row in resultados_cat:
                producto = {
                    'id': row['id_producto'],
                    'id_producto': row['id_producto'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'price': float(row['precio']),
                    'categoria': row['categoria'],
                    'category': row['categoria'].lower(),
                    'id_categoria': row['id_categoria'],
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.8,
                    'match_reasons': ['afd_categoria'],
                    'source': 'afd_clean'
                }
                productos.append(producto)
        
        print(f"Total productos encontrados: {len(productos)}")
        return productos[:10]
        
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Iniciando LCLN API con AFDs (versión limpia) en puerto 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8007, log_level="info")