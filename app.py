from flask import Flask, render_template, request, redirect, session, send_file, jsonify
import sqlite3
import os
import subprocess
import threading
import sys
from db import get_db_path

app = Flask(__name__)
app.secret_key = "taller_secreto"


# ---------------- BD ----------------
def conectar_db():
    """Conectar a SQLite localmente"""
    conn = sqlite3.connect(get_db_path())
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
@app.route("/login", methods=["GET", "POST"])
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


@app.route("/registro", methods=["GET", "POST"])
def registrar():
    """Mostrar formulario de registro o procesar registro"""
    if request.method == "GET":
        # Mostrar el formulario de registro
        return render_template("registro.html")
    
    # Procesar el registro (POST)
    nombre = request.form.get("reg_nombre")
    telefono = request.form.get("reg_telefono")
    correo = request.form.get("reg_correo")
    password = request.form.get("reg_password")
    password_confirm = request.form.get("reg_password_confirm")

    # Validaciones
    if not all([nombre, telefono, correo, password, password_confirm]):
        return render_template("registro.html", error_registro="Completa todos los campos")

    if password != password_confirm:
        return render_template("registro.html", error_registro="Las contraseñas no coinciden")

    if len(password) < 4:
        return render_template("registro.html", error_registro="La contraseña debe tener al menos 4 caracteres")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    # Verificar si el cliente ya existe
    cur.execute(f"SELECT id FROM clientes WHERE nombre={p}", (nombre,))
    if fetchone(cur):
        conn.close()
        return render_template("registro.html", error_registro="El nombre de usuario ya existe")

    # Insertar nuevo cliente
    try:
        sql = f"""
        INSERT INTO clientes (nombre, telefono, correo, password)
        VALUES ({p}, {p}, {p}, {p})
        """
        cur.execute(sql, (nombre, telefono, correo, password))
        conn.commit()
        conn.close()

        # Mostrar página de éxito
        return render_template("registro_exitoso.html")
    except Exception as e:
        conn.close()
        return render_template("registro.html", error_registro=f"Error al registrar: {str(e)}")


# ---------------- RESTABLECER CONTRASEÑA ----------------
@app.route("/restablecer-password", methods=["GET", "POST"])
def restablecer_password():
    """Formulario para verificar identidad del cliente"""
    if request.method == "GET":
        return render_template("restablecer_password.html")
    
    # Procesar verificación (POST)
    nombre = request.form.get("nombre")
    telefono = request.form.get("telefono")
    correo = request.form.get("correo")

    if not all([nombre, telefono, correo]):
        return render_template("restablecer_password.html", error="Completa todos los campos")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    # Verificar que el cliente existe con esos datos
    cur.execute(f"""
        SELECT id, nombre FROM clientes 
        WHERE nombre={p} AND telefono={p} AND correo={p}
    """, (nombre, telefono, correo))
    
    cliente = fetchone(cur)
    conn.close()

    if not cliente:
        return render_template("restablecer_password.html", 
                             error="Los datos no coinciden con ningún cliente registrado")

    # Redirigir al formulario de nueva contraseña
    return redirect(f"/nueva-password/{cliente[0]}")


@app.route("/nueva-password/<int:cliente_id>", methods=["GET", "POST"])
def nueva_password(cliente_id):
    """Formulario para establecer nueva contraseña"""
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    # Obtener nombre del cliente
    cur.execute(f"SELECT nombre FROM clientes WHERE id={p}", (cliente_id,))
    cliente = fetchone(cur)
    
    if not cliente:
        conn.close()
        return redirect("/login")

    if request.method == "GET":
        conn.close()
        return render_template("nueva_password.html", nombre=cliente[0])
    
    # Procesar cambio de contraseña (POST)
    nueva_password = request.form.get("nueva_password")
    confirmar_password = request.form.get("confirmar_password")

    if not all([nueva_password, confirmar_password]):
        conn.close()
        return render_template("nueva_password.html", nombre=cliente[0], 
                             error="Completa todos los campos")

    if nueva_password != confirmar_password:
        conn.close()
        return render_template("nueva_password.html", nombre=cliente[0], 
                             error="Las contraseñas no coinciden")

    if len(nueva_password) < 4:
        conn.close()
        return render_template("nueva_password.html", nombre=cliente[0], 
                             error="La contraseña debe tener al menos 4 caracteres")

    # Actualizar contraseña en la base de datos
    try:
        cur.execute(f"""
            UPDATE clientes 
            SET password={p} 
            WHERE id={p}
        """, (nueva_password, cliente_id))
        conn.commit()
        conn.close()

        # Redirigir al login con mensaje de éxito
        return redirect("/login?password_changed=1")
    except Exception as e:
        conn.close()
        return render_template("nueva_password.html", nombre=cliente[0], 
                             error=f"Error al actualizar contraseña: {str(e)}")



# ---------------- INICIO CLIENTE ----------------
@app.route("/inicio")
def inicio():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()
    cliente_id = session["cliente_id"]

    # 1. Próxima cita (más cercana a la fecha actual)
    cur.execute(f"""
        SELECT citas.id, citas.fecha, citas.hora, citas.servicio, citas.estado
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id = {p}
        ORDER BY citas.fecha ASC
        LIMIT 1
    """, (cliente_id,))
    proxima_cita = fetchone(cur)

    # 2. Mis vehículos (total de autos)
    cur.execute(f"SELECT COUNT(*) FROM autos WHERE cliente_id = {p}", (cliente_id,))
    total_autos_row = fetchone(cur)
    total_autos = total_autos_row[0] if isinstance(total_autos_row, tuple) else total_autos_row["COUNT(*)"]

    # 3. Último auto atendido
    cur.execute(f"""
        SELECT a.marca, a.modelo
        FROM autos a
        WHERE a.cliente_id = {p}
        ORDER BY a.id DESC
        LIMIT 1
    """, (cliente_id,))
    ultimo_auto = fetchone(cur)

    # 4. Último pedido de piezas
    cur.execute(f"""
        SELECT p.fecha, p.servicio, p.pieza_refaccion, p.estado, pr.nombre as proveedor_nombre
        FROM piezas p
        JOIN proveedores pr ON p.proveedor_id = pr.id
        WHERE p.cliente_id = {p}
        ORDER BY p.fecha DESC
        LIMIT 1
    """, (cliente_id,))
    ultimo_servicio = fetchone(cur)

    # 5. Estado actual del vehículo (cita activa más reciente)
    cur.execute(f"""
        SELECT citas.estado, citas.fecha, citas.servicio, autos.marca, autos.modelo
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id = {p} AND citas.estado IN ('En reparación', 'En espera', 'Listo para entrega')
        ORDER BY citas.fecha DESC
        LIMIT 1
    """, (cliente_id,))
    estado_actual = fetchone(cur)

    conn.close()

    # Convertir resultados a diccionarios si es necesario
    proxima_cita_dict = None
    if proxima_cita:
        proxima_cita_dict = {
            "id": proxima_cita["id"] if isinstance(proxima_cita, sqlite3.Row) else proxima_cita[0],
            "fecha": proxima_cita["fecha"] if isinstance(proxima_cita, sqlite3.Row) else proxima_cita[1],
            "hora": proxima_cita["hora"] if isinstance(proxima_cita, sqlite3.Row) else proxima_cita[2],
            "servicio": proxima_cita["servicio"] if isinstance(proxima_cita, sqlite3.Row) else proxima_cita[3],
            "estado": proxima_cita["estado"] if isinstance(proxima_cita, sqlite3.Row) else proxima_cita[4],
        }

    ultimo_auto_dict = None
    if ultimo_auto:
        ultimo_auto_dict = {
            "marca": ultimo_auto["marca"] if isinstance(ultimo_auto, sqlite3.Row) else ultimo_auto[0],
            "modelo": ultimo_auto["modelo"] if isinstance(ultimo_auto, sqlite3.Row) else ultimo_auto[1],
        }

    ultimo_servicio_dict = None
    if ultimo_servicio:
        ultimo_servicio_dict = {
            "fecha": ultimo_servicio["fecha"] if isinstance(ultimo_servicio, sqlite3.Row) else ultimo_servicio[0],
            "servicio": ultimo_servicio["servicio"] if isinstance(ultimo_servicio, sqlite3.Row) else ultimo_servicio[1],
            "pieza_refaccion": ultimo_servicio["pieza_refaccion"] if isinstance(ultimo_servicio, sqlite3.Row) else ultimo_servicio[2],
            "estado": ultimo_servicio["estado"] if isinstance(ultimo_servicio, sqlite3.Row) else ultimo_servicio[3],
            "proveedor_nombre": ultimo_servicio["proveedor_nombre"] if isinstance(ultimo_servicio, sqlite3.Row) else ultimo_servicio[4],
        }

    estado_actual_dict = None
    if estado_actual:
        estado_actual_dict = {
            "estado": estado_actual["estado"] if isinstance(estado_actual, sqlite3.Row) else estado_actual[0],
            "fecha": estado_actual["fecha"] if isinstance(estado_actual, sqlite3.Row) else estado_actual[1],
            "servicio": estado_actual["servicio"] if isinstance(estado_actual, sqlite3.Row) else estado_actual[2],
            "marca": estado_actual["marca"] if isinstance(estado_actual, sqlite3.Row) else estado_actual[3],
            "modelo": estado_actual["modelo"] if isinstance(estado_actual, sqlite3.Row) else estado_actual[4],
        }

    return render_template("cliente_inicio.html", 
        nombre=session["cliente_nombre"],
        proxima_cita=proxima_cita_dict,
        total_autos=total_autos,
        ultimo_auto=ultimo_auto_dict,
        ultimo_servicio=ultimo_servicio_dict,
        estado_actual=estado_actual_dict
    )


# ---------------- PIEZAS (CLIENTE) ----------------
@app.route("/piezas")
def piezas():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()

    p = placeholder()
    sql = f"""
    SELECT 
        p.id, p.fecha, c.nombre as cliente, a.marca, a.modelo, a.placas, p.servicio, 
        p.pieza_refaccion, prov.nombre as proveedor, prov.telefono, 
        prov.correo, prov.direccion, prov.ruc, p.estado, COALESCE(p.costo, 0) AS costo
    FROM piezas p
    JOIN clientes c ON p.cliente_id = c.id
    JOIN autos a ON p.auto_id = a.id
    JOIN proveedores prov ON p.proveedor_id = prov.id
    WHERE c.id = {p}
    ORDER BY p.fecha DESC
    """
    
    cur.execute(sql, (session["cliente_id"],))
    pedidos = cur.fetchall()
    conn.close()

    # Convertir a diccionarios para el template
    pedidos_list = []
    for pedido in pedidos:
        pedidos_list.append({
            "id": pedido["id"],
            "fecha": pedido["fecha"],
            "cliente": pedido["cliente"],
            "auto": f"{pedido['marca']} {pedido['modelo']}" if isinstance(pedido, sqlite3.Row) else f"{pedido[3]} {pedido[4]}",
            "placa": pedido["placas"] if isinstance(pedido, sqlite3.Row) else pedido[5],
            "servicio": pedido["servicio"],
            "pieza_refaccion": pedido["pieza_refaccion"],
            "proveedor": pedido["proveedor"],
            "telefono": pedido["telefono"],
            "correo": pedido["correo"],
            "direccion": pedido["direccion"],
            "ruc": pedido["ruc"],
            "estado": pedido["estado"],
            "costo": pedido["costo"]
        })

    return render_template("piezas.html", pedidos=pedidos_list)

@app.route("/api/piezas")
def api_piezas():
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()
    cur.execute(f"""
    SELECT 
        p.id, p.fecha, c.nombre as cliente, a.marca, a.modelo, a.placas, p.servicio, 
        p.pieza_refaccion, prov.nombre as proveedor, prov.telefono, 
        prov.correo, prov.direccion, prov.ruc, p.estado, COALESCE(p.costo, 0) AS costo
    FROM piezas p
    JOIN clientes c ON p.cliente_id = c.id
    JOIN autos a ON p.auto_id = a.id
    JOIN proveedores prov ON p.proveedor_id = prov.id
    WHERE c.id = {p}
    ORDER BY p.fecha DESC
    """, (session["cliente_id"],))
    rows = cur.fetchall()
    conn.close()
    pedidos_list = []
    for r in rows:
        pedidos_list.append({
            "id": r["id"] if isinstance(r, sqlite3.Row) else r[0],
            "fecha": r["fecha"] if isinstance(r, sqlite3.Row) else r[1],
            "cliente": r["cliente"] if isinstance(r, sqlite3.Row) else r[2],
            "auto": f"{r['marca']} {r['modelo']}" if isinstance(r, sqlite3.Row) else f"{r[3]} {r[4]}",
            "placa": r["placas"] if isinstance(r, sqlite3.Row) else r[5],
            "servicio": r["servicio"] if isinstance(r, sqlite3.Row) else r[6],
            "pieza_refaccion": r["pieza_refaccion"] if isinstance(r, sqlite3.Row) else r[7],
            "proveedor": r["proveedor"] if isinstance(r, sqlite3.Row) else r[8],
            "telefono": r["telefono"] if isinstance(r, sqlite3.Row) else r[9],
            "correo": r["correo"] if isinstance(r, sqlite3.Row) else r[10],
            "direccion": r["direccion"] if isinstance(r, sqlite3.Row) else r[11],
            "ruc": r["ruc"] if isinstance(r, sqlite3.Row) else r[12],
            "estado": r["estado"] if isinstance(r, sqlite3.Row) else r[13],
            "costo": r["costo"] if isinstance(r, sqlite3.Row) else r[14],
        })
    return jsonify({"ok": True, "pedidos": pedidos_list})


@app.route("/api/proveedores")
def api_proveedores():
    """Obtener lista de proveedores para el dropdown"""
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, telefono, correo, direccion, ruc FROM proveedores")
    proveedores = cur.fetchall()
    conn.close()
    
    prov_list = []
    for prov in proveedores:
        prov_list.append({
            "id": prov["id"] if isinstance(prov, sqlite3.Row) else prov[0],
            "nombre": prov["nombre"] if isinstance(prov, sqlite3.Row) else prov[1],
            "telefono": prov["telefono"] if isinstance(prov, sqlite3.Row) else prov[2],
            "correo": prov["correo"] if isinstance(prov, sqlite3.Row) else prov[3],
            "direccion": prov["direccion"] if isinstance(prov, sqlite3.Row) else prov[4],
            "ruc": prov["ruc"] if isinstance(prov, sqlite3.Row) else prov[5],
        })
    
    return jsonify({"ok": True, "proveedores": prov_list})


@app.route("/api/autos")
def api_autos():
    """Obtener lista de autos del cliente"""
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()
    cur.execute(f"SELECT id, marca, modelo, placas FROM autos WHERE cliente_id = {p}", (session["cliente_id"],))
    autos = cur.fetchall()
    conn.close()
    
    autos_list = []
    for auto in autos:
        autos_list.append({
            "id": auto["id"] if isinstance(auto, sqlite3.Row) else auto[0],
            "marca": auto["marca"] if isinstance(auto, sqlite3.Row) else auto[1],
            "modelo": auto["modelo"] if isinstance(auto, sqlite3.Row) else auto[2],
            "placas": auto["placas"] if isinstance(auto, sqlite3.Row) else auto[3],
        })
    
    return jsonify({"ok": True, "autos": autos_list})


@app.route("/api/crear_pedido", methods=["POST"])
def crear_pedido():
    """Crear un nuevo pedido de pieza"""
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    
    data = request.get_json()
    
    try:
        conn = conectar_db()
        cur = conn.cursor()
        p = placeholder()
        
        from datetime import datetime
        fecha = datetime.now().strftime("%d/%m/%Y")
        
        sql = f"""
        INSERT INTO piezas (cliente_id, auto_id, proveedor_id, servicio, pieza_refaccion, costo, estado, fecha)
        VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """
        
        cur.execute(sql, (
            session["cliente_id"],
            data.get("auto_id"),
            data.get("proveedor_id"),
            data.get("servicio"),
            data.get("pieza_refaccion"),
            data.get("costo", 0),
            "Pendiente",
            fecha
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({"ok": True, "message": "Pedido creado exitosamente"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


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

        # Verificar si ya existe una cita para esa fecha y hora (no rechazada)
        cur.execute(
            f"SELECT COUNT(*) FROM citas WHERE fecha={p} AND hora={p} AND estado != 'Rechazada'",
            (fecha, hora)
        )
        citas_conflicto = cur.fetchone()[0]

        if citas_conflicto > 0:
            conn.close()
            return render_template("agendar_cita.html", autos=autos, error=f"Ya existe una cita programada para {fecha} a las {hora}")

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
            citas.hora,
            citas.servicio,
            citas.estado,
            autos.id as auto_id,
            autos.marca,
            autos.modelo,
            autos.placas
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id = {p} AND (citas.origen = 'cliente' OR citas.origen IS NULL)
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))

    citas = fetchall(cur)
    conn.close()

    return render_template("mis_citas.html", citas=citas)

@app.route("/api/mis_citas")
def api_mis_citas():
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()
    cur.execute(f"""
        SELECT 
            citas.id,
            citas.fecha,
            citas.hora,
            citas.servicio,
            citas.estado,
            autos.id as auto_id,
            autos.marca,
            autos.modelo,
            autos.placas
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE autos.cliente_id = {p} AND (citas.origen = 'cliente' OR citas.origen IS NULL)
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))
    rows = cur.fetchall()
    conn.close()
    citas_list = []
    for r in rows:
        citas_list.append({
            "id": r[0] if not isinstance(r, sqlite3.Row) else r["id"],
            "fecha": r[1] if not isinstance(r, sqlite3.Row) else r["fecha"],
            "hora": r[2] if not isinstance(r, sqlite3.Row) else r["hora"],
            "servicio": r[3] if not isinstance(r, sqlite3.Row) else r["servicio"],
            "estado": r[4] if not isinstance(r, sqlite3.Row) else r["estado"],
            "auto_id": r[5] if not isinstance(r, sqlite3.Row) else r["auto_id"],
            "marca": r[6] if not isinstance(r, sqlite3.Row) else r["marca"],
            "modelo": r[7] if not isinstance(r, sqlite3.Row) else r["modelo"],
            "placas": r[8] if not isinstance(r, sqlite3.Row) else r["placas"],
        })
    return jsonify({"ok": True, "citas": citas_list})


@app.route("/api/mis_citas/<int:cita_id>/update", methods=["POST"])
def api_update_mis_cita(cita_id):
    """Actualizar cita del cliente (solo origen cliente)"""
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401

    data = request.get_json(silent=True) or {}
    fecha = (data.get("fecha") or "").strip()
    hora = (data.get("hora") or "").strip()
    servicio = (data.get("servicio") or "").strip()
    auto_id = (data.get("auto_id") or "").strip()

    if not fecha or not hora or not servicio or not auto_id:
        return jsonify({"ok": False, "error": "Completa todos los campos"}), 400

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"""
        SELECT citas.id, citas.estado
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        WHERE citas.id = {p} AND autos.cliente_id = {p}
          AND (citas.origen = 'cliente' OR citas.origen IS NULL)
    """, (cita_id, session["cliente_id"]))
    cita = cur.fetchone()

    if not cita:
        conn.close()
        return jsonify({"ok": False, "error": "No autorizado"}), 403

    estado = cita[1] if not isinstance(cita, sqlite3.Row) else cita["estado"]
    if estado != "En admisión":
        conn.close()
        return jsonify({"ok": False, "error": "Solo se pueden editar citas en admisión"}), 400

    # Validar que el auto pertenezca al cliente
    cur.execute(
        f"SELECT COUNT(*) FROM autos WHERE id={p} AND cliente_id={p}",
        (auto_id, session["cliente_id"])
    )
    if cur.fetchone()[0] == 0:
        conn.close()
        return jsonify({"ok": False, "error": "Auto no válido"}), 400

    try:
        cur.execute(
            f"UPDATE citas SET fecha={p}, hora={p}, servicio={p}, auto_id={p} WHERE id={p}",
            (fecha, hora, servicio, auto_id, cita_id)
        )
        conn.commit()
        return jsonify({"ok": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        conn.close()


# ---------------- CITAS ASIGNADAS (CLIENTE) ----------------
@app.route("/citas_asignadas")
def citas_asignadas():
    """Ver citas asignadas por empleados"""
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"""
        SELECT 
            citas.id,
            citas.fecha,
            citas.hora,
            citas.servicio,
            citas.estado,
            autos.marca,
            autos.modelo,
            autos.placas,
            COALESCE(empleados.nombre, 'Sin asignar') as mecanico
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        LEFT JOIN empleados ON citas.mecanico_id = empleados.id
        WHERE autos.cliente_id = {p} AND citas.origen = 'empleado'
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))

    citas = fetchall(cur)
    conn.close()

    return render_template("citas_asignadas.html", citas=citas)

@app.route("/api/citas_asignadas")
def api_citas_asignadas():
    """API para obtener citas asignadas por empleados"""
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()
    
    cur.execute(f"""
        SELECT 
            citas.id,
            citas.fecha,
            citas.hora,
            citas.servicio,
            citas.estado,
            autos.marca,
            autos.modelo,
            autos.placas,
            COALESCE(empleados.nombre, 'Sin asignar') as mecanico
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        LEFT JOIN empleados ON citas.mecanico_id = empleados.id
        WHERE autos.cliente_id = {p} AND citas.origen = 'empleado'
        ORDER BY citas.fecha DESC
    """, (session["cliente_id"],))
    
    rows = cur.fetchall()
    conn.close()
    
    citas_list = []
    for r in rows:
        citas_list.append({
            "id": r[0] if not isinstance(r, sqlite3.Row) else r["id"],
            "fecha": r[1] if not isinstance(r, sqlite3.Row) else r["fecha"],
            "hora": r[2] if not isinstance(r, sqlite3.Row) else r["hora"],
            "servicio": r[3] if not isinstance(r, sqlite3.Row) else r["servicio"],
            "estado": r[4] if not isinstance(r, sqlite3.Row) else r["estado"],
            "marca": r[5] if not isinstance(r, sqlite3.Row) else r["marca"],
            "modelo": r[6] if not isinstance(r, sqlite3.Row) else r["modelo"],
            "placas": r[7] if not isinstance(r, sqlite3.Row) else r["placas"],
            "mecanico": r[8] if not isinstance(r, sqlite3.Row) else r["mecanico"],
        })
    
    return jsonify({"ok": True, "citas": citas_list})


# ---------------- HISTORIAL ----------------
@app.route("/historial")
def historial():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    # Obtener todos los autos del cliente con sus citas
    cur.execute(f"""
        SELECT autos.id, autos.marca, autos.modelo, autos.placas, 
               citas.fecha, citas.servicio, citas.estado, citas.costo, COALESCE(empleados.nombre, 'Sin asignar')
        FROM autos
        LEFT JOIN citas ON citas.auto_id = autos.id
        LEFT JOIN empleados ON citas.mecanico_id = empleados.id
        WHERE autos.cliente_id={p}
        ORDER BY autos.id, citas.fecha DESC
    """, (session["cliente_id"],))

    registros = fetchall(cur)
    conn.close()

    # Agrupar citas por auto
    autos_citas = {}
    for registro in registros:
        auto_id, marca, modelo, placas = registro[0:4]
        cita_data = registro[4:]
        
        if auto_id not in autos_citas:
            autos_citas[auto_id] = {
                'marca': marca,
                'modelo': modelo,
                'placas': placas,
                'citas': []
            }
        
        # Solo agregar cita si existe (no es NULL)
        if cita_data[0] is not None:
            autos_citas[auto_id]['citas'].append({
                'fecha': cita_data[0],
                'servicio': cita_data[1],
                'estado': cita_data[2],
                'costo': cita_data[3] or 0,
                'mecanico': cita_data[4]
            })

    return render_template("historial.html", autos_citas=autos_citas)

@app.route("/api/historial")
def api_historial():
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"""
        SELECT autos.id, autos.marca, autos.modelo, autos.placas, 
               citas.fecha, citas.servicio, citas.estado, citas.costo, COALESCE(empleados.nombre, 'Sin asignar') as mecanico
        FROM autos
        LEFT JOIN citas ON citas.auto_id = autos.id
        LEFT JOIN empleados ON citas.mecanico_id = empleados.id
        WHERE autos.cliente_id={p}
        ORDER BY autos.id, citas.fecha DESC
    """, (session["cliente_id"],))

    registros = fetchall(cur)
    conn.close()

    autos_citas = {}
    for registro in registros:
        auto_id = registro[0] if not isinstance(registro, sqlite3.Row) else registro["id"]
        marca = registro[1] if not isinstance(registro, sqlite3.Row) else registro["marca"]
        modelo = registro[2] if not isinstance(registro, sqlite3.Row) else registro["modelo"]
        placas = registro[3] if not isinstance(registro, sqlite3.Row) else registro["placas"]
        cita_data = registro[4:] if not isinstance(registro, sqlite3.Row) else (
            registro["fecha"], registro["servicio"], registro["estado"], 
            registro["costo"], registro["mecanico"]
        )
        
        if auto_id not in autos_citas:
            autos_citas[auto_id] = {
                'marca': marca,
                'modelo': modelo,
                'placas': placas,
                'citas': []
            }
        
        if cita_data[0] is not None:
            autos_citas[auto_id]['citas'].append({
                'fecha': cita_data[0],
                'servicio': cita_data[1],
                'estado': cita_data[2],
                'costo': cita_data[3] or 0,
                'mecanico': cita_data[4]
            })

    return jsonify({"ok": True, "autos_citas": autos_citas})


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

# ---------------- CITAS PENDIENTES (EMPLEADO) ----------------
@app.route("/empleado/inicio")
def empleado_inicio():
    """Página de inicio para empleados"""
    return render_template("empleado_inicio.html")


@app.route("/empleado/citas_pendientes")
def citas_pendientes():
    """Ver citas pendientes para aceptar o rechazar"""
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(f"""
        SELECT 
            citas.id,
            clientes.nombre,
            autos.marca,
            autos.modelo,
            autos.placas,
            citas.fecha,
            citas.hora,
            citas.servicio,
            COALESCE(empleados.nombre, 'Sin asignar')
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        JOIN clientes ON autos.cliente_id = clientes.id
        LEFT JOIN empleados ON citas.mecanico_id = empleados.id
        WHERE citas.estado = 'En admisión'
        ORDER BY citas.fecha, citas.hora
    """)

    citas = fetchall(cur)
    conn.close()

    return render_template("citas_pendientes.html", citas=citas)


# ---------------- ACEPTAR CITA (EMPLEADO) ----------------
@app.route("/empleado/aceptar_cita/<int:cita_id>", methods=["POST"])
def aceptar_cita_empleado(cita_id):
    """Aceptar una cita pendiente"""
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    try:
        cur.execute(f"UPDATE citas SET estado='Aceptada' WHERE id={p}", (cita_id,))
        conn.commit()
        print(f"✓ Cita {cita_id} aceptada")
    except Exception as e:
        print(f"Error al aceptar cita: {e}")
    finally:
        conn.close()

    return redirect("/empleado/citas_pendientes")


# ---------------- RECHAZAR CITA (EMPLEADO) ----------------
@app.route("/empleado/rechazar_cita/<int:cita_id>", methods=["POST"])
def rechazar_cita_empleado(cita_id):
    """Rechazar una cita pendiente"""
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    try:
        cur.execute(f"UPDATE citas SET estado='Rechazada' WHERE id={p}", (cita_id,))
        conn.commit()
        print(f"✓ Cita {cita_id} rechazada")
    except Exception as e:
        print(f"Error al rechazar cita: {e}")
    finally:
        conn.close()

    return redirect("/empleado/citas_pendientes")

# ---------------- PERFIL DEL CLIENTE ----------------
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    # Si el usuario guarda cambios
    if request.method == "POST":
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")
        password = request.form.get("password")

        if not all([telefono, correo, password]):
            return render_template(
                "perfil.html",
                error="Completa todos los campos"
            )

        cur.execute(
            f"""
            UPDATE clientes
            SET telefono={p}, correo={p}, password={p}
            WHERE id={p}
            """,
            (telefono, correo, password, session["cliente_id"])
        )
        conn.commit()

    # Obtener datos actualizados del cliente
    cur.execute(
        f"""
        SELECT nombre, telefono, correo, password
        FROM clientes
        WHERE id={p}
        """,
        (session["cliente_id"],)
    )

    cliente = fetchone(cur)
    conn.close()

    cliente_data = {
        "nombre": cliente["nombre"],
        "telefono": cliente["telefono"],
        "correo": cliente["correo"],
        "password": cliente["password"]
    }

    return render_template("perfil.html", cliente=cliente_data)

@app.route("/api/perfil")
def api_perfil():
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    conn = conectar_db()
    cur = conectar_db().cursor()
    p = placeholder()
    cur.execute(
        f"""
        SELECT nombre, telefono, correo, password
        FROM clientes
        WHERE id={p}
        """,
        (session["cliente_id"],)
    )
    c = cur.fetchone()
    conn.close()
    if not c:
        return jsonify({"ok": False, "error": "No encontrado"}), 404
    cliente_data = {
        "nombre": c["nombre"] if isinstance(c, sqlite3.Row) else c[0],
        "telefono": c["telefono"] if isinstance(c, sqlite3.Row) else c[1],
        "correo": c["correo"] if isinstance(c, sqlite3.Row) else c[2],
        "password": c["password"] if isinstance(c, sqlite3.Row) else c[3],
    }
    return jsonify({"ok": True, "cliente": cliente_data})

#-----------------MIS AUTOS-----------------
@app.route("/mis_autos")
def mis_autos():
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, marca, modelo, placas
        FROM autos
        WHERE cliente_id = ?
    """, (session["cliente_id"],))

    autos = cur.fetchall()
    conn.close()

    return render_template("mis_autos.html", autos=autos)

@app.route("/api/mis_autos")
def api_mis_autos():
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, marca, modelo, placas
        FROM autos
        WHERE cliente_id = ?
        ORDER BY id DESC
        """,
        (session["cliente_id"],)
    )
    rows = cur.fetchall()
    conn.close()
    autos_list = []
    for r in rows:
        autos_list.append({
            "id": r["id"] if isinstance(r, sqlite3.Row) else r[0],
            "marca": r["marca"] if isinstance(r, sqlite3.Row) else r[1],
            "modelo": r["modelo"] if isinstance(r, sqlite3.Row) else r[2],
            "placas": r["placas"] if isinstance(r, sqlite3.Row) else r[3],
        })
    return jsonify({"ok": True, "autos": autos_list})
#---------------- GUARDAR AUTO (CLIENTE) ----------------
@app.route("/agregar_auto", methods=["GET", "POST"])
def agregar_auto():
    if "cliente_id" not in session:
        return redirect("/")

    if request.method == "POST":
        marca = request.form.get("marca")
        modelo = request.form.get("modelo")
        placas = request.form.get("placas")

        if not all([marca, modelo, placas]):
            return render_template("agregar_auto.html", error="Completa todos los campos")

        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO autos (cliente_id, marca, modelo, placas)
            VALUES (?, ?, ?, ?)
        """, (session["cliente_id"], marca, modelo, placas))
        conn.commit()
        conn.close()

        return redirect("/mis_autos")

    return render_template("agregar_auto.html")


# ---------------- EDITAR AUTO (CLIENTE) ----------------
@app.route("/editar_auto/<int:auto_id>")
def editar_auto(auto_id):
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    cur.execute(
        f"""
        SELECT id, marca, modelo, placas
        FROM autos
        WHERE id={p} AND cliente_id={p}
        """,
        (auto_id, session["cliente_id"],)
    )
    auto = cur.fetchone()
    conn.close()

    if not auto:
        return redirect("/mis_autos")

    # sqlite3.Row permite acceso por nombre; si es tuple, adaptamos
    auto_data = {
        "id": auto["id"] if isinstance(auto, sqlite3.Row) else auto[0],
        "marca": auto["marca"] if isinstance(auto, sqlite3.Row) else auto[1],
        "modelo": auto["modelo"] if isinstance(auto, sqlite3.Row) else auto[2],
        "placas": auto["placas"] if isinstance(auto, sqlite3.Row) else auto[3],
    }

    return render_template("editar_auto.html", auto=auto_data)


# ---------------- API: GUARDADO AUTOMÁTICO DE AUTO ----------------
@app.route("/api/auto/<int:auto_id>/update", methods=["POST"])
def api_update_auto(auto_id):
    if "cliente_id" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401

    data = request.get_json(silent=True) or {}
    campos = {}
    for campo in ("marca", "modelo", "placas"):
        if campo in data:
            valor = (data.get(campo) or "").strip()
            campos[campo] = valor

    if not campos:
        return jsonify({"ok": False, "error": "Sin cambios"}), 400

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    # Verificar que el auto pertenezca al cliente
    cur.execute(f"SELECT COUNT(*) FROM autos WHERE id={p} AND cliente_id={p}", (auto_id, session["cliente_id"]))
    existe = cur.fetchone()[0]
    if existe == 0:
        conn.close()
        return jsonify({"ok": False, "error": "No autorizado"}), 403

    # Construir UPDATE dinámico
    set_clause = ", ".join([f"{k}={p}" for k in campos.keys()])
    params = list(campos.values()) + [auto_id, session["cliente_id"]]

    try:
        cur.execute(
            f"UPDATE autos SET {set_clause} WHERE id={p} AND cliente_id={p}",
            tuple(params)
        )
        conn.commit()
        return jsonify({"ok": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        conn.close()


# ---------------- ELIMINAR AUTO (CLIENTE) ----------------
@app.route("/eliminar_auto/<int:auto_id>")
def eliminar_auto(auto_id):
    if "cliente_id" not in session:
        return redirect("/")

    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()

    try:
        cur.execute(f"DELETE FROM autos WHERE id={p} AND cliente_id={p}", (auto_id, session["cliente_id"]))
        conn.commit()
    except Exception as e:
        print(f"Error al eliminar auto: {e}")
    finally:
        conn.close()

    return redirect("/mis_autos")





# ---------------- GENERAR PDF DE AUTO ----------------
@app.route("/generar_pdf/<int:auto_id>")
def generar_pdf(auto_id):
    if "cliente_id" not in session:
        return redirect("/")
    
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from io import BytesIO
    from datetime import datetime
    
    conn = conectar_db()
    cur = conn.cursor()
    p = placeholder()
    
    # Obtener información del auto y cliente
    cur.execute(f"""
        SELECT autos.marca, autos.modelo, autos.placas, clientes.nombre, clientes.telefono, clientes.correo
        FROM autos
        JOIN clientes ON autos.cliente_id = clientes.id
        WHERE autos.id={p} AND autos.cliente_id={p}
    """, (auto_id, session["cliente_id"]))
    
    auto_info = cur.fetchone()
    if not auto_info:
        conn.close()
        return redirect("/historial")
    
    marca, modelo, placas, cliente_nombre, telefono, correo = auto_info
    
    # Obtener citas del auto
    cur.execute(f"""
        SELECT fecha, servicio, costo, estado
        FROM citas
        WHERE auto_id={p}
        ORDER BY fecha DESC
    """, (auto_id,))
    
    citas = cur.fetchall()
    conn.close()
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff9800'),
        spaceAfter=10,
        alignment=1
    )
    
    # Título
    elements.append(Paragraph("TALLER MECÁNICO", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del cliente y auto
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=5
    )
    
    elements.append(Paragraph(f"<b>Cliente:</b> {cliente_nombre}", info_style))
    elements.append(Paragraph(f"<b>Teléfono:</b> {telefono}", info_style))
    elements.append(Paragraph(f"<b>Correo:</b> {correo}", info_style))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph(f"<b>Vehículo:</b> {marca} {modelo}", info_style))
    elements.append(Paragraph(f"<b>Placas:</b> {placas}", info_style))
    elements.append(Paragraph(f"<b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de citas
    if citas:
        table_data = [['Fecha', 'Servicio', 'Costo', 'Estado']]
        total_costo = 0
        
        for cita in citas:
            fecha, servicio, costo, estado = cita
            costo = costo or 0
            total_costo += costo
            table_data.append([
                str(fecha),
                str(servicio),
                f"${costo:.2f}",
                str(estado)
            ])
        
        # Agregar fila de total
        table_data.append(['', '', 'TOTAL:', f"${total_costo:.2f}"])
        
        table = Table(table_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("<b>No hay citas registradas para este vehículo</b>", info_style))
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Ticket_{marca}_{placas}_{datetime.now().strftime('%d%m%Y')}.pdf"
    )


# ============ SEGUIMIENTO DE ESTADO DEL VEHÍCULO ============

@app.route("/empleado/seguimiento")
def seguimiento_estado():
    """Panel de seguimiento de estado de vehículos para empleados"""
    from actualizacion_estado_vehiculo import obtener_autos_con_citas, obtener_estadisticas
    
    if "empleado_id" not in session:
        return redirect("/")
    
    autos = obtener_autos_con_citas()
    estadisticas = obtener_estadisticas()
    
    return render_template("seguimiento_estado.html", 
                         autos=autos, 
                         estadisticas=estadisticas)


@app.route("/empleado/seguimiento/detalle/<int:cita_id>")
def detalle_seguimiento(cita_id):
    """Detalle de una cita específica"""
    from actualizacion_estado_vehiculo import obtener_auto_por_id, obtener_empleados
    
    if "empleado_id" not in session:
        return redirect("/")
    
    conn = conectar_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            c.id,
            c.fecha,
            c.hora,
            c.servicio,
            c.estado,
            c.mecanico_id,
            e.nombre as mecanico_nombre,
            a.id as auto_id,
            a.marca,
            a.modelo,
            a.placas,
            cl.nombre as cliente_nombre,
            cl.telefono as cliente_telefono
        FROM citas c
        LEFT JOIN empleados e ON c.mecanico_id = e.id
        JOIN autos a ON c.auto_id = a.id
        JOIN clientes cl ON a.cliente_id = cl.id
        WHERE c.id = ?
    """, (cita_id,))
    
    cita = cur.fetchone()
    conn.close()
    
    if not cita:
        return "Cita no encontrada", 404
    
    empleados = obtener_empleados()
    
    return render_template("detalle_seguimiento.html", 
                         cita=cita, 
                         empleados=empleados)


@app.route("/empleado/seguimiento/actualizar/<int:cita_id>", methods=["POST"])
def actualizar_seguimiento(cita_id):
    """Actualiza el estado de una cita"""
    from actualizacion_estado_vehiculo import actualizar_estado_cita
    
    if "empleado_id" not in session:
        return redirect("/")
    
    nuevo_estado = request.form.get("estado")
    mecanico_id = request.form.get("mecanico_id")
    
    exito, mensaje = actualizar_estado_cita(cita_id, nuevo_estado, mecanico_id if mecanico_id else None)
    
    if exito:
        return redirect(f"/empleado/seguimiento/detalle/{cita_id}?msg=Actualizado")
    else:
        return redirect(f"/empleado/seguimiento/detalle/{cita_id}?error={mensaje}")


# ============ FIN SEGUIMIENTO DE ESTADO ============


# ---------------- LOGOUT ----------------
@app.route("/salir")
def salir():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
