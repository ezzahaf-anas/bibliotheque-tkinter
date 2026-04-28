import sqlite3
def connect():
    return sqlite3.connect("biblio.db")
def create_tables():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS livres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT,
        auteur TEXT,
        genre TEXT,
        annee INTEGER,
        stock INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS membres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prenom TEXT,
        email TEXT,
        numero TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emprunts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livre_id INTEGER,
        membre_id INTEGER,
        date_emprunt TEXT,
        date_retour TEXT
    )
    """)
    conn.commit()
    conn.close()