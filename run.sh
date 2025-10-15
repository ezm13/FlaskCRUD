#!/bin/bash
echo "🚀 Iniciando aplicación Flask en Render..."

# Navega al directorio del proyecto
cd /opt/render/project/src

# ✅ Crear base de datos ANTES de iniciar Gunicorn
echo "📦 Inicializando base de datos..."
python3 - <<END
import app
app.init_db()
END

# ✅ Iniciar el servidor
echo "🔥 Ejecutando Gunicorn..."
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
