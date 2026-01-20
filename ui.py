import tkinter as tk
from tkinter import ttk

from utils import placeholder, mostrar_frame
from clientes import guardar_cliente, cargar_clientes
from autos import guardar_auto, cargar_autos
from citas_pendientes import cargar_citas_pendientes, aceptar_cita, rechazar_cita, mostrar_info_cita


def iniciar_app():
    ventana = tk.Tk()
    ventana.title("Sistema Interno - Taller Mecánico")
    ventana.geometry("1100x650")
    ventana.configure(bg="#1e1e1e")

    ventana.grid_rowconfigure(0, weight=1)
    ventana.grid_columnconfigure(1, weight=1)

    # ------------------ MENÚ ------------------

    menu = tk.Frame(ventana, bg="#2b2b2b", width=220)
    menu.grid(row=0, column=0, sticky="ns")

    tk.Label(
        menu,
        text="TALLER",
        bg="#2b2b2b",
        fg="#ff9800",
        font=("Arial", 22, "bold")
    ).pack(pady=30)

    # ------------------ CONTENEDOR ------------------

    contenedor = tk.Frame(ventana, bg="#1e1e1e")
    contenedor.grid(row=0, column=1, sticky="nsew")

    contenedor.grid_rowconfigure(0, weight=1)
    contenedor.grid_columnconfigure(0, weight=1)

    def crear_frame():
        f = tk.Frame(contenedor, bg="#1e1e1e")
        f.grid(row=0, column=0, sticky="nsew")
        return f

    frame_clientes = crear_frame()
    frame_autos = crear_frame()
    frame_citas = crear_frame()
    frame_citas_pendientes = crear_frame()

    # ------------------ BOTONES MENÚ ------------------

    tk.Button(menu, text="Clientes", width=25,
              command=lambda: mostrar_frame(frame_clientes)).pack(pady=10)

    tk.Button(menu, text="Autos", width=25,
              command=lambda: mostrar_frame(frame_autos)).pack(pady=10)

    tk.Button(menu, text="Citas", width=25,
              command=lambda: mostrar_frame(frame_citas)).pack(pady=10)

    tk.Button(menu, text="Citas pendientes", width=25,
          command=lambda: mostrar_frame(frame_citas_pendientes)).pack(pady=10)

    # ================== CLIENTES ==================

    clientes_box = tk.Frame(frame_clientes, bg="#1e1e1e")
    clientes_box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        clientes_box,
        text="Registro de Clientes",
        fg="#ff9800",
        bg="#1e1e1e",
        font=("Arial", 24, "bold")
    ).pack(pady=20)

    entry_nombre = tk.Entry(clientes_box, width=45, font=("Arial", 15))
    entry_nombre.pack(pady=8)
    placeholder(entry_nombre, "Nombre completo del cliente")

    entry_telefono = tk.Entry(clientes_box, width=45, font=("Arial", 15))
    entry_telefono.pack(pady=8)
    placeholder(entry_telefono, "Teléfono")

    entry_correo = tk.Entry(clientes_box, width=45, font=("Arial", 15))
    entry_correo.pack(pady=8)
    placeholder(entry_correo, "Correo electrónico")

    entry_password = tk.Entry(clientes_box, width=45, font=("Arial", 15))
    entry_password.pack(pady=8)
    placeholder(entry_password, "Contraseña asignada", ocultar=True)

    lista_clientes = tk.Listbox(clientes_box, width=50, height=6, font=("Arial", 12))
    lista_clientes.pack(pady=15)

    tk.Button(
        clientes_box,
        text="Guardar Cliente",
        bg="#ff9800",
        font=("Arial", 15),
        width=22,
        command=lambda: guardar_cliente(
            (entry_nombre, entry_telefono, entry_correo, entry_password),
            lista_clientes,
            lambda: cargar_clientes(lista_clientes),
            lambda: cargar_autos(lista_autos)
        )
    ).pack(pady=20)

    # ================== AUTOS ==================

    autos_box = tk.Frame(frame_autos, bg="#1e1e1e")
    autos_box.place(relx=0.5, rely=0.5, anchor="center")

    lista_clientes_autos = tk.Listbox(autos_box, width=50, height=6, font=("Arial", 12))
    lista_clientes_autos.pack(pady=10)

    entry_marca = tk.Entry(autos_box, width=45, font=("Arial", 15))
    entry_marca.pack(pady=8)
    placeholder(entry_marca, "Marca del vehículo")

    entry_modelo = tk.Entry(autos_box, width=45, font=("Arial", 15))
    entry_modelo.pack(pady=8)
    placeholder(entry_modelo, "Modelo")

    entry_placas = tk.Entry(autos_box, width=45, font=("Arial", 15))
    entry_placas.pack(pady=8)
    placeholder(entry_placas, "Placas")

    tk.Button(
        autos_box,
        text="Guardar Auto",
        bg="#ff9800",
        font=("Arial", 15),
        width=22,
        command=lambda: guardar_auto(
            lista_clientes_autos,
            (entry_marca, entry_modelo, entry_placas),
            lambda: cargar_autos(lista_autos)
        )
    ).pack(pady=20)

    # ================== CITAS ==================

    citas_box = tk.Frame(frame_citas, bg="#1e1e1e")
    citas_box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        citas_box,
        text="Agendar Cita",
        fg="#ff9800",
        bg="#1e1e1e",
        font=("Arial", 24, "bold")
    ).pack(pady=20)

    lista_autos = tk.Listbox(citas_box, width=60, height=6, font=("Arial", 12))
    lista_autos.pack(pady=10)

    entry_fecha = tk.Entry(citas_box, width=45, font=("Arial", 15))
    entry_fecha.pack(pady=8)
    placeholder(entry_fecha, "Fecha (YYYY-MM-DD)")

    # Lista desplegable de horas
    horas = [f"{h:02d}:00" for h in range(8, 18)]
    entry_hora = ttk.Combobox(citas_box, values=horas, width=42, font=("Arial", 15), state="readonly")
    entry_hora.pack(pady=8)
    entry_hora.set("Selecciona hora")

    entry_servicio = tk.Entry(citas_box, width=45, font=("Arial", 15))
    entry_servicio.pack(pady=8)
    placeholder(entry_servicio, "Afinación / Revisión / Garantía")

    entry_estado = tk.Entry(citas_box, width=45, font=("Arial", 15))
    entry_estado.pack(pady=8)
    placeholder(entry_estado, "Pendiente / Realizada")

    tk.Button(
        citas_box,
        text="Agendar Cita",
        bg="#ff9800",
        font=("Arial", 15),
        width=22,
        command=lambda: guardar_cita(
            lista_autos,
            (entry_fecha, entry_hora, entry_servicio, entry_estado)
        )
    ).pack(pady=25)
    
    # ------------------- CITAS PENDIENTES -------------------

    citas_p_box = tk.Frame(frame_citas_pendientes, bg="#1e1e1e")
    citas_p_box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        citas_p_box,
        text="Citas pendientes",
        fg="#ff9800",
        bg="#1e1e1e",
        font=("Arial", 24, "bold")
    ).pack(pady=20)
    lista_citas_pendientes = tk.Listbox(
        citas_p_box,
        width=120,
        height=10,
        font=("Arial", 12)
    )
    lista_citas_pendientes.pack(pady=10)
    # Doble click para ver información completa
    lista_citas_pendientes.bind("<Double-Button-1>", lambda e: mostrar_info_cita(lista_citas_pendientes, ventana))
    
    # Frame para los botones
    botones_frame = tk.Frame(citas_p_box, bg="#1e1e1e")
    botones_frame.pack(pady=15)
    
    tk.Button(
        botones_frame,
        text="Aceptar cita",
        bg="#ff9800",
        font=("Arial", 15),
        width=22,
        command=lambda: aceptar_cita(lista_citas_pendientes)
    ).pack(side="left", padx=10)
    
    tk.Button(
        botones_frame,
        text="Rechazar cita",
        bg="#e74c3c",
        font=("Arial", 15),
        width=22,
        command=lambda: rechazar_cita(lista_citas_pendientes)
    ).pack(side="left", padx=10)
    # 🔹 Cargar automáticamente las citas pendientes
    cargar_citas_pendientes(lista_citas_pendientes)


    # ------------------ CARGA INICIAL ------------------

    cargar_clientes(lista_clientes)
    cargar_clientes(lista_clientes_autos)
    cargar_autos(lista_autos)
    
    # -------- REFRESCO AUTOMÁTICO DE CITAS PENDIENTES --------
    def actualizar_citas_automaticamente():
        """Refrescar citas pendientes cada 5 segundos"""
        cargar_citas_pendientes(lista_citas_pendientes)
        ventana.after(5000, actualizar_citas_automaticamente)  # Cada 5 segundos
    
    actualizar_citas_automaticamente()
    mostrar_frame(frame_clientes)

    ventana.mainloop()