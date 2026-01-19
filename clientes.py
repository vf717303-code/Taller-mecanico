from tkinter import messagebox
from db import conectar_db

def guardar_cliente(entries, lista_clientes, cargar_clientes, cargar_autos):
    entry_nombre, entry_telefono, entry_correo, entry_password = entries

    nombre = entry_nombre.get()
    telefono = entry_telefono.get()
    correo = entry_correo.get()
    password = entry_password.get()

    if nombre.startswith("Nombre") or password.startswith("Contraseña"):
        messagebox.showerror("Error", "Completa los datos correctamente")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre, telefono, correo, password) VALUES (?, ?, ?, ?)",
        (nombre, telefono, correo, password)
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", "Cliente registrado")

    for e in entries:
        e.delete(0, "end")

    cargar_clientes()
    cargar_autos()


def cargar_clientes(lista_clientes):
    lista_clientes.delete(0, "end")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM clientes")
    for c in cursor.fetchall():
        lista_clientes.insert("end", f"{c[0]} - {c[1]}")
    conn.close()
