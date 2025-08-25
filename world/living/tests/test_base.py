"""
Tests for the base living system.
"""
import unittest
from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from world.living.base import LivingMixin


class TestLivingMixin(EvenniaTest):
    """Test suite for LivingMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test living object
        self.living_obj = create_object("world.living.people.Person", key="TestLiving")

    def test_living_mixin_initialization(self):
        """Test LivingMixin initialization."""
        self.assertIsInstance(self.living_obj, LivingMixin)
        self.assertTrue(self.living_obj.tags.has("living_being", category="living_state"))
        self.assertEqual(self.living_obj.default_weight, 60000)

    def test_living_weight_property(self):
        """Test living weight property."""
        self.assertTrue(hasattr(self.living_obj, 'weight'))
        self.assertEqual(self.living_obj.weight.value, 60000)

    def test_living_is_dead_property(self):
        """Test is_dead property."""
        self.assertFalse(self.living_obj.is_dead)

        # Add dead tag
        self.living_obj.tags.add("dead", category="living_state")
        self.assertTrue(self.living_obj.is_dead)

    def test_living_die(self):
        """Test die method."""
        # Ensure object has a location
        self.living_obj.move_to(self.room1)

        # Should not be dead initially
        self.assertFalse(self.living_obj.is_dead)

        # Die
        self.living_obj.die()

        # Should be dead
        self.assertTrue(self.living_obj.is_dead)
        self.assertTrue(self.living_obj.tags.has("dead", category="living_state"))

    def test_living_revive(self):
        """Test revive method."""
        # Ensure object has a location
        self.living_obj.move_to(self.room1)

        # Die first
        self.living_obj.die()
        self.assertTrue(self.living_obj.is_dead)

        # Revive
        self.living_obj.revive()

        # Should not be dead
        self.assertFalse(self.living_obj.is_dead)
        self.assertFalse(self.living_obj.tags.has("dead", category="living_state"))

    def test_living_reset_and_revive(self):
        """Test reset_and_revive method."""
        # Ensure object has a location
        self.living_obj.move_to(self.room1)

        # Set some metabolism values
        self.living_obj.hunger.value = 50
        self.living_obj.thirst.value = 30
        self.living_obj.tiredness.value = 40

        # Die
        self.living_obj.die()
        self.assertTrue(self.living_obj.is_dead)

        # Reset and revive
        self.living_obj.reset_and_revive()

        # Should be alive and reset
        self.assertFalse(self.living_obj.is_dead)
        self.assertEqual(self.living_obj.hunger.value, 0)
        self.assertEqual(self.living_obj.thirst.value, 0)
        self.assertEqual(self.living_obj.tiredness.value, 0)

    def test_living_metabolism_integration(self):
        """Test metabolism integration."""
        self.assertTrue(hasattr(self.living_obj, 'hunger'))
        self.assertTrue(hasattr(self.living_obj, 'thirst'))
        self.assertTrue(hasattr(self.living_obj, 'tiredness'))
        self.assertTrue(hasattr(self.living_obj, 'metabolism'))

    def test_living_perception_integration(self):
        """Test perception integration."""
        self.assertTrue(hasattr(self.living_obj, 'vision'))

    def test_living_weight_integration(self):
        """Test weight system integration."""
        # Living objects should have higher default weight
        self.assertGreater(self.living_obj.weight.value, 100)  # Regular objects have 100

    def test_living_metabolism_script_integration(self):
        """Test metabolism script integration."""
        # Should have metabolism script methods
        self.assertTrue(hasattr(self.living_obj, 'start_metabolism_script'))
        self.assertTrue(hasattr(self.living_obj, 'stop_metabolism_script'))

    def test_living_resting_state_integration(self):
        """Test resting state integration."""
        self.assertTrue(hasattr(self.living_obj, 'is_resting'))
        self.assertTrue(hasattr(self.living_obj, 'start_resting'))
        self.assertTrue(hasattr(self.living_obj, 'stop_resting'))

    def test_living_eat_drink_integration(self):
        """Test eat and drink integration."""
        self.assertTrue(hasattr(self.living_obj, 'eat'))
        self.assertTrue(hasattr(self.living_obj, 'drink'))

    def test_living_update_living_status(self):
        """Test update living status."""
        self.assertTrue(hasattr(self.living_obj, 'update_living_status'))


class TestLivingIntegration(EvenniaTest):
    """Integration tests for living system."""

    def test_living_with_metabolism(self):
        """Test living object with metabolism system."""
        living = create_object("world.living.people.Person", key="LivingMetabolism")

        # Should have metabolism handlers
        self.assertIsNotNone(living.hunger)
        self.assertIsNotNone(living.thirst)
        self.assertIsNotNone(living.tiredness)

        # Should be able to eat and drink
        living.hunger.value = 50
        living.eat(None, 20)
        self.assertEqual(living.hunger.value, 30)

        water = create_object("world.physical.liquid.Water", key="Water")
        water.weight.value = 100
        living.thirst.value = 50
        living.drink(water)
        self.assertEqual(living.thirst.value, 48)

    def test_living_with_perception(self):
        """Test living object with perception system."""
        living = create_object("world.living.people.Person", key="LivingPerception")

        # Should have vision
        self.assertIsNotNone(living.vision)

        # Should be able to see (if light available) - ensure location
        living.move_to(self.room1)
        self.assertIsInstance(living.vision.can_see, bool)

    def test_living_with_weight(self):
        """Test living object with weight system."""
        living = create_object("world.living.people.Person", key="LivingWeight")

        # Should have weight
        self.assertIsNotNone(living.weight)
        self.assertEqual(living.weight.value, 60000)

    def test_living_death_cascade(self):
        """Test death affects all systems."""
        living = create_object("world.living.people.Person", key="LivingDeath")

        # Ensure object has a location
        living.move_to(self.room1)

        # Die
        living.die()

        # Should be dead
        self.assertTrue(living.is_dead)

        # Vision should be disabled
        self.assertTrue(living.vision.disabled)

        # Should not be resting
        self.assertFalse(living.is_resting)

    def test_living_revival_cascade(self):
        """Test revival affects all systems."""
        living = create_object("world.living.people.Person", key="LivingRevival")

        # Ensure object has a location
        living.move_to(self.room1)

        # Die first
        living.die()
        self.assertTrue(living.is_dead)
        self.assertTrue(living.vision.disabled)

        # Revive
        living.revive()

        # Should be alive
        self.assertFalse(living.is_dead)

        # Vision should be enabled
        self.assertFalse(living.vision.disabled)

    def test_living_metabolism_death(self):
        """Test metabolism can cause death."""
        living = create_object("world.living.people.Person", key="LivingMetabolismDeath")

        # Ensure object has a location
        living.move_to(self.room1)

        # Set lethal metabolism values
        living.hunger.value = 100

        # Update status
        living.update_living_status()

        # Should be dead
        self.assertTrue(living.is_dead)
