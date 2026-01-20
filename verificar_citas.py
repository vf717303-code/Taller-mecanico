import sqlite3

def verificar_citas():
    """Verificar qué citas hay en la BD"""
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFICACIÓN DE CITAS EN LA BASE DE DATOS")
    print("=" * 80)
    
    # Ver estructura de tabla citas
    print("\n1. ESTRUCTURA DE TABLA CITAS:")
    cur.execute("PRAGMA table_info(citas)")
    columnas = cur.fetchall()
    for col in columnas:
        print(f"   - {col[1]} ({col[2]})")
    
    # Ver total de citas
    print("\n2. TOTAL DE CITAS:")
    cur.execute("SELECT COUNT(*) FROM citas")
    total = cur.fetchone()[0]
    print(f"   Total: {total} citas")
    
    # Ver citas por estado
    print("\n3. CITAS POR ESTADO:")
    cur.execute("SELECT estado, COUNT(*) FROM citas GROUP BY estado")
    for estado, cantidad in cur.fetchall():
        print(f"   - {estado}: {cantidad}")
    
    # Ver citas pendientes (En admisión)
    print("\n4. CITAS PENDIENTES (En admisión):")
    cur.execute("""
        SELECT 
            citas.id,
            clientes.nombre,
            autos.marca,
            autos.placas,
            citas.fecha,
            citas.hora,
            citas.servicio,
            citas.estado
        FROM citas
        JOIN autos ON citas.auto_id = autos.id
        JOIN clientes ON autos.cliente_id = clientes.id
        WHERE citas.estado = 'En admisión'
        ORDER BY citas.fecha, citas.hora
    """)
    
    citas_pendientes = cur.fetchall()
    if citas_pendientes:
        for cita in citas_pendientes:
            print(f"   ID: {cita[0]}")
            print(f"   Cliente: {cita[1]}")
            print(f"   Auto: {cita[2]} ({cita[3]})")
            print(f"   Fecha: {cita[4]}")
            print(f"   Hora: {cita[5]}")
            print(f"   Servicio: {cita[6]}")
            print(f"   Estado: {cita[7]}")
            print()
    else:
        print("   ⚠ NO HAY CITAS PENDIENTES")
    
    # Ver tabla clientes
    print("\n5. CLIENTES REGISTRADOS:")
    cur.execute("SELECT id, nombre FROM clientes")
    clientes = cur.fetchall()
    for id_cliente, nombre in clientes:
        print(f"   ID: {id_cliente}, Nombre: {nombre}")
    
    # Ver tabla autos
    print("\n6. AUTOS REGISTRADOS:")
    cur.execute("""
        SELECT autos.id, autos.cliente_id, autos.marca, autos.modelo, autos.placas 
        FROM autos
    """)
    autos = cur.fetchall()
    for auto in autos:
        print(f"   ID: {auto[0]}, Cliente: {auto[1]}, {auto[2]} {auto[3]} ({auto[4]})")
    
    conn.close()
    print("\n" + "=" * 80)

if __name__ == "__main__":
    verificar_citas()
