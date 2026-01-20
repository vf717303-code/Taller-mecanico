from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "taller_secreto"


# ---------------- BD ----------------
def conectar_db():
    """Conectar a SQLite localmente"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn


def placeholder():
    """SQLite usa ?"""
    return "?"


def fetchone(cursor):
    row = cursor.fetchone()
    return row


def fetchall(cursor):
    rows = cursor.fetchall()
    return rows


# ---------------- LOGIN CLIENTE ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        password = request.form.get("password")

        if not nombre or not password:
            return render_template("login.html", error="Completa todos los campos")

        conn = conectar_db()
        cur = conn.cursor()

        p = placeholder()
        sql = f"SELECT id, nombre FROM clientes WHERE nombre={p} AND password={p}"

        cur.execute(sql, (nombre, password))
        cliente = fetchone(cur)

        conn.close()

        if cliente:
            # RealDictCursor (Postgres) => dict; SQLite => tuple
            if isinstance(cliente, dict):
                session["cliente_id"] = cliente["id"]
                session["cliente_nombre"] = cliente["nombre"]
            else:
                session["cliente_id"] = cliente[0]
                session["cliente_nombre"] = nombre

            return redirect("/inicio")

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
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"SELECT id, marca, placas FROM autos WHERE cliente_id={p}", (session["cliente_id"],))
    autos = fetchall(cur)

    if request.method == "POST":
        auto_id = request.form.get("auto")
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        servicio = request.form.get("servicio")

        # Validar que todos los campos estén completos
        if not all([auto_id, fecha, hora, servicio]):
            return render_template("agendar_cita.html", autos=autos, error="Completa todos los campos")

        try:
            cur.execute(
                f"INSERT INTO citas (auto_id, fecha, hora, servicio, estado, origen) VALUES ({p}, {p}, {p}, {p}, 'En admisión', 'cliente')",
                (auto_id, fecha, hora, servicio)
            )
            conn.commit()
            conn.close()
            return redirect("/mis_citas")
        except Exception as e:
            print(f"Error al guardar cita: {e}")
            conn.close()
            return render_template("agendar_cita.html", autos=autos, error=f"Error: {str(e)}")

    conn.close()
    return render_template("agendar_cita.html", autos=autos)


# ---------------- MIS CITAS (CLIENTE) ----------------
@app.route("/mis_citas")
def mis_citas():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"""
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
        WHERE autos.cliente_id = {p}
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))

    citas = fetchall(cur)
    conn.close()

    return render_template("mis_citas.html", citas=citas)


# ---------------- HISTORIAL ----------------
@app.route("/historial")
def historial():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"""
        SELECT autos.marca, autos.placas, citas.fecha, citas.servicio, citas.estado
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id={p}
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))

    historial = fetchall(cur)
    conn.close()

    return render_template("historial.html", historial=historial)


# ---------------- EMPLEADO: CITAS EN ADMISION ----------------
@app.route("/empleado/citas_admision")
def citas_admision():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
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

    citas = fetchall(cur)
    conn.close()

    return render_template("citas_admision.html", citas=citas)


@app.route("/empleado/aceptar_cita/<int:cita_id>")
def aceptar_cita(cita_id):
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"UPDATE citas SET estado='Aceptada' WHERE id={p}", (cita_id,))
    conn.commit()
    conn.close()

    return redirect("/empleado/citas_admision")


# ---------------- LOGOUT ----------------
@app.route("/salir")
def salir():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
