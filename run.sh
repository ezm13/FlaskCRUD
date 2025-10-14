#!/usr/bin/env bash
# Script de inicio para Flask en Render

echo "🚀 Iniciando aplicación Flask en Render..."

# Crear base de datos si no existe
python -c "import sqlite3; conn = sqlite3.connect('datos.db'); conn.close()"

# Iniciar el servidor con Gunicorn en el puerto 10000 (Render usa este por defecto)
gunicorn -w 4 -b 0.0.0.0:10000 app:app
