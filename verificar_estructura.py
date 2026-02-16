from db import conectar_db

def verificar_estructura():
    """Verifica la estructura de las tablas"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("ESTRUCTURA DE LAS TABLAS")
    print("=" * 60)
    
    # Ver estructura de piezas
    print("\nTabla PIEZAS:")
    cursor.execute("PRAGMA table_info(piezas)")
    columnas = cursor.fetchall()
    for col in columnas:
        print(f"   {col[1]} ({col[2]})")
    
    # Ver datos de piezas
    print("\nDatos en PIEZAS:")
    cursor.execute("SELECT * FROM piezas LIMIT 5")
    piezas = cursor.fetchall()
    for pieza in piezas:
        print(f"   {pieza}")
    
    # Ver estructura de proveedores
    print("\nTabla PROVEEDORES:")
    cursor.execute("PRAGMA table_info(proveedores)")
    columnas = cursor.fetchall()
    for col in columnas:
        print(f"   {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    verificar_estructura()
