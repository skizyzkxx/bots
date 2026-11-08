import tempfile
import unittest
from pathlib import Path
from domain import Reminders

class ReminderTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'test.sqlite3'
        self.db=Reminders(self.path)
    def tearDown(self): self.temp.cleanup()
    def test_schedule_waits_until_due_and_is_claimed_once(self):
        number=self.db.create(1,2,3,'Estudar',1,now=100)
        self.assertIsNone(self.db.claim(now=159))
        self.assertEqual(self.db.claim(now=160)['id'],number)
        self.assertIsNone(self.db.claim(now=161))
        self.db.finish(number,True,now=161)
        self.assertEqual(self.db.list(1,3),[])
    def test_cancel_checks_owner_and_guild(self):
        number=self.db.create(1,2,3,'Estudar',1,now=100)
        self.assertFalse(self.db.cancel(1,9,number))
        self.assertFalse(self.db.cancel(9,3,number))
        self.assertTrue(self.db.cancel(1,3,number))
        self.assertIsNone(self.db.claim(now=1000))
    def test_persistence_and_recovery_after_crash(self):
        self.db.create(1,2,3,'Estudar',1,now=100)
        first=self.db.claim(now=160)
        reopened=Reminders(self.path)
        self.assertIsNone(reopened.claim(now=459))
        self.assertEqual(reopened.claim(now=460)['id'],first['id'])
    def test_retry_backoff_and_failure_limit(self):
        number=self.db.create(1,2,3,'Estudar',1,now=100)
        now=160
        for attempt in range(1,6):
            self.assertIsNotNone(self.db.claim(now=now))
            self.db.finish(number,False,now=now)
            self.assertIsNone(self.db.claim(now=now+1))
            now += 60*attempt
        self.assertEqual(self.db.list(1,3),[])
        self.assertIsNone(self.db.claim(now=10000))
    def test_limits(self):
        with self.assertRaises(ValueError): self.db.create(1,2,3,'',1)
        with self.assertRaises(ValueError): self.db.create(1,2,3,'x',0)
        for _ in range(20): self.db.create(1,2,3,'Teste',1)
        with self.assertRaises(ValueError): self.db.create(1,2,3,'Extra',1)
