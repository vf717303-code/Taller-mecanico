from tkinter import messagebox
from db import conectar_db
import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime


def guardar_proveedor(entries, tabla_proveedores, cargar_proveedores):
    entry_nombre, entry_telefono, entry_correo, entry_direccion, entry_ruc = entries

    nombre = entry_nombre.get()
    telefono = entry_telefono.get()
    correo = entry_correo.get()
    direccion = entry_direccion.get()
    ruc = entry_ruc.get()

    if nombre.startswith("Nombre") or not nombre:
        messagebox.showerror("Error", "Completa los datos correctamente")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO proveedores (nombre, telefono, correo, direccion, ruc) VALUES (?, ?, ?, ?, ?)",
            (nombre, telefono, correo, direccion, ruc)
        )
        conn.commit()
        messagebox.showinfo("Éxito", "Proveedor registrado")

        for e in entries:
            e.delete(0, "end")
            if e == entry_nombre:
                e.insert(0, "Nombre del proveedor")
                e.config(fg="gray")

        cargar_proveedores()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El proveedor ya existe")
    finally:
        conn.close()


def cargar_proveedores(tabla_proveedores):
    # Limpiar tabla
    for item in tabla_proveedores.get_children():
        tabla_proveedores.delete(item)
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, correo, direccion, ruc FROM proveedores")
    
    for proveedor in cursor.fetchall():
        tabla_proveedores.insert("", "end", values=proveedor)
    
    conn.close()


def cargar_autos_con_cliente():
    """Carga autos con información del cliente vinculado"""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.marca, a.modelo, a.placas, c.nombre 
        FROM autos a 
        JOIN clientes c ON a.cliente_id = c.id
    """)
    autos = cursor.fetchall()
    conn.close()
    return autos


def mostrar_info_proveedor(tabla_proveedores, parent_frame):
    seleccion = tabla_proveedores.selection()
    
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona un proveedor")
        return
    
    item = seleccion[0]
    valores = tabla_proveedores.item(item)['values']
    
    # Crear ventana de detalles
    ventana_info = tk.Toplevel(parent_frame)
    ventana_info.title(f"Detalles - {valores[1]}")
    ventana_info.geometry("500x600")
    ventana_info.configure(bg="#1e1e1e")
    
    frame = tk.Frame(ventana_info, bg="#2b2b2b", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    
    # Mostrar información
    info_datos = [
        ("ID", valores[0]),
        ("Nombre", valores[1]),
        ("Teléfono", valores[2]),
        ("Correo", valores[3]),
        ("Dirección", valores[4]),
        ("RUC", valores[5])
    ]
    
    for label, valor in info_datos:
        tk.Label(
            frame,
            text=f"{label}:",
            fg="#ff9800",
            bg="#2b2b2b",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=5)
        
        tk.Label(
            frame,
            text=str(valor),
            fg="white",
            bg="#2b2b2b",
            font=("Arial", 11),
            wraplength=350
        ).pack(anchor="w", padx=20, pady=(0, 15))
    
    # Botón de editar
    tk.Button(
        frame,
        text="Editar",
        bg="#ff9800",
        fg="black",
        font=("Arial", 11, "bold"),
        command=lambda: editar_proveedor(valores, tabla_proveedores, cargar_proveedores)
    ).pack(pady=10, ipadx=10, ipady=5)
    
    # Botón de realizar pedido
    tk.Button(
        frame,
        text="Realizar un Pedido",
        bg="#4caf50",
        fg="white",
        font=("Arial", 11, "bold"),
        command=lambda: realizar_pedido(valores[0], valores[1], ventana_info, None)
    ).pack(pady=5, ipadx=10, ipady=5)
    
    # Botón de eliminar
    tk.Button(
        frame,
        text="Eliminar",
        bg="#ff5252",
        fg="white",
        font=("Arial", 11, "bold"),
        command=lambda: eliminar_proveedor(valores[0], tabla_proveedores, cargar_proveedores, ventana_info)
    ).pack(pady=5, ipadx=10, ipady=5)


def editar_proveedor(valores, tabla_proveedores, cargar_proveedores):
    ventana_editar = tk.Toplevel()
    ventana_editar.title(f"Editar - {valores[1]}")
    ventana_editar.geometry("400x350")
    ventana_editar.configure(bg="#1e1e1e")
    
    frame = tk.Frame(ventana_editar, bg="#2b2b2b", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    
    # Campos de edición
    campos = [
        ("Nombre", valores[1]),
        ("Teléfono", valores[2]),
        ("Correo", valores[3]),
        ("Dirección", valores[4]),
        ("RUC", valores[5])
    ]
    
    entries = []
    
    for label, valor in campos:
        tk.Label(
            frame,
            text=label,
            fg="#ff9800",
            bg="#2b2b2b",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(10, 0))
        
        entry = tk.Entry(
            frame,
            font=("Arial", 11),
            bg="white",
            fg="black",
            relief="flat"
        )
        entry.insert(0, valor)
        entry.pack(fill="x", pady=(0, 5), ipady=8)
        entries.append(entry)
    
    def guardar_cambios():
        conn = conectar_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE proveedores SET nombre=?, telefono=?, correo=?, direccion=?, ruc=? WHERE id=?",
                (entries[0].get(), entries[1].get(), entries[2].get(), 
                 entries[3].get(), entries[4].get(), valores[0])
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Proveedor actualizado")
            ventana_editar.destroy()
            cargar_proveedores(tabla_proveedores)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        finally:
            conn.close()
    
    tk.Button(
        frame,
        text="Guardar cambios",
        bg="#ff9800",
        fg="black",
        font=("Arial", 11, "bold"),
        command=guardar_cambios
    ).pack(pady=15, ipadx=10, ipady=8, fill="x")


def eliminar_proveedor(proveedor_id, tabla_proveedores, cargar_proveedores, ventana_padre):
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este proveedor?"):
        conn = conectar_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM proveedores WHERE id=?", (proveedor_id,))
            conn.commit()
            messagebox.showinfo("Éxito", "Proveedor eliminado")
            ventana_padre.destroy()
            cargar_proveedores(tabla_proveedores)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        finally:
            conn.close()


def realizar_pedido(proveedor_id, proveedor_nombre, ventana_padre, tabla_pedidos=None):
    """Abre ventana para realizar un pedido"""
    ventana_pedido = tk.Toplevel(ventana_padre)
    ventana_pedido.title(f"Nuevo Pedido - {proveedor_nombre}")
    ventana_pedido.geometry("450x550")
    ventana_pedido.configure(bg="#1e1e1e")
    
    frame = tk.Frame(ventana_pedido, bg="#2b2b2b", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    
    # Título
    tk.Label(
        frame,
        text=f"Pedido a: {proveedor_nombre}",
        fg="#ff9800",
        bg="#2b2b2b",
        font=("Arial", 12, "bold")
    ).pack(anchor="w", pady=(0, 15))
    
    # Cargar autos disponibles
    autos = cargar_autos_con_cliente()
    autos_opciones = ["Selecciona un auto"] + [f"{auto[1]} {auto[2]} - {auto[4]}" for auto in autos]
    auto_ids = [None] + [auto[0] for auto in autos]
    
    tk.Label(frame, text="Auto:", fg="#ff9800", bg="#2b2b2b", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    combo_auto = ttk.Combobox(frame, values=autos_opciones, state="readonly", width=40)
    combo_auto.set("Selecciona un auto")
    combo_auto.pack(fill="x", pady=(0, 10), ipady=8)
    
    # Servicio
    tk.Label(frame, text="Servicio a Realizar:", fg="#ff9800", bg="#2b2b2b", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    entry_servicio = tk.Entry(frame, font=("Arial", 11), bg="white", fg="black", relief="flat")
    entry_servicio.pack(fill="x", pady=(0, 10), ipady=8)
    
    # Pieza de refacción
    tk.Label(frame, text="Pieza de Refacción:", fg="#ff9800", bg="#2b2b2b", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    entry_pieza = tk.Entry(frame, font=("Arial", 11), bg="white", fg="black", relief="flat")
    entry_pieza.pack(fill="x", pady=(0, 10), ipady=8)
    
    # Costo
    tk.Label(frame, text="Costo (S/.):", fg="#ff9800", bg="#2b2b2b", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    entry_costo = tk.Entry(frame, font=("Arial", 11), bg="white", fg="black", relief="flat")
    entry_costo.insert(0, "0.00")
    entry_costo.pack(fill="x", pady=(0, 15), ipady=8)
    
    # Variable para almacenar cliente_id
    cliente_id_var = tk.IntVar(value=0)
    
    def obtener_cliente_id():
        """Obtiene el cliente_id del auto seleccionado"""
        index = combo_auto.current()
        if index > 0:
            auto_id = auto_ids[index]
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT cliente_id FROM autos WHERE id=?", (auto_id,))
            resultado = cursor.fetchone()
            conn.close()
            if resultado:
                cliente_id_var.set(resultado[0])
                return auto_id, resultado[0]
        return None, None
    
    def guardar_pedido():
        """Guarda el pedido en la BD"""
        auto_id, cliente_id = obtener_cliente_id()
        servicio = entry_servicio.get()
        pieza = entry_pieza.get()
        costo_texto = entry_costo.get()
        
        if not auto_id or not servicio or not pieza:
            messagebox.showerror("Error", "Completa todos los datos")
            return
        
        # Validar costo
        try:
            costo = float(costo_texto)
            if costo < 0:
                messagebox.showerror("Error", "El costo no puede ser negativo")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingresa un costo válido")
            return
        
        conn = conectar_db()
        cursor = conn.cursor()
        
        try:
            fecha = datetime.now().strftime("%d/%m/%Y")
            cursor.execute(
                """INSERT INTO piezas (proveedor_id, auto_id, cliente_id, servicio, pieza_refaccion, fecha, estado, costo) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (proveedor_id, auto_id, cliente_id, servicio, pieza, fecha, "Pendiente", costo)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Pedido registrado correctamente")
            ventana_pedido.destroy()
            
            # Refrescar tabla de pedidos si existe
            if tabla_pedidos:
                cargar_pedidos(tabla_pedidos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el pedido: {e}")
        finally:
            conn.close()
    
    # Botón guardar
    tk.Button(
        frame,
        text="Guardar Pedido",
        bg="#4caf50",
        fg="white",
        font=("Arial", 11, "bold"),
        command=guardar_pedido
    ).pack(pady=15, ipadx=10, ipady=8, fill="x")


def cargar_pedidos(tabla_pedidos):
    """Carga todos los pedidos en la tabla"""
    for item in tabla_pedidos.get_children():
        tabla_pedidos.delete(item)
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.fecha, prov.nombre, c.nombre, (a.marca || ' ' || a.modelo) AS auto_nombre, p.servicio, p.pieza_refaccion, 
               COALESCE(p.costo, 0) as costo, p.estado
        FROM piezas p
        JOIN proveedores prov ON p.proveedor_id = prov.id
        JOIN clientes c ON p.cliente_id = c.id
        JOIN autos a ON p.auto_id = a.id
        ORDER BY p.fecha DESC
    """)
    
    for pedido in cursor.fetchall():
        # Formatear el costo
        pedido_lista = list(pedido)
        pedido_lista[7] = f"S/. {pedido_lista[7]:.2f}"  # Formatear costo
        tabla_pedidos.insert("", "end", values=pedido_lista)
    
    conn.close()


def mostrar_detalles_pedido(tabla_pedidos):
    """Muestra detalles de un pedido seleccionado"""
    seleccion = tabla_pedidos.selection()
    
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona un pedido")
        return
    
    item = seleccion[0]
    valores = tabla_pedidos.item(item)['values']
    
    # Crear ventana de detalles
    ventana_info = tk.Toplevel()
    ventana_info.title(f"Detalles Pedido #{valores[0]}")
    ventana_info.geometry("500x750")
    ventana_info.configure(bg="#1e1e1e")
    
    frame = tk.Frame(ventana_info, bg="#2b2b2b", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    
    info_datos = [
        ("ID Pedido", valores[0]),
        ("Fecha", valores[1]),
        ("Proveedor", valores[2]),
        ("Cliente", valores[3]),
        ("Auto", valores[4]),
        ("Servicio", valores[5]),
        ("Pieza", valores[6]),
        ("Costo", valores[7]),
        ("Estado", valores[8])
    ]
    
    estado_actual = valores[8]
    
    for label, valor in info_datos:
        tk.Label(
            frame,
            text=f"{label}:",
            fg="#ff9800",
            bg="#2b2b2b",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=5)
        
        tk.Label(
            frame,
            text=str(valor),
            fg="white",
            bg="#2b2b2b",
            font=("Arial", 11),
            wraplength=400
        ).pack(anchor="w", padx=20, pady=(0, 10))
    
    # Botón para cambiar estado
    def cambiar_estado():
        nuevo_estado = "Realizado" if estado_actual == "Pendiente" else "Pendiente"
        
        conn = conectar_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE piezas SET estado=? WHERE id=?",
                (nuevo_estado, valores[0])
            )
            conn.commit()
            messagebox.showinfo("Éxito", f"Estado cambiado a: {nuevo_estado}")
            ventana_info.destroy()
            cargar_pedidos(tabla_pedidos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el estado: {e}")
        finally:
            conn.close()
    
    # Determinar el botón a mostrar
    texto_boton = "Marcar como Realizado" if estado_actual == "Pendiente" else "Marcar como Pendiente"
    color_boton = "#4caf50" if estado_actual == "Pendiente" else "#ff9800"
    
    tk.Button(
        frame,
        text=texto_boton,
        bg=color_boton,
        fg="white" if estado_actual == "Pendiente" else "black",
        font=("Arial", 11, "bold"),
        command=cambiar_estado
    ).pack(pady=15, ipadx=10, ipady=8, fill="x")
    
    # Botón para eliminar pedido
    def eliminar_pedido():
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este pedido?"):
            conn = conectar_db()
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM piezas WHERE id=?", (valores[0],))
                conn.commit()
                messagebox.showinfo("Éxito", "Pedido eliminado correctamente")
                ventana_info.destroy()
                cargar_pedidos(tabla_pedidos)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el pedido: {e}")
            finally:
                conn.close()
    
    tk.Button(
        frame,
        text="Eliminar Pedido",
        bg="#ff5252",
        fg="white",
        font=("Arial", 11, "bold"),
        command=eliminar_pedido
    ).pack(pady=5, ipadx=10, ipady=8, fill="x")
