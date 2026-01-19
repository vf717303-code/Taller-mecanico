from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "taller_secreto"

# ---------------- BD ----------------

def conectar_db():
    return sqlite3.connect("database.db")

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
        cursor.execute(
            "SELECT id FROM clientes WHERE nombre=? AND password=?",
            (nombre, password)
        )
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

    return render_template(
        "cliente_inicio.html",
        nombre=session["cliente_nombre"]
    )

# ---------------- AGENDAR CITA (CLIENTE) ----------------

@app.route("/agendar", methods=["GET", "POST"])
def agendar():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, marca, placas FROM autos WHERE cliente_id=?",
        (session["cliente_id"],)
    )
    autos = cursor.fetchall()

    if request.method == "POST":
        auto_id = request.form.get("auto")
        fecha = request.form.get("fecha")
        servicio = request.form.get("servicio")

        cursor.execute("""
            INSERT INTO citas (auto_id, fecha, servicio, estado, origen)
            VALUES (?, ?, ?, 'En admisión', 'cliente')
        """, (auto_id, fecha, servicio))

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
    cursor.execute("""
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
        WHERE autos.cliente_id = ?
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))

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
    cursor.execute("""
        SELECT autos.marca, autos.placas, citas.fecha, citas.servicio, citas.estado
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id=?
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))

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
    cursor.execute(
        "UPDATE citas SET estado='Aceptada' WHERE id=?",
        (cita_id,)
    )
    conn.commit()
    conn.close()

    return redirect("/empleado/citas_admision")

# ---------------- LOGOUT ----------------

@app.route("/salir")
def salir():
    session.clear()
    return redirect("/")

# ---------------- RUN (ACCESO EXTERNO) ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
