from db import conectar_db
from tkinter import messagebox
import tkinter as tk


def cargar_citas_pendientes(lista):
    lista.delete(0, "end")

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        query = """
            SELECT 
                citas.id,
                clientes.nombre,
                autos.marca,
                autos.placas,
                citas.fecha,
                citas.hora,
                citas.servicio
            FROM citas
            JOIN autos ON citas.auto_id = autos.id
            JOIN clientes ON autos.cliente_id = clientes.id
            WHERE citas.estado = 'En admisión'
            ORDER BY citas.fecha, citas.hora
        """
        
        cursor.execute(query)
        filas = cursor.fetchall()
        
        if not filas:
            lista.insert("end", "No hay citas pendientes")
        else:
            for fila in filas:
                texto = f"{fila[0]} | {fila[1]} | {fila[2]} | {fila[3]} | {fila[4]} {fila[5]} | {fila[6]}"
                lista.insert("end", texto)

        conn.close()
        
    except Exception as e:
        print(f"ERROR en cargar_citas_pendientes: {e}")
        import traceback
        traceback.print_exc()
        lista.insert("end", f"Error: {str(e)}")


# ---------------- ACEPTAR CITA ----------------

def aceptar_cita(lista):
    if not lista.curselection():
        messagebox.showerror("Error", "Selecciona una cita")
        return

    texto_seleccionado = lista.get(lista.curselection()[0])
    
    # Parsear el ID (primera parte antes del pipe)
    try:
        cita_id = int(texto_seleccionado.split(" | ")[0])
    except (ValueError, IndexError):
        messagebox.showerror("Error", "No se pudo extraer el ID de la cita")
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE citas SET estado='Aceptada' WHERE id=?",
            (cita_id,)
        )
        conn.commit()
        print(f"✓ Cita {cita_id} aceptada")
        messagebox.showinfo("Éxito", "Cita aceptada")
    except Exception as e:
        print(f"Error al aceptar cita: {e}")
        messagebox.showerror("Error", f"Error al aceptar: {e}")
    finally:
        conn.close()
        cargar_citas_pendientes(lista)


# ---------------- RECHAZAR CITA ----------------

def rechazar_cita(lista):
    if not lista.curselection():
        messagebox.showerror("Error", "Selecciona una cita")
        return

    texto_seleccionado = lista.get(lista.curselection()[0])
    
    # Parsear el ID (primera parte antes del pipe)
    try:
        cita_id = int(texto_seleccionado.split(" | ")[0])
    except (ValueError, IndexError):
        messagebox.showerror("Error", "No se pudo extraer el ID de la cita")
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE citas SET estado='Rechazada' WHERE id=?",
            (cita_id,)
        )
        conn.commit()
        print(f"✓ Cita {cita_id} rechazada")
        messagebox.showinfo("Éxito", "Cita rechazada")
    except Exception as e:
        print(f"Error al rechazar cita: {e}")
        messagebox.showerror("Error", f"Error al rechazar: {e}")
    finally:
        conn.close()
        cargar_citas_pendientes(lista)


# ---------------- MOSTRAR INFORMACIÓN COMPLETA DE LA CITA ----------------

def mostrar_info_cita(lista, ventana_padre):
    """Mostrar toda la información de la cita en una ventana emergente"""
    
    if not lista.curselection():
        return

    texto_seleccionado = lista.get(lista.curselection()[0])
    
    try:
        cita_id = int(texto_seleccionado.split(" | ")[0])
    except (ValueError, IndexError):
        messagebox.showerror("Error", "No se pudo extraer el ID de la cita")
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                citas.id,
                clientes.nombre,
                clientes.telefono,
                clientes.correo,
                autos.marca,
                autos.modelo,
                autos.placas,
                citas.fecha,
                citas.hora,
                citas.servicio,
                citas.estado
            FROM citas
            JOIN autos ON citas.auto_id = autos.id
            JOIN clientes ON autos.cliente_id = clientes.id
            WHERE citas.id = ?
        """, (cita_id,))
        
        cita = cursor.fetchone()
        
        if not cita:
            messagebox.showerror("Error", "No se encontró la cita")
            return
        
        # Crear ventana emergente
        ventana_info = tk.Toplevel(ventana_padre)
        ventana_info.title(f"Información de Cita #{cita[0]}")
        ventana_info.geometry("550x500")
        ventana_info.configure(bg="#2b2b2b")
        ventana_info.resizable(False, False)
        
        # Título
        tk.Label(
            ventana_info,
            text="INFORMACIÓN DE LA CITA",
            bg="#ff9800",
            fg="black",
            font=("Arial", 14, "bold"),
            padx=20,
            pady=10
        ).pack(fill="x")
        
        # Contenedor de información
        frame_info = tk.Frame(ventana_info, bg="#2b2b2b")
        frame_info.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Información a mostrar
        info_datos = [
            ("ID Cita", str(cita[0])),
            ("", ""),
            ("CLIENTE", ""),
            ("Nombre", cita[1]),
            ("Teléfono", cita[2] or "No disponible"),
            ("Correo", cita[3] or "No disponible"),
            ("", ""),
            ("VEHÍCULO", ""),
            ("Marca", cita[4]),
            ("Modelo", cita[5]),
            ("Placas", cita[6]),
            ("", ""),
            ("SERVICIO REQUERIDO", ""),
            ("Servicio", cita[9]),
            ("", ""),
            ("DETALLES DE LA CITA", ""),
            ("Fecha", cita[7]),
            ("Hora", cita[8]),
            ("Estado", cita[10]),
        ]
        
        # Mostrar información
        for label_text, valor_text in info_datos:
            if label_text == "":
                tk.Label(frame_info, bg="#2b2b2b", text="").pack()
            elif valor_text == "":
                tk.Label(
                    frame_info,
                    text=label_text,
                    bg="#ff9800",
                    fg="black",
                    font=("Arial", 10, "bold"),
                    padx=10,
                    pady=5
                ).pack(fill="x")
            else:
                frame_dato = tk.Frame(frame_info, bg="#2b2b2b")
                frame_dato.pack(fill="x", pady=5)
                
                tk.Label(
                    frame_dato,
                    text=f"{label_text}:",
                    bg="#2b2b2b",
                    fg="#ff9800",
                    font=("Arial", 10, "bold"),
                    width=15,
                    anchor="w"
                ).pack(side="left", padx=5)
                
                tk.Label(
                    frame_dato,
                    text=str(valor_text),
                    bg="#2b2b2b",
                    fg="white",
                    font=("Arial", 10),
                    anchor="w"
                ).pack(side="left", padx=5, fill="x", expand=True)
        
        # Botón cerrar
        tk.Button(
            ventana_info,
            text="Cerrar",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            command=ventana_info.destroy
        ).pack(pady=10)
        
        ventana_info.transient(ventana_padre)
        ventana_info.grab_set()
        
    except Exception as e:
        print(f"Error al obtener información de la cita: {e}")
        messagebox.showerror("Error", f"Error: {e}")
    finally:
        conn.close()
