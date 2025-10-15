# app.py
import os
import re
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# ======================================================
# 🔹 CONFIGURACIÓN PRINCIPAL
# ======================================================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clave-super-secreta")

# Base de datos en ruta temporal (Render reinicia /tmp en cada despliegue)
DATABASE = "/tmp/datos.db"


# ======================================================
# 🔹 FUNCIÓN PARA CREAR LAS TABLAS SI NO EXISTEN
# ======================================================
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Tabla CRUD
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            edad INTEGER NOT NULL
        )
    """)

    # Tabla de login
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tablas inicializadas correctamente.")


# ======================================================
# 🔹 CONFIGURAR FLASK-LOGIN
# ======================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ======================================================
# 🔹 CLASE USER PARA LOGIN
# ======================================================
class User(UserMixin):
    def __init__(self, id, nombre, correo, password):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.password = password

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


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


# ======================================================
# 🔹 RUTA DE REGISTRO
# ======================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        correo = request.form["correo"].strip()
        password = request.form["password"].strip()

        if not nombre or not correo or not password:
            flash("⚠️ Todos los campos son obligatorios.", "warning")
            return render_template("register.html")

        if User.get_by_email(correo):
            flash("🚫 Ya existe una cuenta con ese correo.", "danger")
            return render_template("register.html")

        hashed_pw = generate_password_hash(password)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO users (nombre, correo, password) VALUES (?, ?, ?)",
                  (nombre, correo, hashed_pw))
        conn.commit()
        conn.close()

        flash("✅ Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ======================================================
# 🔹 RUTA DE LOGIN
# ======================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip()
        password = request.form["password"].strip()

        user = User.get_by_email(correo)
        if not user or not check_password_hash(user.password, password):
            flash("❌ Credenciales incorrectas.", "danger")
            return render_template("login.html")

        login_user(user)
        flash(f"👋 Bienvenido, {user.nombre}!", "success")
        return redirect(url_for("usuarios"))

    return render_template("login.html")


# ======================================================
# 🔹 RUTA DE LOGOUT
# ======================================================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("👋 Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))


# ======================================================
# 🔹 CRUD DE USUARIOS
# ======================================================
@app.route("/")
@login_required
def home():
    return redirect(url_for("usuarios"))


@app.route("/usuarios")
@login_required
def usuarios():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/formulario", methods=["GET", "POST"])
@login_required
def formulario():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        correo = request.form["correo"].strip()
        edad = request.form["edad"].strip()

        if not nombre or not correo or not edad:
            flash("⚠️ Todos los campos son obligatorios.", "warning")
            return render_template("formulario.html")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
            flash("📧 Ingresa un correo electrónico válido.", "warning")
            return render_template("formulario.html")

        if not edad.isdigit() or int(edad) <= 0:
            flash("🔢 La edad debe ser un número positivo.", "warning")
            return render_template("formulario.html")

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT id FROM usuarios WHERE correo = ?", (correo,))
        existente = c.fetchone()
        if existente:
            conn.close()
            flash("🚫 Ya existe un usuario con ese correo.", "danger")
            return render_template("formulario.html")

        c.execute("INSERT INTO usuarios (nombre, correo, edad) VALUES (?, ?, ?)",
                  (nombre, correo, edad))
        conn.commit()
        conn.close()
        flash("✅ Usuario agregado correctamente.", "success")
        return redirect(url_for("usuarios"))

    return render_template("formulario.html")


@app.route("/usuarios/editar/<int:user_id>", methods=["GET", "POST"])
@login_required
def editar_usuario(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        correo = request.form["correo"].strip()
        edad = request.form["edad"].strip()

        c.execute("UPDATE usuarios SET nombre=?, correo=?, edad=? WHERE id=?",
                  (nombre, correo, edad, user_id))
        conn.commit()
        conn.close()
        flash("✏️ Usuario actualizado correctamente.", "info")
        return redirect(url_for("usuarios"))
    else:
        c.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
        usuario = c.fetchone()
        conn.close()
        return render_template("editar.html", usuario=usuario)


@app.route("/usuarios/eliminar/<int:user_id>")
@login_required
@app.route('/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("🗑️ Usuario eliminado correctamente.", "success")
    return redirect(url_for('usuarios'))



# ======================================================
# 🔹 EJECUCIÓN LOCAL
# ======================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
