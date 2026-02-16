import sqlite3

try:
    conn = sqlite3.connect("database.db")  # usa el nombre real de tu BD
    cursor = conn.cursor()

    cursor.execute("""
        ALTER TABLE citas
        ADD COLUMN mecanico_id INTEGER
    """)

    conn.commit()
    conn.close()

    print("✅ Columna 'mecanico_id' agregada correctamente a la tabla citas")

except sqlite3.OperationalError as e:
    print("⚠️ Error:", e)

