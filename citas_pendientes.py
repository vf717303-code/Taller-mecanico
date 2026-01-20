from db import conectar_db
from tkinter import messagebox


def cargar_citas_pendientes(lista):
    lista.delete(0, "end")

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
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
        """)

        filas = cursor.fetchall()
        print(f"DEBUG: Se encontraron {len(filas)} citas pendientes")
        
        if not filas:
            lista.insert("end", "No hay citas pendientes")
        
        for fila in filas:
            texto = f"{fila[0]} | {fila[1]} | {fila[2]} | {fila[3]} | {fila[4]} {fila[5]} | {fila[6]}"
            lista.insert("end", texto)
            print(f"DEBUG: Cita agregada: {texto}")

        conn.close()
        
    except Exception as e:
        print(f"ERROR en cargar_citas_pendientes: {e}")
        lista.insert("end", f"Error: {str(e)}")


# ---------------- ACEPTAR CITA ----------------

def aceptar_cita(lista):
    if not lista.curselection():
        messagebox.showerror("Error", "Selecciona una cita")
        return

    cita_id = int(lista.get(lista.curselection()[0]).split(" | ")[0])

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE citas SET estado='Aceptada' WHERE id=?",
        (cita_id,)
    )

    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", "Cita aceptada")
    cargar_citas_pendientes(lista)
