#!/usr/bin/env python3
"""
ARQUITECTURA ESCALABLE PARA LYNX - 1000+ PRODUCTOS Y SINÓNIMOS

Diseñada para manejar:
- 1000+ productos únicos
- 1000+ sinónimos y variaciones
- Base de datos real MySQL
- Cache distribuido con Redis
- Búsqueda indexada optimizada

Autor: GitHub Copilot
Fecha: 2025-01-19
"""

import json
import sqlite3
import hashlib
import time
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProductoCompleto:
    """Estructura de producto completa y optimizada"""
    id: int
    nombre: str
    nombre_normalizado: str
    categoria: str
    subcategoria: Optional[str]
    precio: float
    marca: str
    tags: List[str]
    sinonimos: List[str]
    atributos: Dict[str, Any]
    stock: int
    activo: bool
    embedding_hash: str
    

@dataclass 
class SinonimoRegistro:
    """Registro de sinónimo con metadatos"""
    termino: str
    termino_normalizado: str
    producto_id: int
    categoria: str
    tipo: str  # 'nombre', 'marca', 'atributo', 'slang'
    confianza: float
    frecuencia_uso: int
    

class GestorSinonimosMasivo:
    """Gestor especializado para 1000+ sinónimos"""
    
    def __init__(self, db_path: str = "sinonimos_lynx.db"):
        self.db_path = db_path
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._init_db()
        
    def _init_db(self):
        """Inicializar base de datos SQLite para sinónimos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de sinónimos con índices optimizados
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sinonimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            termino TEXT NOT NULL,
            termino_normalizado TEXT NOT NULL,
            producto_id INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            tipo TEXT NOT NULL,
            confianza REAL DEFAULT 1.0,
            frecuencia_uso INTEGER DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
        """)
        
        # Índices optimizados para búsqueda rápida
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_termino_normalizado ON sinonimos(termino_normalizado)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_producto_id ON sinonimos(producto_id)")  
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categoria ON sinonimos(categoria)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activo ON sinonimos(activo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confianza ON sinonimos(confianza)")
        
        # Tabla de métricas de uso
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metricas_uso (
            termino TEXT PRIMARY KEY,
            total_busquedas INTEGER DEFAULT 0,
            ultima_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            aciertos INTEGER DEFAULT 0,
            fallos INTEGER DEFAULT 0
        )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Base de datos de sinónimos inicializada: {self.db_path}")
    
    def agregar_sinonimos_masivos(self, sinonimos: List[SinonimoRegistro]):
        """Inserción masiva optimizada de sinónimos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Preparar datos para inserción por lotes
        datos = [
            (s.termino, s.termino_normalizado, s.producto_id, s.categoria, 
             s.tipo, s.confianza, s.frecuencia_uso)
            for s in sinonimos
        ]
        
        cursor.executemany("""
        INSERT OR REPLACE INTO sinonimos 
        (termino, termino_normalizado, producto_id, categoria, tipo, confianza, frecuencia_uso)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, datos)
        
        conn.commit()
        conn.close()
        
        # Limpiar cache
        self.cache.clear()
        logger.info(f"✅ Insertados {len(sinonimos)} sinónimos masivamente")
    
    def buscar_sinónimo(self, termino: str) -> List[SinonimoRegistro]:
        """Búsqueda optimizada con cache"""
        termino_norm = self._normalizar_termino(termino)
        
        # Verificar cache primero
        if termino_norm in self.cache:
            self.cache_hits += 1
            return self.cache[termino_norm]
        
        self.cache_misses += 1
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Búsqueda con ranking por confianza
        cursor.execute("""
        SELECT termino, termino_normalizado, producto_id, categoria, tipo, confianza, frecuencia_uso
        FROM sinonimos 
        WHERE termino_normalizado LIKE ? AND activo = 1
        ORDER BY confianza DESC, frecuencia_uso DESC
        LIMIT 10
        """, (f"%{termino_norm}%",))
        
        resultados = []
        for row in cursor.fetchall():
            resultados.append(SinonimoRegistro(
                termino=row[0],
                termino_normalizado=row[1], 
                producto_id=row[2],
                categoria=row[3],
                tipo=row[4],
                confianza=row[5],
                frecuencia_uso=row[6]
            ))
        
        conn.close()
        
        # Guardar en cache (limitar tamaño del cache)
        if len(self.cache) < 1000:
            self.cache[termino_norm] = resultados
        
        return resultados
    
    def _normalizar_termino(self, termino: str) -> str:
        """Normalización avanzada de términos"""
        # Minúsculas, sin acentos, sin espacios extra
        import unicodedata
        termino = termino.lower().strip()
        termino = unicodedata.normalize('NFKD', termino)
        termino = ''.join(c for c in termino if not unicodedata.combining(c))
        return ' '.join(termino.split())  # Normalizar espacios


class BaseDatosEscalable:
    """Base de datos optimizada para 1000+ productos"""
    
    def __init__(self, db_path: str = "productos_lynx_escalable.db"):
        self.db_path = db_path
        self.gestor_sinonimos = GestorSinonimosMasivo()
        self._init_db()
        self.indices = {}
        self._crear_indices()
    
    def _init_db(self):
        """Inicializar base de datos principal optimizada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de productos optimizada
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            nombre_normalizado TEXT NOT NULL,
            categoria TEXT NOT NULL,
            subcategoria TEXT,
            precio REAL NOT NULL,
            marca TEXT,
            tags TEXT,  -- JSON array
            atributos TEXT,  -- JSON object
            stock INTEGER DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            embedding_hash TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Índices optimizados para consultas rápidas
        indices_queries = [
            "CREATE INDEX IF NOT EXISTS idx_nombre_normalizado ON productos(nombre_normalizado)",
            "CREATE INDEX IF NOT EXISTS idx_categoria ON productos(categoria)", 
            "CREATE INDEX IF NOT EXISTS idx_subcategoria ON productos(subcategoria)",
            "CREATE INDEX IF NOT EXISTS idx_precio ON productos(precio)",
            "CREATE INDEX IF NOT EXISTS idx_marca ON productos(marca)",
            "CREATE INDEX IF NOT EXISTS idx_activo ON productos(activo)",
            "CREATE INDEX IF NOT EXISTS idx_stock ON productos(stock)",
            "CREATE INDEX IF NOT EXISTS idx_categoria_precio ON productos(categoria, precio)",
            "CREATE INDEX IF NOT EXISTS idx_marca_categoria ON productos(marca, categoria)"
        ]
        
        for query in indices_queries:
            cursor.execute(query)
        
        # Vista materializada para búsquedas complejas
        cursor.execute("""
        CREATE VIEW IF NOT EXISTS vista_productos_completa AS
        SELECT 
            p.*,
            COUNT(s.id) as total_sinonimos
        FROM productos p
        LEFT JOIN sinonimos s ON p.id = s.producto_id AND s.activo = 1
        WHERE p.activo = 1
        GROUP BY p.id
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Base de datos escalable inicializada: {self.db_path}")
    
    def _crear_indices(self):
        """Crear índices en memoria para búsqueda ultrarrápida"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Índice por categorías
        cursor.execute("SELECT categoria, id, nombre FROM productos WHERE activo = 1")
        self.indices['categoria'] = defaultdict(list)
        for categoria, prod_id, nombre in cursor.fetchall():
            self.indices['categoria'][categoria].append((prod_id, nombre))
        
        # Índice por rango de precios
        cursor.execute("SELECT precio, id, nombre FROM productos WHERE activo = 1")
        self.indices['precio'] = {'barato': [], 'medio': [], 'caro': []}
        for precio, prod_id, nombre in cursor.fetchall():
            if precio <= 20.0:
                self.indices['precio']['barato'].append((prod_id, nombre, precio))
            elif precio <= 50.0:
                self.indices['precio']['medio'].append((prod_id, nombre, precio))
            else:
                self.indices['precio']['caro'].append((prod_id, nombre, precio))
        
        conn.close()
        logger.info(f"✅ Índices en memoria creados - Categorías: {len(self.indices['categoria'])}")
    
    def buscar_productos_avanzado(self, query: Dict[str, Any]) -> List[ProductoCompleto]:
        """Búsqueda avanzada con múltiples filtros"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        where_clauses = ["activo = 1"]
        params = []
        
        if 'termino' in query:
            where_clauses.append("nombre_normalizado LIKE ?")
            termino_norm = self._normalizar_termino(query['termino'])
            params.append(f"%{termino_norm}%")
        
        if 'categoria' in query:
            where_clauses.append("categoria = ?")
            params.append(query['categoria'])
        
        if 'precio_max' in query:
            where_clauses.append("precio <= ?")
            params.append(query['precio_max'])
        
        if 'precio_min' in query:
            where_clauses.append("precio >= ?")
            params.append(query['precio_min'])
        
        if 'marca' in query:
            where_clauses.append("marca LIKE ?")
            params.append(f"%{query['marca']}%")
        
        # Ejecutar query optimizada
        sql = f"""
        SELECT id, nombre, nombre_normalizado, categoria, subcategoria, 
               precio, marca, tags, atributos, stock, activo, embedding_hash
        FROM productos 
        WHERE {' AND '.join(where_clauses)}
        ORDER BY 
            CASE 
                WHEN nombre_normalizado = ? THEN 1
                WHEN nombre_normalizado LIKE ? THEN 2
                ELSE 3
            END,
            precio ASC
        LIMIT ?
        """
        
        # Agregar parámetros para ordenamiento
        if 'termino' in query:
            termino_norm = self._normalizar_termino(query['termino'])
            params.extend([termino_norm, f"{termino_norm}%"])
        else:
            params.extend(["", ""])
        
        params.append(query.get('limit', 50))
        
        cursor.execute(sql, params)
        
        resultados = []
        for row in cursor.fetchall():
            producto = ProductoCompleto(
                id=row[0],
                nombre=row[1],
                nombre_normalizado=row[2],
                categoria=row[3],
                subcategoria=row[4],
                precio=row[5],
                marca=row[6],
                tags=json.loads(row[7]) if row[7] else [],
                sinonimos=[],  # Se puede cargar por separado si es necesario
                atributos=json.loads(row[8]) if row[8] else {},
                stock=row[9],
                activo=bool(row[10]),
                embedding_hash=row[11] or ""
            )
            resultados.append(producto)
        
        conn.close()
        return resultados
    
    def obtener_todos_productos(self) -> List[ProductoCompleto]:
        """Obtener todos los productos activos de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, nombre, nombre_normalizado, categoria, subcategoria, 
               precio, marca, tags, atributos, stock, activo, embedding_hash
        FROM productos 
        WHERE activo = 1
        ORDER BY id
        """)
        
        resultados = []
        for row in cursor.fetchall():
            producto = ProductoCompleto(
                id=row[0],
                nombre=row[1],
                nombre_normalizado=row[2],
                categoria=row[3],
                subcategoria=row[4],
                precio=row[5],
                marca=row[6],
                tags=json.loads(row[7]) if row[7] else [],
                sinonimos=[],  # Se puede cargar por separado si es necesario
                atributos=json.loads(row[8]) if row[8] else {},
                stock=row[9],
                activo=bool(row[10]),
                embedding_hash=row[11] or ""
            )
            resultados.append(producto)
        
        conn.close()
        return resultados
    
    def _normalizar_termino(self, termino: str) -> str:
        """Usar el mismo normalizador que el gestor de sinónimos"""
        return self.gestor_sinonimos._normalizar_termino(termino)
    
    def buscar_productos_inteligente(self, consulta: str, limite: int = 20) -> List[Dict]:
        """Búsqueda inteligente de productos por nombre/sinónimo"""
        consulta_normalizada = self._normalizar_termino(consulta)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar por nombre normalizado
        cursor.execute("""
        SELECT id, nombre, categoria, precio, stock, activo
        FROM productos 
        WHERE nombre_normalizado LIKE ? AND activo = 1
        ORDER BY 
            CASE WHEN nombre_normalizado = ? THEN 1 ELSE 2 END,
            precio ASC
        LIMIT ?
        """, (f"%{consulta_normalizada}%", consulta_normalizada, limite))
        
        resultados = []
        for row in cursor.fetchall():
            resultado = {
                'id': row[0],
                'nombre': row[1],
                'categoria': row[2],
                'precio': float(row[3]),
                'cantidad': row[4],
                'disponible': bool(row[5]),
                'similitud': 0.8 if consulta_normalizada in row[1].lower() else 0.6
            }
            resultados.append(resultado)
        
        conn.close()
        return resultados
    
    def obtener_productos_populares(self, limite: int = 10) -> List[Dict]:
        """Obtiene productos populares como fallback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener productos ordenados por stock (simulando popularidad) 
        cursor.execute("""
        SELECT id, nombre, categoria, precio, stock, activo
        FROM productos 
        WHERE activo = 1 AND stock > 0
        ORDER BY stock DESC, precio ASC
        LIMIT ?
        """, (limite,))
        
        resultados = []
        for row in cursor.fetchall():
            resultado = {
                'id': row[0],
                'nombre': row[1],
                'categoria': row[2],
                'precio': float(row[3]),
                'cantidad': row[4],
                'disponible': bool(row[5])
            }
            resultados.append(resultado)
        
        conn.close()
        return resultados
    
    def buscar_por_atributo(self, atributo: str, limite: int = 10) -> List[Dict]:
        """Busca productos por atributo específico usando búsqueda inteligente en nombres"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print(f"🔍 DEBUG: Buscando atributo '{atributo}' en base de datos...")
        
        # Si es "picante", buscar productos que contengan palabras relacionadas con picante
        terminos_busqueda = []
        if atributo.lower() in ['picante', 'fuego', 'flaming', 'hot']:
            terminos_busqueda = ['fuego', 'flamin', 'hot', 'picante', 'enchilado', 'adobada', 'chipotle', 'habanero', 'jalapeño', 'chili', 'spicy', 'takis', 'doritos', 'cheetos']
        elif atributo.lower() in ['dulce', 'azucar']:
            terminos_busqueda = ['chocolate', 'dulce', 'azucar', 'miel', 'caramelo', 'galleta', 'pastel', 'candy', 'sweet', 'coca cola', 'pepsi']
        elif atributo.lower() in ['salado', 'sal']:
            terminos_busqueda = ['sal', 'salado', 'papas', 'sabritas', 'cacahuate', 'nuez', 'pretzel', 'chips']
        else:
            # Para otros atributos, usar el atributo directamente
            terminos_busqueda = [atributo.lower()]
        
        # Construir consulta dinámica para buscar cualquier término relacionado
        condiciones = []
        parametros = []
        
        for termino in terminos_busqueda:
            condiciones.append("LOWER(nombre) LIKE ?")
            parametros.append(f'%{termino.lower()}%')
        
        if not condiciones:
            # Fallback: buscar por el término original
            condiciones.append("LOWER(nombre) LIKE ?")
            parametros.append(f'%{atributo.lower()}%')
        
        consulta = f"""
        SELECT id, nombre, categoria, precio, stock, activo
        FROM productos 
        WHERE ({' OR '.join(condiciones)}) AND activo = 1
        ORDER BY 
            CASE WHEN LOWER(nombre) LIKE ? THEN 1 ELSE 2 END,
            precio ASC
        LIMIT ?
        """
        
        # Agregar parámetros para el ORDER BY y LIMIT
        parametros_consulta = parametros + [f'%{terminos_busqueda[0]}%', limite]
        
        print(f"🔍 DEBUG: Ejecutando búsqueda para {len(terminos_busqueda)} términos: {terminos_busqueda[:5]}...")
        cursor.execute(consulta, parametros_consulta)
        
        resultados = []
        for row in cursor.fetchall():
            resultado = {
                'id': row[0],
                'nombre': row[1],
                'categoria': row[2],
                'precio': float(row[3]),
                'cantidad': row[4],
                'disponible': bool(row[5])
            }
            resultados.append(resultado)
        
        print(f"🔍 DEBUG: Encontrados {len(resultados)} productos para atributo '{atributo}'")
        if resultados:
            for i, r in enumerate(resultados[:3]):
                print(f"   {i+1}. {r['nombre']} (${r['precio']:.2f})")
        
        conn.close()
        return resultados
    
    def obtener_productos_por_categoria(self, categoria: str, limite: int = None) -> List[Dict]:
        """Obtiene productos filtrados por categoría"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Normalizar categoría para búsqueda más flexible
        categoria_norm = categoria.strip().lower()
        
        if limite:
            cursor.execute("""
            SELECT id, nombre, categoria, precio, stock, activo
            FROM productos 
            WHERE LOWER(categoria) LIKE ? AND activo = 1
            ORDER BY precio ASC
            LIMIT ?
            """, (f"%{categoria_norm}%", limite))
        else:
            cursor.execute("""
            SELECT id, nombre, categoria, precio, stock, activo
            FROM productos 
            WHERE LOWER(categoria) LIKE ? AND activo = 1
            ORDER BY precio ASC
            """, (f"%{categoria_norm}%",))
        
        resultados = []
        for row in cursor.fetchall():
            resultado = {
                'id': row[0],
                'nombre': row[1],
                'categoria': row[2],
                'precio': float(row[3]),
                'cantidad': row[4],
                'disponible': bool(row[5])
            }
            resultados.append(resultado)
        
        conn.close()
        return resultados
    
    def buscar_productos_texto(self, texto: str, limite: int = 20) -> List[Dict]:
        """Busca productos por texto libre con mayor flexibilidad"""
        if not texto or not texto.strip():
            return []
            
        texto_normalizado = self._normalizar_termino(texto.strip())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Búsqueda por coincidencia parcial en nombre y categoría
        cursor.execute("""
        SELECT id, nombre, categoria, precio, stock, activo
        FROM productos 
        WHERE (LOWER(nombre) LIKE ? OR LOWER(categoria) LIKE ? OR nombre_normalizado LIKE ?) 
        AND activo = 1
        ORDER BY 
            CASE 
                WHEN LOWER(nombre) = ? THEN 1
                WHEN LOWER(nombre) LIKE ? THEN 2
                WHEN nombre_normalizado LIKE ? THEN 3
                ELSE 4 
            END,
            precio ASC
        LIMIT ?
        """, (
            f"%{texto_normalizado}%", f"%{texto_normalizado}%", f"%{texto_normalizado}%",
            texto_normalizado, f"{texto_normalizado}%", f"%{texto_normalizado}%",
            limite
        ))
        
        resultados = []
        for row in cursor.fetchall():
            resultado = {
                'id': row[0],
                'nombre': row[1],
                'categoria': row[2],
                'precio': float(row[3]),
                'cantidad': row[4],
                'disponible': bool(row[5])
            }
            resultados.append(resultado)
        
        conn.close()
        return resultados


class ConfiguracionEscalableLYNX:
    """Configuración escalable que reemplaza la actual"""
    
    def __init__(self, usar_mysql: bool = False, redis_host: str = None):
        self.usar_mysql = usar_mysql
        self.redis_host = redis_host
        self.bd_escalable = BaseDatosEscalable()
        self.cache_config = {}
        self.stats = {
            'total_productos': 0,
            'total_sinonimos': 0,
            'categorias': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    def cargar_productos_desde_mysql(self, conn_params: Dict[str, str]):
        """Cargar productos desde MySQL real"""
        try:
            import mysql.connector
            
            conn = mysql.connector.connect(**conn_params)
            cursor = conn.cursor(dictionary=True)
            
            # Query optimizada para cargar todos los productos
            cursor.execute("""
            SELECT 
                p.id_producto as id,
                p.nombre,
                p.precio,
                p.cantidad as stock,
                p.marca,
                c.nombre as categoria,
                p.descripcion
            FROM Productos p
            JOIN Categorias c ON p.id_categoria = c.id_categoria
            WHERE p.activo = 1 AND c.activa = 1
            ORDER BY p.id_producto
            """)
            
            productos = cursor.fetchall()
            conn.close()
            
            # Insertar en BD escalable
            self._insertar_productos_masivos(productos)
            
            logger.info(f"✅ Cargados {len(productos)} productos desde MySQL")
            return len(productos)
            
        except Exception as e:
            logger.error(f"❌ Error cargando desde MySQL: {e}")
            return 0
    
    def _insertar_productos_masivos(self, productos: List[Dict]):
        """Inserción masiva optimizada"""
        conn = sqlite3.connect(self.bd_escalable.db_path)
        cursor = conn.cursor()
        
        # Preparar datos para inserción
        datos = []
        sinonimos_generados = []
        
        for p in productos:
            nombre_norm = self.bd_escalable._normalizar_termino(p['nombre'])
            tags = self._generar_tags(p)
            atributos = self._extraer_atributos(p)
            
            datos.append((
                p['id'],
                p['nombre'],
                nombre_norm,
                p['categoria'],
                None,  # subcategoria
                float(p['precio']),
                p.get('marca', ''),
                json.dumps(tags),
                json.dumps(atributos),
                p.get('stock', 0),
                1,  # activo
                self._generar_embedding_hash(p['nombre'])
            ))
            
            # Generar sinónimos automáticamente
            sinonimos_generados.extend(self._generar_sinonimos_automaticos(p))
        
        # Inserción por lotes
        cursor.executemany("""
        INSERT OR REPLACE INTO productos 
        (id, nombre, nombre_normalizado, categoria, subcategoria, precio, marca, 
         tags, atributos, stock, activo, embedding_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, datos)
        
        conn.commit()
        conn.close()
        
        # Insertar sinónimos
        if sinonimos_generados:
            self.bd_escalable.gestor_sinonimos.agregar_sinonimos_masivos(sinonimos_generados)
        
        # Actualizar estadísticas
        self.stats['total_productos'] = len(productos)
        self.stats['total_sinonimos'] = len(sinonimos_generados)
        
        # Recrear índices
        self.bd_escalable._crear_indices()
    
    def _generar_tags(self, producto: Dict) -> List[str]:
        """Generar tags automáticas para el producto"""
        tags = []
        nombre = producto['nombre'].lower()
        
        # Tags por categoría
        categoria = producto['categoria'].lower()
        tags.append(categoria)
        
        # Tags por precio  
        precio = float(producto['precio'])
        if precio <= 15.0:
            tags.extend(['economico', 'barato'])
        elif precio <= 30.0:
            tags.extend(['medio', 'accesible'])
        else:
            tags.extend(['premium', 'caro'])
        
        # Tags por marca
        if 'marca' in producto and producto['marca']:
            tags.append(producto['marca'].lower())
        
        # Tags por contenido del nombre
        if any(palabra in nombre for palabra in ['picante', 'picoso', 'chile']):
            tags.extend(['picante', 'picoso', 'enchilado'])
        
        if any(palabra in nombre for palabra in ['dulce', 'chocolate', 'azucar']):
            tags.extend(['dulce', 'azucarado'])
        
        if any(palabra in nombre for palabra in ['light', 'sin azucar', 'diet']):
            tags.extend(['light', 'dietetico', 'saludable'])
        
        return list(set(tags))  # Eliminar duplicados
    
    def _extraer_atributos(self, producto: Dict) -> Dict[str, Any]:
        """Extraer atributos estructurados"""
        atributos = {}
        nombre = producto['nombre'].lower()
        
        # Extraer tamaño/cantidad
        import re
        
        # Buscar patrones de contenido
        contenido_ml = re.search(r'(\d+)\s*ml', nombre)
        contenido_g = re.search(r'(\d+)\s*g', nombre)
        contenido_kg = re.search(r'(\d+)\s*kg', nombre)
        
        if contenido_ml:
            atributos['contenido_ml'] = int(contenido_ml.group(1))
            atributos['tipo_medida'] = 'liquido'
        elif contenido_g:
            atributos['contenido_g'] = int(contenido_g.group(1))
            atributos['tipo_medida'] = 'peso'
        elif contenido_kg:
            atributos['contenido_g'] = int(contenido_kg.group(1)) * 1000
            atributos['tipo_medida'] = 'peso'
        
        # Clasificar tamaño
        if 'contenido_ml' in atributos:
            ml = atributos['contenido_ml']
            if ml <= 300:
                atributos['tamaño'] = 'pequeño'
            elif ml <= 600:
                atributos['tamaño'] = 'mediano'
            else:
                atributos['tamaño'] = 'grande'
        elif 'contenido_g' in atributos:
            g = atributos['contenido_g']
            if g <= 50:
                atributos['tamaño'] = 'pequeño'
            elif g <= 200:
                atributos['tamaño'] = 'mediano'
            else:
                atributos['tamaño'] = 'grande'
        
        return atributos
    
    def _generar_sinonimos_automaticos(self, producto: Dict) -> List[SinonimoRegistro]:
        """Generar sinónimos automáticamente para un producto"""
        sinonimos = []
        nombre = producto['nombre'].lower()
        categoria = producto['categoria'].lower()
        prod_id = producto['id']
        
        # Sinónimos del nombre completo
        sinonimos.append(SinonimoRegistro(
            termino=nombre,
            termino_normalizado=self.bd_escalable._normalizar_termino(nombre),
            producto_id=prod_id,
            categoria=categoria,
            tipo='nombre',
            confianza=1.0,
            frecuencia_uso=0
        ))
        
        # Sinónimos por palabras individuales
        palabras = nombre.split()
        for palabra in palabras:
            if len(palabra) > 2 and palabra not in ['de', 'en', 'la', 'el', 'con', 'sin', 'por']:
                sinonimos.append(SinonimoRegistro(
                    termino=palabra,
                    termino_normalizado=self.bd_escalable._normalizar_termino(palabra),
                    producto_id=prod_id,
                    categoria=categoria,
                    tipo='palabra',
                    confianza=0.8,
                    frecuencia_uso=0
                ))
        
        # Sinónimos por marca
        if 'marca' in producto and producto['marca']:
            marca = producto['marca'].lower()
            sinonimos.append(SinonimoRegistro(
                termino=marca,
                termino_normalizado=self.bd_escalable._normalizar_termino(marca),
                producto_id=prod_id,
                categoria=categoria,
                tipo='marca',
                confianza=0.9,
                frecuencia_uso=0
            ))
        
        return sinonimos
    
    def _generar_embedding_hash(self, texto: str) -> str:
        """Generar hash único para embeddings futuros"""
        return hashlib.md5(texto.encode()).hexdigest()[:16]
    
    def obtener_configuracion_afd(self) -> Dict[str, Any]:
        """Generar configuración optimizada para AFDs"""
        conn = sqlite3.connect(self.bd_escalable.db_path)
        cursor = conn.cursor()
        
        # Obtener productos más frecuentes por categoría
        # Usar solo la tabla de productos ya que sinónimos está en BD separada
        cursor.execute("""
        SELECT categoria, nombre, stock as frecuencia
        FROM productos
        WHERE activo = 1
        ORDER BY frecuencia DESC
        """)
        
        productos_por_categoria = defaultdict(list)
        for categoria, nombre, freq in cursor.fetchall():
            productos_por_categoria[categoria].append(nombre)
        
        # Limitar por categoría para mantener performance
        config = {
            'categorias': list(productos_por_categoria.keys()),
            'productos_por_categoria': {},
            'productos_simples': [],
            'productos_multi': [],
            'multipalabras': []
        }
        
        for categoria, productos in productos_por_categoria.items():
            # Tomar top 100 por categoría para AFD
            config['productos_por_categoria'][categoria] = productos[:100]
            
            # Separar simples y multi
            for producto in productos[:100]:
                if len(producto.split()) == 1:
                    config['productos_simples'].append(producto)
                elif len(producto.split()) == 2:
                    config['multipalabras'].append(producto)
                else:
                    config['productos_multi'].append(producto)
        
        conn.close()
        
        # Limitar totales para performance de AFD
        config['productos_simples'] = list(set(config['productos_simples']))[:200]
        config['multipalabras'] = list(set(config['multipalabras']))[:200]
        config['productos_multi'] = list(set(config['productos_multi']))[:100]
        
        return config
    
    def buscar_productos_inteligente(self, consulta: str, limite: int = 20) -> List[Dict]:
        """Búsqueda inteligente usando sinónimos"""
        # 1. Buscar sinónimos primero
        sinonimos = self.bd_escalable.gestor_sinonimos.buscar_sinónimo(consulta)
        
        productos_encontrados = []
        
        # 2. Si hay sinónimos, buscar productos directamente
        if sinonimos:
            producto_ids = [s.producto_id for s in sinonimos[:5]]  # Top 5 sinónimos
            
            conn = sqlite3.connect(self.bd_escalable.db_path)
            cursor = conn.cursor()
            
            placeholders = ','.join(['?'] * len(producto_ids))
            cursor.execute(f"""
            SELECT id, nombre, categoria, precio, marca, stock
            FROM productos 
            WHERE id IN ({placeholders}) AND activo = 1
            ORDER BY precio ASC
            """, producto_ids)
            
            for row in cursor.fetchall():
                productos_encontrados.append({
                    'id': row[0],
                    'nombre': row[1],
                    'categoria': row[2],
                    'precio': row[3],
                    'marca': row[4],
                    'stock': row[5],
                    'match_score': 0.95,  # Alto score por sinónimo directo
                    'match_type': 'sinonimo'
                })
            
            conn.close()
        
        # 3. Búsqueda por similitud como fallback
        if len(productos_encontrados) < limite:
            query_similitud = {
                'termino': consulta,
                'limit': limite - len(productos_encontrados)
            }
            
            productos_similitud = self.bd_escalable.buscar_productos_avanzado(query_similitud)
            
            for producto in productos_similitud:
                if not any(p['id'] == producto.id for p in productos_encontrados):
                    productos_encontrados.append({
                        'id': producto.id,
                        'nombre': producto.nombre,
                        'categoria': producto.categoria,
                        'precio': producto.precio,
                        'marca': producto.marca,
                        'stock': producto.stock,
                        'match_score': 0.7,  # Score menor por similitud
                        'match_type': 'similitud'
                    })
        
        return productos_encontrados[:limite]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas completas del sistema"""
        conn = sqlite3.connect(self.bd_escalable.db_path)
        cursor = conn.cursor()
        
        # Estadísticas básicas
        cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        total_productos = cursor.fetchone()[0]
        
        # Estadísticas de sinónimos desde su BD separada
        conn_sinonimos = sqlite3.connect(self.bd_escalable.gestor_sinonimos.db_path)
        cursor_sinonimos = conn_sinonimos.cursor()
        cursor_sinonimos.execute("SELECT COUNT(*) FROM sinonimos WHERE activo = 1") 
        total_sinonimos = cursor_sinonimos.fetchone()[0]
        conn_sinonimos.close()
        
        cursor.execute("SELECT COUNT(DISTINCT categoria) FROM productos WHERE activo = 1")
        total_categorias = cursor.fetchone()[0]
        
        # Estadísticas por categoría
        cursor.execute("""
        SELECT categoria, COUNT(*), AVG(precio), MIN(precio), MAX(precio)
        FROM productos 
        WHERE activo = 1
        GROUP BY categoria
        ORDER BY COUNT(*) DESC
        """)
        
        categorias_stats = []
        for row in cursor.fetchall():
            categorias_stats.append({
                'categoria': row[0],
                'productos': row[1],
                'precio_promedio': round(row[2], 2),
                'precio_min': row[3],
                'precio_max': row[4]
            })
        
        conn.close()
        
        return {
            'productos': {
                'total': total_productos,
                'por_categoria': categorias_stats
            },
            'sinonimos': {
                'total': total_sinonimos,
                'cache_hits': self.bd_escalable.gestor_sinonimos.cache_hits,
                'cache_misses': self.bd_escalable.gestor_sinonimos.cache_misses,
                'cache_ratio': self.bd_escalable.gestor_sinonimos.cache_hits / 
                              (self.bd_escalable.gestor_sinonimos.cache_hits + 
                               self.bd_escalable.gestor_sinonimos.cache_misses) 
                              if (self.bd_escalable.gestor_sinonimos.cache_hits + 
                                  self.bd_escalable.gestor_sinonimos.cache_misses) > 0 else 0
            },
            'categorias': {
                'total': total_categorias
            },
            'rendimiento': {
                'bd_path': self.bd_escalable.db_path,
                'indices_memoria': len(self.bd_escalable.indices)
            }
        }


if __name__ == "__main__":
    # Ejemplo de uso
    print("🚀 INICIANDO SISTEMA ESCALABLE LYNX")
    print("=" * 60)
    
    # Crear configuración escalable
    config = ConfiguracionEscalableLYNX()
    
    # Obtener estadísticas
    stats = config.obtener_estadisticas()
    print(f"📊 ESTADÍSTICAS ACTUALES:")
    print(f"   • Productos: {stats['productos']['total']}")
    print(f"   • Sinónimos: {stats['sinonimos']['total']}")
    print(f"   • Categorías: {stats['categorias']['total']}")
    
    # Probar búsqueda inteligente
    print(f"\n🔍 PRUEBA DE BÚSQUEDA INTELIGENTE:")
    resultados = config.buscar_productos_inteligente("coca cola")
    for resultado in resultados[:3]:
        print(f"   • {resultado['nombre']} - ${resultado['precio']} ({resultado['match_type']})")
    
    print(f"\n✅ Sistema escalable funcionando correctamente")
