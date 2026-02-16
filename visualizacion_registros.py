import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import conectar_db
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from datetime import datetime
import os

def cargar_clientes_info():
    """Carga toda la información de clientes con sus vehículos y citas"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.id, c.nombre, c.telefono, c.correo,
            a.id as auto_id, a.marca, a.modelo, a.placas,
            cit.id as cita_id, cit.fecha, cit.hora, cit.servicio, cit.estado
        FROM clientes c
        LEFT JOIN autos a ON c.id = a.cliente_id
        LEFT JOIN citas cit ON a.id = cit.auto_id
        ORDER BY c.nombre, a.id, cit.fecha DESC
    """)
    
    registros = cursor.fetchall()
    conn.close()
    
    return registros


def cargar_servicios_realizados():
    """Carga los servicios realizados con información completa de piezas y proveedores"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            cit.id as cita_id,
            cit.fecha as fecha_cita,
            cit.hora,
            cit.servicio,
            cit.estado as estado_cita,
            c.id as cliente_id,
            c.nombre as cliente_nombre,
            c.telefono as cliente_telefono,
            c.correo as cliente_correo,
            a.id as auto_id,
            a.marca,
            a.modelo,
            a.placas,
            p.id as pieza_id,
            p.pieza_refaccion,
            p.estado as estado_pieza,
            prov.id as proveedor_id,
            prov.nombre as proveedor_nombre,
            prov.telefono as proveedor_telefono,
            prov.correo as proveedor_correo,
            prov.direccion as proveedor_direccion,
            prov.ruc as proveedor_ruc
        FROM citas cit
        JOIN autos a ON cit.auto_id = a.id
        JOIN clientes c ON a.cliente_id = c.id
        LEFT JOIN piezas p ON p.auto_id = a.id AND p.cliente_id = c.id
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
        WHERE cit.estado IN ('Completado', 'completado', 'Realizada', 'realizada', 'Aceptada', 'aceptada')
        ORDER BY cit.fecha DESC, cit.hora DESC
    """)
    
    registros = cursor.fetchall()
    conn.close()
    
    return registros


def cargar_citas_programadas():
    """Carga todas las citas programadas"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.nombre as cliente, c.telefono, c.correo,
            a.marca, a.modelo, a.placas,
            cit.fecha, cit.hora, cit.servicio, cit.estado
        FROM citas cit
        JOIN autos a ON cit.auto_id = a.id
        JOIN clientes c ON a.cliente_id = c.id
        WHERE cit.estado != 'Completado' AND cit.estado != 'completado'
        ORDER BY cit.fecha ASC, cit.hora ASC
    """)
    
    registros = cursor.fetchall()
    conn.close()
    
    return registros


def mostrar_visualizacion(frame_visualizacion):
    """Muestra la interfaz de visualización de registros"""
    
    # Limpiar frame
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()
    
    # Título
    titulo = tk.Label(
        frame_visualizacion, text="Visualización de Registros",
        fg="#ff9800", bg="#1e1e1e", font=("Arial", 24, "bold")
    )
    titulo.pack(pady=20)
    
    # Frame para botones
    frame_botones = tk.Frame(frame_visualizacion, bg="#1e1e1e")
    frame_botones.pack(pady=10)
    
    # Botones principales
    botones_info = [
        ("Ver Clientes", lambda: mostrar_clientes(frame_visualizacion)),
        ("Ver Vehículos", lambda: mostrar_vehiculos(frame_visualizacion)),
        ("Ver Servicios Realizados", lambda: mostrar_servicios(frame_visualizacion)),
        ("Ver Citas Programadas", lambda: mostrar_citas(frame_visualizacion))
    ]
    
    for texto, comando in botones_info:
        tk.Button(
            frame_botones, text=texto, width=25, height=2,
            font=("Arial", 11, "bold"),
            bg="#ff9800", fg="white",
            command=comando
        ).pack(pady=8)
    
    # Frame para mostrar datos
    frame_datos = tk.Frame(frame_visualizacion, bg="#2b2b2b")
    frame_datos.pack(fill="both", expand=True, padx=20, pady=20)
    frame_datos.grid_propagate(False)
    
    # Label para mostrar datos
    label_info = tk.Label(
        frame_datos, text="Selecciona una opción para ver los registros",
        fg="#ffffff", bg="#2b2b2b", font=("Arial", 14), justify="left", wraplength=800
    )
    label_info.pack(pady=20)


def mostrar_clientes(frame_visualizacion):
    """Muestra todos los clientes registrados"""
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()
    
    titulo = tk.Label(
        frame_visualizacion, text="Clientes Registrados",
        fg="#ff9800", bg="#1e1e1e", font=("Arial", 24, "bold")
    )
    titulo.pack(pady=20)
    
    # Botón para volver
    tk.Button(
        frame_visualizacion, text="← Volver al menú",
        bg="#555555", fg="white", width=15,
        command=lambda: mostrar_visualizacion(frame_visualizacion)
    ).pack(pady=10)
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, correo FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()
    conn.close()
    
    # Crear tabla
    frame_tabla = tk.Frame(frame_visualizacion, bg="#2b2b2b")
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Encabezados
    encabezados = ["ID", "Nombre", "Teléfono", "Correo"]
    for i, encabezado in enumerate(encabezados):
        tk.Label(
            frame_tabla, text=encabezado, bg="#ff9800", fg="white",
            font=("Arial", 11, "bold"), padx=10, pady=10
        ).grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
    
    # Datos
    for idx, cliente in enumerate(clientes, 1):
        id_cli, nombre, telefono, correo = cliente
        datos = [id_cli, nombre, telefono or "N/A", correo or "N/A"]
        
        for col, dato in enumerate(datos):
            bg_color = "#1e1e1e" if idx % 2 == 0 else "#2b2b2b"
            label = tk.Label(
                frame_tabla, text=str(dato), bg=bg_color, fg="white",
                padx=10, pady=10, font=("Arial", 10)
            )
            label.grid(row=idx, column=col, sticky="nsew", padx=2, pady=2)
            
            # Botón exportar a PDF individual
            if col == 0:  # En la primera columna
                tk.Button(
                    frame_tabla, text="PDF", bg="#27ae60", fg="white", width=6,
                    command=lambda c_id=id_cli, c_nom=nombre: exportar_cliente_pdf(c_id, c_nom)
                ).grid(row=idx, column=4, sticky="nsew", padx=2, pady=2)
    
    # Botón exportar todos a PDF
    tk.Button(
        frame_visualizacion, text="Exportar Todos los Clientes a PDF",
        bg="#27ae60", fg="white", width=25, height=2,
        command=exportar_todos_clientes_pdf
    ).pack(pady=10)


def mostrar_vehiculos(frame_visualizacion):
    """Muestra todos los vehículos con su información completa"""
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()
    
    titulo = tk.Label(
        frame_visualizacion, text="Vehículos Asociados a Clientes",
        fg="#ff9800", bg="#1e1e1e", font=("Arial", 24, "bold")
    )
    titulo.pack(pady=20)
    
    tk.Button(
        frame_visualizacion, text="← Volver al menú",
        bg="#555555", fg="white", width=15,
        command=lambda: mostrar_visualizacion(frame_visualizacion)
    ).pack(pady=10)
    
    registros = cargar_clientes_info()
    
    # Crear tabla
    frame_tabla = tk.Frame(frame_visualizacion, bg="#2b2b2b")
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Encabezados
    encabezados = ["Cliente", "Teléfono", "Correo", "Marca", "Modelo", "Placas", "Citas"]
    for i, encabezado in enumerate(encabezados):
        tk.Label(
            frame_tabla, text=encabezado, bg="#ff9800", fg="white",
            font=("Arial", 11, "bold"), padx=10, pady=10
        ).grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
    
    # Procesar datos
    cliente_actual = None
    auto_actual = None
    idx_fila = 1
    
    for registro in registros:
        id_cli, nombre_cli, tel, correo, auto_id, marca, modelo, placas, cita_id, fecha, hora, servicio, estado = registro
        
        # Si es un nuevo cliente
        if cliente_actual != nombre_cli:
            cliente_actual = nombre_cli
            auto_actual = None
        
        # Si es un nuevo vehículo
        if auto_id != auto_actual:
            auto_actual = auto_id
            bg_color = "#1e1e1e" if idx_fila % 2 == 0 else "#2b2b2b"
            
            datos = [nombre_cli, tel or "N/A", correo or "N/A", marca or "N/A", 
                    modelo or "N/A", placas or "N/A", "1" if cita_id else "0"]
            
            for col, dato in enumerate(datos):
                tk.Label(
                    frame_tabla, text=str(dato), bg=bg_color, fg="white",
                    padx=10, pady=10, font=("Arial", 10)
                ).grid(row=idx_fila, column=col, sticky="nsew", padx=2, pady=2)
            
            idx_fila += 1
    
    # Botón exportar a PDF
    tk.Button(
        frame_visualizacion, text="Exportar Vehículos a PDF",
        bg="#27ae60", fg="white", width=25, height=2,
        command=exportar_vehiculos_pdf
    ).pack(pady=10)


def mostrar_servicios(frame_visualizacion):
    """Muestra servicios realizados con información completa de piezas y proveedores"""
    
    # Limpiar frame
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()
    
    # Título
    titulo = tk.Label(
        frame_visualizacion, text="Servicios Realizados - Piezas y Proveedores",
        fg="#ff9800", bg="#1e1e1e", font=("Arial", 20, "bold")
    )
    titulo.pack(pady=20)
    
    # Frame para botones
    frame_botones = tk.Frame(frame_visualizacion, bg="#1e1e1e")
    frame_botones.pack(pady=10)
    
    tk.Button(
        frame_botones, text="← Volver al menú",
        bg="#555555", fg="white", width=15,
        command=lambda: mostrar_visualizacion(frame_visualizacion)
    ).pack(side="left", padx=5)
    
    tk.Button(
        frame_botones, text="Exportar a PDF",
        bg="#27ae60", fg="white", width=20,
        command=exportar_servicios_pdf
    ).pack(side="left", padx=5)
    
    tk.Button(
        frame_botones, text="🔄 Refrescar",
        bg="#3498db", fg="white", width=15,
        command=lambda: mostrar_servicios(frame_visualizacion)
    ).pack(side="left", padx=5)
    
    registros = cargar_servicios_realizados()
    
    if not registros:
        tk.Label(
            frame_visualizacion, text="No hay servicios realizados registrados",
            fg="#ffffff", bg="#1e1e1e", font=("Arial", 14)
        ).pack(pady=20)
        return
    
    # Frame con scroll
    frame_contenedor = tk.Frame(frame_visualizacion, bg="#1e1e1e")
    frame_contenedor.pack(fill="both", expand=True, padx=20, pady=10)
    
    canvas = tk.Canvas(frame_contenedor, bg="#1e1e1e", highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_contenedor, orient="vertical", command=canvas.yview)
    frame_scroll = tk.Frame(canvas, bg="#1e1e1e")
    
    frame_scroll.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Agrupar por auto (cada auto aparece una sola vez con TODAS sus citas y piezas)
    servicios_agrupados = {}
    for registro in registros:
        (cita_id, fecha_cita, hora, servicio, estado_cita,
         cliente_id, cliente_nombre, cliente_telefono, cliente_correo,
         auto_id, marca, modelo, placas,
         pieza_id, pieza_refaccion, estado_pieza,
         proveedor_id, proveedor_nombre, proveedor_telefono, 
         proveedor_correo, proveedor_direccion, proveedor_ruc) = registro
        
        if auto_id not in servicios_agrupados:
            servicios_agrupados[auto_id] = {
                'cliente': {
                    'id': cliente_id,
                    'nombre': cliente_nombre,
                    'telefono': cliente_telefono,
                    'correo': cliente_correo
                },
                'auto': {
                    'id': auto_id,
                    'marca': marca,
                    'modelo': modelo,
                    'placas': placas
                },
                'citas': {},  # Diccionario con cita_id como clave
                'piezas': []
            }
        
        # Agregar cita si no existe (incluso sin piezas)
        if cita_id not in servicios_agrupados[auto_id]['citas']:
            servicios_agrupados[auto_id]['citas'][cita_id] = {
                'id': cita_id,
                'fecha': fecha_cita,
                'hora': hora,
                'servicio': servicio,
                'estado': estado_cita
            }
        
        # Agregar piezas si existen
        if pieza_id:
            servicios_agrupados[auto_id]['piezas'].append({
                'cita_id': cita_id,
                'pieza': pieza_refaccion,
                'estado': estado_pieza,
                'proveedor': {
                    'id': proveedor_id,
                    'nombre': proveedor_nombre,
                    'telefono': proveedor_telefono,
                    'correo': proveedor_correo,
                    'direccion': proveedor_direccion,
                    'ruc': proveedor_ruc
                }
            })
    
    # Mostrar resultados en grid 2 columnas
    fila = 0
    columna = 0
    max_columnas = 2
    
    for idx, (auto_id, datos_auto) in enumerate(servicios_agrupados.items(), 1):
        # Contenedor principal para cada auto
        frame_servicio = tk.Frame(frame_scroll, bg="#2b2b2b", relief="solid", bd=2, width=550, height=450)
        frame_servicio.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")
        frame_servicio.grid_propagate(False)
        
        # Encabezado con información del auto
        encabezado = tk.Frame(frame_servicio, bg="#ff9800")
        encabezado.pack(fill="x", padx=0, pady=0)
        
        tk.Label(
            encabezado, text=f"🚗 {datos_auto['auto']['marca']} {datos_auto['auto']['modelo']}",
            fg="white", bg="#ff9800", font=("Arial", 10, "bold"), padx=8, pady=5, justify="left"
        ).pack(fill="x", anchor="w")
        
        tk.Label(
            encabezado, text=f"Placas: {datos_auto['auto']['placas'] or 'N/A'} | Citas: {len(datos_auto['citas'])}",
            fg="white", bg="#ff9800", font=("Arial", 9), padx=8, pady=3, justify="left"
        ).pack(fill="x", anchor="w")
        
        # Información del cliente
        frame_cliente = tk.Frame(frame_servicio, bg="#2b2b2b")
        frame_cliente.pack(fill="x", padx=8, pady=8)
        
        tk.Label(
            frame_cliente, text=f"👤 {datos_auto['cliente']['nombre']}",
            fg="#ff9800", bg="#2b2b2b", font=("Arial", 9, "bold")
        ).pack(anchor="w")
        
        tk.Label(
            frame_cliente, text=f"📞 {datos_auto['cliente']['telefono'] or 'N/A'}",
            fg="#ffffff", bg="#2b2b2b", font=("Arial", 8)
        ).pack(anchor="w", pady=2)
        
        # Separador
        tk.Frame(frame_servicio, bg="#444444", height=1).pack(fill="x", pady=8)
        
        # Mostrar citas
        tk.Label(
            frame_servicio, text=f"📅 CITAS REALIZADAS ({len(datos_auto['citas'])})",
            fg="#ff9800", bg="#2b2b2b", font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=8, pady=(0, 5))
        
        for cita_id, cita in datos_auto['citas'].items():
            # Obtener piezas para esta cita
            piezas_cita = [p for p in datos_auto['piezas'] if p['cita_id'] == cita_id]
            
            frame_cita = tk.Frame(frame_servicio, bg="#1e1e1e", relief="solid", bd=1)
            frame_cita.pack(fill="x", padx=8, pady=2)
            
            tk.Label(
                frame_cita, text=f"#{cita['id']} | {cita['fecha'][:10]} {cita['hora']} | {cita['servicio']}",
                fg="#ffffff", bg="#1e1e1e", font=("Arial", 7), padx=5, pady=2
            ).pack(anchor="w")
            
            # Mostrar pedido o servicio
            if piezas_cita:
                piezas_text = ", ".join([p['pieza'] for p in piezas_cita])
                tk.Label(
                    frame_cita, text=f"📦 Pedido: {piezas_text[:40]}...",
                    fg="#90EE90", bg="#1e1e1e", font=("Arial", 6, "italic"), padx=5, pady=1
                ).pack(anchor="w")
            else:
                tk.Label(
                    frame_cita, text=f"⚙️ Servicio: {cita['servicio']}",
                    fg="#FFD700", bg="#1e1e1e", font=("Arial", 6, "italic"), padx=5, pady=1
                ).pack(anchor="w")
        
        # Piezas y proveedores
        if datos_auto['piezas']:
            tk.Label(
                frame_servicio, text=f"📦 PIEZAS Y PROVEEDORES ({len(datos_auto['piezas'])})",
                fg="#ff9800", bg="#2b2b2b", font=("Arial", 9, "bold")
            ).pack(anchor="w", padx=8, pady=(5, 8))
            
            for pieza_idx, pieza in enumerate(datos_auto['piezas'], 1):
                # Contenedor de pieza
                frame_pieza = tk.Frame(frame_servicio, bg="#1e1e1e", relief="ridge", bd=1)
                frame_pieza.pack(fill="x", padx=8, pady=4)
                
                # Info de la pieza
                tk.Label(
                    frame_pieza, text=f"#{pieza_idx} {pieza['pieza']} (Cita #{pieza['cita_id']})",
                    fg="#ffffff", bg="#1e1e1e", font=("Arial", 8, "bold"), padx=6, pady=3
                ).pack(anchor="w")
                
                # Info del proveedor
                prov = pieza['proveedor']
                tk.Label(
                    frame_pieza, text=f"🏢 {prov['nombre']}",
                    fg="#ff9800", bg="#1e1e1e", font=("Arial", 7, "bold"), padx=6, pady=2
                ).pack(anchor="w")
                
                tk.Label(
                    frame_pieza, text=f"📞 {prov['telefono'] or 'N/A'}",
                    fg="#ffffff", bg="#1e1e1e", font=("Arial", 7), padx=6, pady=1
                ).pack(anchor="w")
        else:
            tk.Label(
                frame_servicio, text="Sin piezas",
                fg="#cccccc", bg="#2b2b2b", font=("Arial", 7), padx=5, pady=5
            ).pack(anchor="w")
        
        # Estado y botón exportar
        frame_footer = tk.Frame(frame_servicio, bg="#2b2b2b")
        frame_footer.pack(fill="x", padx=0, pady=(10, 0))
        
        # Mostrar estado de la última cita
        ultimo_estado = 'N/A'
        if datos_auto['citas']:
            ultima_cita = list(datos_auto['citas'].values())[-1]
            ultimo_estado = ultima_cita['estado']
        
        estados_completados = ['Completado', 'completado', 'Realizada', 'realizada']
        color_estado = "#27ae60" if ultimo_estado in estados_completados else "#ff9800"
        
        tk.Label(
            frame_footer, text=f"Último Estado: {ultimo_estado}",
            fg="white", bg=color_estado, font=("Arial", 9, "bold"), padx=8, pady=5
        ).pack(side="left", fill="x", expand=True)
        
        # Botón exportar individual
        tk.Button(
            frame_footer, text="📄 Exportar PDF", bg="#27ae60", fg="white",
            font=("Arial", 8, "bold"), padx=12, pady=5,
            command=lambda a_id=auto_id, datos=datos_auto: exportar_auto_completo_pdf(a_id, datos)
        ).pack(side="right", padx=8, pady=0)
        
        # Actualizar posición en el grid
        columna += 1
        if columna >= max_columnas:
            columna = 0
            fila += 1
    
    # Configurar peso de las columnas para distribución uniforme
    for col in range(max_columnas):
        frame_scroll.grid_columnconfigure(col, weight=1, minsize=550)


def mostrar_citas(frame_visualizacion):
    """Muestra citas programadas"""
    for widget in frame_visualizacion.winfo_children():
        widget.destroy()
    
    titulo = tk.Label(
        frame_visualizacion, text="Citas Programadas",
        fg="#ff9800", bg="#1e1e1e", font=("Arial", 24, "bold")
    )
    titulo.pack(pady=20)
    
    tk.Button(
        frame_visualizacion, text="← Volver al menú",
        bg="#555555", fg="white", width=15,
        command=lambda: mostrar_visualizacion(frame_visualizacion)
    ).pack(pady=10)
    
    registros = cargar_citas_programadas()
    
    if not registros:
        tk.Label(
            frame_visualizacion, text="No hay citas programadas",
            fg="#ffffff", bg="#1e1e1e", font=("Arial", 14)
        ).pack(pady=20)
        return
    
    # Crear tabla
    frame_tabla = tk.Frame(frame_visualizacion, bg="#2b2b2b")
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Encabezados
    encabezados = ["Cliente", "Teléfono", "Vehículo", "Placas", "Fecha", "Hora", "Servicio", "Estado"]
    for i, encabezado in enumerate(encabezados):
        tk.Label(
            frame_tabla, text=encabezado, bg="#ff9800", fg="white",
            font=("Arial", 11, "bold"), padx=10, pady=10
        ).grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
    
    # Datos
    for idx, registro in enumerate(registros, 1):
        cliente, tel, correo, marca, modelo, placas, fecha, hora, servicio, estado = registro
        
        bg_color = "#1e1e1e" if idx % 2 == 0 else "#2b2b2b"
        datos = [cliente, tel or "N/A", f"{marca} {modelo}", placas or "N/A", 
                fecha or "N/A", hora or "N/A", servicio or "N/A", estado]
        
        for col, dato in enumerate(datos):
            tk.Label(
                frame_tabla, text=str(dato), bg=bg_color, fg="white",
                padx=10, pady=10, font=("Arial", 10)
            ).grid(row=idx, column=col, sticky="nsew", padx=2, pady=2)
    
    # Botón exportar
    tk.Button(
        frame_visualizacion, text="Exportar Citas a PDF",
        bg="#27ae60", fg="white", width=25, height=2,
        command=exportar_citas_pdf
    ).pack(pady=10)


# ============== FUNCIONES DE EXPORTACIÓN A PDF ==============

def exportar_auto_completo_pdf(auto_id, datos_auto):
    """Exporta información completa de un auto con todas sus citas y piezas a PDF"""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Auto_{datos_auto['auto']['marca']}_{datos_auto['auto']['modelo']}_{datetime.now().strftime('%d%m%Y')}.pdf"
    )
    
    if not ruta:
        return
    
    try:
        doc = SimpleDocTemplate(ruta, pagesize=A4, rightMargin=0.4*inch, leftMargin=0.4*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        estilo_titulo = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#ff9800'),
            spaceAfter=12,
            alignment=1
        )
        
        # Título
        titulo = Paragraph(f"VEHÍCULO: {datos_auto['auto']['marca'].upper()} {datos_auto['auto']['modelo'].upper()}", estilo_titulo)
        story.append(titulo)
        story.append(Spacer(1, 0.2*inch))
        
        # Información del vehículo
        info_auto = f"""
        <b>Placas:</b> {datos_auto['auto']['placas'] or 'N/A'}<br/>
        <b>Total de Citas:</b> {len(datos_auto['citas'])}<br/>
        <b>Total de Piezas:</b> {len(datos_auto['piezas'])}
        """
        story.append(Paragraph(info_auto, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del cliente
        story.append(Paragraph("<b>INFORMACIÓN DEL PROPIETARIO</b>", styles['Heading2']))
        info_cliente = f"""
        <b>Nombre:</b> {datos_auto['cliente']['nombre']}<br/>
        <b>Teléfono:</b> {datos_auto['cliente']['telefono'] or 'N/A'}<br/>
        <b>Correo:</b> {datos_auto['cliente']['correo'] or 'N/A'}
        """
        story.append(Paragraph(info_cliente, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Citas realizadas
        story.append(Paragraph(f"<b>CITAS REALIZADAS ({len(datos_auto['citas'])})</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        for cita_id, cita in datos_auto['citas'].items():
            cita_info = f"""
            <b>Cita #{cita['id']}</b> - {cita['fecha']} a las {cita['hora']}<br/>
            <b>Servicio:</b> {cita['servicio']}<br/>
            <b>Estado:</b> {cita['estado']}
            """
            story.append(Paragraph(cita_info, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        # Piezas y proveedores
        if datos_auto['piezas']:
            story.append(Paragraph(f"<b>PIEZAS Y PROVEEDORES ({len(datos_auto['piezas'])})</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for pieza_idx, pieza in enumerate(datos_auto['piezas'], 1):
                # Información de la pieza en formato texto (sin tabla)
                nombre_pieza = str(pieza['pieza']) if pieza.get('pieza') else 'N/A'
                cita_id_pieza = str(pieza['cita_id']) if pieza.get('cita_id') else 'N/A'
                estado_pieza = str(pieza['estado']) if pieza.get('estado') else 'N/A'
                
                prov = pieza.get('proveedor', {})
                nombre_prov = str(prov.get('nombre')) if prov.get('nombre') else 'N/A'
                telefono_prov = str(prov.get('telefono')) if prov.get('telefono') else 'N/A'
                correo_prov = str(prov.get('correo')) if prov.get('correo') else 'N/A'
                direccion_prov = str(prov.get('direccion')) if prov.get('direccion') else 'N/A'
                ruc_prov = str(prov.get('ruc')) if prov.get('ruc') else 'N/A'
                
                info_pieza = f"""
                <b>PIEZA #{pieza_idx}:</b> {nombre_pieza}<br/>
                <b>Cita #:</b> {cita_id_pieza}<br/>
                <b>Estado:</b> {estado_pieza}<br/>
                <b>Proveedor:</b> {nombre_prov}<br/>
                <b>Teléfono:</b> {telefono_prov}<br/>
                <b>Correo:</b> {correo_prov}<br/>
                <b>Dirección:</b> {direccion_prov}<br/>
                <b>RUC:</b> {ruc_prov}
                """
                story.append(Paragraph(info_pieza, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        else:
            story.append(Paragraph("<b>PIEZAS Y PROVEEDORES</b>", styles['Heading2']))
            story.append(Paragraph("<i>Sin piezas registradas</i>", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Fecha de generación
        story.append(Spacer(1, 0.3*inch))
        fecha_gen = Paragraph(
            f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</i>",
            styles['Normal']
        )
        story.append(fecha_gen)
        
        doc.build(story)
        messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")


def exportar_servicio_individual_pdf(cita_id, datos_cita):
    """Exporta un servicio individual a PDF"""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Servicio_#{cita_id}_{datetime.now().strftime('%d%m%Y')}.pdf"
    )
    
    if not ruta:
        return
    
    try:
        doc = SimpleDocTemplate(ruta, pagesize=A4, rightMargin=0.4*inch, leftMargin=0.4*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        estilo_titulo = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#ff9800'),
            spaceAfter=12,
            alignment=1
        )
        
        # Título
        titulo = Paragraph(f"SERVICIO #{cita_id} - {datos_cita['servicio'].upper()}", estilo_titulo)
        story.append(titulo)
        story.append(Spacer(1, 0.2*inch))
        
        # Información de la cita
        info_cita = f"""
        <b>Fecha:</b> {datos_cita['fecha']}<br/>
        <b>Hora:</b> {datos_cita['hora']}<br/>
        <b>Estado:</b> <b>{datos_cita['estado']}</b>
        """
        story.append(Paragraph(info_cita, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del cliente
        story.append(Paragraph("<b>INFORMACIÓN DEL CLIENTE</b>", styles['Heading2']))
        info_cliente = f"""
        <b>Nombre:</b> {datos_cita['cliente']['nombre']}<br/>
        <b>Teléfono:</b> {datos_cita['cliente']['telefono'] or 'N/A'}<br/>
        <b>Correo:</b> {datos_cita['cliente']['correo'] or 'N/A'}
        """
        story.append(Paragraph(info_cliente, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del vehículo
        story.append(Paragraph("<b>INFORMACIÓN DEL VEHÍCULO</b>", styles['Heading2']))
        info_auto = f"""
        <b>Marca:</b> {datos_cita['auto']['marca']}<br/>
        <b>Modelo:</b> {datos_cita['auto']['modelo']}<br/>
        <b>Placas:</b> {datos_cita['auto']['placas'] or 'N/A'}
        """
        story.append(Paragraph(info_auto, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Piezas y proveedores
        if datos_cita['piezas']:
            story.append(Paragraph("<b>PIEZAS Y PROVEEDORES</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for pieza_idx, pieza in enumerate(datos_cita['piezas'], 1):
                # Tabla para cada pieza
                pieza_data = [
                    [f"<b>PIEZA #{pieza_idx}</b>", f"<b>{pieza['pieza']}</b>"],
                    [f"<b>Estado:</b>", pieza['estado']],
                    [f"<b>Proveedor:</b>", pieza['proveedor']['nombre']],
                    [f"<b>Teléfono:</b>", pieza['proveedor']['telefono'] or 'N/A'],
                    [f"<b>Correo:</b>", pieza['proveedor']['correo'] or 'N/A'],
                    [f"<b>Dirección:</b>", pieza['proveedor']['direccion'] or 'N/A'],
                    [f"<b>RUC:</b>", pieza['proveedor']['ruc'] or 'N/A']
                ]
                
                tabla_pieza = Table(pieza_data, colWidths=[1.5*inch, 4*inch])
                tabla_pieza.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ff9800')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8)
                ]))
                story.append(tabla_pieza)
                story.append(Spacer(1, 0.2*inch))
        else:
            story.append(Paragraph("<b>PIEZAS Y PROVEEDORES</b>", styles['Heading2']))
            story.append(Paragraph("<i>Sin piezas registradas</i>", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Fecha de generación
        story.append(Spacer(1, 0.3*inch))
        fecha_gen = Paragraph(
            f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</i>",
            styles['Normal']
        )
        story.append(fecha_gen)
        
        doc.build(story)
        messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")


def exportar_cliente_pdf(cliente_id, cliente_nombre):
    """Exporta información completa de un cliente a PDF"""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Cliente_{cliente_nombre}.pdf"
    )
    
    if not ruta:
        return
    
    try:
        doc = SimpleDocTemplate(ruta, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo = Paragraph(f"<b>REGISTRO DE CLIENTE: {cliente_nombre.upper()}</b>", styles['Title'])
        story.append(titulo)
        story.append(Spacer(1, 0.3*inch))
        
        # Información del cliente
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, telefono, correo FROM clientes WHERE id = ?", (cliente_id,))
        cliente_info = cursor.fetchone()
        
        if cliente_info:
            nombre, telefono, correo = cliente_info
            info_texto = f"""
            <b>Nombre:</b> {nombre}<br/>
            <b>Teléfono:</b> {telefono or 'N/A'}<br/>
            <b>Correo:</b> {correo or 'N/A'}<br/>
            """
            story.append(Paragraph(info_texto, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Vehículos
        story.append(Paragraph("<b>VEHÍCULOS ASOCIADOS</b>", styles['Heading2']))
        
        cursor.execute("""
            SELECT id, marca, modelo, placas FROM autos WHERE cliente_id = ?
        """, (cliente_id,))
        autos = cursor.fetchall()
        
        if autos:
            for auto in autos:
                auto_id, marca, modelo, placas = auto
                story.append(Paragraph(f"<b>• {marca} {modelo} - Placas: {placas}</b>", styles['Normal']))
                
                # Citas del vehículo
                cursor.execute("""
                    SELECT fecha, hora, servicio, estado FROM citas WHERE auto_id = ? ORDER BY fecha DESC
                """, (auto_id,))
                citas = cursor.fetchall()
                
                if citas:
                    citas_data = [["Fecha", "Hora", "Servicio", "Estado"]]
                    for cita in citas:
                        citas_data.append([
                            cita[0] or "N/A",
                            cita[1] or "N/A",
                            cita[2] or "N/A",
                            cita[3] or "N/A"
                        ])
                    
                    tabla_citas = Table(citas_data, colWidths=[1.5*inch, 1*inch, 2*inch, 1.5*inch])
                    tabla_citas.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(tabla_citas)
                else:
                    story.append(Paragraph("Sin citas registradas", styles['Normal']))
                
                story.append(Spacer(1, 0.2*inch))
        else:
            story.append(Paragraph("Sin vehículos registrados", styles['Normal']))
        
        # Fecha de generación
        story.append(Spacer(1, 0.5*inch))
        fecha_gen = Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Normal'])
        story.append(fecha_gen)
        
        doc.build(story)
        messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
        conn.close()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")


def exportar_todos_clientes_pdf():
    """Exporta todos los clientes a un PDF"""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Reporte_Clientes_{datetime.now().strftime('%d%m%Y')}.pdf"
    )
    
    if not ruta:
        return
    
    try:
        doc = SimpleDocTemplate(ruta, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo = Paragraph(f"<b>REPORTE DE CLIENTES REGISTRADOS</b>", styles['Title'])
        story.append(titulo)
        story.append(Spacer(1, 0.3*inch))
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, telefono, correo FROM clientes ORDER BY nombre")
        clientes = cursor.fetchall()
        
        # Tabla de clientes
        datos_tabla = [["ID", "Nombre", "Teléfono", "Correo"]]
        for cliente in clientes:
            datos_tabla.append([
                str(cliente[0]),
                cliente[1],
                cliente[2] or "N/A",
                cliente[3] or "N/A"
            ])
        
        tabla = Table(datos_tabla, colWidths=[0.8*inch, 2*inch, 1.5*inch, 2.5*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(tabla)
        
        # Fecha
        story.append(Spacer(1, 0.3*inch))
        fecha_gen = Paragraph(f"<i>Total de clientes: {len(clientes)}</i>", styles['Normal'])
        story.append(fecha_gen)
        story.append(Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Normal']))
        
        doc.build(story)
        messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
        conn.close()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")


def exportar_vehiculos_pdf():
    """Exporta todos los vehículos a PDF"""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Reporte_Vehiculos_{datetime.now().strftime('%d%m%Y')}.pdf"
    )
    
    if not ruta:
        return
    
    try:
        doc = SimpleDocTemplate(ruta, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo = Paragraph(f"<b>REPORTE DE VEHÍCULOS ASOCIADOS</b>", styles['Title'])
        story.append(titulo)
        story.append(Spacer(1, 0.3*inch))
        
        registros = cargar_clientes_info()
        
        datos_tabla = [["Cliente", "Teléfono", "Correo", "Marca", "Modelo", "Placas", "Citas"]]
        cliente_actual = None
        auto_actual = None
        
        for registro in registros:
            id_cli, nombre_cli, tel, correo, auto_id, marca, modelo, placas, cita_id, fecha, hora, servicio, estado = registro
            
            if cliente_actual != nombre_cli:
                cliente_actual = nombre_cli
                auto_actual = None
            
            if auto_id != auto_actual:
                auto_actual = auto_id
                datos_tabla.append([
                    nombre_cli,
                    tel or "N/A",
                    correo or "N/A",
                    marca or "N/A",
                    modelo or "N/A",
                    placas or "N/A",
                    "Sí" if cita_id else "No"
                ])
        
        tabla = Table(datos_tabla, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch, 1.5*inch, 1.2*inch, 1*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        story.append(tabla)
        
        story.append(Spacer(1, 0.3*inch))
        fecha_gen = Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Normal'])
        story.append(fecha_gen)
        
        doc.build(story)
        messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")


def exportar_servicios_pdf():
    """Exporta servicios realizados a PDF con información de piezas y proveedores"""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Reporte_Servicios_{datetime.now().strftime('%d%m%Y')}.pdf"
    )
    
    if not ruta:
        return
    
    try:
        doc = SimpleDocTemplate(ruta, pagesize=A4, rightMargin=0.4*inch, leftMargin=0.4*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        estilo_titulo = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#ff9800'),
            spaceAfter=12,
            alignment=1
        )
        
        estilo_encabezado = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.white,
            backColor=colors.HexColor('#ff9800'),
            alignment=0,
            spaceAfter=8,
            padding=6
        )
        
        # Título
        titulo = Paragraph("REPORTE DE SERVICIOS REALIZADOS - PIEZAS Y PROVEEDORES", estilo_titulo)
        story.append(titulo)
        story.append(Spacer(1, 0.2*inch))
        
        registros = cargar_servicios_realizados()
        
        if not registros:
            story.append(Paragraph("No hay servicios realizados registrados", styles['Normal']))
            doc.build(story)
            messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
            return
        
        # Agrupar por cita
        servicios_agrupados = {}
        for registro in registros:
            (cita_id, fecha_cita, hora, servicio, estado_cita,
             cliente_id, cliente_nombre, cliente_telefono, cliente_correo,
             auto_id, marca, modelo, placas,
             pieza_id, pieza_refaccion, estado_pieza,
             proveedor_id, proveedor_nombre, proveedor_telefono, 
             proveedor_correo, proveedor_direccion, proveedor_ruc) = registro
            
            if cita_id not in servicios_agrupados:
                servicios_agrupados[cita_id] = {
                    'fecha': fecha_cita,
                    'hora': hora,
                    'servicio': servicio,
                    'estado': estado_cita,
                    'cliente': {
                        'nombre': cliente_nombre,
                        'telefono': cliente_telefono,
                        'correo': cliente_correo
                    },
                    'auto': {
                        'marca': marca,
                        'modelo': modelo,
                        'placas': placas
                    },
                    'piezas': []
                }
            
            if pieza_id:
                servicios_agrupados[cita_id]['piezas'].append({
                    'pieza': pieza_refaccion,
                    'estado': estado_pieza,
                    'proveedor': {
                        'nombre': proveedor_nombre,
                        'telefono': proveedor_telefono,
                        'correo': proveedor_correo,
                        'direccion': proveedor_direccion,
                        'ruc': proveedor_ruc
                    }
                })
        
        # Generar PDF con cada servicio
        total_servicios = len(servicios_agrupados)
        for idx, (cita_id, datos_cita) in enumerate(servicios_agrupados.items()):
            # Encabezado de cita
            encabezado_cita = Paragraph(
                f"<b>CITA #{cita_id} | {datos_cita['fecha']} a las {datos_cita['hora']} | {datos_cita['servicio']}</b>",
                estilo_encabezado
            )
            story.append(encabezado_cita)
            story.append(Spacer(1, 0.1*inch))
            
            # Información del cliente
            info_cliente = f"""
            <b>👤 CLIENTE:</b> {datos_cita['cliente']['nombre']}<br/>
            <b>📞 Teléfono:</b> {datos_cita['cliente']['telefono'] or 'N/A'}<br/>
            <b>📧 Correo:</b> {datos_cita['cliente']['correo'] or 'N/A'}<br/>
            <br/>
            <b>🚗 VEHÍCULO:</b> {datos_cita['auto']['marca']} {datos_cita['auto']['modelo']}<br/>
            <b>Placas:</b> {datos_cita['auto']['placas'] or 'N/A'}<br/>
            <b>Estado de la Cita:</b> <b>{datos_cita['estado']}</b>
            """
            story.append(Paragraph(info_cliente, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
            
            # Piezas y proveedores
            if datos_cita['piezas']:
                story.append(Paragraph("<b>PIEZAS Y PROVEEDORES:</b>", styles['Heading3']))
                story.append(Spacer(1, 0.1*inch))
                
                for pieza_idx, pieza in enumerate(datos_cita['piezas'], 1):
                    # Información de la pieza en formato texto (sin tabla)
                    nombre_pieza = str(pieza['pieza']) if pieza['pieza'] else 'N/A'
                    estado_pieza = str(pieza['estado']) if pieza['estado'] else 'N/A'
                    nombre_prov = str(pieza['proveedor']['nombre']) if pieza['proveedor'] and pieza['proveedor'].get('nombre') else 'N/A'
                    telefono_prov = str(pieza['proveedor']['telefono']) if pieza['proveedor'] and pieza['proveedor'].get('telefono') else 'N/A'
                    correo_prov = str(pieza['proveedor']['correo']) if pieza['proveedor'] and pieza['proveedor'].get('correo') else 'N/A'
                    direccion_prov = str(pieza['proveedor']['direccion']) if pieza['proveedor'] and pieza['proveedor'].get('direccion') else 'N/A'
                    ruc_prov = str(pieza['proveedor']['ruc']) if pieza['proveedor'] and pieza['proveedor'].get('ruc') else 'N/A'
                    
                    info_pieza = f"""
                    <b>PIEZA #{pieza_idx}:</b> {nombre_pieza}<br/>
                    <b>Estado:</b> {estado_pieza}<br/>
                    <b>Proveedor:</b> {nombre_prov}<br/>
                    <b>Teléfono:</b> {telefono_prov}<br/>
                    <b>Correo:</b> {correo_prov}<br/>
                    <b>Dirección:</b> {direccion_prov}<br/>
                    <b>RUC:</b> {ruc_prov}
                    """
                    story.append(Paragraph(info_pieza, styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))
            else:
                story.append(Paragraph("<i>Sin piezas registradas</i>", styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
            
            # Separador entre servicios
            if idx < total_servicios - 1:
                story.append(PageBreak())
        
        # Fecha de generación
        story.append(Spacer(1, 0.3*inch))
        fecha_gen = Paragraph(
            f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</i>",
            styles['Normal']
        )
        story.append(fecha_gen)
        
        doc.build(story)
        messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")


def exportar_citas_pdf():
    """Exporta citas programadas a PDF"""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialfile=f"Reporte_Citas_{datetime.now().strftime('%d%m%Y')}.pdf"
    )
    
    if not ruta:
        return
    
    try:
        doc = SimpleDocTemplate(ruta, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        titulo = Paragraph(f"<b>REPORTE DE CITAS PROGRAMADAS</b>", styles['Title'])
        story.append(titulo)
        story.append(Spacer(1, 0.3*inch))
        
        registros = cargar_citas_programadas()
        
        if registros:
            datos_tabla = [["Cliente", "Teléfono", "Vehículo", "Placas", "Fecha", "Hora", "Servicio", "Estado"]]
            for registro in registros:
                cliente, tel, correo, marca, modelo, placas, fecha, hora, servicio, estado = registro
                datos_tabla.append([
                    cliente,
                    tel or "N/A",
                    f"{marca} {modelo}",
                    placas or "N/A",
                    fecha or "N/A",
                    hora or "N/A",
                    servicio or "N/A",
                    estado
                ])
            
            tabla = Table(datos_tabla, colWidths=[1.2*inch, 1*inch, 1.2*inch, 0.9*inch, 0.9*inch, 0.7*inch, 1.4*inch, 0.8*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7)
            ]))
            story.append(tabla)
        else:
            story.append(Paragraph("No hay citas programadas", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        fecha_gen = Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Normal'])
        story.append(fecha_gen)
        
        doc.build(story)
        messagebox.showinfo("Éxito", f"PDF generado correctamente:\n{ruta}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")
