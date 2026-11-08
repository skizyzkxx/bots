import time
from storage import Database

class Warnings(Database):
    def __init__(self, path):
        super().__init__(path, '''CREATE TABLE IF NOT EXISTS warnings(
            id INTEGER PRIMARY KEY, guild INTEGER NOT NULL, member INTEGER NOT NULL,
            moderator INTEGER NOT NULL, reason TEXT NOT NULL, created REAL NOT NULL,
            removed INTEGER NOT NULL DEFAULT 0);
            CREATE INDEX IF NOT EXISTS member_warnings ON warnings(guild,member,removed);''')

    def add(self, guild, member, moderator, reason):
        reason = reason.strip()
        if not 1 <= len(reason) <= 400:
            raise ValueError('O motivo deve ter entre 1 e 400 caracteres.')
        with self.connect() as db:
            return db.execute('INSERT INTO warnings(guild,member,moderator,reason,created) VALUES(?,?,?,?,?)',
                              (guild, member, moderator, reason, time.time())).lastrowid

    def list(self, guild, member):
        with self.connect() as db:
            return db.execute('SELECT * FROM warnings WHERE guild=? AND member=? AND removed=0 ORDER BY id DESC LIMIT 10', (guild, member)).fetchall()

    def remove(self, guild, warning_id):
        with self.connect() as db:
            return db.execute('UPDATE warnings SET removed=1 WHERE guild=? AND id=? AND removed=0', (guild, warning_id)).rowcount == 1

def can_target(actor_id, actor_rank, target_id, target_rank, owner_id, bot_rank, target_is_bot=False):
    if actor_id == target_id or target_id == owner_id or target_is_bot:
        return False
    return bot_rank > target_rank and (actor_id == owner_id or actor_rank > target_rank)
