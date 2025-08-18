"""Test the weight system for items."""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.objects import Object, WeightMixin
from typeclasses.food import Food, PortionedFood, RoastedChicken
from typeclasses.items import Torch, HeadItem, BodyItem
from typeclasses.liquid import LiquidContainer


class TestWeightSystem(EvenniaTest):
    """Test the weight system functionality."""

    def setUp(self):
        """Set up test objects."""
        super().setUp()
        # Create test objects with different weights
        self.test_obj = create_object(Object, key="test_object", location=self.room1)
        self.light_obj = create_object(Object, key="light_object", location=self.room1)
        self.heavy_obj = create_object(Object, key="heavy_object", location=self.room1)

        # Create containers for testing
        self.container = create_object(Object, key="container", location=self.room1)
        self.large_container = create_object(Object, key="large_container", location=self.room1)

        # Create items to put inside containers
        self.small_item = create_object(Object, key="small_item", location=self.room1)
        self.medium_item = create_object(Object, key="medium_item", location=self.room1)
        self.large_item = create_object(Object, key="large_item", location=self.room1)

    def test_default_weight(self):
        """Test that objects have default weight of 100g."""
        self.assertEqual(self.test_obj.weight, 100)
        self.assertEqual(self.light_obj.weight, 100)
        self.assertEqual(self.heavy_obj.weight, 100)

    def test_set_weight_positive(self):
        """Test setting positive weight values."""
        self.test_obj.set_weight(250)
        self.assertEqual(self.test_obj.weight, 250)

        self.test_obj.set_weight(0)
        self.assertEqual(self.test_obj.weight, 0)

        self.test_obj.set_weight(1000)
        self.assertEqual(self.test_obj.weight, 1000)

    def test_set_weight_negative_raises_error(self):
        """Test that setting negative weight raises ValueError."""
        with self.assertRaises(ValueError):
            self.test_obj.set_weight(-50)

        # Weight should remain unchanged
        self.assertEqual(self.test_obj.weight, 100)

    def test_set_weight_invalid_type_raises_error(self):
        """Test that setting invalid weight types raises ValueError."""
        with self.assertRaises(ValueError):
            self.test_obj.set_weight("invalid")

        with self.assertRaises(ValueError):
            self.test_obj.set_weight(None)

        # Weight should remain unchanged
        self.assertEqual(self.test_obj.weight, 100)

    def test_set_weight_float_converts_to_int(self):
        """Test that setting float weight converts to integer."""
        self.test_obj.set_weight(3.14)
        self.assertEqual(self.test_obj.weight, 3)

        self.test_obj.set_weight(5.9)
        self.assertEqual(self.test_obj.weight, 5)

        # Weight should be updated, not remain unchanged
        self.assertNotEqual(self.test_obj.weight, 100)

    def test_total_weight_single_object(self):
        """Test total_weight for objects without contents."""
        self.test_obj.set_weight(150)
        self.assertEqual(self.test_obj.total_weight, 150)

        self.light_obj.set_weight(25)
        self.assertEqual(self.light_obj.total_weight, 25)

        self.heavy_obj.set_weight(500)
        self.assertEqual(self.heavy_obj.total_weight, 500)

    def test_total_weight_container_with_contents(self):
        """Test total_weight for containers with items inside."""
        # Set weights for container and items
        self.container.set_weight(200)
        self.small_item.set_weight(50)
        self.medium_item.set_weight(100)

        # Put items in container
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        # Container weight should be: container (200) + small_item (50) + medium_item (100) = 350
        expected_weight = 200 + 50 + 100
        self.assertEqual(self.container.total_weight, expected_weight)

        # Individual items should still have their own weight
        self.assertEqual(self.small_item.total_weight, 50)
        self.assertEqual(self.medium_item.total_weight, 100)

    def test_total_weight_nested_containers(self):
        """Test total_weight for nested containers."""
        # Set weights
        self.container.set_weight(200)
        self.large_container.set_weight(300)
        self.small_item.set_weight(50)
        self.medium_item.set_weight(100)
        self.large_item.set_weight(150)

        # Create nested structure: large_container -> container -> small_item
        # large_container also contains medium_item and large_item directly
        self.container.move_to(self.large_container)
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.large_container)
        self.large_item.move_to(self.large_container)

        # Calculate expected weights:
        # container total: 200 (container) + 50 (small_item) = 250
        # large_container total: 300 (large_container) + 250 (container with contents) + 100 (medium_item) + 150 (large_item) = 800

        self.assertEqual(self.container.total_weight, 250)
        self.assertEqual(self.large_container.total_weight, 800)

    def test_total_weight_empty_container(self):
        """Test total_weight for empty containers."""
        self.container.set_weight(150)
        self.assertEqual(self.container.total_weight, 150)

        # Container with no contents should just return its own weight
        self.assertEqual(len(self.container.contents), 0)
        self.assertEqual(self.container.total_weight, 150)

    def test_total_weight_after_removing_contents(self):
        """Test total_weight changes when contents are removed."""
        # Set up container with items
        self.container.set_weight(200)
        self.small_item.set_weight(50)
        self.medium_item.set_weight(100)

        # Add items to container
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        # Verify total weight
        self.assertEqual(self.container.total_weight, 350)

        # Remove one item
        self.small_item.move_to(self.room1)
        self.assertEqual(self.container.total_weight, 300)

        # Remove all items
        self.medium_item.move_to(self.room1)
        self.assertEqual(self.container.total_weight, 200)

    def test_total_weight_liquid_container(self):
        """Test total_weight for liquid containers."""
        # Create a liquid container (which inherits from Object and WeightMixin)
        liquid_container = create_object(LiquidContainer, key="water_bottle", location=self.room1)

        # LiquidContainer has default weight of 150g
        self.assertEqual(liquid_container.weight, 150)
        self.assertEqual(liquid_container.total_weight, 150)

        # Add an item to the liquid container
        self.small_item.set_weight(75)
        self.small_item.move_to(liquid_container)

        # Total weight should be container (150) + item (75) = 225
        self.assertEqual(liquid_container.total_weight, 225)

    def test_total_weight_complex_nesting(self):
        """Test total_weight with complex nested container structures."""
        # Create a complex structure with multiple levels
        level1_container = create_object(Object, key="level1", location=self.room1)
        level2_container = create_object(Object, key="level2", location=self.room1)
        level3_container = create_object(Object, key="level3", location=self.room1)

        # Set weights
        level1_container.set_weight(100)
        level2_container.set_weight(200)
        level3_container.set_weight(300)

        # Create items
        item1 = create_object(Object, key="item1", location=self.room1)
        item2 = create_object(Object, key="item2", location=self.room1)
        item3 = create_object(Object, key="item3", location=self.room1)

        item1.set_weight(50)
        item2.set_weight(75)
        item3.set_weight(125)

        # Build nested structure: level1 -> level2 -> level3 -> item3
        # level1 also contains item1 directly
        # level2 also contains item2 directly
        level2_container.move_to(level1_container)
        level3_container.move_to(level2_container)
        item3.move_to(level3_container)
        item1.move_to(level1_container)
        item2.move_to(level2_container)

        # Calculate expected weights:
        # level3: 300 + 125 = 425
        # level2: 200 + 425 + 75 = 700
        # level1: 100 + 700 + 50 = 850

        self.assertEqual(level3_container.total_weight, 425)
        self.assertEqual(level2_container.total_weight, 700)
        self.assertEqual(level1_container.total_weight, 850)

    def test_total_weight_with_zero_weight_items(self):
        """Test total_weight with items that have zero weight."""
        self.container.set_weight(100)

        # Create items with zero weight
        zero_weight_item1 = create_object(Object, key="zero1", location=self.room1)
        zero_weight_item2 = create_object(Object, key="zero2", location=self.room1)

        zero_weight_item1.set_weight(0)
        zero_weight_item2.set_weight(0)

        # Add to container
        zero_weight_item1.move_to(self.container)
        zero_weight_item2.move_to(self.container)

        # Container weight should be: 100 + 0 + 0 = 100
        self.assertEqual(self.container.total_weight, 100)

    def test_set_weight_preserves_contents(self):
        """Test that changing container weight doesn't affect contents."""
        # Set up container with items
        self.container.set_weight(200)
        self.small_item.set_weight(50)
        self.medium_item.set_weight(100)

        # Add items to container
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        # Verify initial state
        self.assertEqual(self.container.total_weight, 350)
        self.assertEqual(len(self.container.contents), 2)

        # Change container weight
        self.container.set_weight(300)

        # Contents should remain unchanged
        self.assertEqual(len(self.container.contents), 2)
        self.assertEqual(self.small_item.location, self.container)
        self.assertEqual(self.medium_item.location, self.container)

        # Total weight should reflect new container weight
        self.assertEqual(self.container.total_weight, 450)  # 300 + 50 + 100

    def test_weight_inheritance(self):
        """Test that weight functionality is properly inherited."""
        # Test that Object class has weight functionality
        self.assertTrue(hasattr(self.test_obj, 'weight'))
        self.assertTrue(hasattr(self.test_obj, 'total_weight'))
        self.assertTrue(hasattr(self.test_obj, 'set_weight'))

        # Test that LiquidContainer has weight functionality
        liquid_container = create_object(LiquidContainer, key="test_liquid", location=self.room1)
        self.assertTrue(hasattr(liquid_container, 'weight'))
        self.assertTrue(hasattr(liquid_container, 'total_weight'))
        self.assertTrue(hasattr(liquid_container, 'set_weight'))

        # Test that Food items have weight functionality
        food_item = create_object(Food, key="test_food", location=self.room1)
        self.assertTrue(hasattr(food_item, 'weight'))
        self.assertTrue(hasattr(food_item, 'total_weight'))
        self.assertTrue(hasattr(food_item, 'set_weight'))
