from flask import Flask, render_template, request, redirect, session
import os
import sqlite3
import psycopg2

app = Flask(__name__)
app.secret_key = "taller_secreto"

# ---------------- BD ----------------

def conectar_db():
    db_url = os.environ.get("DATABASE_URL")

    # Producción (Render) -> PostgreSQL
    if db_url:
        # Render a veces da postgres:// pero psycopg2 quiere postgresql://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(db_url)

    # Local -> SQLite
    return sqlite3.connect("database.db")


def es_postgres():
    return os.environ.get("DATABASE_URL") is not None


def p(s):
    """
    Helper para placeholders:
    - SQLite usa ? 
    - PostgreSQL usa %s
    """
    return "%s" if es_postgres() else "?"


# ---------------- LOGIN CLIENTE ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        password = request.form.get("password")

        if not nombre or not password:
            return render_template("login.html", error="Completa todos los campos")

        conn = conectar_db()
        cursor = conn.cursor()

        q = f"SELECT id FROM clientes WHERE nombre={p('')} AND password={p('')}"
        cursor.execute(q, (nombre, password))
        cliente = cursor.fetchone()

        conn.close()

        if cliente:
            session["cliente_id"] = cliente[0]
            session["cliente_nombre"] = nombre
            return redirect("/inicio")
        else:
            return render_template("login.html", error="Nombre o contraseña incorrectos")

    return render_template("login.html")


# ---------------- INICIO CLIENTE ----------------

@app.route("/inicio")
def inicio():
    if "cliente_id" not in session:
        return redirect("/")

    return render_template("cliente_inicio.html", nombre=session["cliente_nombre"])


# ---------------- AGENDAR CITA (CLIENTE) ----------------

@app.route("/agendar", methods=["GET", "POST"])
def agendar():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cursor = conn.cursor()

    q_autos = f"SELECT id, marca, placas FROM autos WHERE cliente_id={p('')}"
    cursor.execute(q_autos, (session["cliente_id"],))
    autos = cursor.fetchall()

    if request.method == "POST":
        auto_id = request.form.get("auto")
        fecha = request.form.get("fecha")
        servicio = request.form.get("servicio")

        q_insert = f"""
            INSERT INTO citas (auto_id, fecha, servicio, estado, origen)
            VALUES ({p('')}, {p('')}, {p('')}, 'En admisión', 'cliente')
        """
        cursor.execute(q_insert, (auto_id, fecha, servicio))

        conn.commit()
        conn.close()
        return redirect("/mis_citas")

    conn.close()
    return render_template("agendar_cita.html", autos=autos)


# ---------------- MIS CITAS (CLIENTE) ----------------

@app.route("/mis_citas")
def mis_citas():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cursor = conn.cursor()

    q = f"""
        SELECT 
            citas.id,
            citas.fecha,
            citas.servicio,
            citas.estado,
            autos.marca,
            autos.modelo,
            autos.placas
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id = {p('')}
        ORDER BY citas.fecha DESC
    """
    cursor.execute(q, (session["cliente_id"],))
    citas = cursor.fetchall()

    conn.close()
    return render_template("mis_citas.html", citas=citas)


# ---------------- HISTORIAL ----------------

@app.route("/historial")
def historial():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cursor = conn.cursor()

    q = f"""
        SELECT autos.marca, autos.placas, citas.fecha, citas.servicio, citas.estado
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id = {p('')}
        ORDER BY citas.fecha DESC
    """
    cursor.execute(q, (session["cliente_id"],))
    historial = cursor.fetchall()

    conn.close()
    return render_template("historial.html", historial=historial)


# =====================================================
# ======= SECCIÓN EMPLEADOS (ADMISIÓN DE CITAS) =======
# =====================================================

@app.route("/empleado/citas_admision")
def citas_admision():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            citas.id,
            citas.fecha,
            citas.servicio,
            autos.marca,
            autos.modelo,
            autos.placas,
            clientes.nombre
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        JOIN clientes ON autos.cliente_id = clientes.id
        WHERE citas.estado = 'En admisión'
        ORDER BY citas.fecha
    """)

    citas = cursor.fetchall()
    conn.close()

    return render_template("citas_admision.html", citas=citas)


@app.route("/empleado/aceptar_cita/<int:cita_id>")
def aceptar_cita(cita_id):
    conn = conectar_db()
    cursor = conn.cursor()

    q = f"UPDATE citas SET estado='Aceptada' WHERE id={p('')}"
    cursor.execute(q, (cita_id,))

    conn.commit()
    conn.close()

    return redirect("/empleado/citas_admision")


# ---------------- LOGOUT ----------------

@app.route("/salir")
def salir():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
# En Render NO uses app.run; Render usa gunicorn.
# Esto solo aplica localmente.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
