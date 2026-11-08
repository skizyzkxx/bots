import tempfile
import unittest
from pathlib import Path
from domain import Suggestions

class SuggestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/'test.sqlite3'
        self.db = Suggestions(self.path)
        self.number = self.db.create(1,10,'Um canal para estudos')
    def tearDown(self): self.temp.cleanup()
    def test_vote_is_unique_and_can_change(self):
        self.db.vote(1,self.number,20,1)
        self.db.vote(1,self.number,20,1)
        self.assertEqual(self.db.get(1,self.number)['yes'],1)
        self.db.vote(1,self.number,20,-1)
        row = self.db.get(1,self.number)
        self.assertEqual((row['yes'],row['no']),(0,1))
    def test_closed_suggestion_rejects_votes(self):
        self.assertTrue(self.db.decide(1,self.number,'aprovada'))
        self.assertFalse(self.db.vote(1,self.number,20,1))
        self.assertFalse(self.db.decide(1,self.number,'recusada'))
    def test_guild_isolation(self):
        self.assertIsNone(self.db.get(2,self.number))
        self.assertFalse(self.db.vote(2,self.number,20,1))
        self.assertFalse(self.db.decide(2,self.number,'aprovada'))
    def test_persistence_and_validation(self):
        self.assertEqual(Suggestions(self.path).get(1,self.number)['text'],'Um canal para estudos')
        with self.assertRaises(ValueError): self.db.create(1,10,'    ')
        with self.assertRaises(ValueError): self.db.vote(1,self.number,20,0)
