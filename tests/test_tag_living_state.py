"""
Test the tag-based living state system.

This test verifies that the mutually exclusive tag approach for living/dead
states works correctly and maintains backward compatibility.
"""

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest
from typeclasses.characters import Character


class TestTagLivingState(EvenniaTest):
    """Test the tag-based living state system."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.char = create_object(Character, key="TestChar", location=self.room1)

    def test_initial_living_state(self):
        """Test that characters start as living."""
        # Check tag-based state
        self.assertTrue(self.char.is_living_tag())
        self.assertFalse(self.char.is_dead_tag())

        # Check living state methods
        self.assertTrue(self.char.is_living())
        self.assertFalse(self.char.is_dead())

        # Check that living_being tag exists (all characters are living beings)
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))
        self.assertFalse(self.char.tags.has("dead", category="living_state"))

    def test_set_living_state_alive(self):
        """Test setting character to alive state."""
        # First set to dead
        self.char.set_living_state(False)
        self.assertFalse(self.char.is_living_tag())
        self.assertTrue(self.char.is_dead_tag())

        # Then set back to alive
        self.char.set_living_state(True)
        self.assertTrue(self.char.is_living_tag())
        self.assertFalse(self.char.is_dead_tag())

        # Check tags
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))
        self.assertFalse(self.char.tags.has("dead", category="living_state"))

    def test_set_living_state_dead(self):
        """Test setting character to dead state."""
        # Set to dead
        self.char.set_living_state(False)
        self.assertFalse(self.char.is_living_tag())
        self.assertTrue(self.char.is_dead_tag())

        # Check tags
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))
        self.assertTrue(self.char.tags.has("dead", category="living_state"))

    def test_additive_tags(self):
        """Test that living_being and dead tags work additively."""
        # Start alive
        self.assertTrue(self.char.is_living_tag())
        self.assertFalse(self.char.is_dead_tag())
        self.assertTrue(self.char.is_living_being_tag())

        # Set to dead
        self.char.set_living_state(False)
        self.assertFalse(self.char.is_living_tag())
        self.assertTrue(self.char.is_dead_tag())
        self.assertTrue(self.char.is_living_being_tag())

        # Set back to alive
        self.char.set_living_state(True)
        self.assertTrue(self.char.is_living_tag())
        self.assertFalse(self.char.is_dead_tag())
        self.assertTrue(self.char.is_living_being_tag())

        # Verify living_being tag always exists
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))
        # Verify dead tag is added/removed appropriately
        self.assertFalse(self.char.tags.has("dead", category="living_state"))

    def test_at_death_method(self):
        """Test that at_death() properly sets living state."""
        # Call at_death
        self.char.at_death()

        # Check tag-based state
        self.assertFalse(self.char.is_living_tag())
        self.assertTrue(self.char.is_dead_tag())

        # Check living state methods
        self.assertFalse(self.char.is_living())
        self.assertTrue(self.char.is_dead())

        # Check tags
        self.assertTrue(self.char.tags.has("living_being", category="living_state"))
        self.assertTrue(self.char.tags.has("dead", category="living_state"))

    def test_living_state_methods(self):
        """Test that living state methods work correctly."""
        # Set using tag method
        self.char.set_living_state(False)

        # Check that living state methods work
        self.assertFalse(self.char.is_living())
        self.assertTrue(self.char.is_dead())

    def test_object_creation_default_state(self):
        """Test that new objects get proper default living state."""
        # Create a new character
        new_char = create_object(Character, key="NewChar", location=self.room1)

        # Should start as living
        self.assertTrue(new_char.is_living_tag())
        self.assertFalse(new_char.is_dead_tag())

        # Should have living_being tag
        self.assertTrue(new_char.tags.has("living_being", category="living_state"))
        self.assertFalse(new_char.tags.has("dead", category="living_state"))

    def test_tag_search_functionality(self):
        """Test that we can search for living/dead characters using tags."""
        from evennia import search_tag

        # Create a dead character
        dead_char = create_object(Character, key="DeadChar", location=self.room1)
        dead_char.set_living_state(False)

        # Search for living beings (both alive and dead)
        living_beings = search_tag("living_being", category="living_state")
        self.assertIn(self.char, living_beings)
        self.assertIn(dead_char, living_beings)

        # Search for living characters (alive only)
        # Note: We need to filter living beings that don't have the dead tag
        living_chars = [char for char in living_beings if not char.tags.has("dead", category="living_state")]
        self.assertIn(self.char, living_chars)
        self.assertNotIn(dead_char, living_chars)

        # Search for dead characters
        dead_chars = search_tag("dead", category="living_state")
        self.assertIn(dead_char, dead_chars)
        self.assertNotIn(self.char, dead_chars)

    def test_living_being_inheritance(self):
        """Test that all living beings share the base tag regardless of state."""
        from evennia import search_tag

        # Create multiple characters in different states
        alive_char = create_object(Character, key="AliveChar", location=self.room1)
        dead_char = create_object(Character, key="DeadChar", location=self.room1)
        dead_char.set_living_state(False)

        # All should be living beings
        self.assertTrue(alive_char.is_living_being_tag())
        self.assertTrue(dead_char.is_living_being_tag())
        self.assertTrue(self.char.is_living_being_tag())

        # Find all living beings (regardless of state)
        living_beings = search_tag("living_being", category="living_state")
        self.assertIn(alive_char, living_beings)
        self.assertIn(dead_char, living_beings)
        self.assertIn(self.char, living_beings)

        # Verify we can find all living beings in a room
        room_living_beings = [obj for obj in self.room1.contents
                             if obj.tags.has("living_being", category="living_state")]
        # Check that our three characters are among the living beings
        self.assertIn(alive_char, room_living_beings)
        self.assertIn(dead_char, room_living_beings)
        self.assertIn(self.char, room_living_beings)
        # There might be other living beings in the room (like NPCs), so just verify our characters are there
