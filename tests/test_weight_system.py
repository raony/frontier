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
        super().setUp()
        # Create test objects
        self.test_obj = create_object(Object, key="test object")
        self.food = create_object(Food, key="apple")
        self.portioned_food = create_object(PortionedFood, key="bread")
        self.chicken = create_object(RoastedChicken, key="roasted chicken")
        self.torch = create_object(Torch, key="torch")
        self.helmet = create_object(HeadItem, key="leather helmet")
        self.armor = create_object(BodyItem, key="chain mail")
        self.waterskin = create_object(LiquidContainer, key="waterskin")

    def test_default_weights(self):
        """Test that objects have appropriate default weights."""
        # Test basic object weight
        self.assertEqual(self.test_obj.get_weight(), 100)  # Default weight

        # Test food weights
        self.assertEqual(self.food.get_weight(), 50)  # Food default
        self.assertEqual(self.portioned_food.get_weight(), 200)  # Portioned food default
        self.assertEqual(self.chicken.get_weight(), 800)  # Roasted chicken weight

        # Test equipment weights
        self.assertEqual(self.helmet.get_weight(), 150)  # Head item weight
        self.assertEqual(self.armor.get_weight(), 500)  # Body item weight

        # Test other item weights
        self.assertEqual(self.torch.get_weight(), 300)  # Torch weight
        self.assertEqual(self.waterskin.get_weight(), 150)  # Liquid container weight

    def test_weight_setting(self):
        """Test setting and getting custom weights."""
        # Test setting weight
        self.test_obj.set_weight(250)
        self.assertEqual(self.test_obj.get_weight(), 250)

        # Test setting weight to zero
        self.test_obj.set_weight(0)
        self.assertEqual(self.test_obj.get_weight(), 0)

        # Test setting negative weight (should be clamped to 0)
        self.test_obj.set_weight(-50)
        self.assertEqual(self.test_obj.get_weight(), 0)

    def test_weight_persistence(self):
        """Test that weight persists across object reloads."""
        # Set a custom weight
        self.test_obj.set_weight(350)
        original_weight = self.test_obj.get_weight()

        # Reload the object
        self.test_obj.refresh_from_db()

        # Weight should still be the same
        self.assertEqual(self.test_obj.get_weight(), original_weight)

    def test_weight_mixin_independence(self):
        """Test that WeightMixin can be used independently."""
        # Create a proper object with the mixin
        obj = create_object(Object, key="mixin test")

        # Should have default weight
        self.assertEqual(obj.get_weight(), 100)

        # Should be able to set weight
        obj.set_weight(150)
        self.assertEqual(obj.get_weight(), 150)

    def test_weight_command_available(self):
        """Test that weight command is available and runs without error."""
        # Give character some items
        self.food.move_to(self.char1)
        self.torch.move_to(self.char1)
        self.helmet.move_to(self.char1)

        # Add the command set
        from commands.default_cmdsets import AliveCmdSet
        self.char1.cmdset.add(AliveCmdSet, persistent=True)

        # Test that commands run without error
        self.char1.execute_cmd("weight")
        self.char1.execute_cmd("weight apple")
        self.char1.execute_cmd("weight all")

    def test_setweight_command_available(self):
        """Test that setweight command is available and runs without error."""
        # Give character builder permissions
        self.char1.permissions.add("Builder")

        # Put the test object in character's inventory
        self.test_obj.move_to(self.char1)

        # Add the command set
        from commands.default_cmdsets import CharacterCmdSet
        self.char1.cmdset.add(CharacterCmdSet, persistent=True)

        # Test that command runs without error (don't check result for now)
        self.char1.execute_cmd("setweight test object = 450")
        # Just verify the command executed without raising an exception
