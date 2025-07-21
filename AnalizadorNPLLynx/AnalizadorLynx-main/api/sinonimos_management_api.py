"""
API DE GESTIÓN DE SINÓNIMOS PARA ADMIN PANEL
Endpoints para crear, leer, actualizar y eliminar sinónimos específicos por producto
Integración con sistema LCLN con prioridades

Autor: Sistema LCLN v2.0
Fecha: Julio 2025
"""

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import mysql.connector
from datetime import datetime, timedelta
import json
import re

# Configuración MySQL
mysql_config = {
    'host': 'localhost',
    'database': 'lynxshop',
    'user': 'root',
    'password': '12345678',
    'charset': 'utf8mb4',
    'autocommit': True
}

# Router para endpoints de sinónimos
router = APIRouter(prefix="/api/admin/sinonimos", tags=["Gestión Sinónimos Admin"])


# ================================================
# MODELOS PYDANTIC
# ================================================

class SinonimoCreate(BaseModel):
    """Modelo para crear nuevo sinónimo"""
    producto_id: int = Field(..., description="ID del producto")
    sinonimo: str = Field(..., min_length=2, max_length=255, description="Término sinónimo")
    fuente: str = Field(default="admin", description="Fuente del sinónimo")
    
    @validator('sinonimo')
    def validar_sinonimo(cls, v):
        # Limpiar y validar sinónimo
        v = v.strip().lower()
        if not re.match(r'^[a-záéíóúñ\s]+$', v):
            raise ValueError('El sinónimo solo puede contener letras y espacios')
        return v
    
    @validator('fuente')
    def validar_fuente(cls, v):
        fuentes_validas = ['admin', 'auto_learning', 'user_feedback']
        if v not in fuentes_validas:
            raise ValueError(f'Fuente debe ser una de: {fuentes_validas}')
        return v


class SinonimoResponse(BaseModel):
    """Modelo para respuesta de sinónimo"""
    id: int
    producto_id: int
    sinonimo: str
    popularidad: int
    precision_score: float
    fuente: str
    activo: bool
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime


class SinonimoUpdate(BaseModel):
    """Modelo para actualizar sinónimo"""
    popularidad: Optional[int] = Field(None, ge=0, description="Popularidad del sinónimo")
    precision_score: Optional[float] = Field(None, ge=0, le=1, description="Precisión del sinónimo")
    activo: Optional[bool] = Field(None, description="Estado activo/inactivo")


class AtributoCreate(BaseModel):
    """Modelo para crear atributo de producto"""
    producto_id: int = Field(..., description="ID del producto")
    atributo: str = Field(..., min_length=2, max_length=100, description="Nombre del atributo")
    valor: bool = Field(..., description="Valor del atributo (True/False)")
    intensidad: int = Field(default=5, ge=1, le=10, description="Intensidad del atributo")
    
    @validator('atributo')
    def validar_atributo(cls, v):
        return v.strip().lower()


class EstadisticasSinonimos(BaseModel):
    """Modelo para estadísticas de sinónimos"""
    total_productos: int
    productos_con_sinonimos: int
    total_sinonimos: int
    sinonimos_populares: List[Dict[str, Any]]
    productos_mas_sinonimos: List[Dict[str, Any]]


# ================================================
# ENDPOINTS DE GESTIÓN DE SINÓNIMOS
# ================================================

@router.get("/producto/{producto_id}", response_model=List[SinonimoResponse])
async def obtener_sinonimos_producto(producto_id: int):
    """
    Obtener todos los sinónimos de un producto específico
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el producto existe
        cursor.execute("SELECT nombre FROM productos WHERE id_producto = %s", [producto_id])
        producto = cursor.fetchone()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Obtener sinónimos del producto
        cursor.execute("""
            SELECT * FROM producto_sinonimos 
            WHERE producto_id = %s
            ORDER BY popularidad DESC, fecha_creacion DESC
        """, [producto_id])
        
        sinonimos = cursor.fetchall()
        return sinonimos
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@router.post("/", response_model=Dict[str, Any])
async def crear_sinonimo(sinonimo: SinonimoCreate):
    """
    Crear nuevo sinónimo para un producto
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Verificar que el producto existe
        cursor.execute("SELECT nombre FROM productos WHERE id_producto = %s", [sinonimo.producto_id])
        producto = cursor.fetchone()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Verificar que el sinónimo no existe ya para este producto
        cursor.execute(
            "SELECT id FROM producto_sinonimos WHERE producto_id = %s AND sinonimo = %s",
            [sinonimo.producto_id, sinonimo.sinonimo]
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Este sinónimo ya existe para este producto")
        
        # Verificar que el sinónimo no está siendo usado por otro producto
        cursor.execute(
            "SELECT p.nombre FROM producto_sinonimos ps JOIN productos p ON ps.producto_id = p.id_producto WHERE ps.sinonimo = %s AND ps.activo = 1",
            [sinonimo.sinonimo]
        )
        producto_conflicto = cursor.fetchone()
        if producto_conflicto:
            raise HTTPException(
                status_code=409, 
                detail=f"El sinónimo '{sinonimo.sinonimo}' ya está asignado al producto: {producto_conflicto[0]}"
            )
        
        # Crear sinónimo
        cursor.execute("""
            INSERT INTO producto_sinonimos 
            (producto_id, sinonimo, fuente, activo, fecha_creacion, fecha_ultima_actualizacion)
            VALUES (%s, %s, %s, 1, %s, %s)
        """, [
            sinonimo.producto_id, 
            sinonimo.sinonimo, 
            sinonimo.fuente,
            datetime.now(),
            datetime.now()
        ])
        
        conn.commit()
        sinonimo_id = cursor.lastrowid
        
        return {
            "success": True,
            "message": "Sinónimo creado correctamente",
            "id": sinonimo_id,
            "sinonimo": sinonimo.sinonimo,
            "producto_id": sinonimo.producto_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@router.put("/{sinonimo_id}", response_model=Dict[str, Any])
async def actualizar_sinonimo(sinonimo_id: int, actualizacion: SinonimoUpdate):
    """
    Actualizar un sinónimo existente
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Verificar que el sinónimo existe
        cursor.execute("SELECT * FROM producto_sinonimos WHERE id = %s", [sinonimo_id])
        sinonimo_actual = cursor.fetchone()
        if not sinonimo_actual:
            raise HTTPException(status_code=404, detail="Sinónimo no encontrado")
        
        # Construir query de actualización dinámica
        campos_actualizar = []
        valores = []
        
        if actualizacion.popularidad is not None:
            campos_actualizar.append("popularidad = %s")
            valores.append(actualizacion.popularidad)
        
        if actualizacion.precision_score is not None:
            campos_actualizar.append("precision_score = %s")
            valores.append(actualizacion.precision_score)
        
        if actualizacion.activo is not None:
            campos_actualizar.append("activo = %s")
            valores.append(actualizacion.activo)
        
        if not campos_actualizar:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        # Actualizar fecha de modificación
        campos_actualizar.append("fecha_ultima_actualizacion = %s")
        valores.append(datetime.now())
        valores.append(sinonimo_id)
        
        query = f"UPDATE producto_sinonimos SET {', '.join(campos_actualizar)} WHERE id = %s"
        cursor.execute(query, valores)
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Sinónimo actualizado correctamente",
            "id": sinonimo_id,
            "campos_actualizados": len(campos_actualizar) - 1  # -1 por la fecha
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@router.delete("/{sinonimo_id}")
async def eliminar_sinonimo(sinonimo_id: int, permanente: bool = Query(False, description="Eliminar permanentemente")):
    """
    Eliminar (desactivar) o eliminar permanentemente un sinónimo
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Verificar que el sinónimo existe
        cursor.execute("SELECT sinonimo FROM producto_sinonimos WHERE id = %s", [sinonimo_id])
        sinonimo = cursor.fetchone()
        if not sinonimo:
            raise HTTPException(status_code=404, detail="Sinónimo no encontrado")
        
        if permanente:
            # Eliminación permanente
            cursor.execute("DELETE FROM producto_sinonimos WHERE id = %s", [sinonimo_id])
            mensaje = f"Sinónimo '{sinonimo[0]}' eliminado permanentemente"
        else:
            # Desactivación (soft delete)
            cursor.execute(
                "UPDATE producto_sinonimos SET activo = 0, fecha_ultima_actualizacion = %s WHERE id = %s",
                [datetime.now(), sinonimo_id]
            )
            mensaje = f"Sinónimo '{sinonimo[0]}' desactivado"
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sinónimo no encontrado")
        
        conn.commit()
        
        return {
            "success": True,
            "message": mensaje,
            "id": sinonimo_id,
            "eliminacion_permanente": permanente
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ================================================
# ENDPOINTS DE GESTIÓN DE ATRIBUTOS
# ================================================

@router.get("/producto/{producto_id}/atributos")
async def obtener_atributos_producto(producto_id: int):
    """
    Obtener todos los atributos de un producto específico
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM producto_atributos 
            WHERE producto_id = %s
            ORDER BY atributo ASC
        """, [producto_id])
        
        atributos = cursor.fetchall()
        return atributos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@router.post("/producto/{producto_id}/atributos")
async def crear_atributo_producto(producto_id: int, atributo: AtributoCreate):
    """
    Crear nuevo atributo para un producto
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Verificar que el producto existe
        cursor.execute("SELECT nombre FROM productos WHERE id_producto = %s", [producto_id])
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Verificar que el atributo no existe ya
        cursor.execute(
            "SELECT id FROM producto_atributos WHERE producto_id = %s AND atributo = %s",
            [producto_id, atributo.atributo]
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Este atributo ya existe para este producto")
        
        # Crear atributo
        cursor.execute("""
            INSERT INTO producto_atributos 
            (producto_id, atributo, valor, intensidad, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s)
        """, [
            producto_id, 
            atributo.atributo, 
            atributo.valor, 
            atributo.intensidad,
            datetime.now()
        ])
        
        conn.commit()
        atributo_id = cursor.lastrowid
        
        return {
            "success": True,
            "message": "Atributo creado correctamente",
            "id": atributo_id,
            "atributo": atributo.atributo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ================================================
# ENDPOINTS DE ESTADÍSTICAS Y ANÁLISIS
# ================================================

@router.get("/estadisticas", response_model=EstadisticasSinonimos)
async def obtener_estadisticas_sinonimos():
    """
    Obtener estadísticas generales del sistema de sinónimos
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        # Estadísticas básicas
        cursor.execute("SELECT COUNT(*) as total FROM productos WHERE activo = 1")
        total_productos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT producto_id) as total FROM producto_sinonimos WHERE activo = 1")
        productos_con_sinonimos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM producto_sinonimos WHERE activo = 1")
        total_sinonimos = cursor.fetchone()['total']
        
        # Sinónimos más populares
        cursor.execute("""
            SELECT ps.sinonimo, ps.popularidad, p.nombre as producto
            FROM producto_sinonimos ps
            JOIN productos p ON ps.producto_id = p.id_producto
            WHERE ps.activo = 1
            ORDER BY ps.popularidad DESC
            LIMIT 10
        """)
        sinonimos_populares = cursor.fetchall()
        
        # Productos con más sinónimos
        cursor.execute("""
            SELECT 
                p.nombre as producto,
                COUNT(ps.sinonimo) as total_sinonimos,
                GROUP_CONCAT(ps.sinonimo ORDER BY ps.popularidad DESC LIMIT 5) as top_sinonimos
            FROM productos p
            LEFT JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id AND ps.activo = 1
            WHERE p.activo = 1
            GROUP BY p.id_producto, p.nombre
            HAVING total_sinonimos > 0
            ORDER BY total_sinonimos DESC
            LIMIT 10
        """)
        productos_mas_sinonimos = cursor.fetchall()
        
        return EstadisticasSinonimos(
            total_productos=total_productos,
            productos_con_sinonimos=productos_con_sinonimos,
            total_sinonimos=total_sinonimos,
            sinonimos_populares=sinonimos_populares,
            productos_mas_sinonimos=productos_mas_sinonimos
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@router.get("/sugerencias/producto/{producto_id}")
async def obtener_sugerencias_sinonimos(producto_id: int, limite: int = Query(10, le=20)):
    """
    Obtener sugerencias de sinónimos basadas en métricas de búsqueda
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el producto existe
        cursor.execute("SELECT nombre FROM productos WHERE id_producto = %s", [producto_id])
        producto = cursor.fetchone()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Obtener términos de búsqueda que resultaron en clicks/conversiones para este producto
        cursor.execute("""
            SELECT 
                bm.termino_busqueda, 
                COUNT(*) as frecuencia,
                AVG(bm.clicks) as promedio_clicks,
                MAX(bm.fecha_busqueda) as ultima_busqueda
            FROM busqueda_metricas bm
            WHERE bm.producto_id = %s 
              AND bm.fecha_busqueda > DATE_SUB(NOW(), INTERVAL 30 DAY)
              AND bm.termino_busqueda NOT IN (
                  SELECT sinonimo FROM producto_sinonimos 
                  WHERE producto_id = %s AND activo = 1
              )
              AND LENGTH(bm.termino_busqueda) > 2
            GROUP BY bm.termino_busqueda
            HAVING frecuencia >= 2 AND promedio_clicks > 0
            ORDER BY frecuencia DESC, promedio_clicks DESC
            LIMIT %s
        """, [producto_id, producto_id, limite])
        
        sugerencias = cursor.fetchall()
        
        # Si no hay métricas, generar sugerencias básicas basadas en el nombre del producto
        if not sugerencias:
            nombre_producto = producto['nombre'].lower()
            sugerencias_basicas = []
            
            # Generar variaciones del nombre
            palabras = nombre_producto.split()
            for palabra in palabras:
                if len(palabra) > 3:
                    sugerencias_basicas.append({
                        'termino_busqueda': palabra,
                        'frecuencia': 0,
                        'promedio_clicks': 0,
                        'ultima_busqueda': None,
                        'tipo': 'sugerencia_basica'
                    })
            
            return {
                'producto_id': producto_id,
                'producto_nombre': producto['nombre'],
                'sugerencias': sugerencias_basicas[:limite],
                'fuente': 'nombre_producto',
                'total_sugerencias': len(sugerencias_basicas)
            }
        
        return {
            'producto_id': producto_id,
            'producto_nombre': producto['nombre'],
            'sugerencias': sugerencias,
            'fuente': 'metricas_busqueda',
            'total_sugerencias': len(sugerencias)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@router.post("/batch/importar")
async def importar_sinonimos_batch(
    sinonimos: List[SinonimoCreate],
    sobrescribir: bool = Query(False, description="Sobrescribir sinónimos existentes")
):
    """
    Importar múltiples sinónimos en lote
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        resultados = {
            'exitosos': 0,
            'fallidos': 0,
            'sobrescritos': 0,
            'errores': []
        }
        
        for sinonimo in sinonimos:
            try:
                # Verificar si existe
                cursor.execute(
                    "SELECT id FROM producto_sinonimos WHERE producto_id = %s AND sinonimo = %s",
                    [sinonimo.producto_id, sinonimo.sinonimo]
                )
                existe = cursor.fetchone()
                
                if existe and sobrescribir:
                    # Actualizar existente
                    cursor.execute("""
                        UPDATE producto_sinonimos 
                        SET fuente = %s, activo = 1, fecha_ultima_actualizacion = %s
                        WHERE id = %s
                    """, [sinonimo.fuente, datetime.now(), existe[0]])
                    resultados['sobrescritos'] += 1
                    
                elif not existe:
                    # Crear nuevo
                    cursor.execute("""
                        INSERT INTO producto_sinonimos 
                        (producto_id, sinonimo, fuente, activo, fecha_creacion, fecha_ultima_actualizacion)
                        VALUES (%s, %s, %s, 1, %s, %s)
                    """, [
                        sinonimo.producto_id, 
                        sinonimo.sinonimo, 
                        sinonimo.fuente,
                        datetime.now(),
                        datetime.now()
                    ])
                    resultados['exitosos'] += 1
                else:
                    # Existe y no se sobrescribe
                    resultados['errores'].append(f"Sinónimo '{sinonimo.sinonimo}' ya existe para producto {sinonimo.producto_id}")
                    resultados['fallidos'] += 1
                    
            except Exception as e:
                resultados['errores'].append(f"Error con sinónimo '{sinonimo.sinonimo}': {str(e)}")
                resultados['fallidos'] += 1
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Procesados {len(sinonimos)} sinónimos",
            "resultados": resultados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ================================================
# FUNCIONES AUXILIARES
# ================================================

def validar_conexion_mysql():
    """
    Validar que la conexión MySQL está funcionando
    """
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return True
    except:
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@router.get("/health")
async def health_check():
    """
    Verificar estado del servicio de sinónimos
    """
    mysql_ok = validar_conexion_mysql()
    
    return {
        "service": "Sinónimos Management API",
        "status": "healthy" if mysql_ok else "unhealthy",
        "mysql_connection": "ok" if mysql_ok else "error",
        "timestamp": datetime.now()
    }