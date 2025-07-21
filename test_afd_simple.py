#!/usr/bin/env python3
"""
TEST SIMPLE DEL SISTEMA AFD PARA VERIFICAR FUNCIONAMIENTO
"""

import mysql.connector
from typing import List, Dict

# Config MySQL
mysql_config = {
    'host': 'localhost',
    'database': 'lynxshop',
    'user': 'root',
    'password': '12345678',
    'charset': 'utf8mb4'
}

def test_afd_system():
    """Test simple del sistema AFD"""
    
    # AFD_Palabras simple
    afd_palabras = {
        'coquita': 'PRODUCTO_SINONIMO',
        'coca': 'PRODUCTO_SINONIMO',
        'barata': 'ATRIBUTO_PRECIO',
        'barato': 'ATRIBUTO_PRECIO'
    }
    
    query = "coquita barata"
    palabras = query.split()
    
    print(f"Testing query: {query}")
    
    # Tokenizar
    tokens = []
    for palabra in palabras:
        if palabra in afd_palabras:
            token = {
                'tipo': afd_palabras[palabra],
                'valor': palabra
            }
            tokens.append(token)
            print(f"  Token: {palabra} -> {afd_palabras[palabra]}")
    
    # Buscar productos por sinónimo
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor(dictionary=True)
    
    for token in tokens:
        if token['tipo'] == 'PRODUCTO_SINONIMO':
            print(f"Buscando productos para sinonimo: {token['valor']}")
            
            cursor.execute("""
                SELECT DISTINCT p.*, c.nombre as categoria, ps.sinonimo
                FROM productos p
                INNER JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id
                INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE ps.sinonimo = %s AND ps.activo = 1
                ORDER BY ps.popularidad DESC
                LIMIT 3
            """, [token['valor']])
            
            resultados = cursor.fetchall()
            print(f"  Encontrados {len(resultados)} productos:")
            for row in resultados:
                print(f"    - {row['nombre']} (${row['precio']}) - {row['sinonimo']}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_afd_system()