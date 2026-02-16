"""
Módulo para que los empleados actualicen el estado de los vehículos
y realicen seguimiento del servicio de los clientes.
"""

import sqlite3
from datetime import datetime
from db import conectar_db


def obtener_autos_con_citas():
    """Obtiene todos los autos con sus citas activas"""
    conn = conectar_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Obtener autos con citas activas o pendientes
    cur.execute("""
        SELECT DISTINCT
            a.id,
            a.marca,
            a.modelo,
            a.placas,
            c.id as cita_id,
            c.fecha,
            c.hora,
            c.servicio,
            c.estado,
            c.mecanico_id,
            e.nombre as mecanico_nombre,
            cl.nombre as cliente_nombre,
            cl.telefono as cliente_telefono
        FROM autos a
        LEFT JOIN citas c ON a.id = c.auto_id
        LEFT JOIN empleados e ON c.mecanico_id = e.id
        LEFT JOIN clientes cl ON a.cliente_id = cl.id
        WHERE c.estado IS NOT NULL AND c.estado != 'Completada'
        ORDER BY c.fecha DESC, a.marca, a.modelo
    """)
    
    autos = cur.fetchall()
    conn.close()
    
    return autos


def obtener_auto_por_id(auto_id):
    """Obtiene un auto específico con su cita actual"""
    conn = conectar_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT
            a.id,
            a.marca,
            a.modelo,
            a.placas,
            c.id as cita_id,
            c.fecha,
            c.hora,
            c.servicio,
            c.estado,
            c.mecanico_id,
            e.nombre as mecanico_nombre,
            cl.nombre as cliente_nombre,
            cl.telefono as cliente_telefono
        FROM autos a
        LEFT JOIN citas c ON a.id = c.auto_id
        LEFT JOIN empleados e ON c.mecanico_id = e.id
        LEFT JOIN clientes cl ON a.cliente_id = cl.id
        WHERE a.id = ?
        ORDER BY c.fecha DESC
        LIMIT 1
    """, (auto_id,))
    
    auto = cur.fetchone()
    conn.close()
    
    return auto


def obtener_empleados():
    """Obtiene lista de empleados (mecánicos)"""
    conn = conectar_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, nombre FROM empleados ORDER BY nombre
    """)
    
    empleados = cur.fetchall()
    conn.close()
    
    return empleados


def actualizar_estado_cita(cita_id, nuevo_estado, mecanico_id=None):
    """Actualiza el estado de una cita y asigna mecánico si es necesario"""
    conn = conectar_db()
    cur = conn.cursor()
    
    try:
        # Estados válidos
        estados_validos = ["En espera", "En reparación", "Listo para entrega", "Completada"]
        
        if nuevo_estado not in estados_validos:
            return False, "Estado no válido"
        
        if mecanico_id:
            cur.execute("""
                UPDATE citas
                SET estado = ?, mecanico_id = ?
                WHERE id = ?
            """, (nuevo_estado, mecanico_id, cita_id))
        else:
            cur.execute("""
                UPDATE citas
                SET estado = ?
                WHERE id = ?
            """, (nuevo_estado, cita_id))
        
        conn.commit()
        conn.close()
        
        return True, "Estado actualizado correctamente"
        
    except Exception as e:
        conn.close()
        return False, str(e)


def crear_reporte_estado(cita_id, observaciones=""):
    """Crea un mini reporte del estado del vehículo"""
    conn = conectar_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        # Obtener datos de la cita
        cur.execute("""
            SELECT 
                c.id,
                c.fecha,
                c.hora,
                c.servicio,
                c.estado,
                e.nombre as mecanico_nombre,
                a.marca,
                a.modelo,
                a.placas,
                cl.nombre as cliente_nombre
            FROM citas c
            LEFT JOIN empleados e ON c.mecanico_id = e.id
            JOIN autos a ON c.auto_id = a.id
            JOIN clientes cl ON a.cliente_id = cl.id
            WHERE c.id = ?
        """, (cita_id,))
        
        cita = cur.fetchone()
        
        if not cita:
            return None
        
        reporte = {
            "cita_id": cita["id"],
            "cliente": cita["cliente_nombre"],
            "vehiculo": f"{cita['marca']} {cita['modelo']} ({cita['placas']})",
            "servicio": cita["servicio"],
            "estado": cita["estado"],
            "mecanico": cita["mecanico_nombre"] or "Sin asignar",
            "fecha_cita": cita["fecha"],
            "hora_cita": cita["hora"],
            "observaciones": observaciones,
            "fecha_reporte": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        conn.close()
        return reporte
        
    except Exception as e:
        conn.close()
        return None


def obtener_estadisticas():
    """Obtiene estadísticas de los servicios"""
    conn = conectar_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        # Contar por estado
        cur.execute("""
            SELECT estado, COUNT(*) as cantidad
            FROM citas
            WHERE estado IN ('En espera', 'En reparación', 'Listo para entrega')
            GROUP BY estado
        """)
        
        estadisticas = {}
        for row in cur.fetchall():
            estadisticas[row["estado"]] = row["cantidad"]
        
        # Totales
        cur.execute("""
            SELECT COUNT(*) as total FROM citas
            WHERE estado IN ('En espera', 'En reparación', 'Listo para entrega')
        """)
        
        total = cur.fetchone()["total"]
        
        conn.close()
        
        return {
            "por_estado": estadisticas,
            "total": total,
            "en_espera": estadisticas.get("En espera", 0),
            "en_reparacion": estadisticas.get("En reparación", 0),
            "listo_entrega": estadisticas.get("Listo para entrega", 0)
        }
        
    except Exception as e:
        conn.close()
        return None
