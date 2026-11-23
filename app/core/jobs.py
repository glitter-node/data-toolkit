
import json
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from app.core.config import settings

LOCK = threading.Lock()

def database():
    folder = settings.data_dir
    folder.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(folder / "jobs.sqlite3", timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, state TEXT NOT NULL, filename TEXT, error TEXT, created REAL NOT NULL, updated REAL NOT NULL)")
    columns = {row[1] for row in db.execute("PRAGMA table_info(jobs)")}
    for name, definition in {"progress": "INTEGER NOT NULL DEFAULT 0", "result_size": "INTEGER", "finished": "REAL"}.items():
        if name not in columns:
            db.execute(f"ALTER TABLE jobs ADD COLUMN {name} {definition}")
    db.commit()
    return db

def create(filename):
    import hashlib
    job_id = secrets.token_hex(16)
    token = secrets.token_urlsafe(32)
    now = time.time()
    with LOCK, database() as db:
        db.execute("INSERT INTO jobs (id, token_hash, state, filename, error, created, updated) VALUES (?,?,?,?,?,?,?)", (job_id, hashlib.sha256(token.encode()).hexdigest(), "queued", filename, None, now, now))
    return job_id, token

def get(job_id, token):
    import hashlib
    with database() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if row is None or not token or not secrets.compare_digest(row["token_hash"], hashlib.sha256(token.encode()).hexdigest()):
        return None
    return dict(row)

def transition(job_id, old, new):
    with LOCK, database() as db:
        cursor = db.execute("UPDATE jobs SET state=?, progress=CASE WHEN ?='completed' THEN 100 WHEN ?='running' THEN MAX(progress,10) ELSE progress END, finished=CASE WHEN ? IN ('completed','failed','cancelled') THEN ? ELSE finished END, updated=? WHERE id=? AND state=?", (new, new, new, new, time.time(), time.time(), job_id, old))
        return cursor.rowcount == 1

def update(job_id, state, error=None):
    with LOCK, database() as db:
        db.execute("UPDATE jobs SET state=?, error=?, finished=CASE WHEN ? IN ('completed','failed','cancelled') THEN ? ELSE finished END, updated=? WHERE id=?", (state, error, state, time.time(), time.time(), job_id))

def recover():
    with LOCK, database() as db:
        db.execute("UPDATE jobs SET state='failed', error='Interrupted by server restart', finished=?, updated=? WHERE state IN ('queued','running')", (time.time(), time.time()))

def progress(job_id, value):
    with LOCK, database() as db:
        db.execute("UPDATE jobs SET progress=?, updated=? WHERE id=? AND state='running'", (max(0, min(99, int(value))), time.time(), job_id))

def result_size(job_id, size):
    with LOCK, database() as db:
        db.execute("UPDATE jobs SET result_size=?, updated=? WHERE id=? AND state='running'", (size, time.time(), job_id))

def delete(job_id, token):
    with LOCK, database() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        import hashlib
        if row is None or not token or not secrets.compare_digest(row["token_hash"], hashlib.sha256(token.encode()).hexdigest()):
            return None
        if row["state"] in ("queued", "running"):
            return False
        db.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    (settings.data_dir / "output" / (job_id + ".bin")).unlink(missing_ok=True)
    (settings.data_dir / "output" / (job_id + ".tmp")).unlink(missing_ok=True)
    return True

def cleanup():
    cutoff = time.time() - settings.job_ttl_seconds
    with LOCK, database() as db:
        expired = db.execute("SELECT id FROM jobs WHERE COALESCE(finished,created) < ? AND state IN ('completed','failed','cancelled')", (cutoff,)).fetchall()
        db.execute("DELETE FROM jobs WHERE COALESCE(finished,created) < ? AND state IN ('completed','failed','cancelled')", (cutoff,))
    for row in expired:
        path = settings.data_dir / "output" / (row["id"] + ".bin")
        path.unlink(missing_ok=True)
        (settings.data_dir / "output" / (row["id"] + ".tmp")).unlink(missing_ok=True)
