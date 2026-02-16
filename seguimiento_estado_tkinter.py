"""
Módulo Tkinter para la interfaz de Seguimiento de Estado del Vehículo
Diseño mejorado con vista de tarjetas y mini-reportes
"""

import tkinter as tk
from tkinter import messagebox, ttk
from db import conectar_db
from actualizacion_estado_vehiculo import obtener_autos_con_citas, obtener_empleados, actualizar_estado_cita


def cargar_autos_seguimiento(lista):
    """Carga los autos en servicio en la lista"""
    lista.delete(0, "end")
    
    try:
        autos = obtener_autos_con_citas()
        
        if not autos:
            lista.insert("end", "No hay vehículos en servicio")
            return
        
        for auto in autos:
            texto = f"{auto['marca']} {auto['modelo']} | Placas: {auto['placas']} | Cliente: {auto['cliente_nombre']} | Estado: {auto['estado']}"
            lista.insert("end", texto)
    
    except Exception as e:
        lista.insert("end", f"Error: {str(e)}")


def obtener_datos_auto_seleccionado(lista_autos, indice):
    """Obtiene los datos del auto seleccionado"""
    autos = obtener_autos_con_citas()
    
    if 0 <= indice < len(autos):
        return autos[indice]
    
    return None


def vista_seguimiento_estado(frame):
    """Vista principal del módulo de seguimiento de estado con diseño mejorado"""
    
    # Limpiar frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Frame principal
    main_frame = tk.Frame(frame, bg="#1e1e1e")
    main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # HEADER
    header = tk.Frame(main_frame, bg="#ff9800", height=80)
    header.pack(fill="x", padx=0, pady=0)
    header.pack_propagate(False)

    tk.Label(
        header,
        text="⏱️ SEGUIMIENTO DE ESTADO DEL VEHÍCULO",
        fg="black",
        bg="#ff9800",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    tk.Label(
        header,
        text="Actualiza el estado y asigna mecánico a los vehículos en servicio",
        fg="black",
        bg="#ff9800",
        font=("Arial", 10)
    ).pack(pady=5)

    # CONTENIDO
    content = tk.Frame(main_frame, bg="#1e1e1e")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    # PANEL IZQUIERDO - Lista de vehículos
    left_panel = tk.Frame(content, bg="#2b2b2b", relief="ridge", bd=1)
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

    tk.Label(
        left_panel,
        text="🚗 VEHÍCULOS EN SERVICIO",
        fg="#ff9800",
        bg="#2b2b2b",
        font=("Arial", 12, "bold")
    ).pack(pady=10, padx=10)

    # Listbox con scrollbar
    frame_lista = tk.Frame(left_panel, bg="#2b2b2b")
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side="right", fill="y")

    lista_autos = tk.Listbox(
        frame_lista, 
        width=50, 
        height=15, 
        font=("Arial", 9),
        bg="#1a1a1a",
        fg="white",
        yscrollcommand=scrollbar.set,
        selectmode="single"
    )
    lista_autos.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=lista_autos.yview)

    # PANEL DERECHO - Detalles y controles
    right_panel = tk.Frame(content, bg="#2b2b2b", relief="ridge", bd=1)
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

    tk.Label(
        right_panel,
        text="📋 MINI REPORTE",
        fg="#ff9800",
        bg="#2b2b2b",
        font=("Arial", 12, "bold")
    ).pack(pady=10, padx=10)

    # Frame para el reporte
    report_frame = tk.Frame(right_panel, bg="#1a1a1a", relief="ridge", bd=1)
    report_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Variables de información
    info_var = tk.StringVar(value="Selecciona un vehículo de la lista izquierda")
    info_label = tk.Label(
        report_frame,
        textvariable=info_var,
        fg="#ccc",
        bg="#1a1a1a",
        font=("Arial", 10),
        justify="left",
        wraplength=280
    )
    info_label.pack(fill="both", expand=True, padx=15, pady=15)

    # CONTROLES
    control_frame = tk.Frame(right_panel, bg="#2b2b2b")
    control_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(
        control_frame,
        text="📊 Nuevo Estado:",
        fg="#ff9800",
        bg="#2b2b2b",
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(0, 5))

    estados = ["En espera", "En reparación", "Listo para entrega", "Completada"]
    combo_estado = ttk.Combobox(
        control_frame,
        values=estados,
        state="readonly",
        width=30,
        font=("Arial", 10)
    )
    combo_estado.pack(fill="x", pady=(0, 15))

    tk.Label(
        control_frame,
        text="👨‍🔧 Mecánico Asignado:",
        fg="#ff9800",
        bg="#2b2b2b",
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(0, 5))

    empleados = obtener_empleados()
    lista_empleados = [f"{emp['nombre']}" for emp in empleados]
    combo_mecanico = ttk.Combobox(
        control_frame,
        values=lista_empleados,
        state="readonly",
        width=30,
        font=("Arial", 10)
    )
    combo_mecanico.pack(fill="x", pady=(0, 15))

    # BOTONES
    button_frame = tk.Frame(right_panel, bg="#2b2b2b")
    button_frame.pack(fill="x", padx=10, pady=10)

    def actualizar_cita():
        seleccion = lista_autos.curselection()
        
        if not seleccion:
            messagebox.showwarning("Selección", "Selecciona un vehículo")
            return
        
        if not combo_estado.get():
            messagebox.showwarning("Estado", "Selecciona un estado")
            return
        
        try:
            autos = obtener_autos_con_citas()
            auto = autos[seleccion[0]]
            cita_id = auto['cita_id']
            nuevo_estado = combo_estado.get()
            
            # Extraer ID del mecánico si se seleccionó
            mecanico_id = None
            if combo_mecanico.get():
                for emp in empleados:
                    if emp['nombre'] == combo_mecanico.get():
                        mecanico_id = emp['id']
                        break
            
            exito, mensaje = actualizar_estado_cita(cita_id, nuevo_estado, mecanico_id)
            
            if exito:
                messagebox.showinfo("✓ Éxito", f"Estado actualizado correctamente")
                cargar_autos_seguimiento(lista_autos)
                info_var.set("Selecciona un vehículo de la lista izquierda")
                combo_estado.set("")
                combo_mecanico.set("")
            else:
                messagebox.showerror("Error", f"No se pudo actualizar: {mensaje}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def refrescar_lista():
        cargar_autos_seguimiento(lista_autos)
        info_var.set("Selecciona un vehículo de la lista izquierda")
        combo_estado.set("")
        combo_mecanico.set("")

    def mostrar_reporte(event=None):
        """Muestra el reporte del vehículo seleccionado"""
        seleccion = lista_autos.curselection()
        if not seleccion:
            return
        
        try:
            autos = obtener_autos_con_citas()
            auto = autos[seleccion[0]]
            
            reporte = f"""
🚗 VEHÍCULO
{auto['marca']} {auto['modelo']}
Placa: {auto['placas']}

👤 CLIENTE
{auto['cliente_nombre']}
📞 {auto['cliente_telefono']}

📋 SERVICIO
{auto['servicio']}

⏱️ ESTADO DEL VEHÍCULO
{auto['estado']}

👨‍🔧 MECÁNICO ASIGNADO
{auto['mecanico_nombre'] or 'Sin asignar'}

📅 CITA
{auto['fecha']} {auto['hora']}
            """
            info_var.set(reporte)
        except Exception as e:
            info_var.set(f"Error al cargar datos: {str(e)}")

    tk.Button(
        button_frame,
        text="✅ ACTUALIZAR ESTADO",
        bg="#4caf50",
        fg="white",
        font=("Arial", 11, "bold"),
        command=actualizar_cita
    ).pack(fill="x", pady=5)

    tk.Button(
        button_frame,
        text="🔃 REFRESCAR",
        bg="#666666",
        fg="white",
        font=("Arial", 11, "bold"),
        command=refrescar_lista
    ).pack(fill="x", pady=5)

    # Vincular evento de selección
    lista_autos.bind('<<ListboxSelect>>', mostrar_reporte)

    # Cargar datos iniciales
    cargar_autos_seguimiento(lista_autos)

