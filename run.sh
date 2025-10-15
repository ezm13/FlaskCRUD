#!/bin/bash
echo "🚀 Iniciando aplicación Flask en Render..."
cd /opt/render/project/src
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
