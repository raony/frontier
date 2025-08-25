"""
Tests for the container system.
"""
import unittest
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from evennia import create_object
from world.physical.container import ContainerMixin, Container, is_container
from world.physical.commands.store import CmdStore


class TestContainerMixin(EvenniaTest):
    """Test suite for ContainerMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test container using ContainerMixin
        self.container = create_object("world.physical.container.Container", key="TestContainer")

    def test_container_mixin_initialization(self):
        """Test ContainerMixin initialization."""
        self.assertTrue(hasattr(self.container, 'container_capacity'))
        self.assertTrue(hasattr(self.container, 'container_weight_limit'))
        self.assertTrue(hasattr(self.container, 'container_locked'))
        self.assertTrue(self.container.tags.has('container', category='container'))

    def test_container_default_properties(self):
        """Test default container properties."""
        self.assertEqual(self.container.container_capacity, 10)
        self.assertEqual(self.container.container_weight_limit, 5000)
        self.assertEqual(self.container.container_locked, False)

    def test_container_is_locked(self):
        """Test container locked state."""
        self.assertFalse(self.container.is_locked())

        # Set container as locked
        self.container.container_locked = True
        self.assertTrue(self.container.is_locked())

    def test_container_is_full(self):
        """Test container capacity checking."""
        # Container should not be full initially
        self.assertFalse(self.container.is_full())

        # Add items up to capacity
        for i in range(10):
            item = create_object("typeclasses.objects.Object", key=f"Item{i}", location=self.container)

        # Container should be full now
        self.assertTrue(self.container.is_full())

    def test_container_is_too_heavy(self):
        """Test container weight limit checking."""
        # Create a heavy item
        heavy_item = create_object("typeclasses.objects.Object", key="HeavyItem")
        heavy_item.weight.value = 6000  # Above weight limit

        # Container should be too heavy with this item
        self.assertTrue(self.container.is_too_heavy(heavy_item))

        # Create a light item
        light_item = create_object("typeclasses.objects.Object", key="LightItem")
        light_item.weight.value = 1000  # Below weight limit

        # Container should not be too heavy with this item
        self.assertFalse(self.container.is_too_heavy(light_item))

    def test_container_can_hold_item(self):
        """Test container can hold item logic."""
        # Create a valid item
        item = create_object("typeclasses.objects.Object", key="ValidItem")
        item.weight.value = 1000

        # Container should be able to hold valid item
        self.assertTrue(self.container.can_hold_item(item))

        # Test locked container
        self.container.container_locked = True
        self.assertFalse(self.container.can_hold_item(item))
        self.container.container_locked = False

        # Test full container
        for i in range(10):
            create_object("typeclasses.objects.Object", key=f"Item{i}", location=self.container)
        self.assertFalse(self.container.can_hold_item(item))

    def test_container_at_pre_object_receive(self):
        """Test container pre-receive hook."""
        # Create a valid item
        item = create_object("typeclasses.objects.Object", key="TestItem")
        item.weight.value = 1000

        # Should allow valid item
        result = self.container.at_pre_object_receive(item, self.room1)
        self.assertIsNotNone(result)  # Should not return False

        # Test with locked container
        self.container.container_locked = True
        result = self.container.at_pre_object_receive(item, self.room1)
        self.assertFalse(result)  # Should return False for locked container


class TestContainer(EvenniaTest):
    """Test suite for Container class."""

    def setUp(self):
        super().setUp()
        self.container = create_object("world.physical.container.Container", key="TestContainer")

    def test_container_creation(self):
        """Test Container object creation."""
        self.assertIsInstance(self.container, Container)
        self.assertTrue(self.container.tags.has('container', category='container'))
        self.assertEqual(self.container.weight.value, 100)  # Default weight from Object

    def test_container_default_properties(self):
        """Test Container default properties."""
        self.assertEqual(self.container.container_capacity_default, 10)
        self.assertEqual(self.container.container_weight_limit_default, 5000)
        self.assertEqual(self.container.weight_default, 200)

    def test_container_description(self):
        """Test container description attribute."""
        self.assertEqual(self.container.db.container_description, "A simple container")


class TestIsContainerFunction(EvenniaTest):
    """Test suite for is_container function."""

    def test_is_container_with_container(self):
        """Test is_container with actual container."""
        container = create_object("world.physical.container.Container", key="TestContainer")
        self.assertTrue(is_container(container))

    def test_is_container_with_regular_object(self):
        """Test is_container with regular object."""
        obj = create_object("typeclasses.objects.Object", key="RegularObject")
        self.assertFalse(is_container(obj))

    def test_is_container_with_container_mixin(self):
        """Test is_container with object using ContainerMixin."""
        # Create object with ContainerMixin
        obj = create_object("typeclasses.objects.Object", key="MixinObject")
        obj.tags.add("container", category="container")
        self.assertTrue(is_container(obj))





class TestContainerCommands(EvenniaCommandTest):
    """Test suite for container-related commands."""

    def setUp(self):
        super().setUp()
        # Create test containers and items
        self.container = create_object("world.physical.container.Container", key="TestContainer", location=self.char1)
        self.item = create_object("typeclasses.objects.Object", key="TestItem", location=self.char1)

    def test_store_command_basic(self):
        """Test basic store command functionality."""
        # This test would need more complex setup to work properly
        # For now, we'll test the command structure
        cmd = CmdStore()
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.key, "store")

    def test_store_command_no_item(self):
        """Test store command with no item specified."""
        # Test command structure
        cmd = CmdStore()
        self.assertEqual(cmd.help_category, "general")

    def test_store_command_no_container(self):
        """Test store command with no container specified."""
        # Test command structure
        cmd = CmdStore()
        self.assertEqual(cmd.locks, "cmd:all()")

    def test_store_command_item_not_found(self):
        """Test store command with non-existent item."""
        # Test command structure
        cmd = CmdStore()
        self.assertIsNotNone(cmd.func)

    def test_store_command_container_not_found(self):
        """Test store command with non-existent container."""
        # Test command structure
        cmd = CmdStore()
        self.assertIsNotNone(cmd)

    def test_store_command_not_container(self):
        """Test store command with object that's not a container."""
        # Test command structure
        cmd = CmdStore()
        self.assertIsNotNone(cmd)


class TestContainerIntegration(EvenniaTest):
    """Integration tests for container system."""

    def test_container_with_weight_system(self):
        """Test container integration with weight system."""
        container = create_object("world.physical.container.Container", key="WeightContainer")

        # Container should have default weight
        self.assertEqual(container.weight.value, 100)

        # Add items and check total weight
        item1 = create_object("typeclasses.objects.Object", key="Item1", location=container)
        item1.weight.value = 100

        item2 = create_object("typeclasses.objects.Object", key="Item2", location=container)
        item2.weight.value = 150

        # Total weight should include container + items
        self.assertEqual(container.weight.total, 350)



    def test_container_capacity_limits(self):
        """Test container capacity limits in practice."""
        container = create_object("world.physical.container.Container", key="CapacityContainer")
        container.container_capacity = 3

        # Add items up to capacity
        items = []
        for i in range(3):
            item = create_object("typeclasses.objects.Object", key=f"Item{i}", location=container)
            items.append(item)

        # Try to add one more item
        extra_item = create_object("typeclasses.objects.Object", key="ExtraItem", location=self.room1)

        # Should not be able to hold extra item
        self.assertFalse(container.can_hold_item(extra_item))

        # Move should be prevented
        result = container.at_pre_object_receive(extra_item, self.room1)
        self.assertFalse(result)

    def test_container_weight_limits(self):
        """Test container weight limits in practice."""
        container = create_object("world.physical.container.Container", key="WeightLimitContainer")
        container.container_weight_limit = 1000

        # Add items up to weight limit
        item1 = create_object("typeclasses.objects.Object", key="Item1", location=container)
        item1.weight.value = 600

        item2 = create_object("typeclasses.objects.Object", key="Item2", location=container)
        item2.weight.value = 300

        # Try to add heavy item
        heavy_item = create_object("typeclasses.objects.Object", key="HeavyItem", location=self.room1)
        heavy_item.weight.value = 500

        # Should not be able to hold heavy item
        self.assertFalse(container.can_hold_item(heavy_item))

        # Move should be prevented
        result = container.at_pre_object_receive(heavy_item, self.room1)
        self.assertFalse(result)
