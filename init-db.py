#!/usr/bin/env python3
"""
Script para inicializar la base de datos de Railway con el esquema de LynxShop
"""
import os
import pymysql
import sys

def init_database():
    try:
        # Conexión a la base de datos Railway
        connection = pymysql.connect(
            host=os.getenv('MYSQLHOST', 'mysql.railway.internal'),
            port=int(os.getenv('MYSQLPORT', 3306)),
            user=os.getenv('MYSQLUSER', 'root'),
            password=os.getenv('MYSQLPASSWORD'),
            database=os.getenv('MYSQLDATABASE', 'railway'),
            charset='utf8mb4'
        )
        
        print("✅ Conexión exitosa a Railway MySQL")
        
        # Leer el archivo SQL
        with open('/app/database/railway-import.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir en statements individuales
        statements = sql_content.split(';')
        
        cursor = connection.cursor()
        
        executed = 0
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--') and not statement.startswith('/*'):
                try:
                    cursor.execute(statement)
                    executed += 1
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Error ejecutando statement: {e}")
        
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
        sys.exit(1)

if __name__ == "__main__":
    init_database()
