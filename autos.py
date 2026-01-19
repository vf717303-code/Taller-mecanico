from tkinter import messagebox
from db import conectar_db

def guardar_auto(lista_clientes, entries, cargar_autos):
    if not lista_clientes.curselection():
        messagebox.showerror("Error", "Selecciona un cliente")
        return

    cliente_id = int(lista_clientes.get(lista_clientes.curselection()[0]).split(" - ")[0])
    entry_marca, entry_modelo, entry_placas = entries

    marca = entry_marca.get()
    modelo = entry_modelo.get()
    placas = entry_placas.get()

    if marca.startswith("Marca") or placas.startswith("Placas"):
        messagebox.showerror("Error", "Completa los datos del auto")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO autos (cliente_id, marca, modelo, placas) VALUES (?, ?, ?, ?)",
        (cliente_id, marca, modelo, placas)
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", "Auto registrado")

    for e in entries:
        e.delete(0, "end")

    cargar_autos()


def cargar_autos(lista_autos):
    lista_autos.delete(0, "end")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT autos.id, autos.marca, autos.placas, clientes.nombre
        FROM autos
        JOIN clientes ON autos.cliente_id = clientes.id
    """)
    for a in cursor.fetchall():
        lista_autos.insert("end", f"{a[0]} | {a[1]} | {a[2]} | {a[3]}")
    conn.close()
