import time
from storage import Database

class Reminders(Database):
    def __init__(self,path):
        super().__init__(path, '''CREATE TABLE IF NOT EXISTS reminders(
            id INTEGER PRIMARY KEY, guild INTEGER NOT NULL, channel INTEGER NOT NULL,
            author INTEGER NOT NULL, text TEXT NOT NULL, due REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
            retry_at REAL NOT NULL DEFAULT 0, leased REAL NOT NULL DEFAULT 0);
            CREATE INDEX IF NOT EXISTS due_reminders ON reminders(status,due,retry_at);''')

    def create(self,guild,channel,author,text,minutes,now=None):
        text=text.strip()
        if not 1 <= len(text) <= 500 or not 1 <= minutes <= 43200:
            raise ValueError('Use texto de 1 a 500 caracteres e prazo entre 1 minuto e 30 dias.')
        now=time.time() if now is None else now
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            count=db.execute("SELECT COUNT(*) FROM reminders WHERE guild=? AND author=? AND status IN('pending','sending')",(guild,author)).fetchone()[0]
            if count >= 20: raise ValueError('Você já tem 20 lembretes ativos neste servidor.')
            return db.execute('INSERT INTO reminders(guild,channel,author,text,due) VALUES(?,?,?,?,?)',(guild,channel,author,text,now+minutes*60)).lastrowid

    def list(self,guild,author):
        with self.connect() as db:
            return db.execute("SELECT * FROM reminders WHERE guild=? AND author=? AND status IN('pending','sending') ORDER BY due",(guild,author)).fetchall()

    def cancel(self,guild,author,number):
        with self.connect() as db:
            return db.execute("UPDATE reminders SET status='cancelled' WHERE guild=? AND author=? AND id=? AND status='pending'",(guild,author,number)).rowcount==1

    def claim(self,now=None):
        now=time.time() if now is None else now
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute("""SELECT * FROM reminders WHERE
                (status='pending' AND due<=? AND retry_at<=?) OR
                (status='sending' AND leased<=?) ORDER BY due LIMIT 1""",(now,now,now-300)).fetchone()
            if not row: return None
            db.execute("UPDATE reminders SET status='sending',leased=? WHERE id=?",(now,row['id']))
            return row

    def finish(self,number,success,now=None,permanent=False):
        now=time.time() if now is None else now
        with self.connect() as db:
            row=db.execute("SELECT attempts FROM reminders WHERE id=? AND status='sending'",(number,)).fetchone()
            if not row: return
            attempts=row['attempts']+1
            status='sent' if success else ('failed' if permanent or attempts>=5 else 'pending')
            db.execute('UPDATE reminders SET status=?,attempts=?,retry_at=? WHERE id=?',(status,attempts,now+60*attempts,number))
