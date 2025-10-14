#!/bin/bash
cd /opt/render/project/src
echo "🚀 Iniciando aplicación Flask en Render..."
gunicorn --bind 0.0.0.0:$PORT app:app
