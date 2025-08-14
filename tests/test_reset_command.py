from evennia.utils.test_resources import EvenniaTest
from commands.reset import CmdResetChar
from commands.dead_cmdset import DeadCmdSet


class TestResetCommand(EvenniaTest):
    def test_resetchar_resets_and_revives(self):
        # Put character in a bad state
        self.char1.hunger = 50
        self.char1.thirst = 80
        self.char1.tiredness = 30
        self.char1.is_dead = True
        self.char1.is_living = False
        self.char1.is_resting = True
        self.char1.cmdset.add(DeadCmdSet, persistent=True)

        # Execute the command via the command handler
        self.char1.execute_cmd("resetchar")

        # Assert all reset
        self.assertEqual(self.char1.hunger, 0)
        self.assertEqual(self.char1.thirst, 0)
        self.assertEqual(self.char1.tiredness, 0)
        self.assertFalse(self.char1.is_dead)
        self.assertTrue(self.char1.is_living)
        self.assertFalse(self.char1.is_resting)

        # Dead cmdset should be removed
        self.assertFalse(any(cs.key == "DeadCmdSet" for cs in self.char1.cmdset.current))
