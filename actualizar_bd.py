import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE citas ADD COLUMN origen TEXT DEFAULT 'EMPLEADO'")
    print("Columna 'origen' agregada correctamente")
except:
    print("La columna 'origen' ya existe")

conn.commit()
conn.close()
