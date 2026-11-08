import time
from storage import Database

class Suggestions(Database):
    def __init__(self, path):
        super().__init__(path, '''CREATE TABLE IF NOT EXISTS suggestions(
            id INTEGER PRIMARY KEY, guild INTEGER NOT NULL, author INTEGER NOT NULL,
            text TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'aberta', created REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS votes(
            suggestion INTEGER NOT NULL REFERENCES suggestions(id), voter INTEGER NOT NULL,
            value INTEGER NOT NULL CHECK(value IN(-1,1)), PRIMARY KEY(suggestion,voter));''')

    def create(self, guild, author, text):
        text = text.strip()
        if not 5 <= len(text) <= 1000:
            raise ValueError('A sugestão deve ter entre 5 e 1000 caracteres.')
        with self.connect() as db:
            return db.execute('INSERT INTO suggestions(guild,author,text,created) VALUES(?,?,?,?)',
                              (guild,author,text,time.time())).lastrowid

    def get(self, guild, number):
        with self.connect() as db:
            return db.execute('''SELECT s.*, COALESCE(SUM(v.value=1),0) AS yes,
                COALESCE(SUM(v.value=-1),0) AS no FROM suggestions s
                LEFT JOIN votes v ON s.id=v.suggestion
                WHERE s.guild=? AND s.id=? GROUP BY s.id''',(guild,number)).fetchone()

    def vote(self, guild, number, voter, value):
        if value not in (-1,1): raise ValueError('Voto inválido.')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT status FROM suggestions WHERE guild=? AND id=?',(guild,number)).fetchone()
            if not row or row['status'] != 'aberta':
                return False
            db.execute('''INSERT INTO votes VALUES(?,?,?) ON CONFLICT(suggestion,voter)
                DO UPDATE SET value=excluded.value''',(number,voter,value))
            return True

    def decide(self, guild, number, status):
        if status not in ('aprovada','recusada'): raise ValueError('Status inválido.')
        with self.connect() as db:
            return db.execute("UPDATE suggestions SET status=? WHERE guild=? AND id=? AND status='aberta'",(status,guild,number)).rowcount == 1
