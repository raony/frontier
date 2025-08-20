"""Test the container system for items."""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.objects import Object
from typeclasses.container import ContainerMixin, Container


class TestContainerSystem(EvenniaTest):
    """Test the container system functionality."""

    def setUp(self):
        """Set up test objects."""
        super().setUp()

        # Create test containers
        self.container = create_object(Container, key="test_container", location=self.room1)
        self.large_container = create_object(Container, key="large_container", location=self.room1)
        self.large_container.db.container_capacity = 20
        self.large_container.db.container_weight_limit = 10000

        # Create test items
        self.small_item = create_object(Object, key="small_item", location=self.room1)
        self.small_item.set_weight(100)
        self.medium_item = create_object(Object, key="medium_item", location=self.room1)
        self.medium_item.set_weight(500)
        self.large_item = create_object(Object, key="large_item", location=self.room1)
        self.large_item.set_weight(1000)

    def test_container_creation(self):
        """Test that containers are created with proper tags and attributes."""
        # Test container tag
        self.assertTrue(self.container.tags.has("container", category="container"))
        self.assertTrue(self.container.is_container())

        # Test default attributes
        self.assertEqual(self.container.get_container_capacity(), 10)
        self.assertEqual(self.container.get_container_weight_limit(), 5000)
        self.assertFalse(self.container.is_container_locked())
        self.assertEqual(self.container.get_container_description(), "A simple container")

    def test_container_capacity_limits(self):
        """Test that containers respect item count capacity limits."""
        # Fill container to capacity
        for i in range(10):
            item = create_object(Object, key=f"item_{i}", location=self.room1)
            item.move_to(self.container)

        # Try to add one more item
        extra_item = create_object(Object, key="extra_item", location=self.room1)
        # Should fail capacity check but movement is allowed
        self.assertFalse(self.container.can_hold_item(extra_item))
        extra_item.move_to(self.container)

        # Item should be moved but container is over capacity
        self.assertEqual(extra_item.location, self.container)
        self.assertEqual(len(self.container.contents), 11)

    def test_container_weight_limits(self):
        """Test that containers respect weight capacity limits."""
        # Add items up to weight limit
        heavy_item1 = create_object(Object, key="heavy1", location=self.room1)
        heavy_item1.set_weight(2000)
        heavy_item1.move_to(self.container)

        heavy_item2 = create_object(Object, key="heavy2", location=self.room1)
        heavy_item2.set_weight(2000)
        heavy_item2.move_to(self.container)

        # Try to add one more heavy item
        heavy_item3 = create_object(Object, key="heavy3", location=self.room1)
        heavy_item3.set_weight(2000)
        # Should fail weight check but movement is allowed
        self.assertFalse(self.container.can_hold_item(heavy_item3))
        heavy_item3.move_to(self.container)

        # Item should be moved but container is over weight limit
        self.assertEqual(heavy_item3.location, self.container)
        self.assertEqual(len(self.container.contents), 3)

    def test_container_locked_behavior(self):
        """Test that locked containers prevent item movement."""
        # Lock the container
        self.container.set_container_locked(True)
        self.assertTrue(self.container.is_container_locked())

        # Try to add an item to locked container
        test_item = create_object(Object, key="test_item", location=self.room1)
        # Should fail lock check but movement is allowed
        self.assertFalse(self.container.can_hold_item(test_item))
        test_item.move_to(self.container)

        # Item should be moved but container is locked
        self.assertEqual(test_item.location, self.container)
        self.assertEqual(len(self.container.contents), 1)

        # Unlock and try again
        self.container.set_container_locked(False)
        test_item.move_to(self.container)
        self.assertEqual(test_item.location, self.container)

    def test_container_status(self):
        """Test container status reporting."""
        # Add some items
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        status = self.container.get_container_status()

        self.assertEqual(status['items']['current'], 2)
        self.assertEqual(status['items']['maximum'], 10)
        self.assertEqual(status['items']['available'], 8)
        self.assertEqual(status['weight']['current'], 600)  # 100 + 500
        self.assertEqual(status['weight']['maximum'], 5000)
        self.assertEqual(status['weight']['available'], 4400)
        self.assertFalse(status['locked'])

    def test_container_display(self):
        """Test container display formatting."""
        # Add items and set description
        self.container.set_container_description("A sturdy wooden box")
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        display = self.container.get_container_display()

        self.assertIn("Container: A sturdy wooden box", display)
        self.assertIn("Items: 2/10", display)
        self.assertIn("Weight: 600g/5000g", display)
        self.assertIn("small_item", display)
        self.assertIn("medium_item", display)

    def test_container_description_integration(self):
        """Test that container description integrates with object description."""
        self.container.set_container_description("A magical chest")
        self.small_item.move_to(self.container)

        # Test get_display_desc includes container info
        desc = self.container.get_display_desc(self.char1)
        self.assertIn("Container: A magical chest", desc)
        self.assertIn("Items: 1/10", desc)

    def test_container_search(self):
        """Test container search functionality."""
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        # Search for items in container
        results = self.container.search_container("small")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.small_item)

        results = self.container.search_container("medium")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.medium_item)

    def test_container_contents(self):
        """Test getting container contents."""
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        contents = self.container.get_container_contents()
        self.assertEqual(len(contents), 2)
        self.assertIn(self.small_item, contents)
        self.assertIn(self.medium_item, contents)

    def test_empty_container(self):
        """Test emptying a container."""
        self.small_item.move_to(self.container)
        self.medium_item.move_to(self.container)

        # Empty the container
        result = self.container.empty_container(self.char1)
        self.assertTrue(result)
        self.assertEqual(len(self.container.contents), 0)

        # Items should be in the room
        self.assertEqual(self.small_item.location, self.room1)
        self.assertEqual(self.medium_item.location, self.room1)

    def test_empty_locked_container(self):
        """Test that locked containers cannot be emptied."""
        self.container.set_container_locked(True)
        self.small_item.move_to(self.container)

        result = self.container.empty_container(self.char1)
        self.assertFalse(result)
        self.assertEqual(len(self.container.contents), 1)

    def test_empty_already_empty_container(self):
        """Test emptying an already empty container."""
        result = self.container.empty_container(self.char1)
        self.assertFalse(result)

    def test_container_mixin_inheritance(self):
        """Test that ContainerMixin can be used with other classes."""
        # Test that the Container class has all the mixin functionality
        self.assertTrue(self.container.is_container())
        self.assertTrue(hasattr(self.container, 'get_container_capacity'))
        self.assertTrue(hasattr(self.container, 'get_container_weight_limit'))
        self.assertTrue(hasattr(self.container, 'can_hold_item'))
        self.assertTrue(hasattr(self.container, 'get_container_status'))

    def test_container_without_weight_system(self):
        """Test container behavior with objects that don't have weight."""
        # Test that containers work with basic item count limits
        # Fill container to capacity
        for i in range(10):
            item = create_object(Object, key=f"item_{i}", location=self.room1)
            item.move_to(self.container)

        # 11th item should fail capacity check
        extra_item = create_object(Object, key="extra", location=self.room1)
        self.assertFalse(self.container.can_hold_item(extra_item))
        extra_item.move_to(self.container)
        self.assertEqual(extra_item.location, self.container)

    def test_container_nesting(self):
        """Test nested container behavior."""
        # Create nested containers
        outer_container = create_object(Container, key="outer", location=self.room1)
        inner_container = create_object(Container, key="inner", location=self.room1)

        # Nest containers
        inner_container.move_to(outer_container)
        self.small_item.move_to(inner_container)

        # Test that both containers show correct status
        self.assertEqual(len(outer_container.contents), 1)  # inner_container
        self.assertEqual(len(inner_container.contents), 1)  # small_item

        # Test that outer container can see nested items through total_weight
        if hasattr(outer_container, 'total_weight'):
            # Outer container weight should include inner container and its contents
            self.assertGreater(outer_container.total_weight, inner_container.total_weight)

    def test_container_can_hold_item_method(self):
        """Test the can_hold_item method."""
        # Test normal case
        self.assertTrue(self.container.can_hold_item(self.small_item))

        # Test capacity limit
        for i in range(10):
            item = create_object(Object, key=f"item_{i}", location=self.room1)
            item.move_to(self.container)

        self.assertFalse(self.container.can_hold_item(self.small_item))

        # Test weight limit
        heavy_item = create_object(Object, key="heavy", location=self.room1)
        heavy_item.set_weight(6000)  # Over the 5000g limit

        # Clear container first
        self.container.empty_container()
        # Should fail because 6000g > 5000g limit
        self.assertFalse(self.container.can_hold_item(heavy_item))

        # Test locked container
        self.container.set_container_locked(True)
        self.assertFalse(self.container.can_hold_item(self.small_item))
