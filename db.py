import sqlite3

def conectar_db():
    return sqlite3.connect("database.db")
