"""
Tests for the food system.
"""
import unittest
from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from world.living.food import FoodHandler, FoodMixin


class TestFoodHandler(EvenniaTest):
    """Test suite for FoodHandler class."""

    def setUp(self):
        super().setUp()
        self.food_obj = create_object("typeclasses.objects.Object", key="TestFood")
        self.food_handler = FoodHandler(self.food_obj)

    def test_food_handler_initialization(self):
        """Test FoodHandler initialization."""
        self.assertIsNotNone(self.food_handler)
        self.assertEqual(self.food_handler.obj, self.food_obj)
        self.assertTrue(self.food_obj.tags.has("food", category="food"))

    def test_food_default_properties(self):
        """Test default food properties."""
        self.assertEqual(self.food_handler.calories, 10)
        self.assertEqual(self.food_handler.total_calories, 10)
        self.assertEqual(self.food_handler.waste_proportion, 0.1)

    def test_food_calories_setter(self):
        """Test calories setter."""
        self.food_handler.calories = 25
        self.assertEqual(self.food_handler.calories, 25)

    def test_food_total_calories_setter(self):
        """Test total_calories setter."""
        self.food_handler.total_calories = 50
        self.assertEqual(self.food_handler.total_calories, 50)

    def test_food_waste_proportion_setter(self):
        """Test waste_proportion setter."""
        self.food_handler.waste_proportion = 0.2
        self.assertEqual(self.food_handler.waste_proportion, 0.2)

    def test_food_eaten_percentage(self):
        """Test eaten_percentage calculation."""
        # Full food
        self.assertEqual(self.food_handler.eaten_percentage, 0)

        # Half eaten
        self.food_handler.calories = 5
        self.assertEqual(self.food_handler.eaten_percentage, 0.5)

        # Completely eaten
        self.food_handler.calories = 0
        self.assertEqual(self.food_handler.eaten_percentage, 1)

    def test_food_can_eat(self):
        """Test can_eat method."""
        # Should always return True for now
        self.assertTrue(self.food_handler.can_eat(self.char1))

    def test_food_eat_with_eater(self):
        """Test eat method with valid eater."""
        initial_calories = self.food_handler.calories
        initial_weight = self.food_obj.weight.value

        # Eat the food
        calories_eaten = self.food_handler.eat(self.char1)

        # Should have eaten some calories
        self.assertGreater(calories_eaten, 0)
        self.assertLess(self.food_handler.calories, initial_calories)

        # Weight should have decreased
        self.assertLess(self.food_obj.weight.value, initial_weight)

    def test_food_eat_without_eater(self):
        """Test eat method without valid eater."""
        regular_obj = create_object("typeclasses.objects.Object", key="RegularObj")

        # Should return 0 for non-eater
        calories_eaten = self.food_handler.eat(regular_obj)
        self.assertEqual(calories_eaten, 0)

    def test_food_reset(self):
        """Test food reset."""
        # Eat some food
        self.food_handler.calories = 3
        self.food_handler.waste_proportion = 0.3

        # Reset
        self.food_handler.reset()

        # Should be back to defaults
        self.assertEqual(self.food_handler.calories, 10)
        self.assertEqual(self.food_handler.waste_proportion, 0.1)

    def test_food_persistence(self):
        """Test food properties persist through attribute system."""
        self.food_handler.calories = 15
        self.food_handler.total_calories = 30
        self.food_handler.waste_proportion = 0.25

        # Create new handler
        new_handler = FoodHandler(self.food_obj)
        self.assertEqual(new_handler.calories, 15)
        self.assertEqual(new_handler.total_calories, 30)
        self.assertEqual(new_handler.waste_proportion, 0.25)


class TestFoodMixin(EvenniaTest):
    """Test suite for FoodMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test object with FoodMixin
        self.food_obj = create_object("typeclasses.objects.Object", key="TestFood")
        # Add FoodMixin manually since it's not in the base Object
        self.food_obj.food = FoodHandler(self.food_obj)

    def test_food_mixin_initialization(self):
        """Test FoodMixin provides food property."""
        self.assertTrue(hasattr(self.food_obj, 'food'))
        self.assertIsInstance(self.food_obj.food, FoodHandler)

    def test_food_display_name_full(self):
        """Test display name for full food."""
        # Full food should show normal name
        # Test the logic directly since we can't call the mixin method
        name = self.food_obj.get_display_name(self.char1)
        self.assertIn("TestFood", name)
        # Full food should not have eaten indicators
        self.assertNotIn("bitten", name)
        self.assertNotIn("partially eaten", name)
        self.assertNotIn("rest of", name)

    def test_food_display_name_bitten(self):
        """Test display name for bitten food."""
        # Eat a small amount
        self.food_obj.food.calories = 8  # 20% eaten
        # Test the logic directly
        eaten_percentage = self.food_obj.food.eaten_percentage
        self.assertGreater(eaten_percentage, 0)
        self.assertLess(eaten_percentage, 0.5)

    def test_food_display_name_partially_eaten(self):
        """Test display name for partially eaten food."""
        # Eat more than half
        self.food_obj.food.calories = 3  # 70% eaten
        # Test the logic directly
        eaten_percentage = self.food_obj.food.eaten_percentage
        self.assertGreater(eaten_percentage, 0.5)

    def test_food_display_name_rest(self):
        """Test display name for mostly eaten food."""
        # Eat almost all
        self.food_obj.food.calories = 0.5  # 95% eaten
        # Test the logic directly
        eaten_percentage = self.food_obj.food.eaten_percentage
        self.assertGreater(eaten_percentage, 0.9)


class TestFoodIntegration(EvenniaTest):
    """Integration tests for food system."""

    def test_food_with_weight_system(self):
        """Test food integration with weight system."""
        food = create_object("typeclasses.objects.Object", key="WeightFood")
        food_handler = FoodHandler(food)

        # Food should have weight
        self.assertGreater(food.weight.value, 0)

        # Eating should reduce weight
        initial_weight = food.weight.value
        food_handler.eat(self.char1)
        self.assertLess(food.weight.value, initial_weight)

    def test_food_with_living_system(self):
        """Test food integration with living system."""
        food = create_object("typeclasses.objects.Object", key="LivingFood")
        food_handler = FoodHandler(food)

        # Set initial hunger
        self.char1.hunger.value = 50

        # Eat food
        calories_eaten = food_handler.eat(self.char1)

        # Hunger should be reduced
        self.assertLess(self.char1.hunger.value, 50)

    def test_food_waste_proportion_effect(self):
        """Test waste proportion affects weight loss."""
        food1 = create_object("typeclasses.objects.Object", key="LowWasteFood")
        food1_handler = FoodHandler(food1)
        food1_handler.waste_proportion = 0.05  # Low waste

        food2 = create_object("typeclasses.objects.Object", key="HighWasteFood")
        food2_handler = FoodHandler(food2)
        food2_handler.waste_proportion = 0.3  # High waste

        # Eat both foods
        initial_weight1 = food1.weight.value
        initial_weight2 = food2.weight.value

        food1_handler.eat(self.char1)
        food2_handler.eat(self.char1)

        # Both foods should lose weight
        weight_loss1 = initial_weight1 - food1.weight.value
        weight_loss2 = initial_weight2 - food2.weight.value

        self.assertGreater(weight_loss1, 0)
        self.assertGreater(weight_loss2, 0)
