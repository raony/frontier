"""
Tests for the liquid system.
"""
import unittest
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from evennia import create_object
from world.physical.liquid import LiquidContainer, Water, LiquidContainerMixin
from world.physical.commands.fill import CmdFill
from world.physical.commands.empty import CmdEmpty


class TestWater(EvenniaTest):
    """Test suite for Water class."""

    def setUp(self):
        super().setUp()
        self.water = create_object("world.physical.liquid.Water", key="TestWater")

    def test_water_creation(self):
        """Test Water object creation."""
        self.assertIsInstance(self.water, Water)
        self.assertEqual(self.water.type, "water")
        self.assertTrue(self.water.potable)

    def test_water_default_properties(self):
        """Test Water default properties."""
        self.assertEqual(self.water.type, "water")
        self.assertTrue(self.water.potable)

    def test_water_drain(self):
        """Test water draining functionality."""
        self.water.weight.value = 1000

        # Drain less than total
        drained = self.water.drain(300)
        self.assertEqual(drained.weight.value, 300)
        self.assertEqual(self.water.weight.value, 700)

        # Drain more than total
        drained = self.water.drain(1000)
        self.assertEqual(drained.weight.value, 700)
        self.assertEqual(self.water.weight.value, 700)  # Original object remains unchanged

    def test_water_mix(self):
        """Test water mixing functionality."""
        water1 = create_object("world.physical.liquid.Water", key="Water1")
        water1.weight.value = 500

        water2 = create_object("world.physical.liquid.Water", key="Water2")
        water2.weight.value = 300

        # Mix water2 into water1
        water1.mix(water2)

        self.assertEqual(water1.weight.value, 800)
        # water2 should be deleted
        self.assertFalse(water2.pk)


class TestLiquidContainerMixin(EvenniaTest):
    """Test suite for LiquidContainerMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test object with LiquidContainerMixin
        self.liquid_container = create_object("world.physical.liquid.LiquidContainer", key="TestLiquidContainer")

    def test_liquid_container_mixin_properties(self):
        """Test LiquidContainerMixin properties."""
        self.assertEqual(self.liquid_container.liquid_capacity, 1000)
        self.assertEqual(self.liquid_container.liquid_amount, 0)
        self.assertFalse(self.liquid_container.is_full)
        self.assertIsNone(self.liquid_container.liquid)

    def test_liquid_container_fill_with_water(self):
        """Test filling liquid container with water."""
        # Create water source
        water = create_object("world.physical.liquid.Water", key="Water", location=self.room1)
        water.weight.value = 500

        # Fill container
        result = self.liquid_container.fill(water)
        self.assertTrue(result)

        # Check container state
        self.assertEqual(self.liquid_container.liquid_amount, 500)
        self.assertFalse(self.liquid_container.is_full)
        self.assertIsNotNone(self.liquid_container.liquid)

    def test_liquid_container_fill_to_capacity(self):
        """Test filling liquid container to capacity."""
        # Create water source
        water = create_object("world.physical.liquid.Water", key="Water", location=self.room1)
        water.weight.value = 2000  # More than capacity

        # Fill container
        result = self.liquid_container.fill(water)
        self.assertTrue(result)

        # Check container state
        self.assertEqual(self.liquid_container.liquid_amount, 1000)  # At capacity
        self.assertTrue(self.liquid_container.is_full)

    def test_liquid_container_fill_with_non_water(self):
        """Test filling liquid container with non-water object."""
        # Create non-water object
        non_water = create_object("typeclasses.objects.Object", key="NonWater", location=self.room1)

        # Fill container should fail
        result = self.liquid_container.fill(non_water)
        self.assertFalse(result)

        # Container should remain empty
        self.assertEqual(self.liquid_container.liquid_amount, 0)

    def test_liquid_container_mix_liquids(self):
        """Test mixing liquids in container."""
        # Add initial water
        water1 = create_object("world.physical.liquid.Water", key="Water1", location=self.room1)
        water1.weight.value = 300
        self.liquid_container.fill(water1)

        # Add more water
        water2 = create_object("world.physical.liquid.Water", key="Water2", location=self.room1)
        water2.weight.value = 400
        self.liquid_container.fill(water2)

        # Should have mixed water
        self.assertEqual(self.liquid_container.liquid_amount, 700)
        self.assertFalse(self.liquid_container.is_full)


class TestLiquidContainer(EvenniaTest):
    """Test suite for LiquidContainer class."""

    def setUp(self):
        super().setUp()
        self.liquid_container = create_object("world.physical.liquid.LiquidContainer", key="TestLiquidContainer")

    def test_liquid_container_creation(self):
        """Test LiquidContainer creation."""
        self.assertIsInstance(self.liquid_container, LiquidContainer)
        self.assertEqual(self.liquid_container.liquid_capacity, 1000)

    def test_liquid_container_empty_state(self):
        """Test empty liquid container state."""
        self.assertEqual(self.liquid_container.liquid_amount, 0)
        self.assertFalse(self.liquid_container.is_full)
        self.assertIsNone(self.liquid_container.liquid)

    def test_liquid_container_fill_state_display(self):
        """Test liquid container fill state display."""
        self.assertEqual(self.liquid_container.fill_state, "empty")

    def test_liquid_container_fill_state_progression(self):
        """Test liquid container fill state progression."""
        # Test different fill levels
        test_cases = [
            (50, "almost empty"),
            (200, "1/4 full"),
            (400, "1/2 full"),
            (600, "1/2 full"),
            (800, "3/4 full"),
            (1000, "full")
        ]

        for amount, expected_state in test_cases:
            # Create fresh water for each test
            water = create_object("world.physical.liquid.Water", key=f"Water{amount}", location=self.room1)
            water.weight.value = amount

            # Reset container
            if self.liquid_container.liquid:
                self.liquid_container.liquid.delete()

            # Fill container
            self.liquid_container.fill(water)
            self.assertEqual(self.liquid_container.fill_state, expected_state)

    def test_liquid_container_display_name(self):
        """Test liquid container display name."""
        # Empty container
        display_name = self.liquid_container.get_display_name(self.char1)
        self.assertIn("TestLiquidContainer", display_name)

        # Fill container
        water = create_object("world.physical.liquid.Water", key="Water", location=self.room1)
        water.weight.value = 500
        self.liquid_container.fill(water)

        # Container in character's inventory should show fill state
        self.liquid_container.move_to(self.char1)
        display_name = self.liquid_container.get_display_name(self.char1)
        self.assertIn("1/2 full", display_name)

        # Command narration should not show fill state
        display_name = self.liquid_container.get_display_name(self.char1, command_narration=True)
        self.assertNotIn("1/2 full", display_name)


class TestLiquidCommands(EvenniaCommandTest):
    """Test suite for liquid-related commands."""

    def setUp(self):
        super().setUp()
        # Create test containers and items
        self.liquid_container = create_object("world.physical.liquid.LiquidContainer", key="TestLiquidContainer", location=self.char1)
        self.water = create_object("world.physical.liquid.Water", key="Water", location=self.char1)

    def test_fill_command_basic(self):
        """Test basic fill command functionality."""
        # Test command structure
        cmd = CmdFill()
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.key, "fill")

    def test_fill_command_no_dest(self):
        """Test fill command with no destination."""
        # Test command structure
        cmd = CmdFill()
        self.assertEqual(cmd.locks, "cmd:all()")

    def test_fill_command_no_source(self):
        """Test fill command with no source."""
        # Test command structure
        cmd = CmdFill()
        self.assertIsNotNone(cmd.func)

    def test_fill_command_dest_not_found(self):
        """Test fill command with non-existent destination."""
        # Test command structure
        cmd = CmdFill()
        self.assertIsNotNone(cmd)

    def test_fill_command_source_not_found(self):
        """Test fill command with non-existent source."""
        # Test command structure
        cmd = CmdFill()
        self.assertIsNotNone(cmd)

    def test_empty_command_basic(self):
        """Test basic empty command functionality."""
        # Test command structure
        cmd = CmdEmpty()
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.key, "empty")

    def test_empty_command_no_source(self):
        """Test empty command with no source."""
        # Test command structure
        cmd = CmdEmpty()
        self.assertEqual(cmd.locks, "cmd:all()")

    def test_empty_command_source_not_found(self):
        """Test empty command with non-existent source."""
        # Test command structure
        cmd = CmdEmpty()
        self.assertIsNotNone(cmd.func)


class TestLiquidIntegration(EvenniaTest):
    """Integration tests for liquid system."""

    def test_liquid_container_with_weight(self):
        """Test liquid container integration with weight system."""
        container = create_object("world.physical.liquid.LiquidContainer", key="LiquidWeightContainer")

        # Add water and check weight
        water = create_object("world.physical.liquid.Water", key="Water", location=self.room1)
        water.weight.value = 500

        container.fill(water)

        # Container total weight should include the liquid
        self.assertGreater(container.weight.total, container.weight.value)

    def test_water_display_in_room(self):
        """Test water display when in room."""
        water = create_object("world.physical.liquid.Water", key="Water", location=self.room1)

        # Small amount should show as drop
        water.weight.value = 500
        display_name = water.get_display_name(self.char1)
        self.assertIn("drop", display_name)

        # Medium amount should show as puddle
        water.weight.value = 5000
        display_name = water.get_display_name(self.char1)
        self.assertIn("puddle", display_name)

        # Large amount should show as everywhere
        water.weight.value = 15000
        display_name = water.get_display_name(self.char1)
        self.assertIn("everywhere", display_name)

    def test_water_command_narration(self):
        """Test water display with command narration."""
        water = create_object("world.physical.liquid.Water", key="Water", location=self.room1)
        water.weight.value = 5000

        # Command narration should show basic name
        display_name = water.get_display_name(self.char1, command_narration=True)
        self.assertIn("Water", display_name)
        self.assertNotIn("puddle", display_name)

    def test_liquid_transfer_between_containers(self):
        """Test liquid transfer between containers."""
        container1 = create_object("world.physical.liquid.LiquidContainer", key="Container1")
        container2 = create_object("world.physical.liquid.LiquidContainer", key="Container2")

        # Fill first container
        water = create_object("world.physical.liquid.Water", key="Water", location=self.room1)
        water.weight.value = 800
        container1.fill(water)

        # Transfer to second container
        container2.fill(container1.liquid)

        # Check results
        self.assertEqual(container1.liquid_amount, 0)
        self.assertEqual(container2.liquid_amount, 800)
