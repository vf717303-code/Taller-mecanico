from tkinter import messagebox
from tkinter import ttk
from db import conectar_db
from datetime import datetime, date


def cargar_empleados():
    """Cargar todos los empleados disponibles de la BD"""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM empleados ORDER BY nombre")
    empleados = cursor.fetchall()
    conn.close()
    return empleados

def cargar_citas_pendientes(lista):
    """Cargar todas las citas agendadas (no rechazadas)"""
    lista.delete(0, "end")
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, cl.nombre, a.marca, a.placas, c.fecha, c.hora, c.servicio, c.estado
        FROM citas c
        JOIN autos a ON c.auto_id = a.id
        JOIN clientes cl ON a.cliente_id = cl.id
        WHERE c.estado != 'Rechazada'
        ORDER BY c.fecha, c.hora
    """)
    citas = cursor.fetchall()
    conn.close()
    
    if not citas:
        lista.insert("end", "No hay citas agendadas")
    else:
        for cita in citas:
            texto = f"{cita[0]} | {cita[1]} | {cita[2]} {cita[3]} | {cita[4]} {cita[5]} | {cita[6]} | {cita[7]}"
            lista.insert("end", texto)

def guardar_cita(lista_autos, entries, tabla_citas=None, callback=None):
    if not lista_autos.curselection():
        messagebox.showerror("Error", "Selecciona un auto")
        return

    auto_id = int(lista_autos.get(lista_autos.curselection()[0]).split(" | ")[0])
    calendario, entry_hora, combo_servicio, entry_estado, entry_costo, combo_mecanico = entries

    fecha = calendario.get_date()
    hora = entry_hora.get()
    servicio = combo_servicio.get()
    estado = entry_estado.get()
    costo_str = entry_costo.get()
    mecanico_seleccionado = combo_mecanico.get()

    if hora == "Selecciona hora" or hora == "No hay horas disponibles" or servicio == "Selecciona servicio":
        messagebox.showerror("Error", "Completa los datos de la cita")
        return

    if not mecanico_seleccionado or mecanico_seleccionado == "Selecciona mecánico":
        messagebox.showerror("Error", "Selecciona un mecánico")
        return

    # Extraer el ID del mecánico del formato "ID - Nombre"
    try:
        mecanico_id = int(mecanico_seleccionado.split(" - ")[0])
    except (ValueError, IndexError):
        messagebox.showerror("Error", "Error al seleccionar el mecánico")
        return

    # Procesar costo
    costo = 0
    if costo_str and costo_str != "Costo ($) - Gratis si es Garantía":
        try:
            costo = float(costo_str)
        except ValueError:
            messagebox.showerror("Error", "El costo debe ser un número válido")
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

    # Si no hay conflicto, guardar la cita con mecanico_id y origen='empleado'
    cursor.execute(
        "INSERT INTO citas (auto_id, fecha, hora, servicio, estado, costo, mecanico_id, origen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (auto_id, fecha, hora, servicio, estado, costo, mecanico_id, 'empleado')
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", f"Cita agendada - Costo: ${costo:.2f}")

    combo_servicio.set("Selecciona servicio")
    entry_costo.delete(0, "end")
    entry_estado.delete(0, "end")
    entry_hora.set("Selecciona hora")
    combo_mecanico.set("Selecciona mecánico")
    
    # Refrescar tabla si existe
    if tabla_citas is not None:
        cargar_citas_tabla(tabla_citas)
    
    if callback:
        callback()


def entrada_costo():
    """Crear una ventana emergente para solicitar el costo"""
    import tkinter as tk
    
    ventana = tk.Toplevel()
    ventana.title("Ingresar Costo")
    ventana.geometry("300x150")
    ventana.configure(bg="#2b2b2b")
    ventana.resizable(False, False)
    
    tk.Label(
        ventana,
        text="Ingresar Costo de la Cita",
        bg="#ff9800",
        fg="black",
        font=("Arial", 12, "bold"),
        padx=20,
        pady=10
    ).pack(fill="x")
    
    frame = tk.Frame(ventana, bg="#2b2b2b")
    frame.pack(pady=20, padx=20)
    
    tk.Label(
        frame,
        text="Costo ($):",
        bg="#2b2b2b",
        fg="white",
        font=("Arial", 11)
    ).pack(side="left", padx=10)
    
    entry = tk.Entry(frame, width=15, font=("Arial", 11))
    entry.pack(side="left", padx=10)
    entry.focus()
    
    resultado = {'valor': None}
    
    def confirmar():
        resultado['valor'] = entry.get()
        ventana.destroy()
    
    def cancelar():
        resultado['valor'] = None
        ventana.destroy()
    
    botones_frame = tk.Frame(ventana, bg="#2b2b2b")
    botones_frame.pack(pady=10)
    
    tk.Button(
        botones_frame,
        text="Aceptar",
        bg="#4caf50",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=15,
        command=confirmar
    ).pack(side="left", padx=5)
    
    tk.Button(
        botones_frame,
        text="Cancelar",
        bg="#e74c3c",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=15,
        command=cancelar
    ).pack(side="left", padx=5)
    
    ventana.transient()
    ventana.grab_set()
    ventana.wait_window()
    
    return resultado['valor']

# -------------------------------------------------
# CARGAR CITAS EN TABLA
# -------------------------------------------------
def cargar_citas_tabla(tabla_citas):
    """Cargar todas las citas en la tabla Treeview"""
    # Limpiar tabla
    for item in tabla_citas.get_children():
        tabla_citas.delete(item)
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, cl.nombre, a.marca, a.placas, c.fecha, c.hora, c.servicio, c.estado, c.costo, e.nombre
        FROM citas c
        JOIN autos a ON c.auto_id = a.id
        JOIN clientes cl ON a.cliente_id = cl.id
        JOIN empleados e ON c.mecanico_id = e.id
        WHERE c.estado != 'Rechazada'
        ORDER BY c.fecha, c.hora
    """)
    citas = cursor.fetchall()
    conn.close()
    
    for cita in citas:
        cita_id, cliente, marca, placas, fecha, hora, servicio, estado, costo, mecanico = cita
        # Manejar costo NULL
        costo_formateado = f"${costo:.2f}" if costo is not None else "$0.00"
        tabla_citas.insert("", "end", iid=cita_id, values=(
            cita_id, cliente, f"{marca} {placas}", fecha, hora, 
            servicio, estado, costo_formateado, mecanico
        ))


# -------------------------------------------------
# EDITAR CITA (DOBLE CLICK)
# -------------------------------------------------
def editar_cita_ventana(tabla_citas, ventana_padre):
    """Abrir ventana para editar cita seleccionada"""
    import tkinter as tk
    from tkcalendar import DateEntry
    from tkinter import ttk
    
    seleccion = tabla_citas.selection()
    if not seleccion:
        messagebox.showerror("Error", "Selecciona una cita para editar")
        return
    
    item_id = seleccion[0]
    valores = tabla_citas.item(item_id)['values']
    cita_id = valores[0]
    
    # Obtener datos completos de la cita
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.auto_id, c.fecha, c.hora, c.servicio, c.estado, c.costo, c.mecanico_id,
               cl.nombre as cliente_nombre, a.marca, a.modelo, a.placas
        FROM citas c
        JOIN autos a ON c.auto_id = a.id
        JOIN clientes cl ON a.cliente_id = cl.id
        WHERE c.id = ?
    """, (cita_id,))
    cita_data = cursor.fetchone()
    conn.close()
    
    if not cita_data:
        messagebox.showerror("Error", "No se encontró la cita")
        return
    
    cita_id, auto_id, fecha, hora, servicio, estado, costo, mecanico_id, cliente_nombre, marca, modelo, placas = cita_data
    
    # Crear ventana de edición
    ventana_edit = tk.Toplevel(ventana_padre)
    ventana_edit.title(f"Editar Cita - {cliente_nombre}")
    ventana_edit.geometry("600x850")
    ventana_edit.configure(bg="#1e1e1e")
    ventana_edit.resizable(False, False)
    
    # Encabezado
    tk.Label(
        ventana_edit,
        text="Editar Cita",
        bg="#ff9800", fg="black",
        font=("Arial", 16, "bold"),
        padx=20, pady=10
    ).pack(fill="x")
    
    # Frame principal
    frame_edit = tk.Frame(ventana_edit, bg="#1e1e1e")
    frame_edit.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Cliente (solo lectura)
    tk.Label(frame_edit, text="Cliente:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    tk.Label(frame_edit, text=cliente_nombre, fg="white", bg="#2b2b2b", font=("Arial", 11), padx=10, pady=8).pack(fill="x", pady=(0, 10))
    
    # Auto (solo lectura)
    tk.Label(frame_edit, text="Vehículo:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    tk.Label(frame_edit, text=f"{marca} {modelo} ({placas})", fg="white", bg="#2b2b2b", font=("Arial", 11), padx=10, pady=8).pack(fill="x", pady=(0, 10))
    
    # Fecha
    tk.Label(frame_edit, text="Fecha:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    calendario_edit = DateEntry(frame_edit, width=42, font=("Arial", 12))
    
    # Convertir fecha string a date object si es necesario
    try:
        if isinstance(fecha, str):
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        else:
            fecha_obj = fecha
        calendario_edit.set_date(fecha_obj)
    except (ValueError, AttributeError, TypeError):
        # Si hay error, usar fecha actual
        calendario_edit.set_date(date.today())
    
    calendario_edit.pack(pady=(0, 10))
    
    # Hora
    tk.Label(frame_edit, text="Hora:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    horas = [f"{h:02d}:00" for h in range(8, 23)]
    combo_hora_edit = ttk.Combobox(frame_edit, values=horas, width=42, state="readonly", font=("Arial", 11))
    combo_hora_edit.set(hora)
    combo_hora_edit.pack(pady=(0, 10))
    
    # Mecánico
    tk.Label(frame_edit, text="Mecánico:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    empleados = cargar_empleados()
    empleados_opciones = [f"{emp[0]} - {emp[1]}" for emp in empleados]
    combo_mec_edit = ttk.Combobox(frame_edit, values=empleados_opciones, width=42, state="readonly", font=("Arial", 11))
    
    # Seleccionar el mecánico actual
    for opt in empleados_opciones:
        if str(mecanico_id) == opt.split(" - ")[0]:
            combo_mec_edit.set(opt)
            break
    combo_mec_edit.pack(pady=(0, 10))
    
    # Servicio
    tk.Label(frame_edit, text="Servicio:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    servicios_opciones = ["Afinación", "Revisión", "Garantía"]
    combo_serv_edit = ttk.Combobox(frame_edit, values=servicios_opciones, width=42, state="readonly", font=("Arial", 11))
    combo_serv_edit.set(servicio)
    combo_serv_edit.pack(pady=(0, 10))
    
    # Costo
    tk.Label(frame_edit, text="Costo ($):", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    entry_costo_edit = tk.Entry(frame_edit, width=45, font=("Arial", 11), bg="#2b2b2b", fg="white")
    entry_costo_edit.insert(0, str(costo))
    entry_costo_edit.pack(pady=(0, 10))
    
    # Estado
    tk.Label(frame_edit, text="Estado:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    entry_est_edit = tk.Entry(frame_edit, width=45, font=("Arial", 11), bg="#2b2b2b", fg="white")
    entry_est_edit.insert(0, estado)
    entry_est_edit.pack(pady=(0, 20))
    
    # Botones
    frame_botones = tk.Frame(frame_edit, bg="#1e1e1e")
    frame_botones.pack(fill="x")
    
    def guardar_cambios():
        try:
            nueva_fecha = calendario_edit.get_date()
            nueva_hora = combo_hora_edit.get()
            nuevo_servicio = combo_serv_edit.get()
            nuevo_estado = entry_est_edit.get()
            nuevo_costo = float(entry_costo_edit.get())
            nuevo_mecanico = combo_mec_edit.get().split(" - ")[0]
            
            if not nuevo_mecanico or nuevo_mecanico == "Selecciona mecánico":
                messagebox.showerror("Error", "Selecciona un mecánico válido")
                return
            
            conn = conectar_db()
            cursor = conn.cursor()
            
            # Verificar disponibilidad (excluir la cita actual)
            cursor.execute("""
                SELECT COUNT(*) FROM citas 
                WHERE fecha = ? AND hora = ? AND estado != 'Rechazada' AND id != ?
            """, (nueva_fecha, nueva_hora, cita_id))
            
            if cursor.fetchone()[0] > 0:
                conn.close()
                messagebox.showerror("Error", f"Ya existe una cita en {nueva_fecha} a las {nueva_hora}")
                return
            
            cursor.execute("""
                UPDATE citas 
                SET fecha = ?, hora = ?, servicio = ?, estado = ?, costo = ?, mecanico_id = ?
                WHERE id = ?
            """, (nueva_fecha, nueva_hora, nuevo_servicio, nuevo_estado, nuevo_costo, nuevo_mecanico, cita_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Cita actualizada correctamente")
            cargar_citas_tabla(tabla_citas)
            ventana_edit.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "El costo debe ser un número válido")
    
    tk.Button(
        frame_botones, text="Guardar cambios",
        bg="#4caf50", fg="white", font=("Arial", 11, "bold"),
        command=guardar_cambios
    ).pack(side="left", padx=5, ipadx=15, ipady=8)
    
    tk.Button(
        frame_botones, text="Cancelar",
        bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
        command=ventana_edit.destroy
    ).pack(side="left", padx=5, ipadx=15, ipady=8)


# -------------------------------------------------
# ELIMINAR CITA
# -------------------------------------------------
def eliminar_cita(tabla_citas):
    """Eliminar cita de la base de datos"""
    seleccion = tabla_citas.selection()
    if not seleccion:
        messagebox.showerror("Error", "Selecciona una cita para eliminar")
        return
    
    item_id = seleccion[0]
    
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar esta cita?"):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM citas WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Éxito", "Cita eliminada correctamente")
        cargar_citas_tabla(tabla_citas)


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