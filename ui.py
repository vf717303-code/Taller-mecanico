import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime

from utils import placeholder, mostrar_frame
from clientes import guardar_cliente, cargar_clientes
from autos import guardar_auto, cargar_autos
from citas import guardar_cita, cargar_citas_pendientes as cargar_citas_db
from citas_pendientes import cargar_citas_pendientes, aceptar_cita, rechazar_cita, mostrar_info_cita, contar_citas_pendientes
from registro_empleados import guardar_empleado
from proveedores_piezas import (guardar_proveedor, cargar_proveedores, mostrar_info_proveedor, 
                                cargar_pedidos, mostrar_detalles_pedido, realizar_pedido, 
                                editar_proveedor, eliminar_proveedor)
from visualizacion_registros import mostrar_visualizacion
from editar_registros import mostrar_editar_registros
from db import conectar_db


def iniciar_app():
    ventana = tk.Tk()
    ventana.title("Sistema Interno - Taller Mecánico")
    ventana.configure(bg="#1e1e1e")
    ventana.state('zoomed')

    # Configurar estilos de Treeview
    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure("Treeview", 
                     background="#2b2b2b",
                     foreground="white",
                     fieldbackground="#2b2b2b",
                     borderwidth=0,
                     font=("Arial", 10))
    estilo.configure("Treeview.Heading",
                     background="#ff9800",
                     foreground="black",
                     borderwidth=0,
                     font=("Arial", 10, "bold"))
    estilo.map("Treeview",
               background=[("selected", "#ff9800")],
               foreground=[("selected", "black")])

    ventana.grid_rowconfigure(0, weight=1)
    ventana.grid_columnconfigure(1, weight=1)

    # ------------------ MENÚ ------------------

    menu = tk.Frame(ventana, bg="#2b2b2b", width=220)
    menu.grid(row=0, column=0, sticky="ns")

    tk.Label(
        menu, text="TALLER",
        bg="#2b2b2b", fg="#ff9800",
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

    frame_inicio = crear_frame()
    frame_clientes = crear_frame()
    frame_autos = crear_frame()
    frame_citas = crear_frame()
    frame_citas_pendientes = crear_frame()
    frame_empleados = crear_frame()
    frame_proveedores = crear_frame()
    frame_visualizacion = crear_frame()
    frame_editar = crear_frame()
    frame_seguimiento = crear_frame()

    # Variables globales para las listas (se asignarán después)
    listas = {
        'clientes': None,
        'clientes_autos': None,
        'autos': None,
        'citas_pendientes': None
    }

    # ------------------ BOTONES MENÚ ------------------

    botones = [
        ("Inicio", frame_inicio),
        ("Clientes", frame_clientes),
        ("Autos", frame_autos),
        ("Citas", frame_citas),
        ("Citas pendientes", frame_citas_pendientes),
        ("Registrar empleados", frame_empleados),
        ("Proveedores", frame_proveedores),
        ("Seguimiento de Estado", frame_seguimiento),
        ("Editar Registros", frame_editar),
        ("Visualización de Registros", frame_visualizacion)
    ]

    for texto, frame in botones:
        if texto == "Editar Registros":
            tk.Button(
                menu, text=texto, width=25,
                command=lambda f=frame: (mostrar_frame(f), mostrar_editar_registros(f))
            ).pack(pady=8)
        elif texto == "Visualización de Registros":
            tk.Button(
                menu, text=texto, width=25,
                command=lambda f=frame: (mostrar_frame(f), mostrar_visualizacion(f))
            ).pack(pady=8)
        elif texto == "Seguimiento de Estado":
            tk.Button(
                menu, text=texto, width=25,
                command=lambda f=frame: (mostrar_frame(f), mostrar_seguimiento_estado(f))
            ).pack(pady=8)
        else:
            tk.Button(
                menu, text=texto, width=25,
                command=lambda f=frame: mostrar_frame(f)
            ).pack(pady=8)

    # Botón de cerrar sesión
    tk.Button(
        menu, text="Cerrar sesión", width=25,
        bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
        command=lambda: (ventana.destroy(), __import__('login').mostrar_login())
    ).pack(pady=8, side="bottom")

    # ================== INICIO ==================

    inicio_box = tk.Frame(frame_inicio, bg="#1e1e1e")
    inicio_box.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(inicio_box, text="Panel de Inicio",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 26, "bold")).pack(pady=(10, 10))

    tk.Label(inicio_box, text="Resumen y alertas del taller",
             fg="#cccccc", bg="#1e1e1e",
             font=("Arial", 12)).pack(pady=(0, 20))

    def ir_a_citas_pendientes():
        mostrar_frame(frame_citas_pendientes)
        lista = listas.get('citas_pendientes')
        if lista is not None:
            cargar_citas_pendientes(lista)

    notificacion_btn = tk.Button(
        inicio_box,
        text="",
        bg="#ff9800",
        fg="black",
        font=("Arial", 12, "bold"),
        relief="flat",
        cursor="hand2",
        command=ir_a_citas_pendientes
    )

    def actualizar_notificacion_pendientes():
        try:
            count = contar_citas_pendientes()
        except Exception:
            count = 0

        if count > 0:
            notificacion_btn.config(
                text=f"Tienes {count} cita(s) pendientes por aceptar. Haz clic para revisar."
            )
            if not notificacion_btn.winfo_ismapped():
                notificacion_btn.pack(pady=10, ipadx=10, ipady=8)
        else:
            if notificacion_btn.winfo_ismapped():
                notificacion_btn.pack_forget()

        if ventana.winfo_exists():
            ventana.after(5000, actualizar_notificacion_pendientes)

    # ================== CLIENTES ==================

    clientes_box = tk.Frame(frame_clientes, bg="#1e1e1e")
    clientes_box.pack(fill="both", expand=True, padx=20, pady=20)

    # Título
    tk.Label(clientes_box, text="Registro de Clientes",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 26, "bold")).pack(pady=(0, 30))

    # Frame principal para contenido
    content_frame_cli = tk.Frame(clientes_box, bg="#1e1e1e")
    content_frame_cli.pack(fill="both", expand=True)

    # ==== LADO IZQUIERDO: FORMULARIO ====
    left_frame_cli = tk.Frame(content_frame_cli, bg="#1e1e1e")
    left_frame_cli.pack(side="left", fill="both", expand=True, padx=(0, 15))

    # Subtítulo formulario
    tk.Label(left_frame_cli, text="Agregar Nuevo Cliente",
             fg="white", bg="#1e1e1e",
             font=("Arial", 14, "bold")).pack(pady=(0, 20))

    # Campo: Nombre completo
    tk.Label(left_frame_cli, text="👤 Nombre Completo",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    entry_nombre = tk.Entry(left_frame_cli, width=45, font=("Arial", 13),
                            bg="#2b2b2b", fg="white",
                            insertbackground="white",
                            relief="flat", bd=0)
    entry_nombre.pack(pady=(0, 15), ipady=8)
    placeholder(entry_nombre, "Ej: Juan Pérez García")

    # Campo: Teléfono
    tk.Label(left_frame_cli, text="☎️  Teléfono",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    entry_telefono = tk.Entry(left_frame_cli, width=45, font=("Arial", 13),
                              bg="#2b2b2b", fg="white",
                              insertbackground="white",
                              relief="flat", bd=0)
    entry_telefono.pack(pady=(0, 15), ipady=8)
    placeholder(entry_telefono, "Ej: +34 612 345 678")

    # Campo: Correo
    tk.Label(left_frame_cli, text="📧 Correo Electrónico",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    entry_correo = tk.Entry(left_frame_cli, width=45, font=("Arial", 13),
                            bg="#2b2b2b", fg="white",
                            insertbackground="white",
                            relief="flat", bd=0)
    entry_correo.pack(pady=(0, 15), ipady=8)
    placeholder(entry_correo, "Ej: cliente@email.com")

    # Campo: Contraseña
    tk.Label(left_frame_cli, text="🔐 Contraseña",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    entry_password = tk.Entry(left_frame_cli, width=45, font=("Arial", 13),
                              bg="#2b2b2b", fg="white",
                              insertbackground="white",
                              relief="flat", bd=0, show="•")
    entry_password.pack(pady=(0, 25), ipady=8)
    placeholder(entry_password, "Ingresa contraseña segura")

    # Botón Guardar
    tk.Button(
        left_frame_cli, text="✓ Guardar Cliente",
        bg="#4caf50", fg="white", font=("Arial", 12, "bold"),
        padx=20, pady=10, relief="flat", bd=0,
        activebackground="#45a049", activeforeground="white",
        cursor="hand2",
        command=lambda: guardar_cliente(
            (entry_nombre, entry_telefono, entry_correo, entry_password),
            lista_clientes,
            lambda: cargar_clientes_registrados(lista_clientes),
            lambda: (cargar_clientes(listas['clientes_autos']), cargar_autos_registrados(listas['autos']))
        )
    ).pack(pady=(20, 0), ipadx=20)

    # ==== LADO DERECHO: CLIENTES REGISTRADOS ====
    right_frame_cli = tk.Frame(content_frame_cli, bg="#2b2b2b", highlightbackground="#ff9800", highlightthickness=2)
    right_frame_cli.pack(side="right", fill="both", expand=True, padx=(15, 0))

    # Panel de información
    info_frame_cli = tk.Frame(right_frame_cli, bg="#2b2b2b")
    info_frame_cli.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(info_frame_cli, text="👥 Clientes Registrados",
             fg="#ff9800", bg="#2b2b2b",
             font=("Arial", 12, "bold")).pack(pady=(0, 15))

    tk.Label(info_frame_cli, text="Historial de clientes agregados al sistema.",
             fg="white", bg="#2b2b2b",
             font=("Arial", 10), wraplength=250, justify="left").pack(pady=(0, 15))

    # Lista de clientes registrados
    scroll_clientes_reg = ttk.Scrollbar(info_frame_cli)
    scroll_clientes_reg.pack(side="right", fill="y")

    lista_clientes = tk.Listbox(
        info_frame_cli,
        font=("Arial", 10),
        bg="#1e1e1e", fg="white",
        yscrollcommand=scroll_clientes_reg.set,
        relief="solid", bd=1,
        selectmode="none"
    )
    scroll_clientes_reg.config(command=lista_clientes.yview)
    lista_clientes.pack(fill="both", expand=True, pady=(0, 15))
    listas['clientes'] = lista_clientes

    def cargar_clientes_registrados(lista):
        """Carga los clientes registrados en la lista de resumen"""
        lista.delete(0, "end")
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre, correo, telefono
            FROM clientes
            ORDER BY id DESC
        """)
        for cliente in cursor.fetchall():
            nombre, correo, telefono = cliente
            texto = f"{nombre} | {correo} | {telefono}"
            lista.insert("end", texto)
        conn.close()

    # Cargar clientes al inicio
    cargar_clientes_registrados(lista_clientes)

    # Info adicional
    tk.Label(info_frame_cli, text="Total de clientes registrados en el sistema.",
             fg="#999999", bg="#2b2b2b",
             font=("Arial", 9), justify="center").pack()

    # ================== AUTOS ==================

    autos_box = tk.Frame(frame_autos, bg="#1e1e1e")
    autos_box.pack(fill="both", expand=True, padx=20, pady=20)

    # Título
    tk.Label(autos_box, text="Registro de Vehículos",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 26, "bold")).pack(pady=(0, 30))

    # Frame principal para contenido
    content_frame = tk.Frame(autos_box, bg="#1e1e1e")
    content_frame.pack(fill="both", expand=True)

    # ==== LADO IZQUIERDO: FORMULARIO ====
    left_frame = tk.Frame(content_frame, bg="#1e1e1e")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

    # Subtítulo formulario
    tk.Label(left_frame, text="Agregar Nuevo Vehículo",
             fg="white", bg="#1e1e1e",
             font=("Arial", 14, "bold")).pack(pady=(0, 20))

    # Selector de cliente con label
    tk.Label(left_frame, text="📋 Selecciona un Cliente:",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 8))

    lista_clientes_autos = tk.Listbox(
        left_frame, width=50, height=8, 
        font=("Arial", 10),
        bg="#2b2b2b", fg="white", 
        selectmode="single", 
        highlightcolor="#ff9800",
        highlightthickness=2
    )
    lista_clientes_autos.pack(pady=(0, 20), fill="both")
    listas['clientes_autos'] = lista_clientes_autos

    # Separador visual
    separator = tk.Frame(left_frame, height=2, bg="#ff9800")
    separator.pack(fill="x", pady=(0, 20))

    # Campo: Marca
    tk.Label(left_frame, text="🏷️  Marca del Vehículo",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    entry_marca = tk.Entry(left_frame, width=45, font=("Arial", 13), 
                           bg="#2b2b2b", fg="white", 
                           insertbackground="white",
                           relief="flat", bd=0)
    entry_marca.pack(pady=(0, 15), ipady=8)
    placeholder(entry_marca, "Ej: Toyota, Honda, BMW...")

    # Campo: Modelo
    tk.Label(left_frame, text="⚙️  Modelo",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    entry_modelo = tk.Entry(left_frame, width=45, font=("Arial", 13),
                            bg="#2b2b2b", fg="white",
                            insertbackground="white",
                            relief="flat", bd=0)
    entry_modelo.pack(pady=(0, 15), ipady=8)
    placeholder(entry_modelo, "Ej: Corolla, Civic, Serie 3...")

    # Campo: Placas
    tk.Label(left_frame, text="🚗 Placas",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    entry_placas = tk.Entry(left_frame, width=45, font=("Arial", 13),
                            bg="#2b2b2b", fg="white",
                            insertbackground="white",
                            relief="flat", bd=0)
    entry_placas.pack(pady=(0, 25), ipady=8)
    placeholder(entry_placas, "Ej: ABC-1234")

    # Botón Guardar
    tk.Button(
        left_frame, text="✓ Guardar Vehículo",
        bg="#4caf50", fg="white", font=("Arial", 12, "bold"),
        padx=20, pady=10, relief="flat", bd=0,
        activebackground="#45a049", activeforeground="white",
        cursor="hand2",
        command=lambda: guardar_auto(
            lista_clientes_autos,
            (entry_marca, entry_modelo, entry_placas),
            lambda: (cargar_autos_registrados(lista_autos_registrados), cargar_autos(listas['autos']))
        )
    ).pack(pady=(20, 0), ipadx=20)

    # ==== LADO DERECHO: AUTOS REGISTRADOS ====
    right_frame = tk.Frame(content_frame, bg="#2b2b2b", highlightbackground="#ff9800", highlightthickness=2)
    right_frame.pack(side="right", fill="both", expand=True, padx=(15, 0))

    # Panel de información
    info_frame = tk.Frame(right_frame, bg="#2b2b2b")
    info_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(info_frame, text="🚗 Vehículos Registrados",
             fg="#ff9800", bg="#2b2b2b",
             font=("Arial", 12, "bold")).pack(pady=(0, 15))

    tk.Label(info_frame, text="Historial de vehículos agregados al sistema.",
             fg="white", bg="#2b2b2b",
             font=("Arial", 10), wraplength=250, justify="left").pack(pady=(0, 15))

    # Lista de autos registrados
    scroll_autos_reg = ttk.Scrollbar(info_frame)
    scroll_autos_reg.pack(side="right", fill="y")

    lista_autos_registrados = tk.Listbox(
        info_frame, 
        font=("Arial", 10),
        bg="#1e1e1e", fg="white",
        yscrollcommand=scroll_autos_reg.set,
        relief="solid", bd=1,
        selectmode="none"
    )
    scroll_autos_reg.config(command=lista_autos_registrados.yview)
    lista_autos_registrados.pack(fill="both", expand=True, pady=(0, 15))

    def cargar_autos_registrados(lista):
        """Carga los autos registrados en la lista de resumen"""
        lista.delete(0, "end")
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT autos.marca, autos.modelo, autos.placas, clientes.nombre
            FROM autos
            JOIN clientes ON autos.cliente_id = clientes.id
            ORDER BY autos.id DESC
        """)
        for auto in cursor.fetchall():
            marca, modelo, placas, cliente = auto
            texto = f"{marca} {modelo} | {placas} | {cliente}"
            lista.insert("end", texto)
        conn.close()

    # Cargar autos al inicio
    cargar_autos_registrados(lista_autos_registrados)

    # Info adicional
    tk.Label(info_frame, text="Total de vehículos registrados en el sistema.",
             fg="#999999", bg="#2b2b2b",
             font=("Arial", 9), justify="center").pack()

    # ================== CITAS ==================

    citas_box = tk.Frame(frame_citas, bg="#1e1e1e")
    citas_box.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(citas_box, text="Agendar Cita",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 24, "bold")).pack(pady=20)

    # Frame para el formulario
    form_frame = tk.Frame(citas_box, bg="#2b2b2b", padx=20, pady=20)
    form_frame.pack(fill="x", pady=(0, 20))

    autos_header_frame = tk.Frame(form_frame, bg="#2b2b2b")
    autos_header_frame.pack(fill="x", pady=(10, 5))
    
    tk.Label(autos_header_frame, text="Selecciona Auto:", fg="#ff9800", bg="#2b2b2b", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
    
    tk.Button(
        autos_header_frame, text="🔄 Actualizar",
        bg="#2196F3", fg="white", font=("Arial", 9, "bold"),
        command=lambda: cargar_autos(lista_autos)
    ).pack(side="right")
    
    lista_autos = tk.Listbox(form_frame, width=60, height=4, font=("Arial", 10), bg="#1e1e1e", fg="white", selectmode="single")
    lista_autos.pack(pady=10)
    listas['autos'] = lista_autos
    
    # Flag para pausar refresco durante interacción
    refresco_autos_pausado = {"paused": False, "timer": None}
    
    def pausar_refresco_autos(event=None):
        """Pausa el refresco automático cuando el usuario interactúa"""
        refresco_autos_pausado["paused"] = True
        # Desprogramar el timer anterior si existe
        if refresco_autos_pausado["timer"]:
            ventana.after_cancel(refresco_autos_pausado["timer"])
        # Reanudar después de 8 segundos
        refresco_autos_pausado["timer"] = ventana.after(8000, lambda: refresco_autos_pausado.update({"paused": False}))
    
    lista_autos.bind("<Button-1>", pausar_refresco_autos)
    lista_autos.bind("<MouseWheel>", pausar_refresco_autos)
    lista_autos.bind("<Button-4>", pausar_refresco_autos)
    lista_autos.bind("<Button-5>", pausar_refresco_autos)

    calendario = DateEntry(form_frame, width=42, font=("Arial", 15))
    calendario.pack(pady=8)

    horas = [f"{h:02d}:00" for h in range(8, 23)]
    entry_hora = ttk.Combobox(form_frame, values=horas, width=42, state="readonly")
    entry_hora.set("Selecciona hora")
    entry_hora.pack(pady=8)

    # Cargar mecánicos disponibles
    from citas import cargar_empleados, cargar_citas_tabla, editar_cita_ventana, eliminar_cita
    empleados = cargar_empleados()
    empleados_opciones = ["Selecciona mecánico"] + [f"{emp[0]} - {emp[1]}" for emp in empleados]
    
    combo_mecanico = ttk.Combobox(form_frame, values=empleados_opciones, width=42, state="readonly")
    combo_mecanico.set("Selecciona mecánico")
    combo_mecanico.pack(pady=8)

    # Servicios disponibles
    servicios_opciones = ["Afinación", "Revisión", "Garantía"]
    combo_servicio = ttk.Combobox(form_frame, values=servicios_opciones, width=42, state="readonly")
    combo_servicio.set("Selecciona servicio")
    combo_servicio.pack(pady=8)

    entry_costo = tk.Entry(form_frame, width=45, font=("Arial", 15), bg="#2b2b2b", fg="white")
    entry_costo.pack(pady=6)
    placeholder(entry_costo, "Costo ($) - Gratis si es Garantía")

    entry_estado = tk.Entry(form_frame, width=45, font=("Arial", 15), bg="#2b2b2b", fg="white")
    entry_estado.pack(pady=6)
    placeholder(entry_estado, "Estado")

    # Frame para tabla de citas
    tabla_frame = tk.Frame(citas_box, bg="#1e1e1e")
    tabla_frame.pack(fill="both", expand=True, pady=(20, 0))

    # Título de tabla
    tk.Label(tabla_frame, text="Citas Agendadas",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 14, "bold")).pack(pady=(0, 10))

    # Scroll
    scroll = ttk.Scrollbar(tabla_frame)
    scroll.pack(side="right", fill="y")

    # Tabla Treeview
    tabla_citas = ttk.Treeview(
        tabla_frame,
        columns=("ID", "Cliente", "Vehículo", "Fecha", "Hora", "Servicio", "Estado", "Costo", "Mecánico"),
        height=8,
        yscrollcommand=scroll.set
    )
    scroll.config(command=tabla_citas.yview)

    # Configurar columnas
    tabla_citas.column("#0", width=0, stretch="no")
    tabla_citas.column("ID", width=30, anchor="center")
    tabla_citas.column("Cliente", width=90, anchor="w")
    tabla_citas.column("Vehículo", width=110, anchor="w")
    tabla_citas.column("Fecha", width=80, anchor="center")
    tabla_citas.column("Hora", width=60, anchor="center")
    tabla_citas.column("Servicio", width=100, anchor="w")
    tabla_citas.column("Estado", width=80, anchor="center")
    tabla_citas.column("Costo", width=70, anchor="center")
    tabla_citas.column("Mecánico", width=90, anchor="w")

    # Encabezados
    tabla_citas.heading("#0", text="", anchor="w")
    tabla_citas.heading("ID", text="ID", anchor="center")
    tabla_citas.heading("Cliente", text="Cliente", anchor="w")
    tabla_citas.heading("Vehículo", text="Vehículo", anchor="w")
    tabla_citas.heading("Fecha", text="Fecha", anchor="center")
    tabla_citas.heading("Hora", text="Hora", anchor="center")
    tabla_citas.heading("Servicio", text="Servicio", anchor="w")
    tabla_citas.heading("Estado", text="Estado", anchor="center")
    tabla_citas.heading("Costo", text="Costo", anchor="center")
    tabla_citas.heading("Mecánico", text="Mecánico", anchor="w")

    tabla_citas.pack(fill="both", expand=True)

    # Doble click para editar
    tabla_citas.bind("<Double-Button-1>", lambda e: editar_cita_ventana(tabla_citas, ventana))

    # Frame para botones
    botones_frame = tk.Frame(citas_box, bg="#1e1e1e")
    botones_frame.pack(fill="x", pady=(15, 0))

    tk.Button(
        botones_frame, text="Agendar Cita",
        bg="#ff9800", font=("Arial", 12, "bold"), width=20,
        command=lambda: guardar_cita(
            lista_autos,
            (calendario, entry_hora, combo_servicio, entry_estado, entry_costo, combo_mecanico),
            tabla_citas,
            lambda: cargar_citas_pendientes(lista_citas_pendientes)
        )
    ).pack(side="left", padx=10, ipadx=10, ipady=8)

    tk.Button(
        botones_frame, text="Editar Cita",
        bg="#4caf50", font=("Arial", 12, "bold"), width=20,
        command=lambda: editar_cita_ventana(tabla_citas, ventana)
    ).pack(side="left", padx=10, ipadx=10, ipady=8)

    tk.Button(
        botones_frame, text="Eliminar Cita",
        bg="#e74c3c", font=("Arial", 12, "bold"), width=20,
        command=lambda: eliminar_cita(tabla_citas)
    ).pack(side="left", padx=10, ipadx=10, ipady=8)

    # ================== CITAS PENDIENTES ==================

    citas_pend_box = tk.Frame(frame_citas_pendientes, bg="#1e1e1e")
    citas_pend_box.pack(fill="x", padx=20, pady=20)

    tk.Label(citas_pend_box, text="Citas Pendientes",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 24, "bold")).pack(pady=20)

    lista_citas_pendientes = tk.Listbox(citas_pend_box, width=100, height=3, font=("Arial", 10))
    lista_citas_pendientes.pack(pady=10)
    listas['citas_pendientes'] = lista_citas_pendientes
    
    # Doble click para ver información completa
    lista_citas_pendientes.bind("<Double-Button-1>", lambda e: mostrar_info_cita(lista_citas_pendientes, ventana))

    botones_box = tk.Frame(citas_pend_box, bg="#1e1e1e")
    botones_box.pack(pady=15)

    tk.Button(
        botones_box, text="Aceptar Cita",
        bg="#4caf50", fg="white", font=("Arial", 12), width=20,
        command=lambda: aceptar_cita(lista_citas_pendientes)
    ).pack(side="left", padx=10)

    tk.Button(
        botones_box, text="Rechazar Cita",
        bg="#f44336", fg="white", font=("Arial", 12), width=20,
        command=lambda: rechazar_cita(lista_citas_pendientes)
    ).pack(side="left", padx=10)

    # ================== EMPLEADOS ==================

    from registro_empleados import vista_registro_empleados
    vista_registro_empleados(frame_empleados)

    # ================== PROVEEDORES ==================

    prov_box = tk.Frame(frame_proveedores, bg="#1e1e1e")
    prov_box.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(prov_box, text="Gestión de Proveedores",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 24, "bold")).pack(pady=20)

    # Formulario de entrada
    form_frame = tk.Frame(prov_box, bg="#2b2b2b", padx=20, pady=20)
    form_frame.pack(fill="x", pady=(0, 20))

    tk.Label(form_frame, text="Nuevo Proveedor", fg="#ff9800", bg="#2b2b2b", 
             font=("Arial", 14, "bold")).pack()

    entry_prov_nombre = tk.Entry(form_frame, width=45, font=("Arial", 12))
    entry_prov_nombre.pack(pady=6)
    placeholder(entry_prov_nombre, "Nombre del proveedor")

    entry_prov_telefono = tk.Entry(form_frame, width=45, font=("Arial", 12))
    entry_prov_telefono.pack(pady=6)
    placeholder(entry_prov_telefono, "Teléfono")

    entry_prov_correo = tk.Entry(form_frame, width=45, font=("Arial", 12))
    entry_prov_correo.pack(pady=6)
    placeholder(entry_prov_correo, "Correo electrónico")

    entry_prov_direccion = tk.Entry(form_frame, width=45, font=("Arial", 12))
    entry_prov_direccion.pack(pady=6)
    placeholder(entry_prov_direccion, "Dirección")

    entry_prov_ruc = tk.Entry(form_frame, width=45, font=("Arial", 12))
    entry_prov_ruc.pack(pady=6)
    placeholder(entry_prov_ruc, "RUC")

    tk.Button(
        form_frame, text="Agregar Proveedor",
        bg="#ff9800", fg="black", font=("Arial", 12, "bold"), width=30,
        command=lambda: guardar_proveedor(
            (entry_prov_nombre, entry_prov_telefono, entry_prov_correo, 
             entry_prov_direccion, entry_prov_ruc),
            tabla_proveedores,
            lambda: cargar_proveedores(tabla_proveedores)
        )
    ).pack(pady=15)

    # Tabla de proveedores
    tabla_frame = tk.Frame(prov_box, bg="#1e1e1e")
    tabla_frame.pack(fill="both", expand=True)

    # Scroll
    scroll = ttk.Scrollbar(tabla_frame)
    scroll.pack(side="right", fill="y")

    tabla_proveedores = ttk.Treeview(
        tabla_frame,
        columns=("ID", "Nombre", "Teléfono", "Correo", "Dirección", "RUC"),
        height=12,
        yscrollcommand=scroll.set
    )
    scroll.config(command=tabla_proveedores.yview)

    # Configurar columnas
    tabla_proveedores.column("#0", width=0, stretch="no")
    tabla_proveedores.column("ID", width=30, anchor="center")
    tabla_proveedores.column("Nombre", width=120, anchor="w")
    tabla_proveedores.column("Teléfono", width=100, anchor="center")
    tabla_proveedores.column("Correo", width=150, anchor="w")
    tabla_proveedores.column("Dirección", width=150, anchor="w")
    tabla_proveedores.column("RUC", width=100, anchor="center")

    # Encabezados
    tabla_proveedores.heading("#0", text="", anchor="w")
    tabla_proveedores.heading("ID", text="ID", anchor="center")
    tabla_proveedores.heading("Nombre", text="Nombre", anchor="w")
    tabla_proveedores.heading("Teléfono", text="Teléfono", anchor="center")
    tabla_proveedores.heading("Correo", text="Correo", anchor="w")
    tabla_proveedores.heading("Dirección", text="Dirección", anchor="w")
    tabla_proveedores.heading("RUC", text="RUC", anchor="center")

    tabla_proveedores.pack(fill="both", expand=True)
    # Doble click para ver detalles
    # Se define después de crear tabla_pedidos
    
    # ================== PEDIDOS (en misma sección) ==================

    tk.Label(prov_box, text="Pedidos Realizados",
             fg="#ff9800", bg="#1e1e1e",
             font=("Arial", 16, "bold")).pack(pady=(30, 15))

    # Tabla de pedidos
    tabla_frame_ped = tk.Frame(prov_box, bg="#1e1e1e")
    tabla_frame_ped.pack(fill="both", expand=True, pady=(0, 20))

    # Scroll
    scroll_ped = ttk.Scrollbar(tabla_frame_ped)
    scroll_ped.pack(side="right", fill="y")

    tabla_pedidos = ttk.Treeview(
        tabla_frame_ped,
        columns=("ID", "Fecha", "Proveedor", "Cliente", "Auto", "Servicio", "Pieza", "Costo", "Estado"),
        height=8,
        yscrollcommand=scroll_ped.set
    )
    scroll_ped.config(command=tabla_pedidos.yview)

    # Configurar columnas
    tabla_pedidos.column("#0", width=0, stretch="no")
    tabla_pedidos.column("ID", width=30, anchor="center")
    tabla_pedidos.column("Fecha", width=70, anchor="center")
    tabla_pedidos.column("Proveedor", width=85, anchor="w")
    tabla_pedidos.column("Cliente", width=95, anchor="w")
    tabla_pedidos.column("Auto", width=120, anchor="w")
    tabla_pedidos.column("Servicio", width=85, anchor="w")
    tabla_pedidos.column("Pieza", width=90, anchor="w")
    tabla_pedidos.column("Costo", width=70, anchor="center")
    tabla_pedidos.column("Estado", width=65, anchor="center")

    # Encabezados
    tabla_pedidos.heading("#0", text="", anchor="w")
    tabla_pedidos.heading("ID", text="ID", anchor="center")
    tabla_pedidos.heading("Fecha", text="Fecha", anchor="center")
    tabla_pedidos.heading("Proveedor", text="Proveedor", anchor="w")
    tabla_pedidos.heading("Cliente", text="Cliente", anchor="w")
    tabla_pedidos.heading("Auto", text="Auto", anchor="w")
    tabla_pedidos.heading("Servicio", text="Servicio", anchor="w")
    tabla_pedidos.heading("Pieza", text="Pieza", anchor="w")
    tabla_pedidos.heading("Costo", text="Costo", anchor="center")
    tabla_pedidos.heading("Estado", text="Estado", anchor="center")

    tabla_pedidos.pack(fill="both", expand=True)

    # Doble click para ver detalles
    tabla_pedidos.bind("<Double-Button-1>", lambda e: mostrar_detalles_pedido(tabla_pedidos))
    
    # Binding para proveedores con acceso a tabla_pedidos
    tabla_proveedores.bind("<Double-Button-1>", lambda e: mostrar_info_proveedor_con_pedidos(tabla_proveedores, frame_proveedores, tabla_pedidos))
    
    def mostrar_info_proveedor_con_pedidos(tabla_prov, frame, tabla_ped):
        """Wrapper para pasar tabla_pedidos a mostrar_info_proveedor"""
        seleccion = tabla_prov.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un proveedor")
            return
        
        item = seleccion[0]
        valores = tabla_prov.item(item)['values']
        
        # Crear ventana de detalles
        ventana_info = tk.Toplevel(frame)
        ventana_info.title(f"Detalles - {valores[1]}")
        ventana_info.geometry("500x600")
        ventana_info.configure(bg="#1e1e1e")
        
        frame_det = tk.Frame(ventana_info, bg="#2b2b2b", padx=20, pady=20)
        frame_det.pack(fill="both", expand=True)
        
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
                frame_det,
                text=f"{label}:",
                fg="#ff9800",
                bg="#2b2b2b",
                font=("Arial", 11, "bold")
            ).pack(anchor="w", pady=5)
            
            tk.Label(
                frame_det,
                text=str(valor),
                fg="white",
                bg="#2b2b2b",
                font=("Arial", 11),
                wraplength=350
            ).pack(anchor="w", padx=20, pady=(0, 15))
        
        # Botón de editar
        tk.Button(
            frame_det,
            text="Editar",
            bg="#ff9800",
            fg="black",
            font=("Arial", 11, "bold"),
            command=lambda: editar_proveedor(valores, tabla_prov, cargar_proveedores)
        ).pack(pady=10, ipadx=10, ipady=5)
        
        # Botón de realizar pedido
        tk.Button(
            frame_det,
            text="Realizar un Pedido",
            bg="#4caf50",
            fg="white",
            font=("Arial", 11, "bold"),
            command=lambda: realizar_pedido(valores[0], valores[1], ventana_info, tabla_ped)
        ).pack(pady=5, ipadx=10, ipady=5)
        
        # Botón de eliminar
        tk.Button(
            frame_det,
            text="Eliminar",
            bg="#ff5252",
            fg="white",
            font=("Arial", 11, "bold"),
            command=lambda: eliminar_proveedor(valores[0], tabla_prov, cargar_proveedores, ventana_info)
        ).pack(pady=5, ipadx=10, ipady=5)

    # ------------------ CARGA INICIAL ------------------

    cargar_clientes(lista_clientes)
    cargar_clientes(lista_clientes_autos)
    cargar_autos(lista_autos)
    cargar_citas_tabla(tabla_citas)
    cargar_citas_pendientes(lista_citas_pendientes)
    cargar_proveedores(tabla_proveedores)
    cargar_pedidos(tabla_pedidos)
    
    # Inicializar visualización de registros
    mostrar_visualizacion(frame_visualizacion)
    
    # Inicializar edición de registros
    mostrar_editar_registros(frame_editar)
    
    # Inicializar seguimiento de estado
    from seguimiento_estado_tkinter import vista_seguimiento_estado
    def mostrar_seguimiento_estado(frame):
        vista_seguimiento_estado(frame)
    
    mostrar_seguimiento_estado(frame_seguimiento)

    # Función para refrescar automáticamente las citas pendientes cada 5 segundos
    def refrescar_citas_automatico():
        try:
            # Verificar que la ventana y el widget aún existen antes de intentar actualizarlo
            if ventana.winfo_exists() and lista_citas_pendientes.winfo_exists():
                cargar_citas_pendientes(lista_citas_pendientes)
                # Programar siguiente refresco solo si todo está bien
                ventana.after(5000, refrescar_citas_automatico)
        except Exception as e:
            # Si hay cualquier error, no continuar el ciclo de refresco
            pass

    # Función para refrescar automáticamente la tabla de pedidos cada 5 segundos
    def refrescar_pedidos_automatico():
        try:
            if ventana.winfo_exists() and tabla_pedidos.winfo_exists():
                cargar_pedidos(tabla_pedidos)
                ventana.after(5000, refrescar_pedidos_automatico)
        except Exception:
            pass

    # Función para refrescar automáticamente la lista de autos en Citas cada 2 segundos
    def refrescar_autos_automatico():
        try:
            # Solo refrescar si no está pausado
            if not refresco_autos_pausado.get("paused", False):
                if ventana.winfo_exists() and listas['autos'].winfo_exists():
                    cargar_autos(listas['autos'])
            # Programar siguiente refresco
            if ventana.winfo_exists():
                ventana.after(2000, refrescar_autos_automatico)
        except Exception as e:
            # Si hay cualquier error, reintentar de todas formas
            if ventana.winfo_exists():
                ventana.after(2000, refrescar_autos_automatico)

    # Iniciar el refresco automático
    ventana.after(5000, refrescar_citas_automatico)
    ventana.after(5000, refrescar_pedidos_automatico)
    ventana.after(1000, refrescar_autos_automatico)

    # Iniciar notificación de citas pendientes
    actualizar_notificacion_pendientes()

    mostrar_frame(frame_inicio)

    ventana.mainloop()
