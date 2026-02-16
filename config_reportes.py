"""
config_reportes.py
Configuración de estilos y formatos para los reportes PDF
Personaliza colores, fuentes y formato de los reportes exportados
"""

# ============== COLORES ==============
COLORES = {
    'primario': '#ff9800',      # Naranja (color principal del taller)
    'secundario': '#2196F3',    # Azul
    'exito': '#27ae60',         # Verde
    'error': '#e74c3c',         # Rojo
    'advertencia': '#f39c12',   # Naranja claro
    'fondo_tabla': '#ecf0f1',   # Gris claro
    'texto_oscuro': '#2c3e50',  # Gris oscuro
}

# ============== FUENTES ==============
FUENTES = {
    'titulo': ('Helvetica-Bold', 18),
    'subtitulo': ('Helvetica-Bold', 14),
    'encabezado': ('Helvetica-Bold', 11),
    'normal': ('Helvetica', 10),
    'pequeno': ('Helvetica', 8),
}

# ============== MÁRGENES ==============
MARGENES = {
    'superior': 0.5,    # en pulgadas
    'inferior': 0.5,
    'izquierdo': 0.5,
    'derecho': 0.5,
}

# ============== TAMAÑO DE PÁGINA ==============
TAMAÑO_PAGINA = {
    'carta': 'letter',      # 8.5 x 11 pulgadas
    'a4': 'a4',            # 210 x 297 mm
    'legal': 'legal',       # 8.5 x 14 pulgadas
}

# Usar por defecto
TAMAÑO_DEFECTO = TAMAÑO_PAGINA['carta']

# ============== INFORMACIÓN DEL TALLER ==============
TALLER_INFO = {
    'nombre': 'TALLER MECÁNICO',
    'telefono': '+1 (555) 123-4567',
    'correo': 'contacto@tallermec.com',
    'direccion': 'Calle Principal 123, Ciudad',
    'ruc': '12345678',
    'logo_url': None,  # Dejar None si no hay logo, o indicar ruta al logo
}

# ============== ESTILOS DE TABLA ==============
ESTILOS_TABLA = {
    'encabezado_bg': COLORES['primario'],      # Fondo del encabezado
    'encabezado_fg': '#ffffff',                # Texto del encabezado
    'fila_alterno_bg': COLORES['fondo_tabla'], # Fondo de filas alternas
    'borde_color': '#cccccc',                  # Color de bordes
    'borde_ancho': 1,                          # Ancho de bordes (pt)
    'padding_horizontal': 8,
    'padding_vertical': 6,
}

# ============== COLUMNAS POR REPORTE ==============
COLUMNAS = {
    'clientes': {
        'ancho': [0.8, 2.0, 1.5, 2.5],
        'encabezados': ['ID', 'Nombre', 'Teléfono', 'Correo']
    },
    'vehiculos': {
        'ancho': [1.5, 1.5, 2.0, 1.5, 1.5, 1.2, 1.0],
        'encabezados': ['Cliente', 'Teléfono', 'Correo', 'Marca', 'Modelo', 'Placas', 'Citas']
    },
    'servicios': {
        'ancho': [1.5, 1.5, 1.0, 1.0, 0.8, 1.8, 1.0],
        'encabezados': ['Cliente', 'Vehículo', 'Placas', 'Fecha', 'Hora', 'Servicio', 'Estado']
    },
    'citas': {
        'ancho': [1.2, 1.0, 1.2, 0.9, 0.9, 0.7, 1.4, 0.8],
        'encabezados': ['Cliente', 'Teléfono', 'Vehículo', 'Placas', 'Fecha', 'Hora', 'Servicio', 'Estado']
    },
}

# ============== OPCIONES DE EXPORTACIÓN ==============
OPCIONES_EXPORT = {
    'incluir_fecha': True,           # Incluir fecha de generación
    'incluir_numero_pagina': True,   # Incluir números de página en reportes largos
    'incluir_info_taller': True,     # Incluir datos del taller en el PDF
    'formato_fecha': '%d/%m/%Y %H:%M',  # Formato de fecha (Python strftime)
    'compression': False,             # Comprimir PDF (True = archivo más pequeño)
}

# ============== TEXTOS PERSONALIZABLES ==============
TEXTOS = {
    'titulo_clientes': 'REPORTE DE CLIENTES REGISTRADOS',
    'titulo_vehiculos': 'REPORTE DE VEHÍCULOS ASOCIADOS',
    'titulo_servicios': 'REPORTE DE SERVICIOS REALIZADOS',
    'titulo_citas': 'REPORTE DE CITAS PROGRAMADAS',
    'sin_datos': 'No hay datos disponibles para mostrar',
    'generado_el': 'Reporte generado el',
    'total': 'Total',
}

# ============== FUNCIÓN DE INICIALIZACIÓN ==============
def obtener_estilos():
    """
    Retorna un diccionario consolidado de configuración
    Útil para pasar a las funciones de exportación
    """
    return {
        'colores': COLORES,
        'fuentes': FUENTES,
        'margenes': MARGENES,
        'taller_info': TALLER_INFO,
        'estilos_tabla': ESTILOS_TABLA,
        'opciones_export': OPCIONES_EXPORT,
        'textos': TEXTOS,
        'columnas': COLUMNAS,
    }

# ============== EJEMPLOS DE USO ==============
"""
# En visualizacion_registros.py:

from config_reportes import obtener_estilos, COLORES, FUENTES

def exportar_cliente_pdf(cliente_id, cliente_nombre):
    config = obtener_estilos()
    
    # Usar colores personalizados
    color_primario = config['colores']['primario']
    
    # Usar fuentes personalizadas
    fuente_titulo = config['fuentes']['titulo']
    
    # Usar información del taller
    taller = config['taller_info']
    nombre_taller = taller['nombre']
"""
