import tempfile
import unittest
from pathlib import Path
from domain import Warnings, can_target

class ModerationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/'test.sqlite3'
        self.db = Warnings(self.path)
    def tearDown(self):
        self.temp.cleanup()
    def test_warning_survives_reopen_and_is_scoped(self):
        self.db.add(1,2,3,'Spam')
        self.assertEqual(len(Warnings(self.path).list(1,2)),1)
        self.assertEqual(self.db.list(9,2),[])
    def test_remove_cannot_cross_guilds(self):
        number = self.db.add(1,2,3,'Flood')
        self.assertFalse(self.db.remove(2,number))
        self.assertTrue(self.db.remove(1,number))
        self.assertFalse(self.db.remove(1,number))
        self.assertEqual(self.db.list(1,2),[])
    def test_empty_reason_is_rejected(self):
        with self.assertRaises(ValueError): self.db.add(1,2,3,'  ')
    def test_equal_rank_and_owner_are_protected(self):
        self.assertFalse(can_target(1,5,2,5,9,10))
        self.assertFalse(can_target(1,5,9,1,9,10))
        self.assertFalse(can_target(1,5,1,1,9,10))
        self.assertFalse(can_target(1,5,2,1,9,1))
        self.assertTrue(can_target(1,5,2,1,9,10))
        self.assertTrue(can_target(9,1,2,5,9,10))
        self.assertFalse(can_target(1,5,2,1,9,10,True))
