import sqlite3

def inicializar_db():
    """Crear la base de datos y tablas si no existen"""
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    
    try:
        # Tabla clientes
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            telefono TEXT,
            correo TEXT,
            password TEXT NOT NULL
        )
        """)
        
        # Tabla autos
        cur.execute("""
        CREATE TABLE IF NOT EXISTS autos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            marca TEXT,
            modelo TEXT,
            placas TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
        """)
        
        # Tabla citas
        cur.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auto_id INTEGER NOT NULL,
            fecha TEXT,
            servicio TEXT,
            estado TEXT,
            FOREIGN KEY (auto_id) REFERENCES autos(id)
        )
        """)
        
        conn.commit()
        print("✓ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inicializar_db()
