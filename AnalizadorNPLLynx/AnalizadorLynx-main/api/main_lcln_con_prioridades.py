"""
API PRINCIPAL LCLN CON SISTEMA DE PRIORIDADES
Integración del nuevo motor de búsqueda con prioridades inteligentes
Reemplaza/complementa la funcionalidad de main_lcln_dynamic.py

Funcionalidades:
- Motor LCLN con sistema de prioridades (🥇🥈🥉🏃)
- Gestión de sinónimos específicos por producto
- API de administración de sinónimos
- Compatibilidad completa con frontend existente
- Análisis detallado con breakdown de prioridades

Autor: Sistema LCLN v2.0
Fecha: Julio 2025
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import mysql.connector
from datetime import datetime, timedelta
import json
import uvicorn
import time
import traceback

# Importar nuestro sistema mejorado
from sistema_lcln_con_prioridades import sistema_lcln_con_prioridades
from sinonimos_management_api import router as sinonimos_router

# ================================================
# CONFIGURACIÓN DE FASTAPI
# ================================================

app = FastAPI(
    title="LCLN API con Prioridades Inteligentes",
    description="Motor de búsqueda de lenguaje natural con sistema de prioridades para LynxShop",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir router de gestión de sinónimos
app.include_router(sinonimos_router)

# Configuración MySQL
mysql_config = {
    'host': 'localhost',
    'database': 'lynxshop',
    'user': 'root',
    'password': '12345678',
    'charset': 'utf8mb4'
}

# ================================================
# MODELOS PYDANTIC
# ================================================

class ConsultaNLP(BaseModel):
    """Modelo para consulta NLP"""
    query: str = Field(..., min_length=1, max_length=500, description="Consulta del usuario")
    limit: Optional[int] = Field(20, ge=1, le=100, description="Número máximo de resultados")
    user_id: Optional[int] = Field(None, description="ID del usuario para métricas")
    include_debug: Optional[bool] = Field(False, description="Incluir información de debug")

class ConsultaBatch(BaseModel):
    """Modelo para consultas en lote"""
    queries: List[str] = Field(..., max_items=10, description="Lista de consultas")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Número máximo de resultados por consulta")

class RespuestaNLP(BaseModel):
    """Modelo para respuesta NLP mejorada"""
    success: bool
    processing_time_ms: float
    original_query: str
    corrections: Dict[str, Any]
    interpretation: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    products_found: int
    priority_breakdown: Dict[str, Any]
    strategies_used: List[str]
    user_message: str
    metadata: Dict[str, Any]

# ================================================
# VARIABLES GLOBALES PARA MÉTRICAS
# ================================================

# Estadísticas de rendimiento
stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'average_response_time': 0.0,
    'cache_hits': 0,
    'cache_misses': 0,
    'priority_stats': {
        'productos_especificos': 0,
        'atributos_exactos': 0,
        'categoria_relacionada': 0,
        'fallback_correccion': 0
    },
    'start_time': datetime.now(),
    'last_reset': datetime.now()
}

# Cache simple para consultas frecuentes
cache_consultas = {}
CACHE_DURATION = timedelta(minutes=5)

# ================================================
# ENDPOINTS PRINCIPALES
# ================================================

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "LCLN API con Prioridades Inteligentes",
        "version": "2.0.0",
        "status": "active",
        "description": "Motor de búsqueda de lenguaje natural con sistema de prioridades",
        "features": [
            "🥇 Productos específicos por sinónimo directo",
            "🥈 Búsqueda por atributos exactos (sin picante, sin azúcar)",
            "🥉 Búsqueda por categoría relacionada", 
            "🏃 Fallback con corrección ortográfica",
            "📊 Gestión de sinónimos desde admin panel",
            "📈 Métricas y aprendizaje automático"
        ],
        "endpoints": [
            "/api/nlp/analyze - Búsqueda principal",
            "/api/nlp/batch - Búsquedas en lote",
            "/api/health - Estado del servicio",
            "/api/stats - Estadísticas detalladas",
            "/api/admin/sinonimos/* - Gestión de sinónimos"
        ],
        "timestamp": datetime.now()
    }

@app.get("/api/health")
async def health_check():
    """Estado de salud del servicio con métricas detalladas"""
    try:
        # Verificar conexión MySQL
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Verificar tablas críticas
        cursor.execute("SHOW TABLES LIKE 'producto_sinonimos'")
        tabla_sinonimos = cursor.fetchone() is not None
        
        cursor.execute("SHOW TABLES LIKE 'producto_atributos'")
        tabla_atributos = cursor.fetchone() is not None
        
        cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        total_productos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM producto_sinonimos WHERE activo = 1")
        total_sinonimos = cursor.fetchone()[0] if tabla_sinonimos else 0
        
        uptime = datetime.now() - stats['start_time']
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "uptime_seconds": uptime.total_seconds(),
            "system": {
                "mysql_connection": "ok",
                "tabla_sinonimos": tabla_sinonimos,
                "tabla_atributos": tabla_atributos,
                "total_productos": total_productos,
                "total_sinonimos": total_sinonimos
            },
            "performance": {
                "total_requests": stats['total_requests'],
                "success_rate": round((stats['successful_requests'] / max(stats['total_requests'], 1)) * 100, 2),
                "average_response_time_ms": round(stats['average_response_time'], 2),
                "cache_hit_rate": round((stats['cache_hits'] / max(stats['cache_hits'] + stats['cache_misses'], 1)) * 100, 2)
            },
            "priority_usage": stats['priority_stats']
        }
        
        return health_data
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now()
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.post("/api/nlp/analyze", response_model=Dict[str, Any])
async def analizar_consulta_nlp(consulta: ConsultaNLP):
    """
    Endpoint principal de análisis NLP con sistema de prioridades
    """
    inicio = time.time()
    stats['total_requests'] += 1
    
    try:
        query = consulta.query.strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")
        
        # Verificar cache
        cache_key = f"{query}_{consulta.limit}_{consulta.user_id}"
        if cache_key in cache_consultas:
            cache_entry = cache_consultas[cache_key]
            if datetime.now() - cache_entry['timestamp'] < CACHE_DURATION:
                stats['cache_hits'] += 1
                response = cache_entry['data'].copy()
                response['cached'] = True
                response['cache_age_seconds'] = (datetime.now() - cache_entry['timestamp']).total_seconds()
                return response
        
        stats['cache_misses'] += 1
        
        # Procesar con sistema de prioridades
        resultado = sistema_lcln_con_prioridades.buscar_con_prioridades(
            consulta=query,
            limit=consulta.limit,
            user_id=consulta.user_id
        )
        
        # Actualizar estadísticas de prioridades
        if 'strategies_used' in resultado:
            for estrategia in resultado['strategies_used']:
                if estrategia in stats['priority_stats']:
                    stats['priority_stats'][estrategia] += 1
        
        # Agregar información adicional
        resultado['cached'] = False
        resultado['api_version'] = '2.0.0'
        resultado['timestamp'] = datetime.now().isoformat()
        
        # Información de debug si se solicita
        if consulta.include_debug:
            resultado['debug'] = {
                'cache_key': cache_key,
                'mysql_config': {k: v for k, v in mysql_config.items() if k != 'password'},
                'system_stats': stats.copy()
            }
        
        # Guardar en cache
        cache_consultas[cache_key] = {
            'data': resultado.copy(),
            'timestamp': datetime.now()
        }
        
        # Limpiar cache viejo (mantener solo últimas 100 entradas)
        if len(cache_consultas) > 100:
            oldest_keys = sorted(cache_consultas.keys(), 
                               key=lambda k: cache_consultas[k]['timestamp'])[:20]
            for old_key in oldest_keys:
                del cache_consultas[old_key]
        
        stats['successful_requests'] += 1
        return resultado
        
    except HTTPException:
        stats['failed_requests'] += 1
        raise
    except Exception as e:
        stats['failed_requests'] += 1
        error_detail = f"Error interno: {str(e)}"
        
        # En desarrollo, mostrar traceback completo
        if consulta.include_debug:
            error_detail += f"\n\nTraceback:\n{traceback.format_exc()}"
        
        raise HTTPException(status_code=500, detail=error_detail)
    
    finally:
        # Actualizar tiempo promedio de respuesta
        tiempo_respuesta = (time.time() - inicio) * 1000
        if stats['total_requests'] > 0:
            stats['average_response_time'] = (
                (stats['average_response_time'] * (stats['total_requests'] - 1) + tiempo_respuesta) / 
                stats['total_requests']
            )

@app.post("/api/nlp/batch")
async def analizar_batch(consulta_batch: ConsultaBatch):
    """
    Análisis en lote de múltiples consultas
    """
    inicio = time.time()
    
    try:\n        resultados = []\n        \n        for i, query in enumerate(consulta_batch.queries):\n            try:\n                resultado = sistema_lcln_con_prioridades.buscar_con_prioridades(\n                    consulta=query.strip(),\n                    limit=consulta_batch.limit or 10\n                )\n                resultado['batch_index'] = i\n                resultado['batch_query'] = query\n                resultados.append(resultado)\n                \n            except Exception as e:\n                # Error individual no debe fallar todo el batch\n                resultados.append({\n                    'success': False,\n                    'error': str(e),\n                    'batch_index': i,\n                    'batch_query': query,\n                    'original_query': query,\n                    'recommendations': [],\n                    'products_found': 0\n                })\n        \n        tiempo_total = (time.time() - inicio) * 1000\n        \n        return {\n            'success': True,\n            'total_queries': len(consulta_batch.queries),\n            'successful_queries': sum(1 for r in resultados if r.get('success', False)),\n            'failed_queries': sum(1 for r in resultados if not r.get('success', False)),\n            'total_processing_time_ms': round(tiempo_total, 2),\n            'average_time_per_query_ms': round(tiempo_total / len(consulta_batch.queries), 2),\n            'results': resultados,\n            'timestamp': datetime.now().isoformat()\n        }\n        \n    except Exception as e:\n        raise HTTPException(status_code=500, detail=f\"Error en procesamiento batch: {str(e)}\")

@app.get("/api/stats")
async def obtener_estadisticas_detalladas():
    """
    Estadísticas detalladas del sistema
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        # Estadísticas de base de datos
        cursor.execute("SELECT COUNT(*) as total FROM productos WHERE activo = 1")
        total_productos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT producto_id) as total FROM producto_sinonimos WHERE activo = 1")
        productos_con_sinonimos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM producto_sinonimos WHERE activo = 1")
        total_sinonimos = cursor.fetchone()['total']
        
        # Top sinónimos más populares
        cursor.execute("""
            SELECT ps.sinonimo, ps.popularidad, p.nombre as producto
            FROM producto_sinonimos ps
            JOIN productos p ON ps.producto_id = p.id_producto
            WHERE ps.activo = 1
            ORDER BY ps.popularidad DESC
            LIMIT 5
        """)
        top_sinonimos = cursor.fetchall()
        
        # Métricas de búsqueda recientes (si existe la tabla)
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_busquedas,
                    COUNT(DISTINCT termino_busqueda) as terminos_unicos,
                    AVG(clicks) as promedio_clicks
                FROM busqueda_metricas 
                WHERE fecha_busqueda > DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            metricas_busqueda = cursor.fetchone()
        except:
            metricas_busqueda = {'total_busquedas': 0, 'terminos_unicos': 0, 'promedio_clicks': 0}
        
        uptime = datetime.now() - stats['start_time']
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": {
                "seconds": uptime.total_seconds(),
                "formatted": str(uptime).split('.')[0]
            },
            "database": {
                "total_productos": total_productos,
                "productos_con_sinonimos": productos_con_sinonimos,
                "total_sinonimos": total_sinonimos,
                "cobertura_sinonimos": round((productos_con_sinonimos / max(total_productos, 1)) * 100, 1)
            },
            "performance": {
                "total_requests": stats['total_requests'],
                "successful_requests": stats['successful_requests'],
                "failed_requests": stats['failed_requests'],
                "success_rate": round((stats['successful_requests'] / max(stats['total_requests'], 1)) * 100, 2),
                "average_response_time_ms": round(stats['average_response_time'], 2),
                "cache_hits": stats['cache_hits'],
                "cache_misses": stats['cache_misses'],
                "cache_hit_rate": round((stats['cache_hits'] / max(stats['cache_hits'] + stats['cache_misses'], 1)) * 100, 2)
            },
            "priority_usage": stats['priority_stats'],
            "top_synonyms": top_sinonimos,
            "search_metrics_7d": metricas_busqueda,
            "cache_info": {
                "current_entries": len(cache_consultas),
                "max_entries": 100,
                "ttl_minutes": 5
            }\n        }\n        \n    except Exception as e:\n        raise HTTPException(status_code=500, detail=f\"Error obteniendo estadísticas: {str(e)}\")\n    finally:\n        if 'cursor' in locals():\n            cursor.close()\n        if 'conn' in locals():\n            conn.close()

@app.post("/api/force-cache-refresh")
async def forzar_limpieza_cache():
    """
    Forzar limpieza del cache
    """
    global cache_consultas
    entries_antes = len(cache_consultas)
    cache_consultas.clear()
    
    return {
        "success": True,
        "message": f"Cache limpiado. {entries_antes} entradas eliminadas",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/reset-stats")
async def resetear_estadisticas():
    """
    Resetear estadísticas del servicio
    """
    global stats
    stats = {
        'total_requests': 0,
        'successful_requests': 0,
        'failed_requests': 0,
        'average_response_time': 0.0,
        'cache_hits': 0,
        'cache_misses': 0,
        'priority_stats': {
            'productos_especificos': 0,
            'atributos_exactos': 0,
            'categoria_relacionada': 0,
            'fallback_correccion': 0
        },
        'start_time': datetime.now(),
        'last_reset': datetime.now()
    }
    
    return {
        "success": True,
        "message": "Estadísticas reseteadas correctamente",
        "timestamp": datetime.now().isoformat()
    }

# ================================================
# ENDPOINTS DE COMPATIBILIDAD CON SISTEMA ANTERIOR
# ================================================

@app.post("/api/nlp")
async def endpoint_compatibilidad(request: Request):
    """
    Endpoint de compatibilidad con el sistema anterior
    Redirige a /api/nlp/analyze manteniendo la misma funcionalidad
    """
    try:
        data = await request.json()
        consulta = ConsultaNLP(
            query=data.get('query', ''),
            limit=data.get('limit', 20),
            user_id=data.get('user_id'),
            include_debug=data.get('include_debug', False)
        )
        return await analizar_consulta_nlp(consulta)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en endpoint de compatibilidad: {str(e)}")

# ================================================
# MANEJO DE ERRORES GLOBAL
# ================================================

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Manejo global de errores"""
    stats['failed_requests'] += 1
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# ================================================
# STARTUP Y SHUTDOWN EVENTS
# ================================================

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio del servicio"""
    print("🚀 LCLN API con Prioridades Inteligentes iniciando...")
    print("📊 Verificando conexión a base de datos...")
    
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        print("✅ Conexión MySQL establecida")
        
        # Verificar tablas críticas
        cursor.execute("SHOW TABLES LIKE 'producto_sinonimos'")
        if cursor.fetchone():
            print("✅ Tabla producto_sinonimos encontrada")
        else:
            print("⚠️  Tabla producto_sinonimos no encontrada - ejecutar setup_mysql_tables.sql")
        
        cursor.execute("SHOW TABLES LIKE 'producto_atributos'")
        if cursor.fetchone():
            print("✅ Tabla producto_atributos encontrada")
        else:
            print("⚠️  Tabla producto_atributos no encontrada - ejecutar setup_mysql_tables.sql")
            
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    print("🌟 Servicio LCLN con Prioridades listo en puerto 8004")
    print("📖 Documentación disponible en: http://localhost:8004/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre del servicio"""
    print("🔄 Cerrando LCLN API con Prioridades...")
    uptime = datetime.now() - stats['start_time']
    print(f"📊 Estadísticas finales:")
    print(f"   - Tiempo activo: {str(uptime).split('.')[0]}")
    print(f"   - Total requests: {stats['total_requests']}")
    print(f"   - Tasa de éxito: {round((stats['successful_requests'] / max(stats['total_requests'], 1)) * 100, 2)}%")
    print("👋 Servicio cerrado correctamente")

# ================================================
# EJECUCIÓN PRINCIPAL
# ================================================

if __name__ == "__main__":
    print("🔧 Iniciando servidor LCLN con Prioridades...")
    print("📋 Configuración:")
    print(f"   - Host: 0.0.0.0")
    print(f"   - Puerto: 8004") 
    print(f"   - Base de datos: {mysql_config['database']}")
    print(f"   - Auto-reload: True")
    print("")
    
    uvicorn.run(
        "main_lcln_con_prioridades:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )