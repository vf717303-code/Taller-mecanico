from tkinter import messagebox
from db import conectar_db

def guardar_cita(lista_autos, entries):
    if not lista_autos.curselection():
        messagebox.showerror("Error", "Selecciona un auto")
        return

    auto_id = int(lista_autos.get(lista_autos.curselection()[0]).split(" | ")[0])
    calendario, entry_hora, entry_servicio, entry_estado = entries

    fecha = calendario.get_date()
    hora = entry_hora.get()
    servicio = entry_servicio.get()
    estado = entry_estado.get()

    if hora == "Selecciona hora" or hora == "No hay horas disponibles" or servicio.startswith("Afinación"):
        messagebox.showerror("Error", "Completa los datos de la cita")
        return

    # Verificar si ya existe una cita para esa fecha y hora (no rechazada)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM citas 
        WHERE fecha = ? AND hora = ? AND estado != 'Rechazada'
    """, (fecha, hora))
    
    citas_conflicto = cursor.fetchone()[0]
    
    if citas_conflicto > 0:
        conn.close()
        messagebox.showerror("Error", f"Ya existe una cita programada para {fecha} a las {hora}")
        return

    # Si no hay conflicto, guardar la cita
    cursor.execute(
        "INSERT INTO citas (auto_id, fecha, hora, servicio, estado) VALUES (?, ?, ?, ?, ?)",
        (auto_id, fecha, hora, servicio, estado)
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", "Cita agendada")

    entry_servicio.delete(0, "end")
    entry_estado.delete(0, "end")
    entry_hora.set("Selecciona hora")

# -------------------------------------------------
# CARGAR CITAS PENDIENTES
# -------------------------------------------------
def cargar_citas_pendientes(lista_citas):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fecha, servicio FROM citas WHERE estado = 'Pendiente'")
    citas = cursor.fetchall()
    conn.close()
    
    lista_citas.delete(0, "end")
    for cita in citas:
        lista_citas.insert("end", f"{cita[0]} | {cita[1]} | {cita[2]}")


# -------------------------------------------------
# ACEPTAR CITA
# -------------------------------------------------
def aceptar_cita(lista_citas):
    if not lista_citas.curselection():
        messagebox.showerror("Error", "Selecciona una cita")
        return
    
    cita_info = lista_citas.get(lista_citas.curselection()[0])
    cita_id = int(cita_info.split(" | ")[0])
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE citas SET estado = 'Aceptada' WHERE id = ?", (cita_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Cita aceptada")


# -------------------------------------------------
# RECHAZAR CITA
# -------------------------------------------------
def rechazar_cita(lista_citas):
    if not lista_citas.curselection():
        messagebox.showerror("Error", "Selecciona una cita")
        return
    
    cita_info = lista_citas.get(lista_citas.curselection()[0])
    cita_id = int(cita_info.split(" | ")[0])
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE citas SET estado = 'Rechazada' WHERE id = ?", (cita_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Cita rechazada")


# -------------------------------------------------
# OBTENER INFO CLIENTE DE CITA
# -------------------------------------------------
def obtener_info_cliente_cita(lista_citas):
    if not lista_citas.curselection():
        messagebox.showerror("Error", "Selecciona una cita")
        return
    
    cita_info = lista_citas.get(lista_citas.curselection()[0])
    cita_id = int(cita_info.split(" | ")[0])
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.nombre, c.telefono, c.correo, a.marca, a.modelo, a.placas, cit.fecha, cit.hora, cit.servicio
        FROM citas cit
        JOIN autos a ON cit.auto_id = a.id
        JOIN clientes c ON a.cliente_id = c.id
        WHERE cit.id = ?
    """, (cita_id,))
    info = cursor.fetchone()
    conn.close()
    
    if info:
        cliente_nombre, telefono, correo, marca, modelo, placas, fecha, hora, servicio = info
        detalles = f"""
        INFORMACIÓN DE LA CITA:
        
        Cliente: {cliente_nombre}
        Teléfono: {telefono}
        Correo: {correo}
        
        Auto: {marca} {modelo}
        Placas: {placas}
        Fecha de cita: {fecha}
        Hora: {hora}
        Servicio: {servicio}
        """
        messagebox.showinfo("Información de la cita", detalles)
    else:
        messagebox.showerror("Error", "No se encontraron datos de la cita")