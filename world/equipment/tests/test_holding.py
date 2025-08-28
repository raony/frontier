"""
Tests for the holding system.
"""
from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from world.equipment.holding import HoldableItem
from world.living.people import Person


class TestHoldableMixin(EvenniaTest):
    """Test suite for HoldableMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test holdable item
        self.holdable_item = create_object("world.equipment.holding.HoldableItem", key="TestHoldable")

    def test_holdable_mixin_initialization(self):
        """Test HoldableMixin initialization."""
        self.assertTrue(self.holdable_item.tags.has("holdable", category="holding"))

    def test_holdable_items_show_weight_indicators(self):
        """Test that holdable items show weight indicators correctly."""
        # Set up character with holding strength
        self.char1.holding_strength = 1000

        # Test light weight
        self.holdable_item.weight.value = 500
        display_name = self.holdable_item.get_display_name(self.char1)
        self.assertIn("░", display_name)

        # Test medium weight
        self.holdable_item.weight.value = 2000
        display_name = self.holdable_item.get_display_name(self.char1)
        self.assertIn("▒", display_name)

        # Test heavy weight
        self.holdable_item.weight.value = 5000
        display_name = self.holdable_item.get_display_name(self.char1)
        self.assertIn("█", display_name)

    def test_holdable_items_no_weight_when_no_holding_strength(self):
        """Test that holdable items don't show weight when looker has no holding strength."""
        # Create character without holding strength
        char_no_strength = create_object("typeclasses.objects.Object", key="NoStrengthChar")

        # Should not show weight indicator
        display_name = self.holdable_item.get_display_name(char_no_strength)
        self.assertNotIn("░", display_name)
        self.assertNotIn("▒", display_name)
        self.assertNotIn("█", display_name)

    def test_holdable_items_command_narration(self):
        """Test that holdable items don't show weight in command narration."""
        self.char1.holding_strength = 1000
        self.holdable_item.weight.value = 500

        # Command narration should not show weight indicators
        display_name = self.holdable_item.get_display_name(self.char1, command_narration=True)
        self.assertNotIn("░", display_name)
        self.assertNotIn("▒", display_name)
        self.assertNotIn("█", display_name)

    def test_holdable_items_held_status(self):
        """Test that holdable items show held status correctly."""
        # Set up character with holding strength
        self.char1.holding_strength = 1000

        # Add holding slots to character
        self.char1.tags.add('main', category="holding_slot", data="main hand")
        self.char1.tags.add('off', category="holding_slot", data="off hand")

        # Test not held
        display_name = self.holdable_item.get_display_name(self.char1)
        self.assertIn("░", display_name)  # Should show weight
        self.assertNotIn("(main hand)", display_name)  # Should not show held status

        # Test held
        self.holdable_item.tags.add("held", category="holding")
        self.holdable_item.tags.add("main", category="holding_slot")
        self.holdable_item.location = self.char1

        display_name = self.holdable_item.get_display_name(self.char1)
        self.assertIn("░", display_name)  # Should still show weight
        self.assertIn("(main hand)", display_name)  # Should show held status


class TestHolderMixin(EvenniaTest):
    """Test suite for HolderMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test character with holder mixin using Person class
        self.holder_char = create_object("world.living.people.Person", key="TestHolder")

    def test_holder_mixin_initialization(self):
        """Test HolderMixin initialization."""
        self.assertTrue(hasattr(self.holder_char, 'holding_strength'))
        self.assertTrue(hasattr(self.holder_char, 'held_items'))
        self.assertTrue(self.holder_char.tags.has('main', category="holding_slot"))
        self.assertTrue(self.holder_char.tags.has('off', category="holding_slot"))

    def test_holder_holding_strength_default(self):
        """Test default holding strength."""
        self.assertEqual(self.holder_char.holding_strength, 10000)

    def test_holder_held_items_handler(self):
        """Test that held items handler is properly initialized."""
        self.assertIsNotNone(self.holder_char.held_items)
        self.assertEqual(len(self.holder_char.held_items.slots), 2)
        self.assertIn('main', self.holder_char.held_items.slots)
        self.assertIn('off', self.holder_char.held_items.slots)
