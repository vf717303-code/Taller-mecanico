from db import conectar_db
from tkinter import messagebox


def cargar_citas_pendientes(lista):
    lista.delete(0, "end")

    try:
        print("\n" + "="*60)
        print("DEBUG: Iniciando cargar_citas_pendientes()")
        print("="*60)
        
        conn = conectar_db()
        print(f"DEBUG: Conexión a BD exitosa")
        cursor = conn.cursor()

        # Verificar estructura
        cursor.execute("PRAGMA table_info(citas)")
        columnas = cursor.fetchall()
        print(f"DEBUG: Columnas en tabla citas: {[c[1] for c in columnas]}")

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
        
        print(f"DEBUG: Ejecutando query...")
        cursor.execute(query)

        filas = cursor.fetchall()
        print(f"DEBUG: Se encontraron {len(filas)} citas pendientes")
        
        if not filas:
            lista.insert("end", "No hay citas pendientes")
            print("DEBUG: No hay citas, mostrando mensaje")
        else:
            for fila in filas:
                texto = f"{fila[0]} | {fila[1]} | {fila[2]} | {fila[3]} | {fila[4]} {fila[5]} | {fila[6]}"
                lista.insert("end", texto)
                print(f"DEBUG: ✓ Cita agregada: {texto}")

        conn.close()
        print("DEBUG: Conexión cerrada exitosamente")
        print("="*60 + "\n")
        
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
