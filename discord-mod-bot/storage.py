import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, path, schema):
        self.path = str(path)
        with self.connect() as db:
            db.executescript(schema)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()
