"""Test the reset character command."""

from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from typeclasses.characters import Character
from commands.reset import CmdResetChar


class TestResetCommand(EvenniaTest):
    """Test the resetchar command."""

    def setUp(self):
        super().setUp()
        self.char = self.char1
        self.room = self.room1

        # Create the command
        self.reset_cmd = CmdResetChar()

    def test_reset_alive_character(self):
        """Test that resetchar works on an alive character."""
        # Set some survival stats
        self.char.hunger = 50
        self.char.thirst = 75
        self.char.tiredness = 25
        self.char.is_resting = True

        # Set threshold message levels
        self.char.ndb.hunger_msg_level = 2
        self.char.ndb.thirst_msg_level = 3
        self.char.ndb.tiredness_msg_level = 1

        # Verify character is alive
        self.assertTrue(self.char.is_living())
        self.assertFalse(self.char.is_dead())

                # Execute reset command
        self.reset_cmd.caller = self.char
        self.reset_cmd.func()

        # Wait a moment for metabolism script to potentially run
        import time
        time.sleep(0.1)

        # Verify stats are reset (allow for small metabolism increases)
        self.assertLessEqual(self.char.hunger, 1.0)  # Allow for metabolism tick
        self.assertLessEqual(self.char.thirst, 1.0)  # Allow for metabolism tick
        self.assertLessEqual(self.char.tiredness, 1.0)  # Allow for metabolism tick
        self.assertFalse(self.char.is_resting)

        # Verify threshold message levels are cleared
        self.assertEqual(self.char.ndb.hunger_msg_level, 0)
        self.assertEqual(self.char.ndb.thirst_msg_level, 0)
        self.assertEqual(self.char.ndb.tiredness_msg_level, 0)

        # Verify character is still alive
        self.assertTrue(self.char.is_living())
        self.assertFalse(self.char.is_dead())

    def test_reset_dead_character(self):
        """Test that resetchar revives a dead character."""
        # Kill the character first
        self.char.at_death()
        self.assertFalse(self.char.is_living())
        self.assertTrue(self.char.is_dead())

        # Wait a moment for any metabolism scripts to stop
        import time
        time.sleep(0.1)

        # Verify metabolism script is stopped
        metabolism_scripts = self.char.scripts.get("metabolism_script")
        self.assertEqual(len(metabolism_scripts), 0)

        # Set some survival stats (should be ignored since dead)
        self.char.hunger = 100
        self.char.thirst = 100
        self.char.tiredness = 100

        # Execute reset command
        self.reset_cmd.caller = self.char
        self.reset_cmd.func()

        # Verify character is revived
        self.assertTrue(self.char.is_living())
        self.assertFalse(self.char.is_dead())

        # Wait a moment for metabolism script to potentially run
        time.sleep(0.1)

        # Verify stats are reset (allow for small metabolism increases)
        self.assertLessEqual(self.char.hunger, 1.0)  # Allow for metabolism tick
        self.assertLessEqual(self.char.thirst, 1.0)  # Allow for metabolism tick
        self.assertLessEqual(self.char.tiredness, 1.0)  # Allow for metabolism tick
        self.assertFalse(self.char.is_resting)

        # Verify threshold message levels are cleared
        self.assertEqual(self.char.ndb.hunger_msg_level, 0)
        self.assertEqual(self.char.ndb.thirst_msg_level, 0)
        self.assertEqual(self.char.ndb.tiredness_msg_level, 0)

        # Verify metabolism script is running
        metabolism_scripts = self.char.scripts.get("metabolism_script")
        self.assertTrue(len(metabolism_scripts) > 0)

        # Verify command sets are correct (alive cmdset should be present)
        from commands.default_cmdsets import AliveCmdSet
        alive_cmdsets = [cmdset for cmdset in self.char.cmdset.all() if isinstance(cmdset, AliveCmdSet)]
        self.assertTrue(len(alive_cmdsets) > 0)

    def test_reset_character_with_high_stats(self):
        """Test that resetchar works with maximum survival stats."""
        # Set maximum survival stats
        self.char.hunger = 100
        self.char.thirst = 100
        self.char.tiredness = 100
        self.char.is_resting = True

        # Set maximum threshold message levels
        self.char.ndb.hunger_msg_level = 3
        self.char.ndb.thirst_msg_level = 3
        self.char.ndb.tiredness_msg_level = 3

                # Execute reset command
        self.reset_cmd.caller = self.char
        self.reset_cmd.func()

        # Wait a moment for metabolism script to potentially run
        import time
        time.sleep(0.1)

        # Verify all stats are reset (allow for small metabolism increases)
        self.assertLessEqual(self.char.hunger, 1.0)  # Allow for metabolism tick
        self.assertLessEqual(self.char.thirst, 1.0)  # Allow for metabolism tick
        self.assertLessEqual(self.char.tiredness, 1.0)  # Allow for metabolism tick
        self.assertFalse(self.char.is_resting)

        # Verify threshold message levels are cleared
        self.assertEqual(self.char.ndb.hunger_msg_level, 0)
        self.assertEqual(self.char.ndb.thirst_msg_level, 0)
        self.assertEqual(self.char.ndb.tiredness_msg_level, 0)

    def test_reset_character_tags(self):
        """Test that resetchar preserves the living_being tag."""
        # Verify character has living_being tag
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))

        # Kill the character
        self.char.at_death()
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))
        self.assertTrue(self.char.tags.has("dead", category="living_state"))

        # Execute reset command
        self.reset_cmd.caller = self.char
        self.reset_cmd.func()

        # Verify living_being tag is preserved, dead tag is removed
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))
        self.assertFalse(self.char.tags.has("dead", category="living_state"))

        # Verify character is alive
        self.assertTrue(self.char.is_living())
        self.assertFalse(self.char.is_dead())
