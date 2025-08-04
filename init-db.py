#!/usr/bin/env python3
"""
Script para inicializar la base de datos de Railway con el esquema de LynxShop
"""
import os
import pymysql
import sys

def init_database():
    try:
        print("🔄 Intentando conectar a Railway MySQL...")
        
        # Conexión a la base de datos Railway
        connection = pymysql.connect(
            host=os.getenv('MYSQLHOST', 'mysql.railway.internal'),
            port=int(os.getenv('MYSQLPORT', 3306)),
            user=os.getenv('MYSQLUSER', 'root'),
            password=os.getenv('MYSQLPASSWORD'),
            database=os.getenv('MYSQLDATABASE', 'railway'),
            charset='utf8mb4',
            connect_timeout=30
        )
        
        print("✅ Conexión exitosa a Railway MySQL")
        
        # Verificar si las tablas ya existen
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES LIKE 'categorias'")
        if cursor.fetchone():
            print("🔍 Las tablas ya existen, saltando inicialización...")
            cursor.close()
            connection.close()
            return
        
        print("📋 Iniciando carga de esquema de base de datos...")
        
        # Leer el archivo SQL
        with open('/app/database/railway-import.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir en statements individuales y filtrar
        statements = []
        for stmt in sql_content.split(';'):
            stmt = stmt.strip()
            if (stmt and 
                not stmt.startswith('--') and 
                not stmt.startswith('/*') and
                'SET @' not in stmt and
                '/*!40' not in stmt):
                statements.append(stmt)
        
        executed = 0
        for statement in statements:
            try:
                cursor.execute(statement)
                executed += 1
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"⚠️  Error ejecutando statement: {e}")
                    print(f"Statement: {statement[:100]}...")
        
        connection.commit()
        print(f"✅ Base de datos inicializada correctamente. {executed} statements ejecutados.")
        
        # Verificar tablas creadas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Tablas disponibles: {[table[0] for table in tables]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        print("⚠️  Continuando sin inicialización de BD...")
        # No hacer sys.exit para que la app pueda continuar

if __name__ == "__main__":
    init_database()
