# app.py
import re
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# ✅ Crear instancia de la app Flask
app = Flask(__name__)

# ✅ Clave secreta para sesiones
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clave-super-secreta")

# ✅ Ruta segura para la base en Render
DATABASE = os.path.join("/tmp", "datos.db")

# ✅ Función para inicializar la base si no existe
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            edad INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ✅ Inicializar la base al iniciar la app
init_db()

# --- 1️⃣ Configurar Flask-Login antes del modelo ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# --- 2️⃣ Modelo User compatible con Flask-Login ---
class User(UserMixin):
    def __init__(self, id, nombre, correo, password_hash):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.password_hash = password_hash

    @staticmethod
    def get_by_email(correo):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE correo = ?", (correo,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(*row)
        return None

    @staticmethod
    def get_by_id(id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(*row)
        return None


# --- 3️⃣ Requerido por Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

DATABASE = 'datos.db'

#DATABASE = 'datos.db'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# --- MODELO USER ---
class User(UserMixin):
    def __init__(self, id, nombre, correo, password_hash):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.password_hash = password_hash

    @staticmethod
    def get_by_email(correo):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE correo = ?", (correo,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(*row)
        return None

    @staticmethod
    def get_by_id(id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(*row)
        return None


# Requerido por Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        correo = request.form['correo'].strip().lower()
        password = request.form['password']

        if not nombre or not correo or not password:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template('register.html')

        # validar formato simple de correo
        import re
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo):
            flash("Correo inválido.", "warning")
            return render_template('register.html')

        # verificar si ya existe
        if User.get_by_email(correo):
            flash("Ya existe una cuenta con ese correo.", "danger")
            return render_template('register.html')

        pw_hash = generate_password_hash(password)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO users (nombre, correo, password_hash) VALUES (?, ?, ?)", (nombre, correo, pw_hash))
        conn.commit()
        conn.close()

        flash("Cuenta creada correctamente. Inicia sesión ahora.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo'].strip().lower()
        password = request.form['password']
        user = User.get_by_email(correo)

        if not user or not check_password_hash(user.password_hash, password):
            flash("❌ Correo o contraseña incorrectos.", "danger")
            return render_template('login.html')

        login_user(user)
        flash(f"👋 Bienvenido {user.nombre}", "success")
        return redirect(url_for('formulario'))  # Redirige al CRUD

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for('login'))


# Ruta principal: redirige al formulario
@app.route('/')
@login_required
def home():
    return redirect('/formulario')

# Crear usuario

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
        return redirect(url_for('usuarios'))

    # GET: mostrar formulario vacío
    return render_template('formulario.html')

   


# Leer usuarios
@app.route('/usuarios')
@login_required
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
