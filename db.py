import sqlite3
import os
import sys
import shutil

from utils import app_dir

def get_db_path():
    # Usar siempre la base de datos en OneDrive/taller_mecanico_db/database
    db_path = r"C:/Users/vf717/OneDrive/taller_mecanico_db/database"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No se encontró la base de datos en {db_path}.\nAsegúrate de que el archivo existe y contiene tus datos.")
    return db_path


def conectar_db():
    conn = sqlite3.connect(get_db_path(), timeout=15.0)
    conn.execute("PRAGMA journal_mode=WAL")  # Modo WAL para mejor concurrencia
    return conn
