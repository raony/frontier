"""
Tests for the weight system.
"""
import unittest
from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from world.physical.weight import WeightHandler, WeightMixin


class TestWeightHandler(EvenniaTest):
    """Test suite for WeightHandler class."""

    def setUp(self):
        super().setUp()
        self.weight_handler = WeightHandler(self.obj1)

    def test_weight_handler_initialization(self):
        """Test WeightHandler initialization."""
        self.assertIsNotNone(self.weight_handler)
        self.assertEqual(self.weight_handler.obj, self.obj1)

    def test_weight_value_default(self):
        """Test default weight value is 100 for regular objects."""
        self.assertEqual(self.weight_handler.value, 100)

    def test_weight_value_setter(self):
        """Test setting weight value."""
        self.weight_handler.value = 50
        self.assertEqual(self.weight_handler.value, 50)

    def test_weight_value_persistence(self):
        """Test weight value persists through attribute system."""
        self.weight_handler.value = 75
        # Create new handler to test persistence
        new_handler = WeightHandler(self.obj1)
        self.assertEqual(new_handler.value, 75)

    def test_weight_total_with_contents(self):
        """Test total weight includes contents."""
        # Set base weight
        self.weight_handler.value = 100

        # Create child object with weight
        child = create_object("typeclasses.objects.Object", key="Child", location=self.obj1)
        child.weight.value = 25

        # Total should be base + child weight
        self.assertEqual(self.weight_handler.total, 125)

    def test_weight_total_nested_contents(self):
        """Test total weight with nested contents."""
        # Set base weight
        self.weight_handler.value = 100

        # Create nested structure
        child1 = create_object("typeclasses.objects.Object", key="Child1", location=self.obj1)
        child1.weight.value = 25

        child2 = create_object("typeclasses.objects.Object", key="Child2", location=child1)
        child2.weight.value = 15

        # Total should be base + child1 + child2
        self.assertEqual(self.weight_handler.total, 140)

    def test_weight_decrease(self):
        """Test weight decrease by proportion."""
        self.weight_handler.value = 100
        self.weight_handler.decrease(0.2)  # Decrease by 20%
        self.assertEqual(self.weight_handler.value, 80)

    def test_weight_increase(self):
        """Test weight increase by proportion."""
        self.weight_handler.value = 100
        self.weight_handler.increase(0.3)  # Increase by 30%
        self.assertEqual(self.weight_handler.value, 130)

    def test_weight_decrease_zero(self):
        """Test weight decrease doesn't go below zero."""
        self.weight_handler.value = 10
        self.weight_handler.decrease(1.0)  # Decrease by 100%
        self.assertEqual(self.weight_handler.value, 0)

    def test_weight_increase_from_zero(self):
        """Test weight increase from zero."""
        self.weight_handler.value = 0
        self.weight_handler.increase(0.5)  # Increase by 50%
        self.assertEqual(self.weight_handler.value, 0)  # 0 * 0.5 = 0


class TestWeightMixin(EvenniaTest):
    """Test suite for WeightMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test object that uses WeightMixin
        self.test_obj = create_object("typeclasses.objects.Object", key="TestWeightObj")

    def test_weight_mixin_initialization(self):
        """Test WeightMixin provides weight property."""
        self.assertTrue(hasattr(self.test_obj, 'weight'))
        self.assertIsInstance(self.test_obj.weight, WeightHandler)

    def test_weight_mixin_lazy_property(self):
        """Test weight is a lazy property."""
        # Accessing weight should create the handler
        weight1 = self.test_obj.weight
        weight2 = self.test_obj.weight
        self.assertIs(weight1, weight2)  # Same instance

    def test_weight_mixin_default_weight(self):
        """Test default weight is set on object creation."""
        # Default weight should be 100 for regular objects
        self.assertEqual(self.test_obj.weight.value, 100)


class TestWeightIntegration(EvenniaTest):
    """Integration tests for weight system."""

    def test_weight_with_container_contents(self):
        """Test weight calculation with container contents."""
        # Create container
        container = create_object("typeclasses.objects.Object", key="Container")
        container.weight.value = 50

        # Add items to container
        item1 = create_object("typeclasses.objects.Object", key="Item1", location=container)
        item1.weight.value = 25

        item2 = create_object("typeclasses.objects.Object", key="Item2", location=container)
        item2.weight.value = 30

        # Container total weight should include its own weight plus contents
        self.assertEqual(container.weight.total, 105)

    def test_weight_transfer_affects_totals(self):
        """Test that moving objects affects weight totals correctly."""
        # Create container and item
        container = create_object("typeclasses.objects.Object", key="Container")
        container.weight.value = 100

        item = create_object("typeclasses.objects.Object", key="Item", location=self.room1)
        item.weight.value = 50

        # Initial weights
        self.assertEqual(container.weight.total, 100)
        # Room doesn't have weight, so we check the item's location
        self.assertEqual(item.location, self.room1)

        # Move item to container
        item.move_to(container)

        # Updated weights
        self.assertEqual(container.weight.total, 150)
        self.assertEqual(item.location, container)

    def test_weight_with_living_objects(self):
        """Test weight system with living objects (characters)."""
        # Characters should have higher default weight
        self.assertGreater(self.char1.weight.value, 100)  # Living objects have higher default

        # Test character can hold items
        item = create_object("typeclasses.objects.Object", key="TestItem", location=self.char1)
        item.weight.value = 25

        # Character's total weight should include held item
        self.assertEqual(self.char1.weight.total, self.char1.weight.value + 25)
