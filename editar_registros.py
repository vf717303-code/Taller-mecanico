import tkinter as tk
from tkinter import messagebox, ttk
from db import conectar_db


def mostrar_editar_registros(frame_editar):
    """Muestra la interfaz para editar clientes y autos"""
    
    # Limpiar frame
    for widget in frame_editar.winfo_children():
        widget.destroy()
    
    # Título
    titulo = tk.Label(
        frame_editar, text="Editar Registros - Clientes y Autos",
        fg="#ff9800", bg="#1e1e1e", font=("Arial", 24, "bold")
    )
    titulo.pack(pady=20)
    
    # Frame principal con dos secciones (sin expand para dejar espacio a botones)
    frame_principal = tk.Frame(frame_editar, bg="#1e1e1e")
    frame_principal.pack(fill="both", expand=True, padx=5, pady=10)
    
    # Frame para scroll si es necesario
    canvas_frame = tk.Canvas(frame_principal, bg="#1e1e1e", highlightthickness=0)
    scrollbar_main = tk.Scrollbar(frame_principal, orient="vertical", command=canvas_frame.yview)
    scrollable_frame = tk.Frame(canvas_frame, bg="#1e1e1e")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
    )
    
    canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_frame.configure(yscrollcommand=scrollbar_main.set)
    
    canvas_frame.pack(side="left", fill="both", expand=True)
    scrollbar_main.pack(side="right", fill="y")
    
    # ==================== SECCIÓN CLIENTES ====================
    frame_clientes_sec = tk.LabelFrame(
        scrollable_frame, text="CLIENTES", 
        bg="#2b2b2b", fg="#ff9800", font=("Arial", 12, "bold"),
        padx=15, pady=15
    )
    frame_clientes_sec.pack(fill="both", expand=True, pady=10, padx=5)
    
    # Búsqueda de cliente
    frame_busqueda = tk.Frame(frame_clientes_sec, bg="#2b2b2b")
    frame_busqueda.pack(fill="x", pady=10)
    
    tk.Label(frame_busqueda, text="Buscar cliente:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(side="left", padx=5)
    
    entry_busqueda = tk.Entry(frame_busqueda, width=60, bg="#1e1e1e", fg="#ffffff", font=("Arial", 10))
    entry_busqueda.pack(side="left", padx=5, fill="x", expand=True)
    
    # Lista de clientes
    frame_lista_clientes = tk.Frame(frame_clientes_sec, bg="#2b2b2b")
    frame_lista_clientes.pack(fill="both", expand=True, pady=10)
    
    tk.Label(frame_lista_clientes, text="Clientes:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 9)).pack(anchor="w", padx=5)
    
    scrollbar_clientes = tk.Scrollbar(frame_lista_clientes)
    scrollbar_clientes.pack(side="right", fill="y")
    
    lista_clientes = tk.Listbox(
        frame_lista_clientes, 
        bg="#1e1e1e", fg="#ffffff", font=("Arial", 9),
        yscrollcommand=scrollbar_clientes.set, height=6
    )
    lista_clientes.pack(fill="both", expand=True, padx=5)
    scrollbar_clientes.config(command=lista_clientes.yview)
    
    # Frame para edición de cliente
    frame_editar_cliente = tk.Frame(frame_clientes_sec, bg="#2b2b2b")
    frame_editar_cliente.pack(fill="x", pady=10)
    
    tk.Label(frame_editar_cliente, text="Nombre:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(8, 3))
    entry_cliente_nombre = tk.Entry(frame_editar_cliente, bg="#1e1e1e", fg="#ffffff", font=("Arial", 16), width=80)
    entry_cliente_nombre.pack(fill="x", padx=5, pady=(0, 15))
    
    tk.Label(frame_editar_cliente, text="Teléfono:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(8, 3))
    entry_cliente_telefono = tk.Entry(frame_editar_cliente, bg="#1e1e1e", fg="#ffffff", font=("Arial", 16), width=80)
    entry_cliente_telefono.pack(fill="x", padx=5, pady=(0, 15))
    
    tk.Label(frame_editar_cliente, text="Correo:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(8, 3))
    entry_cliente_correo = tk.Entry(frame_editar_cliente, bg="#1e1e1e", fg="#ffffff", font=("Arial", 16), width=80)
    entry_cliente_correo.pack(fill="x", padx=5, pady=(0, 15))
    
    tk.Label(frame_editar_cliente, text="Contraseña:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(8, 3))
    entry_cliente_password = tk.Entry(frame_editar_cliente, bg="#1e1e1e", fg="#ffffff", font=("Arial", 16), width=80)
    entry_cliente_password.pack(fill="x", padx=5, pady=(0, 5))
    
    # Variables globales para almacenar datos
    cliente_seleccionado = {'id': None, 'nombre': '', 'telefono': '', 'correo': '', 'password': ''}
    
    def cargar_clientes_lista(filtro=""):
        """Carga la lista de clientes, opcionalmente filtrada"""
        lista_clientes.delete(0, "end")
        conn = conectar_db()
        cursor = conn.cursor()
        
        if filtro:
            cursor.execute(
                "SELECT id, nombre, telefono, correo, password FROM clientes WHERE nombre LIKE ?",
                (f"%{filtro}%",)
            )
        else:
            cursor.execute("SELECT id, nombre, telefono, correo, password FROM clientes")
        
        for cliente in cursor.fetchall():
            lista_clientes.insert("end", f"{cliente[0]} - {cliente[1]} ({cliente[2]})")
        conn.close()
    
    def seleccionar_cliente(event=None):
        """Selecciona un cliente y muestra sus datos"""
        if not lista_clientes.curselection():
            return
        
        seleccion = lista_clientes.get(lista_clientes.curselection()[0])
        cliente_id = int(seleccion.split(" - ")[0])
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, telefono, correo, password FROM clientes WHERE id = ?", (cliente_id,))
        datos = cursor.fetchone()
        conn.close()
        
        if datos:
            cliente_seleccionado['id'] = datos[0]
            cliente_seleccionado['nombre'] = datos[1]
            cliente_seleccionado['telefono'] = datos[2]
            cliente_seleccionado['correo'] = datos[3]
            cliente_seleccionado['password'] = datos[4] if len(datos) > 4 else ''
            
            entry_cliente_nombre.delete(0, "end")
            entry_cliente_nombre.insert(0, datos[1])
            entry_cliente_telefono.delete(0, "end")
            entry_cliente_telefono.insert(0, datos[2] or "")
            entry_cliente_correo.delete(0, "end")
            entry_cliente_correo.insert(0, datos[3] or "")
            entry_cliente_password.delete(0, "end")
            entry_cliente_password.insert(0, datos[4] if len(datos) > 4 and datos[4] else "")
            
            cargar_autos_lista()
    
    def buscar_cliente(event=None):
        """Busca clientes mientras se escribe"""
        filtro = entry_busqueda.get()
        cargar_clientes_lista(filtro)
    
    def guardar_cliente():
        """Guarda los cambios del cliente"""
        if not cliente_seleccionado['id']:
            messagebox.showerror("Error", "Selecciona un cliente primero")
            return
        
        nombre = entry_cliente_nombre.get().strip()
        telefono = entry_cliente_telefono.get().strip()
        correo = entry_cliente_correo.get().strip()
        password = entry_cliente_password.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        if not password:
            messagebox.showerror("Error", "La contraseña no puede estar vacía")
            return
        
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nombre = ?, telefono = ?, correo = ?, password = ? WHERE id = ?",
                (nombre, telefono, correo, password, cliente_seleccionado['id'])
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            cargar_clientes_lista()
            entry_busqueda.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")
    
    # ==================== SECCIÓN AUTOS ====================
    frame_autos_sec = tk.LabelFrame(
        scrollable_frame, text="AUTOS DEL CLIENTE",
        bg="#2b2b2b", fg="#ff9800", font=("Arial", 12, "bold"),
        padx=15, pady=15
    )
    frame_autos_sec.pack(fill="both", expand=True, pady=10, padx=5)
    
    # Lista de autos
    frame_lista_autos = tk.Frame(frame_autos_sec, bg="#2b2b2b")
    frame_lista_autos.pack(fill="both", expand=True, pady=10)
    
    tk.Label(frame_lista_autos, text="Autos:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 9)).pack(anchor="w", padx=5)
    
    scrollbar_autos = tk.Scrollbar(frame_lista_autos)
    scrollbar_autos.pack(side="right", fill="y")
    
    lista_autos = tk.Listbox(
        frame_lista_autos,
        bg="#1e1e1e", fg="#ffffff", font=("Arial", 9),
        yscrollcommand=scrollbar_autos.set, height=5
    )
    lista_autos.pack(fill="both", expand=True, padx=5)
    scrollbar_autos.config(command=lista_autos.yview)
    
    # Frame para edición de auto
    frame_editar_auto = tk.Frame(frame_autos_sec, bg="#2b2b2b")
    frame_editar_auto.pack(fill="x", pady=10)
    
    tk.Label(frame_editar_auto, text="Marca:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(8, 3))
    entry_auto_marca = tk.Entry(frame_editar_auto, bg="#1e1e1e", fg="#ffffff", font=("Arial", 16), width=80)
    entry_auto_marca.pack(fill="x", padx=5, pady=(0, 15))
    
    tk.Label(frame_editar_auto, text="Modelo:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(8, 3))
    entry_auto_modelo = tk.Entry(frame_editar_auto, bg="#1e1e1e", fg="#ffffff", font=("Arial", 16), width=80)
    entry_auto_modelo.pack(fill="x", padx=5, pady=(0, 15))
    
    tk.Label(frame_editar_auto, text="Placas:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(8, 3))
    entry_auto_placas = tk.Entry(frame_editar_auto, bg="#1e1e1e", fg="#ffffff", font=("Arial", 16), width=80)
    entry_auto_placas.pack(fill="x", padx=5, pady=(0, 5))
    
    auto_seleccionado = {'id': None, 'marca': '', 'modelo': '', 'placas': ''}
    
    def cargar_autos_lista():
        """Carga la lista de autos del cliente seleccionado"""
        lista_autos.delete(0, "end")
        
        if not cliente_seleccionado['id']:
            return
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, marca, modelo, placas FROM autos WHERE cliente_id = ?",
            (cliente_seleccionado['id'],)
        )
        
        for auto in cursor.fetchall():
            lista_autos.insert("end", f"{auto[0]} | {auto[1]} {auto[2]} | {auto[3]}")
        conn.close()
    
    def seleccionar_auto(event=None):
        """Selecciona un auto y muestra sus datos"""
        if not lista_autos.curselection():
            return
        
        seleccion = lista_autos.get(lista_autos.curselection()[0])
        auto_id = int(seleccion.split(" | ")[0])
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, marca, modelo, placas FROM autos WHERE id = ?", (auto_id,))
        datos = cursor.fetchone()
        conn.close()
        
        if datos:
            auto_seleccionado['id'] = datos[0]
            auto_seleccionado['marca'] = datos[1]
            auto_seleccionado['modelo'] = datos[2]
            auto_seleccionado['placas'] = datos[3]
            
            entry_auto_marca.delete(0, "end")
            entry_auto_marca.insert(0, datos[1])
            entry_auto_modelo.delete(0, "end")
            entry_auto_modelo.insert(0, datos[2])
            entry_auto_placas.delete(0, "end")
            entry_auto_placas.insert(0, datos[3])
    
    def guardar_auto():
        """Guarda los cambios del auto"""
        if not auto_seleccionado['id']:
            messagebox.showerror("Error", "Selecciona un auto primero")
            return
        
        marca = entry_auto_marca.get().strip()
        modelo = entry_auto_modelo.get().strip()
        placas = entry_auto_placas.get().strip()
        
        if not marca or not modelo or not placas:
            messagebox.showerror("Error", "Completa todos los datos del auto")
            return
        
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE autos SET marca = ?, modelo = ?, placas = ? WHERE id = ?",
                (marca, modelo, placas, auto_seleccionado['id'])
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Auto actualizado correctamente")
            cargar_autos_lista()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")
    
    # ==================== BOTONES ====================
    frame_botones = tk.Frame(frame_editar, bg="#1e1e1e")
    frame_botones.pack(fill="x", pady=20, padx=5)
    
    tk.Button(
        frame_botones, text="💾 Guardar Cliente",
        bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
        command=guardar_cliente, padx=20, pady=10
    ).pack(side="left", padx=15, expand=True, fill="x")
    
    tk.Button(
        frame_botones, text="💾 Guardar Auto",
        bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
        command=guardar_auto, padx=20, pady=10
    ).pack(side="left", padx=15, expand=True, fill="x")
    
    tk.Button(
        frame_botones, text="← Volver al menú",
        bg="#555555", fg="white", font=("Arial", 13, "bold"),
        command=lambda: mostrar_visualizacion(frame_editar), padx=30, pady=15
    ).pack(side="left", padx=15, expand=True, fill="x")
    
    # Eventos
    entry_busqueda.bind("<KeyRelease>", buscar_cliente)
    lista_clientes.bind("<<ListboxSelect>>", seleccionar_cliente)
    lista_autos.bind("<<ListboxSelect>>", seleccionar_auto)
    
    # Cargar datos iniciales
    cargar_clientes_lista()
    
    # Refresco automático cada 4 segundos
    def refrescar_automaticamente():
        try:
            if frame_editar.winfo_exists():
                # Recargar listas sin perder la selección actual
                cliente_actual = cliente_seleccionado['id']
                auto_actual = auto_seleccionado['id']
                
                cargar_clientes_lista()
                
                if cliente_actual:
                    cargar_autos_lista()
                
                frame_editar.after(4000, refrescar_automaticamente)
        except Exception as e:
            # Silenciar errores de widgets destruidos
            pass
    
    refrescar_automaticamente()


def mostrar_visualizacion(frame):
    """Función auxiliar para volver al menú (importará desde visualizacion_registros)"""
    from visualizacion_registros import mostrar_visualizacion as mostrar_viz
    mostrar_viz(frame)
