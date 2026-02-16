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
            hora TEXT,
            servicio TEXT,
            estado TEXT,
            origen TEXT,
            mecanico_id INTEGER,
            FOREIGN KEY (auto_id) REFERENCES autos(id),
            FOREIGN KEY (mecanico_id) REFERENCES empleados(id)
        )
        """)
        
        # Tabla proveedores
        cur.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            telefono TEXT,
            correo TEXT,
            direccion TEXT,
            ruc TEXT
        )
        """)
        
        # Tabla piezas (pedidos)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS piezas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id INTEGER NOT NULL,
            auto_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            servicio TEXT,
            pieza_refaccion TEXT,
            fecha TEXT,
            estado TEXT DEFAULT 'Pendiente',
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
            FOREIGN KEY (auto_id) REFERENCES autos(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
        """)
        
        conn.commit()
        print("✓ Base de datos inicializada correctamente")
        
        # Agregar columna hora a tabla citas si no existe (para tablas existentes)
        try:
            cur.execute("ALTER TABLE citas ADD COLUMN hora TEXT")
            conn.commit()
            print("✓ Columna 'hora' agregada a tabla citas")
        except Exception as e:
            print(f"Nota: Columna 'hora' ya existe o no se puede agregar: {e}")
        
        # Agregar columna costo a tabla piezas si no existe
        try:
            cur.execute("ALTER TABLE piezas ADD COLUMN costo REAL DEFAULT 0")
            conn.commit()
            print("✓ Columna 'costo' agregada a tabla piezas")
        except Exception as e:
            print(f"Nota: Columna 'costo' ya existe o no se puede agregar: {e}")
        
        # Agregar columna mecanico_id a tabla citas si no existe
        try:
            cur.execute("ALTER TABLE citas ADD COLUMN mecanico_id INTEGER")
            conn.commit()
            print("✓ Columna 'mecanico_id' agregada a tabla citas")
        except Exception as e:
            print(f"Nota: Columna 'mecanico_id' ya existe o no se puede agregar: {e}")
        
        # Agregar columna origen a tabla citas si no existe
        try:
            cur.execute("ALTER TABLE citas ADD COLUMN origen TEXT DEFAULT 'cliente'")
            conn.commit()
            print("✓ Columna 'origen' agregada a tabla citas")
        except Exception as e:
            print(f"Nota: Columna 'origen' ya existe o no se puede agregar: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inicializar_db()
