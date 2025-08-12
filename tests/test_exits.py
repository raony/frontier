from evennia.utils.test_resources import EvenniaTest
from typeclasses.exits import EasyExit, HardExit


class TestEasyHardExit(EvenniaTest):
    def test_easy_exit_tiredness(self):
        exit_obj, errors = EasyExit.create("easy", self.room1, self.room2, account=self.account)
        self.assertFalse(errors)
        start = self.char1.tiredness or 0
        exit_obj.at_traverse(self.char1, exit_obj.destination)
        self.assertEqual(self.char1.location, self.room2)
        self.assertEqual(self.char1.tiredness, start + 10)

    def test_hard_exit_tiredness(self):
        exit_obj, errors = HardExit.create("hard", self.room1, self.room2, account=self.account)
        self.assertFalse(errors)
        start = self.char1.tiredness or 0
        exit_obj.at_traverse(self.char1, exit_obj.destination)
        self.assertEqual(self.char1.location, self.room2)
        self.assertEqual(self.char1.tiredness, start + 30)
