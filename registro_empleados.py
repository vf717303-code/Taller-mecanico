import tkinter as tk
from tkinter import messagebox, ttk
from db import conectar_db
from utils import placeholder


def cargar_empleados(tabla):
    """Cargar empleados en la tabla Treeview"""
    # Limpiar tabla
    for item in tabla.get_children():
        tabla.delete(item)

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, correo, telefono, direccion
        FROM empleados
        ORDER BY nombre
    """)

    for emp in cursor.fetchall():
        emp_id, nombre, correo, telefono, direccion = emp
        tabla.insert("", "end", iid=emp_id, values=(emp_id, nombre, correo, telefono, direccion))

    conn.close()


def guardar_empleado(campos, tabla):
    nombre, password, direccion, correo, telefono = [c.get() for c in campos]

    if not all([nombre, password, direccion, correo, telefono]):
        messagebox.showwarning("Campos vacíos", "Completa todos los campos")
        return

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO empleados (nombre, password, direccion, correo, telefono)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, password, direccion, correo, telefono))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Empleado registrado correctamente")

        for c in campos:
            c.delete(0, tk.END)

        # Refrescar tabla
        cargar_empleados(tabla)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def editar_empleado_ventana(tabla, ventana_padre):
    """Abrir ventana para editar empleado seleccionado"""
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showerror("Error", "Selecciona un empleado para editar")
        return
    
    item_id = seleccion[0]
    valores = tabla.item(item_id)['values']
    emp_id, nombre, correo, telefono, direccion = valores
    
    # Obtener contraseña actual
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM empleados WHERE id = ?", (emp_id,))
    password_actual = cursor.fetchone()[0]
    conn.close()
    
    # Crear ventana de edición
    ventana_edit = tk.Toplevel(ventana_padre)
    ventana_edit.title(f"Editar Empleado - {nombre}")
    ventana_edit.geometry("600x700")
    ventana_edit.configure(bg="#1e1e1e")
    ventana_edit.resizable(False, False)
    
    # Encabezado
    tk.Label(
        ventana_edit,
        text="Editar Empleado",
        bg="#ff9800", fg="black",
        font=("Arial", 16, "bold"),
        padx=20, pady=10
    ).pack(fill="x")
    
    # Frame principal
    frame_edit = tk.Frame(ventana_edit, bg="#1e1e1e")
    frame_edit.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Nombre
    tk.Label(frame_edit, text="Nombre completo:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    entry_nombre_edit = tk.Entry(frame_edit, width=45, font=("Arial", 11), bg="#2b2b2b", fg="white")
    entry_nombre_edit.insert(0, nombre)
    entry_nombre_edit.pack(pady=(0, 10))
    
    # Contraseña
    tk.Label(frame_edit, text="Contraseña:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    entry_password_edit = tk.Entry(frame_edit, width=45, font=("Arial", 11), bg="#2b2b2b", fg="white", show="*")
    entry_password_edit.insert(0, password_actual)
    entry_password_edit.pack(pady=(0, 10))
    
    # Dirección
    tk.Label(frame_edit, text="Dirección:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    entry_direccion_edit = tk.Entry(frame_edit, width=45, font=("Arial", 11), bg="#2b2b2b", fg="white")
    entry_direccion_edit.insert(0, direccion)
    entry_direccion_edit.pack(pady=(0, 10))
    
    # Correo
    tk.Label(frame_edit, text="Correo electrónico:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    entry_correo_edit = tk.Entry(frame_edit, width=45, font=("Arial", 11), bg="#2b2b2b", fg="white")
    entry_correo_edit.insert(0, correo)
    entry_correo_edit.pack(pady=(0, 10))
    
    # Teléfono
    tk.Label(frame_edit, text="Teléfono:", fg="#ff9800", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
    entry_telefono_edit = tk.Entry(frame_edit, width=45, font=("Arial", 11), bg="#2b2b2b", fg="white")
    entry_telefono_edit.insert(0, telefono)
    entry_telefono_edit.pack(pady=(0, 20))
    
    # Botones
    frame_botones = tk.Frame(frame_edit, bg="#1e1e1e")
    frame_botones.pack(fill="x")
    
    def guardar_cambios():
        try:
            nuevo_nombre = entry_nombre_edit.get()
            nueva_password = entry_password_edit.get()
            nueva_direccion = entry_direccion_edit.get()
            nuevo_correo = entry_correo_edit.get()
            nuevo_telefono = entry_telefono_edit.get()
            
            if not all([nuevo_nombre, nueva_password, nueva_direccion, nuevo_correo, nuevo_telefono]):
                messagebox.showerror("Error", "Completa todos los campos")
                return
            
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE empleados 
                SET nombre = ?, password = ?, direccion = ?, correo = ?, telefono = ?
                WHERE id = ?
            """, (nuevo_nombre, nueva_password, nueva_direccion, nuevo_correo, nuevo_telefono, emp_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Empleado actualizado correctamente")
            cargar_empleados(tabla)
            ventana_edit.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
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


def eliminar_empleado(tabla):
    """Eliminar empleado de la base de datos"""
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showerror("Error", "Selecciona un empleado para eliminar")
        return
    
    item_id = seleccion[0]
    valores = tabla.item(item_id)['values']
    nombre = valores[1]
    
    if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar a {nombre}?"):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empleados WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Éxito", "Empleado eliminado correctamente")
        cargar_empleados(tabla)


def vista_registro_empleados(frame):
    # Obtener ventana principal
    ventana = frame.winfo_toplevel()
    
    box = tk.Frame(frame, bg="#1e1e1e")
    box.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(
        box,
        text="Registro de Empleados",
        fg="#ff9800",
        bg="#1e1e1e",
        font=("Arial", 24, "bold")
    ).pack(pady=20)

    # Frame para formulario
    form_frame = tk.Frame(box, bg="#2b2b2b", padx=20, pady=20)
    form_frame.pack(fill="x", pady=(0, 20))

    entry_nombre = tk.Entry(form_frame, width=45, font=("Arial", 15), bg="#2b2b2b", fg="white")
    entry_nombre.pack(pady=6)
    placeholder(entry_nombre, "Nombre completo")

    entry_password = tk.Entry(form_frame, width=45, font=("Arial", 15), bg="#2b2b2b", fg="white", show="*")
    entry_password.pack(pady=6)
    placeholder(entry_password, "Contraseña")

    entry_direccion = tk.Entry(form_frame, width=45, font=("Arial", 15), bg="#2b2b2b", fg="white")
    entry_direccion.pack(pady=6)
    placeholder(entry_direccion, "Dirección")

    entry_correo = tk.Entry(form_frame, width=45, font=("Arial", 15), bg="#2b2b2b", fg="white")
    entry_correo.pack(pady=6)
    placeholder(entry_correo, "Correo electrónico")

    entry_telefono = tk.Entry(form_frame, width=45, font=("Arial", 15), bg="#2b2b2b", fg="white")
    entry_telefono.pack(pady=6)
    placeholder(entry_telefono, "Número de teléfono")

    # Frame para tabla
    tabla_frame = tk.Frame(box, bg="#1e1e1e")
    tabla_frame.pack(fill="both", expand=True, pady=(20, 0))

    # Título de tabla
    tk.Label(tabla_frame, text="Empleados Registrados",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 14, "bold")).pack(pady=(0, 10))

    # Scroll
    scroll = ttk.Scrollbar(tabla_frame)
    scroll.pack(side="right", fill="y")

    # Tabla Treeview
    tabla_empleados = ttk.Treeview(
        tabla_frame,
        columns=("ID", "Nombre", "Correo", "Teléfono", "Dirección"),
        height=8,
        yscrollcommand=scroll.set
    )
    scroll.config(command=tabla_empleados.yview)

    # Configurar columnas
    tabla_empleados.column("#0", width=0, stretch="no")
    tabla_empleados.column("ID", width=30, anchor="center")
    tabla_empleados.column("Nombre", width=150, anchor="w")
    tabla_empleados.column("Correo", width=150, anchor="w")
    tabla_empleados.column("Teléfono", width=100, anchor="center")
    tabla_empleados.column("Dirección", width=200, anchor="w")

    # Encabezados
    tabla_empleados.heading("#0", text="", anchor="w")
    tabla_empleados.heading("ID", text="ID", anchor="center")
    tabla_empleados.heading("Nombre", text="Nombre", anchor="w")
    tabla_empleados.heading("Correo", text="Correo", anchor="w")
    tabla_empleados.heading("Teléfono", text="Teléfono", anchor="center")
    tabla_empleados.heading("Dirección", text="Dirección", anchor="w")

    tabla_empleados.pack(fill="both", expand=True)

    # Doble click para editar
    tabla_empleados.bind("<Double-Button-1>", lambda e: editar_empleado_ventana(tabla_empleados, ventana))

    # Frame para botones
    botones_frame = tk.Frame(box, bg="#1e1e1e")
    botones_frame.pack(fill="x", pady=(15, 0))

    tk.Button(
        botones_frame,
        text="Guardar Empleado",
        bg="#ff9800",
        font=("Arial", 12, "bold"),
        width=22,
        command=lambda: guardar_empleado(
            (
                entry_nombre,
                entry_password,
                entry_direccion,
                entry_correo,
                entry_telefono
            ),
            tabla_empleados
        )
    ).pack(side="left", padx=10, ipadx=10, ipady=8)

    tk.Button(
        botones_frame, text="Editar Empleado",
        bg="#4caf50", font=("Arial", 12, "bold"), width=22,
        command=lambda: editar_empleado_ventana(tabla_empleados, ventana)
    ).pack(side="left", padx=10, ipadx=10, ipady=8)

    tk.Button(
        botones_frame, text="Eliminar Empleado",
        bg="#e74c3c", font=("Arial", 12, "bold"), width=22,
        command=lambda: eliminar_empleado(tabla_empleados)
    ).pack(side="left", padx=10, ipadx=10, ipady=8)

    cargar_empleados(tabla_empleados)
