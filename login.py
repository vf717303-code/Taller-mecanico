import tkinter as tk
from tkinter import messagebox
import ui
from PIL import Image, ImageTk

from db import conectar_db
from utils import resource_path

# ---------------- BD ----------------
# ---------------- LOGIN ----------------
def mostrar_login():
    def validar_login():
        nombre = entry_nombre.get()
        password = entry_password.get()

        if not nombre or nombre == "Nombre del cliente":
            messagebox.showerror("Error", "Ingresa tu nombre")
            return

        if not password or password == "Contraseña":
            messagebox.showerror("Error", "Ingresa tu contraseña")
            return

        conn = conectar_db()
        cursor = conn.cursor()
        
        # Buscar en clientes
        cursor.execute(
            "SELECT id FROM clientes WHERE nombre=? AND password=?",
            (nombre, password)
        )
        cliente = cursor.fetchone()
        
        # Si no es cliente, buscar en empleados
        if not cliente:
            cursor.execute(
                "SELECT id FROM empleados WHERE nombre=? AND password=?",
                (nombre, password)
            )
            cliente = cursor.fetchone()
        
        conn.close()

        if cliente:
            ventana.destroy()
            ui.iniciar_app()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    # ---------------- VENTANA ----------------
    ventana = tk.Tk()
    ventana.title("Login - Taller Mecánico")
    ventana.geometry("650x650")
    ventana.configure(bg="#1e1e1e")
    ventana.resizable(True, True)

    # ---------------- TARJETA ----------------
    card = tk.Frame(
        ventana,
        bg="#2b2b2b",
        width=500,
        height=600
    )
    card.place(relx=0.5, rely=0.5, anchor="center")

    # ---------------- LOGO ----------------
    try:
        logo_path = resource_path("LOGO_TALLER.png")
        logo_pil = Image.open(logo_path)
        logo_pil = logo_pil.resize((350, 200), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(logo_pil)
        logo_label = tk.Label(card, image=logo_img, bg="#2b2b2b")
        logo_label.image = logo_img  # Mantener referencia
        logo_label.pack(pady=(15, 10))
    except Exception as e:
        pass  # Si no encuentra la imagen, continúa sin logo

    # ---------------- SUBTITULO ----------------
    tk.Label(
        card,
        fg="white",
        bg="#2b2b2b",
        font=("Arial", 14)
    ).pack(pady=(0, 20))

    # ---------------- ENTRADAS ----------------
    entry_nombre = tk.Entry(
        card,
        font=("Arial", 12),
        bg="white",
        fg="gray",
        relief="flat"
    )
    entry_nombre.insert(0, "Nombre de usuario")
    entry_nombre.pack(ipady=10, ipadx=10, pady=8, fill="x", padx=40)

    def limpiar_nombre(e):
        if entry_nombre.get() == "Nombre de usuario":
            entry_nombre.delete(0, "end")
            entry_nombre.config(fg="black")

    entry_nombre.bind("<FocusIn>", limpiar_nombre)

    entry_password = tk.Entry(
        card,
        font=("Arial", 12),
        bg="white",
        fg="gray",
        relief="flat"
    )
    entry_password.insert(0, "Contraseña")
    entry_password.pack(ipady=10, ipadx=10, pady=8, fill="x", padx=40)

    def limpiar_password(e):
        if entry_password.get() == "Contraseña":
            entry_password.delete(0, "end")
            entry_password.config(fg="black", show="*")

    entry_password.bind("<FocusIn>", limpiar_password)

    # ---------------- BOTÓN ----------------
    tk.Button(
        card,
        text="Entrar",
        bg="#ff9800",
        fg="black",
        font=("Arial", 13, "bold"),
        relief="flat",
        command=validar_login
    ).pack(pady=25, ipadx=10, ipady=8, fill="x", padx=40)

    ventana.mainloop()
