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
import sys
import os

# Importar el sistema LCLN original como fallback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sistema_lcln_simple import SistemaLCLNSimplificado
    sistema_lcln_fallback = SistemaLCLNSimplificado()
    print("Sistema LCLN fallback cargado correctamente")
except ImportError as e:
    print(f"No se pudo cargar sistema LCLN fallback: {e}")
    sistema_lcln_fallback = None

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
        
        print(f"🧠 SISTEMA HÍBRIDO: AFD + LCLN Simple para: '{query}'")
        
        # 🥇 PRIORIDAD 1: Intentar con sistema AFD inteligente
        productos_afd = buscar_por_sinonimos(query)  # Mi nueva función con AFDs
        
        if productos_afd and len(productos_afd) >= 3:  # AFD encontró resultados relevantes
            tiempo_ms = (datetime.now() - inicio).total_seconds() * 1000
            print(f"✅ AFD encontró {len(productos_afd)} productos relevantes")
            return {
                'success': True,
                'processing_time_ms': round(tiempo_ms, 2),
                'original_query': consulta.query,
                'corrections': {'applied': False}, 
                'interpretation': {
                    'type': 'afd_lcln_inteligente',
                    'estrategia_usada': 'afd_multi_nivel',
                    'termino_busqueda': query
                },
                'recommendations': productos_afd,
                'products_found': len(productos_afd),
                'user_message': f"🧠 AFD-LCLN: {len(productos_afd)} productos por análisis inteligente",
                'metadata': {
                    'search_type': 'afd_intelligent',
                    'has_synonyms': True,
                    'source': 'afd_lcln_motor',
                    'productos_comprables': True,
                    'database_real': True,
                    'imagenes_incluidas': True,
                    'adaptativo': True,
                    'cache_timestamp': datetime.now().isoformat()
                },
                'sql_query': "AFD Multi-Level Intelligent Query"
            }
        
        # 🥈 FALLBACK 1: Sistema LCLN simple si AFD no es suficiente
        print("🔄 AFD insuficiente, usando sistema LCLN simple...")
        if sistema_lcln_fallback:
            resultado_lcln = sistema_lcln_fallback.buscar_productos_inteligente(query, limit=consulta.limit or 10)
            if resultado_lcln['success'] and resultado_lcln['products_found'] > 0:
                print(f"✅ LCLN Simple encontró {resultado_lcln['products_found']} productos")
                # Agregar información de que se usó fallback
                resultado_lcln['user_message'] = f"🔄 LCLN-Simple: {resultado_lcln['products_found']} productos encontrados"
                resultado_lcln['metadata']['source'] = 'lcln_simple_fallback'
                return resultado_lcln
        
        # 🥉 FALLBACK 2: Búsqueda básica como último recurso
        print("⚠️ Usando búsqueda básica de último recurso...")
        productos_general = buscar_general(query)
        return formatear_respuesta(productos_general, consulta, inicio, "basic_fallback")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_query": consulta.query,
            "recommendations": [],
            "products_found": 0
        }

# ============================================
# IMPLEMENTACIÓN DE AFDs (AUTÓMATAS FINITOS DETERMINISTAS)
# Según arquitectura de flujo.md
# ============================================

class AnalizadorLexicoAFD:
    """
    Analizador Léxico Multi-AFD según tu arquitectura:
    - AFD_Multipalabra: productos de múltiples palabras 
    - AFD_Palabras: clasificación de palabras individuales
    - AFD_Operadores: operadores de comparación 
    - AFD_Números: valores numéricos
    """
    
    def __init__(self):
        # AFD_Multipalabra: productos complejos
        self.afd_multipalabra = {
            'coca cola': 'PRODUCTO_MULTIPALABRA',
            'coca cola sin azucar': 'PRODUCTO_COMPLETO',
            'coca sin azucar': 'PRODUCTO_COMPLETO',
            'agua mineral': 'PRODUCTO_MULTIPALABRA',
            'agua natural': 'PRODUCTO_MULTIPALABRA'
        }
        
        # AFD_Palabras: clasificación individual
        self.afd_palabras = {
            # Productos específicos
            'coca': 'PRODUCTO_SINONIMO',
            'coka': 'PRODUCTO_SINONIMO', 
            'coquita': 'PRODUCTO_SINONIMO',
            'doritos': 'PRODUCTO_SINONIMO',
            'cheetos': 'PRODUCTO_SINONIMO',
            'chettos': 'PRODUCTO_SINONIMO',
            'sprite': 'PRODUCTO_SINONIMO',
            
            # Categorías genéricas
            'botana': 'CATEGORIA_GENERICA',
            'botanas': 'CATEGORIA_GENERICA',
            'snack': 'CATEGORIA_GENERICA',
            'snacks': 'CATEGORIA_GENERICA',
            'bebida': 'CATEGORIA_GENERICA',
            'bebidas': 'CATEGORIA_GENERICA',
            'refresco': 'CATEGORIA_GENERICA',
            'fruta': 'CATEGORIA_GENERICA',
            'frutas': 'CATEGORIA_GENERICA',
            
            # Atributos de precio
            'barato': 'ATRIBUTO_PRECIO',
            'barata': 'ATRIBUTO_PRECIO',
            'baratos': 'ATRIBUTO_PRECIO',
            'economico': 'ATRIBUTO_PRECIO',
            'caro': 'ATRIBUTO_PRECIO',
            
            # Atributos de sabor
            'picante': 'ATRIBUTO_SABOR',
            'dulce': 'ATRIBUTO_SABOR',
            'salado': 'ATRIBUTO_SABOR',
            
            # Negaciones
            'sin': 'NEGACION',
            'no': 'NEGACION',
            'libre': 'NEGACION'
        }
        
        # AFD_Operadores
        self.afd_operadores = {
            'menor a': 'OP_MENOR',
            'menos de': 'OP_MENOR',
            'mayor a': 'OP_MAYOR',
            'mas de': 'OP_MAYOR',
            'entre': 'OP_ENTRE'
        }
        
        # AFD_Números: detección numérica
        import re
        self.patron_numero = re.compile(r'\d+(\.\d+)?')
    
    def tokenizar_consulta(self, consulta: str) -> List[Dict]:
        """
        Proceso de tokenización con AFDs paralelos según tu arquitectura
        """
        tokens = []
        consulta_lower = consulta.lower().strip()
        palabras = consulta_lower.split()
        
        print(f"AFD - Tokenizando: '{consulta}'")
        
        i = 0
        while i < len(palabras):
            token_encontrado = False
            
            # AFD_Multipalabra (prioridad 1)
            for j in range(min(4, len(palabras) - i), 0, -1):
                frase = ' '.join(palabras[i:i+j])
                if frase in self.afd_multipalabra:
                    token = {
                        'tipo': self.afd_multipalabra[frase],
                        'valor': frase,
                        'posicion': i,
                        'prioridad': 1
                    }
                    tokens.append(token)
                    print(f"  🥇 AFD_Multipalabra: '{frase}' → {self.afd_multipalabra[frase]}")
                    i += j
                    token_encontrado = True
                    break
            
            if token_encontrado:
                continue
            
            # AFD_Operadores (prioridad 2) 
            if i + 1 < len(palabras):
                frase_op = f"{palabras[i]} {palabras[i+1]}"
                if frase_op in self.afd_operadores:
                    token = {
                        'tipo': self.afd_operadores[frase_op],
                        'valor': frase_op,
                        'posicion': i,
                        'prioridad': 2
                    }
                    tokens.append(token)
                    print(f"  🥈 AFD_Operadores: '{frase_op}' → {self.afd_operadores[frase_op]}")
                    i += 2
                    continue
            
            # AFD_Números (prioridad 3)
            if self.patron_numero.match(palabras[i]):
                token = {
                    'tipo': 'NUMERO',
                    'valor': palabras[i],
                    'numero': float(palabras[i]),
                    'posicion': i,
                    'prioridad': 3
                }
                tokens.append(token)
                print(f"  🥉 AFD_Números: '{palabras[i]}' → NUMERO")
                i += 1
                continue
            
            # AFD_Palabras (prioridad 4)
            if palabras[i] in self.afd_palabras:
                token = {
                    'tipo': self.afd_palabras[palabras[i]],
                    'valor': palabras[i],
                    'posicion': i,
                    'prioridad': 4
                }
                tokens.append(token)
                print(f"  🎯 AFD_Palabras: '{palabras[i]}' → {self.afd_palabras[palabras[i]]}")
            else:
                # Token no reconocido
                token = {
                    'tipo': 'PALABRA_NO_RECONOCIDA',
                    'valor': palabras[i],
                    'posicion': i,
                    'prioridad': 15
                }
                tokens.append(token)
                print(f"  ❓ No reconocido: '{palabras[i]}' → PALABRA_NO_RECONOCIDA")
            
            i += 1
        
        return tokens

class AnalizadorContextual:
    """
    Análisis Contextual según reglas de desambiguación de flujo.md
    """
    
    def __init__(self):
        self.reglas_contextuales = [
            {
                'patron': ['NEGACION', 'ATRIBUTO_SABOR'],
                'accion': self._manejar_negacion_atributo,
                'nombre': 'negacion_atributo'
            },
            {
                'patron': ['PRODUCTO_SINONIMO', 'ATRIBUTO_PRECIO'],
                'accion': self._manejar_producto_precio,
                'nombre': 'producto_precio'
            },
            {
                'patron': ['CATEGORIA_GENERICA', 'ATRIBUTO_PRECIO'],
                'accion': self._manejar_categoria_precio,
                'nombre': 'categoria_precio'
            },
            {
                'patron': ['OP_MENOR', 'NUMERO'],
                'accion': self._manejar_comparacion_precio,
                'nombre': 'comparacion_precio'
            }
        ]
    
    def aplicar_reglas_contextuales(self, tokens: List[Dict]) -> Dict:
        """
        Aplicar reglas de desambiguación contextual
        """
        interpretacion = {
            'producto_especifico': None,
            'categoria_inferida': None,
            'filtros_precio': {},
            'negaciones': [],
            'contexto_aplicado': []
        }
        
        print("🧠 ANÁLISIS CONTEXTUAL - Aplicando reglas...")
        
        # Aplicar reglas secuencialmente
        for regla in self.reglas_contextuales:
            patron = regla['patron']
            
            # Buscar patrón en tokens consecutivos
            for i in range(len(tokens) - len(patron) + 1):
                tokens_secuencia = [tokens[i + j]['tipo'] for j in range(len(patron))]
                
                if tokens_secuencia == patron:
                    print(f"  ✅ Regla aplicada: {regla['nombre']} en posición {i}")
                    regla['accion'](tokens[i:i+len(patron)], interpretacion)
                    interpretacion['contexto_aplicado'].append(regla['nombre'])
        
        # Detectar tokens individuales importantes
        for token in tokens:
            if token['tipo'] == 'PRODUCTO_SINONIMO':
                interpretacion['producto_sinonimo'] = token['valor']
            elif token['tipo'] == 'CATEGORIA_GENERICA':
                interpretacion['categoria_inferida'] = token['valor']
        
        return interpretacion
    
    def _manejar_negacion_atributo(self, tokens: List[Dict], interpretacion: Dict):
        """sin picante → excluir productos picantes"""
        negacion = tokens[0]['valor']
        atributo = tokens[1]['valor']
        interpretacion['negaciones'].append({
            'tipo': 'excluir_atributo',
            'atributo': atributo
        })
    
    def _manejar_producto_precio(self, tokens: List[Dict], interpretacion: Dict):
        """coca barata → Coca-Cola + filtro precio bajo"""
        producto = tokens[0]['valor']
        precio_attr = tokens[1]['valor']
        interpretacion['producto_especifico'] = producto
        if precio_attr in ['barato', 'barata', 'economico']:
            interpretacion['filtros_precio']['tendency'] = 'low'
    
    def _manejar_categoria_precio(self, tokens: List[Dict], interpretacion: Dict):
        """botana barata → snacks + filtro precio"""
        categoria = tokens[0]['valor'] 
        precio_attr = tokens[1]['valor']
        interpretacion['categoria_inferida'] = categoria
        if precio_attr in ['barato', 'barata', 'economico']:
            interpretacion['filtros_precio']['tendency'] = 'low'
    
    def _manejar_comparacion_precio(self, tokens: List[Dict], interpretacion: Dict):
        """menor a 20 → precio < 20"""
        operador = tokens[0]['valor']
        numero = tokens[1]['numero']
        if 'menor' in operador:
            interpretacion['filtros_precio']['max'] = numero

# Instanciar analizadores
analizador_afd = AnalizadorLexicoAFD()
analizador_contextual = AnalizadorContextual()

def buscar_por_sinonimos(query):
    """
    BÚSQUEDA INTELIGENTE con AFDs + Análisis Contextual + Sinónimos por Producto
    Implementa la arquitectura completa de flujo.md
    """
    
    print(f"\n🚀 INICIO PROCESAMIENTO INTELIGENTE: '{query}'")
    
    # ========================================
    # FASE 1: ANÁLISIS LÉXICO CON AFDs
    # ========================================
    tokens = analizador_afd.tokenizar_consulta(query)
    
    # ========================================
    # FASE 2: ANÁLISIS CONTEXTUAL
    # ========================================
    interpretacion = analizador_contextual.aplicar_reglas_contextuales(tokens)
    print(f"🧠 Interpretación contextual: {interpretacion}")
    
    # ========================================
    # FASE 3: MOTOR DE RECOMENDACIONES
    # ========================================
    productos_encontrados = []
    
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        # PRIORIDAD 1: Producto específico por sinónimo
        if interpretacion.get('producto_sinonimo'):
            print(f"🔍 PRIORIDAD 1: Búsqueda por sinónimo específico: {interpretacion['producto_sinonimo']}")
            
            cursor.execute("""
                SELECT DISTINCT p.*, c.nombre as categoria, ps.sinonimo, ps.popularidad
                FROM productos p
                INNER JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id
                INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE ps.sinonimo = %s AND ps.activo = 1 AND p.cantidad > 0
                ORDER BY ps.popularidad DESC, p.precio ASC
                LIMIT 5
            """, [interpretacion['producto_sinonimo']])
            
            resultados_sinonimo = cursor.fetchall()
            print(f"📊 Productos por sinónimo: {len(resultados_sinonimo)}")
            
            for row in resultados_sinonimo:
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
                    'match_score': 0.98,  # Score alto por sinónimo exacto
                    'match_reasons': ['afd_sinonimo_exacto', f'token: {interpretacion["producto_sinonimo"]}'],
                    'source': 'afd_lcln_sinonimo',
                    'match_type': 'exact_synonym_afd',
                    'sinonimo_usado': row['sinonimo'],
                    'popularidad': row['popularidad']
                }
                productos_encontrados.append(producto)
        
        # PRIORIDAD 2: Búsqueda por categoría + filtros
        if len(productos_encontrados) < 10 and interpretacion.get('categoria_inferida'):
            categoria = interpretacion['categoria_inferida']
            print(f"🔍 PRIORIDAD 2: Búsqueda por categoría: {categoria}")
            
            # Mapear categoría genérica a nombre real
            mapeo_categoria = {
                'botana': 'snacks',
                'botanas': 'snacks', 
                'snack': 'snacks',
                'bebida': 'bebidas',
                'bebidas': 'bebidas',
                'refresco': 'bebidas',
                'fruta': 'frutas',
                'frutas': 'frutas'
            }
            
            categoria_real = mapeo_categoria.get(categoria, categoria)
            
            query_categoria = """
                SELECT p.*, c.nombre as categoria
                FROM productos p
                INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE LOWER(c.nombre) = %s AND p.cantidad > 0
            """
            
            parametros = [categoria_real.lower()]
            
            # Aplicar filtros de precio
            if interpretacion['filtros_precio'].get('tendency') == 'low':
                query_categoria += " AND p.precio <= 20"
            elif interpretacion['filtros_precio'].get('max'):
                query_categoria += " AND p.precio <= %s"
                parametros.append(interpretacion['filtros_precio']['max'])
            
            query_categoria += " ORDER BY p.precio ASC LIMIT 8"
            
            cursor.execute(query_categoria, parametros)
            resultados_categoria = cursor.fetchall()
            print(f"📊 Productos por categoría: {len(resultados_categoria)}")
            
            for row in resultados_categoria:
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
                    'match_score': 0.85,  # Score medio por categoría
                    'match_reasons': ['afd_categoria', f'categoria: {categoria_real}'],
                    'source': 'afd_lcln_categoria',
                    'match_type': 'category_afd'
                }
                productos_encontrados.append(producto)
        
        # PRIORIDAD 3: Fallback si no hay suficientes resultados
        if len(productos_encontrados) < 5:
            print("🔍 PRIORIDAD 3: Búsqueda fallback")
            cursor.execute("""
                SELECT p.*, c.nombre as categoria
                FROM productos p
                INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.cantidad > 0 AND (
                    LOWER(p.nombre) LIKE %s OR 
                    LOWER(c.nombre) LIKE %s
                )
                ORDER BY p.precio ASC
                LIMIT 5
            """, [f"%{query.lower()}%", f"%{query.lower()}%"])
            
            resultados_fallback = cursor.fetchall()
            
            for row in resultados_fallback:
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
                    'match_score': 0.6,  # Score bajo por fallback
                    'match_reasons': ['afd_fallback'],
                    'source': 'afd_lcln_fallback',
                    'match_type': 'fallback_afd'
                }
                productos_encontrados.append(producto)
        
        print(f"✅ TOTAL PRODUCTOS ENCONTRADOS: {len(productos_encontrados)}")
        return productos_encontrados[:10]  # Máximo 10 como especificaste
        
    except Exception as e:
        print(f"❌ Error en búsqueda inteligente: {e}")
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
    print("Iniciando LCLN API Simple con AFDs en puerto 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")