"""
Tests for the metabolism system.
"""
import unittest
from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from world.living.metabolism import MetabolismHandler, HungerManager, ThirstManager, TirednessManager, MetabolismMixin


class TestMetabolismHandler(EvenniaTest):
    """Test suite for MetabolismHandler class."""

    def setUp(self):
        super().setUp()
        self.metabolism = MetabolismHandler(self.char1, 'test_attr')

    def test_metabolism_handler_initialization(self):
        """Test MetabolismHandler initialization."""
        self.assertIsNotNone(self.metabolism)
        self.assertEqual(self.metabolism.obj, self.char1)
        self.assertEqual(self.metabolism.attribute, 'test_attr')

    def test_metabolism_value_default(self):
        """Test default metabolism value."""
        self.assertEqual(self.metabolism.value, 0.0)

    def test_metabolism_value_setter(self):
        """Test setting metabolism value."""
        self.metabolism.value = 50.0
        self.assertEqual(self.metabolism.value, 50.0)

    def test_metabolism_value_bounds(self):
        """Test metabolism value bounds (0-100)."""
        # Test below 0
        self.metabolism.value = -10
        self.assertEqual(self.metabolism.value, 0)

        # Test above 100
        self.metabolism.value = 150
        self.assertEqual(self.metabolism.value, 100)

    def test_metabolism_level_calculation(self):
        """Test metabolism level calculation based on thresholds."""
        # Default thresholds: [7, 30, 60]
        self.assertEqual(self.metabolism.level, 0)  # 0 value

        self.metabolism.value = 5
        self.assertEqual(self.metabolism.level, 0)  # Below first threshold

        self.metabolism.value = 15
        self.assertEqual(self.metabolism.level, 1)  # Above first threshold

        self.metabolism.value = 45
        self.assertEqual(self.metabolism.level, 2)  # Above second threshold

        self.metabolism.value = 80
        self.assertEqual(self.metabolism.level, 3)  # Above third threshold

    def test_metabolism_increase_decrease(self):
        """Test metabolism increase and decrease."""
        self.metabolism.increase(10)
        self.assertEqual(self.metabolism.value, 10)

        self.metabolism.decrease(5)
        self.assertEqual(self.metabolism.value, 5)

    def test_metabolism_reset(self):
        """Test metabolism reset."""
        self.metabolism.value = 50
        self.metabolism.reset()
        self.assertEqual(self.metabolism.value, 0)

    def test_metabolism_persistence(self):
        """Test metabolism value persists through attribute system."""
        self.metabolism.value = 25
        # Create new handler to test persistence
        new_metabolism = MetabolismHandler(self.char1, 'test_attr')
        self.assertEqual(new_metabolism.value, 25)


class TestHungerManager(EvenniaTest):
    """Test suite for HungerManager class."""

    def setUp(self):
        super().setUp()
        self.hunger = HungerManager(self.char1)

    def test_hunger_manager_initialization(self):
        """Test HungerManager initialization."""
        self.assertIsInstance(self.hunger, HungerManager)
        self.assertEqual(self.hunger.attribute, 'hunger')
        self.assertEqual(self.hunger.increase_modifier, 0.3)

    def test_hunger_messages(self):
        """Test hunger messages."""
        self.assertEqual(self.hunger.messages[0], "")
        self.assertEqual(self.hunger.messages[1], "You feel hungry.")
        self.assertEqual(self.hunger.messages[2], "You're starving.")
        self.assertEqual(self.hunger.messages[3], "You're gonna die.")

    def test_hunger_labels(self):
        """Test hunger labels."""
        self.assertEqual(self.hunger.labels[0], "sated")
        self.assertEqual(self.hunger.labels[1], "hungry")
        self.assertEqual(self.hunger.labels[2], "starving")
        self.assertEqual(self.hunger.labels[3], "starving to death")

    def test_hunger_status(self):
        """Test hunger status based on level."""
        self.assertIsNone(self.hunger.status())  # Level 0 returns None

        self.hunger.value = 15
        self.assertEqual(self.hunger.status(), "hungry")

        self.hunger.value = 45
        self.assertEqual(self.hunger.status(), "starving")

        self.hunger.value = 80
        self.assertEqual(self.hunger.status(), "starving to death")


class TestThirstManager(EvenniaTest):
    """Test suite for ThirstManager class."""

    def setUp(self):
        super().setUp()
        self.thirst = ThirstManager(self.char1)

    def test_thirst_manager_initialization(self):
        """Test ThirstManager initialization."""
        self.assertIsInstance(self.thirst, ThirstManager)
        self.assertEqual(self.thirst.attribute, 'thirst')
        self.assertEqual(self.thirst.increase_modifier, 1.4)

    def test_thirst_messages(self):
        """Test thirst messages."""
        self.assertEqual(self.thirst.messages[1], "You feel thirsty.")
        self.assertEqual(self.thirst.messages[2], "You're starving for water.")
        self.assertEqual(self.thirst.messages[3], "You're gonna die of thirst.")

    def test_thirst_labels(self):
        """Test thirst labels."""
        self.assertEqual(self.thirst.labels[0], "quenched")
        self.assertEqual(self.thirst.labels[1], "thirsty")
        self.assertEqual(self.thirst.labels[2], "parched")
        self.assertEqual(self.thirst.labels[3], "dying of thirst")


class TestTirednessManager(EvenniaTest):
    """Test suite for TirednessManager class."""

    def setUp(self):
        super().setUp()
        self.tiredness = TirednessManager(self.char1)

    def test_tiredness_manager_initialization(self):
        """Test TirednessManager initialization."""
        self.assertIsInstance(self.tiredness, TirednessManager)
        self.assertEqual(self.tiredness.attribute, 'tiredness')
        self.assertEqual(self.tiredness.increase_modifier, 1.0)

    def test_tiredness_tick_resting(self):
        """Test tiredness tick when resting."""
        self.tiredness.value = 50
        self.char1.start_resting()

        self.tiredness.tick()
        # Should decrease when resting
        self.assertLess(self.tiredness.value, 50)

    def test_tiredness_tick_not_resting(self):
        """Test tiredness tick when not resting."""
        initial_value = self.tiredness.value
        self.tiredness.tick()
        # Should increase when not resting
        self.assertGreater(self.tiredness.value, initial_value)


class TestMetabolismMixin(EvenniaTest):
    """Test suite for MetabolismMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test object with MetabolismMixin
        self.living_obj = create_object("world.living.people.Person", key="TestLiving")

    def test_metabolism_mixin_initialization(self):
        """Test MetabolismMixin initialization."""
        self.assertTrue(hasattr(self.living_obj, 'hunger'))
        self.assertTrue(hasattr(self.living_obj, 'thirst'))
        self.assertTrue(hasattr(self.living_obj, 'tiredness'))
        self.assertEqual(self.living_obj.metabolism, 1.0)

    def test_metabolism_handlers(self):
        """Test metabolism handlers list."""
        handlers = self.living_obj.metabolism_handlers
        self.assertEqual(len(handlers), 3)
        self.assertIn(self.living_obj.hunger, handlers)
        self.assertIn(self.living_obj.thirst, handlers)
        self.assertIn(self.living_obj.tiredness, handlers)

    def test_resting_state(self):
        """Test resting state management."""
        self.assertFalse(self.living_obj.is_resting)

        self.living_obj.start_resting()
        self.assertTrue(self.living_obj.is_resting)

        self.living_obj.stop_resting()
        self.assertFalse(self.living_obj.is_resting)

    def test_metabolism_interval(self):
        """Test metabolism interval calculation."""
        self.assertEqual(self.living_obj.metabolism_interval, 600)

        self.living_obj.metabolism = 2.0
        self.assertEqual(self.living_obj.metabolism_interval, 300)

    def test_reset_survival_stats(self):
        """Test reset survival stats."""
        # Set some values
        self.living_obj.hunger.value = 50
        self.living_obj.thirst.value = 30
        self.living_obj.tiredness.value = 40
        self.living_obj.start_resting()

        # Reset
        self.living_obj.reset_survival_stats()

        # Check all reset
        self.assertEqual(self.living_obj.hunger.value, 0)
        self.assertEqual(self.living_obj.thirst.value, 0)
        self.assertEqual(self.living_obj.tiredness.value, 0)
        self.assertFalse(self.living_obj.is_resting)

    def test_eat_drink(self):
        """Test eat and drink functionality."""
        # Test eating
        self.living_obj.hunger.value = 50
        self.living_obj.eat(None, 20)
        self.assertEqual(self.living_obj.hunger.value, 30)

        # Test drinking
        water = create_object("world.physical.liquid.Water", key="Water")
        water.weight.value = 100  # 2 hydration points
        self.living_obj.thirst.value = 50
        self.living_obj.drink(water)
        self.assertEqual(self.living_obj.thirst.value, 48)

    def test_update_living_status(self):
        """Test update living status triggers death."""
        # Ensure object has a location
        self.living_obj.move_to(self.room1)

        # Set hunger to lethal level
        self.living_obj.hunger.value = 100
        self.living_obj.update_living_status()

        # Should be dead
        self.assertTrue(self.living_obj.is_dead)
