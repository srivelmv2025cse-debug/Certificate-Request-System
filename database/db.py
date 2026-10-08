import os
import sqlite3
from flask import g, current_app
from config import Config

def get_db_connection(db_path=None):
    """
    Returns a connection to the SQLite database.
    Enables foreign keys and returns rows as dictionaries/sqlite3.Row objects.
    """
    if db_path is None:
        try:
            db_path = current_app.config.get("DATABASE_PATH", Config.DATABASE_PATH)
        except RuntimeError:
            db_path = Config.DATABASE_PATH

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    """
    Flask request context database connection provider.
    """
    if "db" not in g:
        g.db = get_db_connection()
    return g.db

def close_db(e=None):
    """
    Closes the request context database connection if open.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(db_path=None):
    """
    Initializes database schema from schema.sql.
    """
    conn = get_db_connection(db_path)
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
