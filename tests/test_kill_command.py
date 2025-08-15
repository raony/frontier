"""Test the kill and revive commands."""

from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from typeclasses.characters import Character
from commands.kill import CmdKill, CmdRevive


class TestKillCommand(EvenniaTest):
    """Test the @kill and @revive commands."""

    def setUp(self):
        super().setUp()
        self.char = self.char1
        self.room = self.room1

        # Create a test character to kill
        self.test_char = create_object(Character, key="TestChar", location=self.room)

        # Create the commands
        self.kill_cmd = CmdKill()
        self.revive_cmd = CmdRevive()

    def test_kill_command(self):
        """Test that @kill properly sets a character to dead."""
        # Verify character starts alive
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

        # Execute kill command
        self.kill_cmd.caller = self.char
        self.kill_cmd.args = "TestChar"
        self.kill_cmd.func()

        # Verify character is now dead
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

        # Verify tags are correct
        self.assertTrue(self.test_char.tags.has("living_being", category="living_state"))
        self.assertTrue(self.test_char.tags.has("dead", category="living_state"))

    def test_kill_self(self):
        """Test that @kill works with 'self' target."""
        # Verify character starts alive
        self.assertTrue(self.char.is_living())
        self.assertFalse(self.char.is_dead())

        # Execute kill command on self
        self.kill_cmd.caller = self.char
        self.kill_cmd.args = "self"
        self.kill_cmd.func()

        # Verify character is now dead
        self.assertFalse(self.char.is_living())
        self.assertTrue(self.char.is_dead())

    def test_kill_me(self):
        """Test that @kill works with 'me' target."""
        # Create another character to test with
        other_char = create_object(Character, key="OtherChar", location=self.room)
        self.assertTrue(other_char.is_living())

        # Execute kill command on self using 'me'
        self.kill_cmd.caller = other_char
        self.kill_cmd.args = "me"
        self.kill_cmd.func()

        # Verify character is now dead
        self.assertFalse(other_char.is_living())
        self.assertTrue(other_char.is_dead())

    def test_kill_dbref(self):
        """Test that @kill works with database reference."""
        # Verify character starts alive
        self.assertTrue(self.test_char.is_living())

        # Execute kill command using dbref
        self.kill_cmd.caller = self.char
        self.kill_cmd.args = f"#{self.test_char.id}"
        self.kill_cmd.func()

        # Verify character is now dead
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

    def test_kill_full_death_process(self):
        """Test that @kill triggers the full death process."""
        # Verify character starts alive with metabolism
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

        # Start metabolism script
        self.test_char.start_metabolism_script()
        metabolism_scripts = self.test_char.scripts.get("metabolism_script")
        self.assertTrue(len(metabolism_scripts) > 0)

        # Execute kill command
        self.kill_cmd.caller = self.char
        self.kill_cmd.args = "TestChar"
        self.kill_cmd.func()

        # Verify character is dead
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

        # Verify metabolism script is stopped
        metabolism_scripts = self.test_char.scripts.get("metabolism_script")
        self.assertEqual(len(metabolism_scripts), 0)

        # Verify command sets are updated (dead cmdset should be present)
        from commands.dead_cmdset import DeadCmdSet
        dead_cmdsets = [cmdset for cmdset in self.test_char.cmdset.all() if isinstance(cmdset, DeadCmdSet)]
        self.assertTrue(len(dead_cmdsets) > 0)

    def test_revive_command(self):
        """Test that @revive properly sets a character back to alive."""
        # First kill the character
        self.test_char.set_living_state(False)
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

        # Execute revive command
        self.revive_cmd.caller = self.char
        self.revive_cmd.args = "TestChar"
        self.revive_cmd.func()

        # Verify character is now alive
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

        # Verify tags are correct
        self.assertTrue(self.test_char.tags.has("living_being", category="living_state"))
        self.assertFalse(self.test_char.tags.has("dead", category="living_state"))

    def test_revive_self(self):
        """Test that @revive works with 'self' target."""
        # First kill the character
        self.char.set_living_state(False)
        self.assertFalse(self.char.is_living())

        # Execute revive command on self
        self.revive_cmd.caller = self.char
        self.revive_cmd.args = "self"
        self.revive_cmd.func()

        # Verify character is now alive
        self.assertTrue(self.char.is_living())
        self.assertFalse(self.char.is_dead())

    def test_revive_me(self):
        """Test that @revive works with 'me' target."""
        # Create another character to test with
        other_char = create_object(Character, key="OtherChar", location=self.room)
        other_char.set_living_state(False)
        self.assertFalse(other_char.is_living())

        # Execute revive command on self using 'me'
        self.revive_cmd.caller = other_char
        self.revive_cmd.args = "me"
        self.revive_cmd.func()

        # Verify character is now alive
        self.assertTrue(other_char.is_living())
        self.assertFalse(other_char.is_dead())

    def test_revive_dbref(self):
        """Test that @revive works with database reference."""
        # First kill the character
        self.test_char.set_living_state(False)
        self.assertFalse(self.test_char.is_living())

        # Execute revive command using dbref
        self.revive_cmd.caller = self.char
        self.revive_cmd.args = f"#{self.test_char.id}"
        self.revive_cmd.func()

        # Verify character is now alive
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

    def test_revive_full_life_process(self):
        """Test that @revive triggers the full life restoration process."""
        # First kill the character
        self.test_char.at_death()
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

        # Verify metabolism script is stopped
        metabolism_scripts = self.test_char.scripts.get("metabolism_script")
        self.assertEqual(len(metabolism_scripts), 0)

        # Execute revive command
        self.revive_cmd.caller = self.char
        self.revive_cmd.args = "TestChar"
        self.revive_cmd.func()

        # Verify character is alive
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

        # Verify metabolism script is restarted
        metabolism_scripts = self.test_char.scripts.get("metabolism_script")
        self.assertTrue(len(metabolism_scripts) > 0)

        # Verify command sets are updated (alive cmdset should be present)
        from commands.default_cmdsets import AliveCmdSet
        alive_cmdsets = [cmdset for cmdset in self.test_char.cmdset.all() if isinstance(cmdset, AliveCmdSet)]
        self.assertTrue(len(alive_cmdsets) > 0)

    def test_kill_already_dead(self):
        """Test that @kill on an already dead character gives appropriate message."""
        # Kill the character first
        self.test_char.set_living_state(False)

        # Try to kill again
        self.kill_cmd.caller = self.char
        self.kill_cmd.args = "TestChar"
        self.kill_cmd.func()

        # Should still be dead (no change)
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

    def test_revive_already_alive(self):
        """Test that @revive on an already alive character gives appropriate message."""
        # Character should start alive
        self.assertTrue(self.test_char.is_living())

        # Try to revive
        self.revive_cmd.caller = self.char
        self.revive_cmd.args = "TestChar"
        self.revive_cmd.func()

        # Should still be alive (no change)
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

    def test_kill_with_reason(self):
        """Test that @kill with a reason works correctly."""
        # Execute kill command with reason
        self.kill_cmd.caller = self.char
        self.kill_cmd.args = "TestChar = Testing the kill command"
        self.kill_cmd.func()

        # Verify character is dead
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

    def test_revive_with_reason(self):
        """Test that @revive with a reason works correctly."""
        # First kill the character
        self.test_char.set_living_state(False)

        # Execute revive command with reason
        self.revive_cmd.caller = self.char
        self.revive_cmd.args = "TestChar = Testing the revive command"
        self.revive_cmd.func()

        # Verify character is alive
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

    def test_revive_helper_method(self):
        """Test that the revive helper method works correctly."""
        # First kill the character
        self.test_char.at_death()
        self.assertFalse(self.test_char.is_living())
        self.assertTrue(self.test_char.is_dead())

        # Use the revive helper method directly
        self.revive_cmd._revive_target(self.test_char)

        # Verify character is now alive
        self.assertTrue(self.test_char.is_living())
        self.assertFalse(self.test_char.is_dead())

        # Verify tags are correct
        self.assertTrue(self.test_char.tags.has("living_being", category="living_state"))
        self.assertFalse(self.test_char.tags.has("dead", category="living_state"))

        # Verify metabolism script is running
        metabolism_scripts = self.test_char.scripts.get("metabolism_script")
        self.assertTrue(len(metabolism_scripts) > 0)

        # Verify command sets are correct (alive cmdset should be present)
        from commands.default_cmdsets import AliveCmdSet
        alive_cmdsets = [cmdset for cmdset in self.test_char.cmdset.all() if isinstance(cmdset, AliveCmdSet)]
        self.assertTrue(len(alive_cmdsets) > 0)
