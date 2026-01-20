import sqlite3

def agregar_datos_prueba():
    """Agregar cliente y auto de prueba a la BD"""
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    
    try:
        # Agregar cliente
        cur.execute("""
        INSERT OR IGNORE INTO clientes (id, nombre, telefono, correo, password)
        VALUES (1, 'cliente', '3001234567', 'cliente@email.com', '1234')
        """)
        
        # Agregar auto para el cliente
        cur.execute("""
        INSERT OR IGNORE INTO autos (id, cliente_id, marca, modelo, placas)
        VALUES (1, 1, 'Toyota', 'Corolla', 'ABC123')
        """)
        
        conn.commit()
        print("✓ Datos de prueba agregados:")
        print("  Usuario: cliente")
        print("  Contraseña: 1234")
        print("  Auto: Toyota Corolla (ABC123)")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    agregar_datos_prueba()
