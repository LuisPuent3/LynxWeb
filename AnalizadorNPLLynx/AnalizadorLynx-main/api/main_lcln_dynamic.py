#!/usr/bin/env python3
"""
API LYNX NLP LCLN - FastAPI con Sistema Dinámico
Integra el Sistema LCLN con la API existente para máxima compatibilidad
"""

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from datetime import datetime
from sistema_lcln_mejorado import sistema_lcln_mejorado

# Inicializar FastAPI
app = FastAPI(
    title="LYNX LCLN Dynamic NLP API",
    description="Sistema LCLN dinámico con productos reales MySQL + imágenes",
    version="6.0.0-lcln-dynamic",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class QueryRequest(BaseModel):
    query: str

class BatchQueryRequest(BaseModel):
    queries: list[str]

# Usar la instancia global del sistema LCLN mejorado con extensiones formales
sistema_lcln = sistema_lcln_mejorado

@app.get("/")
def root():
    return {
        "message": "LYNX LCLN Dynamic NLP API",
        "version": "6.0.0-lcln-dynamic", 
        "features": [
            "Sistema LCLN completo segun documentacion tecnica",
            "AFD formal con analisis lexico avanzado",
            "Analizador sintactico con gramaticas BNF",
            "Reglas de desambiguacion RD1-RD4",
            "Validacion gramatical completa",
            "Cache dinamico que se actualiza automaticamente",
            "Soporte completo para nuevas categorias/productos",
            "Imagenes incluidas en respuestas",
            "5 estrategias de busqueda inteligente"
        ],
        "products_source": "mysql_lynxshop_dynamic_cache",
        "status": "active"
    }

@app.get("/api/health")
def health_check():
    """Health check con estadísticas dinámicas"""
    try:
        # Forzar actualización del cache para estadísticas actuales
        sistema_lcln._actualizar_cache_dinamico()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "6.0.0-lcln-dynamic",
            "components": {
                "database": "mysql_dynamic_cache",
                "products": f"{len(sistema_lcln._cache_productos)} productos con imágenes",
                "categories": f"{len(sistema_lcln._cache_categorias)} categorías dinámicas",
                "cache_updated": sistema_lcln._cache_timestamp.isoformat() if sistema_lcln._cache_timestamp else "never",
                "mode": "lcln_dynamic_adaptive"
            },
            "features": {
                "adaptive_to_new_products": True,
                "adaptive_to_new_categories": True,
                "images_included": True,
                "cache_auto_refresh": True,
                "multiple_search_strategies": 5
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/api/nlp/analyze")
def analyze_lcln_dynamic(request: QueryRequest):
    """
    Endpoint principal - Análisis NLP con Sistema LCLN Dinámico
    Se adapta automáticamente cuando el admin agrega productos/categorías
    """
    try:
        # Usar el análisis completo formal LCLN con todas las extensiones
        resultado = sistema_lcln.obtener_analisis_completo_formal(request.query)
        
        # Extraer datos del nuevo formato
        resumen = resultado['resumen_ejecutivo']
        productos_encontrados = resultado['fase_5_motor_recomendaciones']['productos_encontrados']
        correcciones = resultado['fase_1_correccion']['correcciones'] if resultado['fase_1_correccion']['correcciones_aplicadas'] else []
        
        # Preparar respuesta compatible con frontend existente + nuevas extensiones formales
        respuesta = {
            "success": True,
            "processing_time_ms": 50,  # Valor por defecto
            "original_query": request.query,
            "corrections": [corr['palabra_corregida'] for corr in correcciones],
            "interpretation": {
                "type": resumen['estrategia_usada'],
                "termino_busqueda": request.query,
                "categoria": "detectada_automaticamente",
                "estrategia_usada": resumen['estrategia_usada']
            },
            "recommendations": productos_encontrados,
            "user_message": f"Se encontraron {resumen['productos_encontrados']} productos usando {resumen['estrategia_usada']}",
            "metadata": {
                "products_found": resumen['productos_encontrados'],
                "has_corrections": len(correcciones) > 0,
                "source": "lcln_formal_completo",
                "productos_comprables": True,
                "database_real": True,
                "imagenes_incluidas": True,
                "adaptativo": True,
                # NUEVOS METADATOS FORMALES
                "modo_analisis": resumen['modo_analisis'],
                "conformidad_lcln": resumen['conformidad_lcln'],
                "tokens_formales_count": resumen['tokens_formales_count'],
                "validacion_gramatical": resumen.get('validacion_gramatical', None)
            },
            "sql_query": f"LCLN Formal Query - Strategy: {resumen['estrategia_usada']}"
        }
        
        # AGREGAR DATOS FORMALES ADICIONALES (opcionales para analisis avanzado)
        if resultado.get('fase_afd_lexico'):
            respuesta['analisis_formal'] = {
                "afd_lexico": {
                    "total_tokens": resultado['fase_afd_lexico']['estadisticas']['total_tokens'],
                    "tokens_reconocidos": resultado['fase_afd_lexico']['estadisticas']['tokens_reconocidos'],
                    "precision": resultado['fase_afd_lexico']['estadisticas']['precision_reconocimiento'],
                    "tabla_tokens": resultado['fase_afd_lexico']['tabla_tokens']
                }
            }
            
        if resultado.get('fase_analisis_sintactico'):
            if 'analisis_formal' not in respuesta:
                respuesta['analisis_formal'] = {}
            respuesta['analisis_formal']['analisis_sintactico'] = {
                "estructura_valida": resultado['fase_analisis_sintactico']['valida'],
                "tipo_gramatica": resultado['fase_analisis_sintactico'].get('tipo_gramatica'),
                "entidad_prioritaria": resultado['fase_analisis_sintactico'].get('entidad_prioritaria'),
                "reglas_aplicadas": resultado['fase_analisis_sintactico'].get('reglas_aplicadas', [])
            }
            
        if resultado.get('validacion_gramatical'):
            if 'analisis_formal' not in respuesta:
                respuesta['analisis_formal'] = {}
            respuesta['analisis_formal']['validacion_gramatical'] = resultado['validacion_gramatical']
        
        return respuesta
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis LCLN: {str(e)}")

@app.post("/api/nlp/batch")
def analyze_batch_lcln(request: BatchQueryRequest):
    """
    Análisis en lote para múltiples consultas
    """
    try:
        resultados = []
        
        for query in request.queries:
            # Usar análisis completo formal pero con menos productos
            resultado_individual = sistema_lcln.obtener_analisis_completo_formal(query)
            resumen = resultado_individual['resumen_ejecutivo']
            productos = resultado_individual['fase_5_motor_recomendaciones']['productos_encontrados'][:5]
            
            resultados.append({
                "query": query,
                "success": True,
                "products_found": resumen['productos_encontrados'],
                "products": productos,
                "strategy": resumen['estrategia_usada'],
                # Datos formales adicionales para batch
                "conformidad_lcln": resumen['conformidad_lcln'],
                "tokens_formales": resumen['tokens_formales_count']
            })
        
        return {
            "success": True,
            "total_queries": len(request.queries),
            "results": resultados,
            "processing_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis batch: {str(e)}")

@app.get("/api/stats")
def get_stats():
    """
    Estadísticas detalladas del sistema
    """
    try:
        # Actualizar cache para estadísticas frescas
        sistema_lcln._actualizar_cache_dinamico()
        
        # Análisis por categorías
        productos_por_categoria = {}
        precios_por_categoria = {}
        
        for producto in sistema_lcln._cache_productos.values():
            categoria = producto['categoria']
            
            # Contar productos por categoría
            if categoria not in productos_por_categoria:
                productos_por_categoria[categoria] = 0
            productos_por_categoria[categoria] += 1
            
            # Precios por categoría
            if categoria not in precios_por_categoria:
                precios_por_categoria[categoria] = []
            precios_por_categoria[categoria].append(producto['precio'])
        
        # Calcular estadísticas de precios
        estadisticas_precios = {}
        for categoria, precios in precios_por_categoria.items():
            estadisticas_precios[categoria] = {
                "min": min(precios),
                "max": max(precios),
                "promedio": sum(precios) / len(precios)
            }
        
        return {
            "sistema": "LCLN Dynamic",
            "timestamp": datetime.now().isoformat(),
            "cache_actualizado": sistema_lcln._cache_timestamp.isoformat(),
            "totales": {
                "productos": len(sistema_lcln._cache_productos),
                "categorias": len(sistema_lcln._cache_categorias),
                "con_imagenes": sum(1 for p in sistema_lcln._cache_productos.values() if p['imagen'] != 'default.jpg')
            },
            "productos_por_categoria": productos_por_categoria,
            "estadisticas_precios": estadisticas_precios,
            "categorias_disponibles": list(sistema_lcln._cache_categorias.keys()),
            "adaptabilidad": {
                "se_actualiza_automaticamente": True,
                "detecta_nuevas_categorias": True,
                "detecta_nuevos_productos": True,
                "mantiene_imagenes": True
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/nlp/analyze-formal")
def analyze_formal_complete(request: QueryRequest):
    """
    NUEVO - Endpoint de Analisis LCLN FORMAL COMPLETO
    Devuelve todos los datos del AFD, analisis sintactico y validacion gramatical
    """
    try:
        # Análisis completo formal sin filtrar ningún dato
        resultado_completo = sistema_lcln.obtener_analisis_completo_formal(request.query)
        
        return {
            "success": True,
            "query": request.query,
            "timestamp": datetime.now().isoformat(),
            
            # Resumen ejecutivo
            "resumen_ejecutivo": resultado_completo['resumen_ejecutivo'],
            
            # Todas las fases del análisis
            "fase_1_correccion": resultado_completo['fase_1_correccion'],
            "fase_2_expansion_sinonimos": resultado_completo['fase_2_expansion_sinonimos'],
            "fase_3_tokenizacion": resultado_completo['fase_3_tokenizacion'],
            "fase_4_interpretacion": resultado_completo['fase_4_interpretacion'],
            "fase_5_motor_recomendaciones": resultado_completo['fase_5_motor_recomendaciones'],
            
            # Fases formales nuevas
            "fase_afd_lexico": resultado_completo.get('fase_afd_lexico'),
            "fase_analisis_sintactico": resultado_completo.get('fase_analisis_sintactico'),
            "validacion_gramatical": resultado_completo.get('validacion_gramatical'),
            
            # Metadatos técnicos
            "metadatos_tecnicos": {
                "modo_analisis_formal_activo": sistema_lcln.modo_analisis_formal,
                "version_sistema": "LCLN_FORMAL_COMPLETO",
                "cache_timestamp": sistema_lcln._cache_timestamp.isoformat() if sistema_lcln._cache_timestamp else None,
                "productos_en_cache": len(sistema_lcln._cache_productos),
                "categorias_en_cache": len(sistema_lcln._cache_categorias)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis formal completo: {str(e)}")

@app.get("/api/toggle-formal-mode/{mode}")
def toggle_formal_mode(mode: bool):
    """
    Endpoint para activar/desactivar el modo de analisis formal
    """
    try:
        sistema_lcln.modo_analisis_formal = mode
        
        return {
            "success": True,
            "modo_analisis_formal": sistema_lcln.modo_analisis_formal,
            "message": f"Modo formal {'activado' if mode else 'desactivado'}",
            "impacto": {
                "rendimiento": "Mayor precisión, algo más lento" if mode else "Más rápido, menos análisis formal",
                "funcionalidades": "AFD + BNF + RD1-4 + Validación" if mode else "Solo análisis tradicional"
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/force-cache-refresh")
def force_cache_refresh():
    """
    Forzar actualización del cache (útil después de que admin agrega productos)
    """
    try:
        # Resetear timestamp para forzar actualización
        sistema_lcln._cache_timestamp = None
        sistema_lcln._actualizar_cache_dinamico()
        
        return {
            "success": True,
            "message": "Cache actualizado exitosamente",
            "timestamp": sistema_lcln._cache_timestamp.isoformat(),
            "productos_cargados": len(sistema_lcln._cache_productos),
            "categorias_cargadas": len(sistema_lcln._cache_categorias)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    
    print("[INICIO] LYNX LCLN FORMAL Dynamic NLP API...")
    print("[FORMAL] Sistema LCLN completo con extensiones formales:")
    print("   - AFD (Automata Finito Determinista) con tokenizacion formal")
    print("   - Analizador sintactico con gramaticas BNF")
    print("   - Reglas de desambiguacion RD1-RD4")
    print("   - Validacion gramatical completa")
    print("[SISTEMA] Sistema adaptativo para productos dinamicos")
    print("[IMAGENES] Imagenes incluidas automaticamente")
    print("[CACHE] Cache que se actualiza cada 5 minutos")
    print("")
    print("[ENDPOINTS] Endpoints disponibles:")
    print("   - /api/nlp/analyze (compatible con frontend)")
    print("   - /api/nlp/analyze-formal (analisis formal completo)")
    print("   - /api/toggle-formal-mode/{true|false} (activar/desactivar)")
    print("")
    print(f"[CONFIG] Modo analisis formal: {'ACTIVO' if sistema_lcln.modo_analisis_formal else 'DESACTIVADO'}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8005,  # Puerto cambiado para evitar conflicto
        log_level="info"
    )
