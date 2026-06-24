import sqlite3
from contextlib import contextmanager
from typing import Generator

from .config import settings


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sistema_config (
                id TEXT PRIMARY KEY,
                valor_cifrado BLOB NOT NULL,
                iv BLOB NOT NULL,
                tag BLOB NOT NULL,
                actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS libros (
                id TEXT PRIMARY KEY,
                titulo_libro TEXT NOT NULL,
                nombre_archivo_original TEXT NOT NULL,
                ruta_local TEXT,
                total_capitulos INTEGER DEFAULT 0,
                fecha_procesado DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS capitulos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libro_id TEXT NOT NULL REFERENCES libros(id) ON DELETE CASCADE,
                numero_capitulo INTEGER NOT NULL,
                titulo_capitulo TEXT,
                pagina_inicio INTEGER,
                pagina_fin INTEGER,
                ruta_archivo_corto TEXT,
                gdrive_file_id TEXT
            );
        """)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
