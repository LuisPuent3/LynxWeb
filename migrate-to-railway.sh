#!/bin/bash

# Script de migración para Railway
# Ejecutar después de crear el servicio MySQL en Railway

echo "Iniciando migración de base de datos a Railway..."

# Verificar que las variables estén configuradas
if [ -z "$MYSQLHOST" ] || [ -z "$MYSQLUSER" ] || [ -z "$MYSQLPASSWORD" ] || [ -z "$MYSQLDATABASE" ]; then
    echo "Error: Variables de Railway no configuradas"
    echo "Asegúrate de tener un servicio MySQL activo en Railway"
    exit 1
fi

echo "Conectando a: $MYSQLHOST:$MYSQLPORT"
echo "Base de datos: $MYSQLDATABASE"
echo "Usuario: $MYSQLUSER"

# Ejecutar el dump SQL
mysql -h $MYSQLHOST -P $MYSQLPORT -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE < database/lynxshop.sql

if [ $? -eq 0 ]; then
    echo "✅ Migración completada exitosamente"
    echo "Base de datos LynxShop migrada a Railway"
else
    echo "❌ Error en la migración"
    exit 1
fi
