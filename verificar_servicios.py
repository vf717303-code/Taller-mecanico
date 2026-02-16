from db import conectar_db

def verificar_datos():
    """Verifica qué datos hay en la base de datos"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("VERIFICACIÓN DE DATOS EN LA BASE DE DATOS")
    print("=" * 60)
    
    # Verificar citas
    print("\n1. CITAS:")
    cursor.execute("SELECT id, fecha, hora, servicio, estado FROM citas")
    citas = cursor.fetchall()
    if citas:
        for cita in citas:
            print(f"   ID: {cita[0]}, Fecha: {cita[1]}, Hora: {cita[2]}, Servicio: {cita[3]}, Estado: '{cita[4]}'")
    else:
        print("   No hay citas registradas")
    
    # Verificar piezas
    print("\n2. PIEZAS:")
    cursor.execute("SELECT id, cita_id, pieza_refaccion, estado, proveedor_id FROM piezas")
    piezas = cursor.fetchall()
    if piezas:
        for pieza in piezas:
            print(f"   ID: {pieza[0]}, Cita ID: {pieza[1]}, Pieza: {pieza[2]}, Estado: {pieza[3]}, Proveedor ID: {pieza[4]}")
    else:
        print("   No hay piezas registradas")
    
    # Verificar proveedores
    print("\n3. PROVEEDORES:")
    cursor.execute("SELECT id, nombre FROM proveedores")
    proveedores = cursor.fetchall()
    if proveedores:
        for prov in proveedores:
            print(f"   ID: {prov[0]}, Nombre: {prov[1]}")
    else:
        print("   No hay proveedores registrados")
    
    # Verificar clientes
    print("\n4. CLIENTES:")
    cursor.execute("SELECT id, nombre FROM clientes")
    clientes = cursor.fetchall()
    if clientes:
        for cliente in clientes:
            print(f"   ID: {cliente[0]}, Nombre: {cliente[1]}")
    else:
        print("   No hay clientes registrados")
    
    # Verificar autos
    print("\n5. AUTOS:")
    cursor.execute("SELECT id, marca, modelo, placas, cliente_id FROM autos")
    autos = cursor.fetchall()
    if autos:
        for auto in autos:
            print(f"   ID: {auto[0]}, {auto[1]} {auto[2]}, Placas: {auto[3]}, Cliente ID: {auto[4]}")
    else:
        print("   No hay autos registrados")
    
    print("\n" + "=" * 60)
    
    conn.close()

if __name__ == "__main__":
    verificar_datos()
