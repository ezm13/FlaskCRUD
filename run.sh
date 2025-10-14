#!/bin/bash
echo "🚀 Iniciando aplicación Flask en Render..."

# Instalar dependencias (opcional si ya están instaladas por Render)
pip install -r requirements.txt

# Ejecutar Gunicorn con tu app Flask
gunicorn app:app --bind 0.0.0.0:$PORT
