import sqlite3
import os

def conectar_db():
    # Usar ruta absoluta para evitar problemas de directorios
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "database.db")
    return sqlite3.connect(db_path)
