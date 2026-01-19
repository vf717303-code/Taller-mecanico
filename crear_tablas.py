import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ---------------- TABLA CLIENTES ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    correo TEXT
);
""")

# ---------------- TABLA AUTOS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS autos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    marca TEXT,
    modelo TEXT,
    placas TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);
""")

# ---------------- TABLA CITAS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS citas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auto_id INTEGER NOT NULL,
    fecha TEXT,
    servicio TEXT,
    estado TEXT,
    FOREIGN KEY (auto_id) REFERENCES autos(id)
);
""")
#----------------CONTRASEÑAS----------------
cursor.execute("ALTER TABLE clientes ADD COLUMN password TEXT")

conn.commit()
conn.close()

print("Columna password agregada correctamente")

print("Base de datos creada correctamente (clientes, autos y citas)")
