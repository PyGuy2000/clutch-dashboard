import os
import sqlite3
import time

from config import Config


def get_db(db_name):
    """Open a read-only SQLite connection. Returns None if the DB file is missing."""
    path = Config.db_path(db_name)
    if not os.path.exists(path):
        return None
    conn = sqlite3.connect(f"file:{path}?mode=ro&nolock=1&immutable=1", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(db_name, sql, params=(), one=False):
    """Run a read-only query and return results as dicts. Returns [] on missing DB."""
    conn = get_db(db_name)
    if conn is None:
        return {} if one else []
    try:
        cur = conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        return rows[0] if one and rows else ({} if one else rows)
    finally:
        conn.close()


def query_scalar(db_name, sql, params=(), default=0):
    """Run a query returning a single scalar value."""
    conn = get_db(db_name)
    if conn is None:
        return default
    try:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else default
    finally:
        conn.close()


def get_data_freshness():
    """Return minutes since newest DB file in data dir was modified."""
    data_dir = Config.DB_BASE_PATH
    if not os.path.exists(data_dir):
        return None
    mtimes = []
    for f in os.listdir(data_dir):
        if f.endswith(".db"):
            try:
                mtimes.append(os.path.getmtime(os.path.join(data_dir, f)))
            except OSError:
                pass
    if not mtimes:
        return None
    return int((time.time() - max(mtimes)) / 60)
