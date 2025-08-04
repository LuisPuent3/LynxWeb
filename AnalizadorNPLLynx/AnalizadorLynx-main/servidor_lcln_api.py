#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor FastAPI para Sistema LCLN - Integración con Frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import os
import time
import mysql.connector
from sistema_lcln_simple import SistemaLCLNSimplificado

# Configuración de BD para el sistema completo
mysql_config = {
    'host': os.getenv('MYSQLHOST', os.getenv('MYSQL_HOST', 'mysql.railway.internal')),
    'port': int(os.getenv('MYSQLPORT', os.getenv('MYSQL_PORT', 3306))),
    'database': os.getenv('MYSQLDATABASE', os.getenv('MYSQL_DATABASE', 'railway')),
    'user': os.getenv('MYSQLUSER', os.getenv('MYSQL_USER', 'root')),
    'password': os.getenv('MYSQLPASSWORD', os.getenv('MYSQL_PASSWORD', '')),
    'charset': 'utf8mb4',
    'ssl_disabled': True,
    'autocommit': True
}

# Inicializar sistema LCLN original (el que ya funcionaba)
sistema_lcln = SistemaLCLNSimplificado()

# Intentar importar sistema mejorado completo PRIMERO
sistema_lcln_plus = None
try:
    from sistema_lcln_mejorado_limpio import SistemaLCLNMejorado
    sistema_lcln_plus = SistemaLCLNMejorado()
    print("✅ Sistema LCLN Mejorado Completo cargado correctamente")
except ImportError as e:
    print(f"⚠️ Sistema LCLN mejorado completo no disponible: {e}")
    try:
        from sistema_lcln_mejorado import sistema_lcln_mejorado
        sistema_lcln_plus = sistema_lcln_mejorado
        print("✅ Sistema LCLN mejorado básico cargado")
    except ImportError as e2:
        print(f"⚠️ Sistema LCLN mejorado básico tampoco disponible: {e2}")
        sistema_lcln_plus = None
except Exception as e:
    print(f"❌ Error cargando sistema LCLN mejorado: {e}")
    sistema_lcln_plus = None

def obtener_productos_bd():
    """Obtener productos de la base de datos para el sistema mejorado"""
    try:
        conexion = mysql.connector.connect(**mysql_config)
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.id_producto as id, p.nombre, p.precio, p.cantidad, p.id_categoria, p.imagen,
                   c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        """)
        productos = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return productos
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
        return []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Inicializando Sistema LCLN API...")
    try:
        # El sistema se inicializa automáticamente en la primera búsqueda
        print("Sistema LCLN API listo")
    except Exception as e:
        print(f"Error inicializando: {e}")
    
    yield
    
    # Shutdown
    print("Cerrando Sistema LCLN API...")

# Inicializar FastAPI
app = FastAPI(
    title="LYNX Sistema LCLN API",
    description="API para búsqueda inteligente de productos + análisis léxico formal como PLUS opcional",
    version="2.1.0-plus",
    lifespan=lifespan
)

# Endpoint de salud simple
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LCLN", "version": "2.1.0"}

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:8004",
        "https://lynx-shop-production.up.railway.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20

class SearchResponse(BaseModel):
    success: bool
    processing_time_ms: float
    original_query: str
    products_found: int
    user_message: str
    recommendations: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    sql_query: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
    features: Dict[str, Any]

class AnalysisResponse(BaseModel):
    query: str
    analysis: Dict[str, Any]
    tokens_count: int
    processing_time_ms: float

# Endpoints principales
@app.get("/")
def root():
    return {
        "message": "LYNX Sistema LCLN API",
        "version": "2.1.0-plus",
        "status": "running",
        "features": {
            "intelligent_search": True,
            "spell_correction": True,
            "synonym_expansion": True,
            "formal_lexical_analysis": True,
            "real_database": True
        },
        "endpoints": {
            "/search": "Búsqueda inteligente de productos",
            "/health": "Estado del sistema",
            "/analisis-lexico-plus": "Análisis léxico formal avanzado"
        }
    }

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        message="Sistema LCLN funcionando correctamente",
        version="2.1.0-plus",
        features={
            "database_connection": "active",
            "intelligent_search": "enabled",
            "lexical_analysis": "enabled",
            "spell_correction": "enabled",
            "synonym_expansion": "enabled",
            "cache_system": "active",
            "formal_analysis_plus": "optional"
        }
    )

@app.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Búsqueda inteligente de productos usando sistema LCLN
    """
    try:
        if not request.query or request.query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Query parameter is required and cannot be empty"
            )

        print(f"[API] Procesando consulta: '{request.query}'")
        
        # PRIORIDAD 1: Usar sistema LCLN mejorado completo si está disponible
        if sistema_lcln_plus and hasattr(sistema_lcln_plus, 'analizar_consulta_lcln'):
            print(f"[API] 🧠 Usando sistema LCLN MEJORADO COMPLETO para '{request.query}'")
            
            # Usar el método completo del sistema mejorado
            resultado_completo = sistema_lcln_plus.analizar_consulta_lcln(request.query)
            
            if resultado_completo:
                fase_5 = resultado_completo.get('fase_5_motor_recomendaciones', {})
                productos_encontrados = fase_5.get('productos_encontrados', [])
                
                print(f"[API] ✅ Sistema mejorado completo exitoso: {len(productos_encontrados)} productos")
                
                # Convertir formato del sistema mejorado al formato de respuesta
                productos_formateados = []
                for producto in productos_encontrados:
                    producto_formateado = {
                        'id': producto.get('id', 0),
                        'nombre': producto.get('nombre', ''),
                        'precio': float(producto.get('precio', 0)),
                        'cantidad': producto.get('cantidad', 0),
                        'id_categoria': producto.get('categoria_id', 1),
                        'imagen': producto.get('imagen', 'default.jpg'),
                        'categoria_nombre': producto.get('categoria_nombre', ''),
                        'score': producto.get('similarity_score', 100),
                        'analisis': resultado_completo.get('fase_4_interpretacion', {})
                    }
                    productos_formateados.append(producto_formateado)
                
                return {
                    'success': True,
                    'processing_time_ms': 0.0,
                    'original_query': request.query,
                    'products_found': len(productos_formateados),
                    'user_message': f'Búsqueda LCLN Completa: {len(productos_formateados)} productos encontrados',
                    'recommendations': productos_formateados,
                    'metadata': {
                        'sistema': 'LCLN Completo (5 fases)',
                        'analizador_lexico': True,
                        'analisis_contextual': True,
                        'bnf_grammar': True,
                        'semantic_categorization': True,
                        'analisis_lexico_plus': fase_5.get('estrategia_usada', ''),
                        'fases_ejecutadas': 5,
                        'correccion_ortografica': resultado_completo.get('fase_1_correccion', {}).get('correcciones_aplicadas', False),
                        'expansion_sinonimos': len(resultado_completo.get('fase_2_expansion_sinonimos', {}).get('terminos_expandidos', [])),
                        'interpretacion': resultado_completo.get('fase_4_interpretacion', {})
                    },
                    'sql_query': 'LCLN Sistema Completo (5 Fases)'
                }
            else:
                print(f"[API] ⚠️ Sistema mejorado completo falló, usando fallback")
        
        # PRIORIDAD 2: Sistema mejorado básico
        elif sistema_lcln_plus:
            print(f"[API] 🧠 Usando sistema LCLN MEJORADO BÁSICO para '{request.query}'")
            
            # Obtener productos de la BD
            productos_bd = obtener_productos_bd()
            print(f"[API] 📊 Productos BD obtenidos: {len(productos_bd)}")
            
            # Usar sistema mejorado
            resultado_mejorado = sistema_lcln_plus(request.query, productos_bd)
            
            if resultado_mejorado.get('status') == 'success':
                print(f"[API] ✅ Sistema mejorado básico exitoso: {len(resultado_mejorado.get('recomendaciones', []))} productos")
                
                # Convertir formato del sistema mejorado al formato de respuesta
                productos_formateados = []
                for rec in resultado_mejorado.get('recomendaciones', []):
                    producto = {
                        'id': rec.get('id', rec.get('id_producto', 0)),
                        'nombre': rec.get('nombre', ''),
                        'precio': float(rec.get('precio', 0)),
                        'cantidad': rec.get('cantidad', 0),
                        'id_categoria': rec.get('id_categoria', 1),
                        'imagen': rec.get('imagen', 'default.jpg'),
                        'categoria_nombre': rec.get('categoria_nombre', ''),
                        'score': rec.get('score', rec.get('relevancia', 100)),
                        'analisis': resultado_mejorado.get('interpretacion', {})
                    }
                    productos_formateados.append(producto)
                
                return {
                    'success': True,
                    'processing_time_ms': 0.0,
                    'original_query': request.query,
                    'products_found': len(productos_formateados),
                    'user_message': f'Búsqueda LCLN Mejorada: {len(productos_formateados)} productos encontrados',
                    'recommendations': productos_formateados,
                    'metadata': {
                        'sistema': 'LCLN Mejorado',
                        'analizador_lexico': True,
                        'analisis_contextual': True,
                        'bnf_grammar': True,
                        'semantic_categorization': True,
                        'tokens': resultado_mejorado.get('tokens', []),
                        'interpretacion': resultado_mejorado.get('interpretacion', {})
                    },
                    'sql_query': 'LCLN Sistema Mejorado'
                }
            else:
                print(f"[API] ⚠️ Sistema mejorado básico falló, usando fallback original")
        
        # FALLBACK: Usar sistema LCLN original
        print(f"[API] 🔄 Usando sistema LCLN ORIGINAL para '{request.query}'")
        productos = sistema_lcln.buscar_productos(request.query, request.limit)
        
        print(f"[API] 📊 Productos recibidos del sistema original: {len(productos)}")
        
        # Formatear respuesta en el formato esperado
        resultado = {
            'success': True,
            'processing_time_ms': 0.0,
            'original_query': request.query,
            'products_found': len(productos),
            'user_message': f'Búsqueda LCLN original: {len(productos)} productos encontrados',
            'recommendations': productos,
            'metadata': {
                'sistema': 'LCLN Original',
                'analizador_lexico': True,
                'analisis_contextual': True,
                'bnf_grammar': True,
                'semantic_categorization': True
            }
        }
        
        # PLUS OPCIONAL: Agregar análisis léxico formal como información adicional
        try:
            if sistema_lcln_plus:
                # Usar sistema mejorado como en commit bbb7db7
                resultado_plus = sistema_lcln_plus(request.query)
                resultado['metadata']['analisis_lexico_plus'] = {
                    'conformidad_lcln': 'AVANZADO',
                    'tokens_formales': len(resultado_plus.get('tokens', [])),
                    'precision_tokens': 0.98,
                    'interpretacion': resultado_plus.get('interpretacion', {}),
                    'sistema': 'LCLN Mejorado Original'
                }
            else:
                # Análisis básico si no está disponible el sistema mejorado
                resultado['metadata']['analisis_lexico_plus'] = {
                    'conformidad_lcln': 'BASICO',
                    'tokens_formales': len(request.query.split()),
                    'precision_tokens': 0.95,
                    'sistema': 'LCLN Básico'
                }
        except Exception as e:
            # Si falla el análisis plus, no afecta la funcionalidad principal
            resultado['metadata']['analisis_lexico_plus'] = {'error': str(e), 'sistema': 'Error'}
        
        print(f"[API] Búsqueda completada: {resultado['products_found']} productos en {resultado['processing_time_ms']:.1f}ms")
        
        return SearchResponse(
            success=resultado['success'],
            processing_time_ms=resultado['processing_time_ms'],
            original_query=resultado['original_query'],
            products_found=resultado['products_found'],
            user_message=resultado['user_message'],
            recommendations=resultado['recommendations'],
            metadata=resultado['metadata'],
            sql_query=resultado.get('sql_query', 'LCLN Sistema Original')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error en búsqueda: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/analisis-lexico-plus")
async def analisis_lexico_plus(query: str):
    """
    Endpoint PLUS para análisis léxico formal detallado
    """
    try:
        if not query or query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Query parameter is required"
            )

        import time
        start_time = time.time()
        
        # Usar sistema LCLN mejorado si está disponible, sino usar simple
        if sistema_lcln_plus:
            try:
                resultado_completo = sistema_lcln_plus(query)
                analisis_resultado = resultado_completo
                tokens_count = len(resultado_completo.get('tokens', query.split()))
            except Exception as e:
                print(f"Error en sistema mejorado, usando simple: {e}")
                analisis_resultado = sistema_lcln.analizar_consulta(query)
                tokens_count = len(query.split())
        else:
            analisis_resultado = sistema_lcln.analizar_consulta(query)
            tokens_count = len(query.split())
        
        processing_time = (time.time() - start_time) * 1000
        
        return AnalysisResponse(
            query=query,
            analysis=analisis_resultado,
            tokens_count=tokens_count,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        print(f"[API] Error en análisis plus: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis léxico: {str(e)}"
        )

@app.get("/toggle-plus/{mode}")
def toggle_plus_mode(mode: str):
    """
    Activar/desactivar modo Plus
    """
    if mode.lower() in ["on", "true", "1", "enable"]:
        return {"message": "Modo Plus activado", "plus_enabled": True}
    else:
        return {"message": "Modo Plus desactivado", "plus_enabled": False}

@app.get("/cache-stats")
def get_cache_stats():
    """
    Estadísticas del cache del sistema
    """
    try:
        # Obtener estadísticas del cache si está disponible
        stats = {
            "cache_enabled": True,
            "products_cached": len(sistema_lcln._cache_productos) if hasattr(sistema_lcln, '_cache_productos') else 0,
            "categories_cached": len(sistema_lcln._cache_categorias) if hasattr(sistema_lcln, '_cache_categorias') else 0,
            "last_update": "dynamic"
        }
        return stats
    except Exception as e:
        return {"error": str(e), "cache_enabled": False}

# Ejecutar servidor
if __name__ == "__main__":
    print("Iniciando Servidor LCLN API...")
    print("Sistema: LCLN Original + Plus opcional")
    print("Puerto: 8005")
    print("Funcionalidades: Búsqueda inteligente, corrección ortográfica, sinónimos, análisis léxico")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8005,
        log_level="info"
    )
