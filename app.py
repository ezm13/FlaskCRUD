from flask import Flask, flash, render_template, request, redirect,url_for
import sqlite3

app = Flask(__name__)
import os
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clave-super-secreta")

# Ruta principal: redirige al formulario
@app.route('/')
def home():
    return redirect('/formulario')

# Crear usuario
import re  # 👈 Importa esto al inicio del archivo, si no lo tienes

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        correo = request.form['correo'].strip()
        edad = request.form['edad'].strip()

        # ⚠️ Validar campos vacíos
        if not nombre or not correo or not edad:
            flash("⚠️ Todos los campos son obligatorios.", "warning")
            return render_template('formulario.html')

        # ⚠️ Validar formato de correo
        patron_correo = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(patron_correo, correo):
            flash("📧 Ingresa un correo electrónico válido.", "warning")
            return render_template('formulario.html')

        # ⚠️ Validar edad
        if not edad.isdigit() or int(edad) <= 0:
            flash("🔢 La edad debe ser un número positivo.", "warning")
            return render_template('formulario.html')

        # 🔍 Verificar si el correo ya existe
        conn = sqlite3.connect('datos.db')
        c = conn.cursor()
        c.execute("SELECT id FROM usuarios WHERE correo = ?", (correo,))
        existente = c.fetchone()

        if existente:
            conn.close()
            flash("🚫 Ya existe un usuario registrado con ese correo.", "danger")
            return render_template('formulario.html')

        # ✅ Insertar nuevo usuario
        c.execute("INSERT INTO usuarios (nombre, correo, edad) VALUES (?, ?, ?)",
                  (nombre, correo, edad))
        conn.commit()
        conn.close()

        flash("✅ Usuario agregado correctamente.", "success")
        return redirect('/usuarios')

    # GET: mostrar formulario vacío
    return render_template('formulario.html')
      
   


# Leer usuarios
@app.route('/usuarios')
def usuarios():
    conn = sqlite3.connect('datos.db')
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios')
    usuarios = c.fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

# Editar usuario
@app.route('/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    conn = sqlite3.connect('datos.db')
    c = conn.cursor()

    # Si el formulario fue enviado (POST)
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        edad = request.form['edad']

        c.execute("UPDATE usuarios SET nombre=?, correo=?, edad=? WHERE id=?", 
                  (nombre, correo, edad, user_id))
        conn.commit()
        conn.close()

        flash("✏️ Usuario actualizado.", "info")
        return redirect('/usuarios')

    # Si solo entramos a ver el formulario (GET)
    c.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    usuario = c.fetchone()
    conn.close()

    if not usuario:
        flash("⚠️ Usuario no encontrado.", "warning")
        return redirect('/usuarios')

    return render_template('editar.html', usuario=usuario)

# Eliminar usuario
@app.route('/usuarios/eliminar/<int:user_id>', methods=['POST'])
def eliminar_usuario(user_id):
    conn = sqlite3.connect('datos.db')
    c = conn.cursor()
    c.execute('DELETE FROM usuarios WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash("🗑️ Usuario eliminado.", "warning")
    return redirect('/usuarios')

if __name__ == '__main__':
    app.run(debug=True, port=5050)
