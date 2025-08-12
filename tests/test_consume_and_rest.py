from evennia.utils.test_resources import EvenniaTest
from commands.default_cmdsets import AliveCmdSet
from evennia.utils.create import create_object


class TestConsumeAndRest(EvenniaTest):
    def setUp(self):
        super().setUp()
        # Place a water source and food in room1
        from typeclasses.liquid import LiquidContainer
        from typeclasses.food import Food

        self.water = create_object(LiquidContainer, key="waterskin", location=self.room1)
        self.food = create_object(Food, key="apple", location=self.room1)

    def test_drink_reduces_thirst(self):
        # Ensure alive cmdset active to expose gameplay commands
        self.char1.cmdset.add(AliveCmdSet, permanent=True)
        self.char1.location = self.room1
        self.char1.thirst = 50
        self.assertEqual(self.char1.thirst, 50)

        # Drink from waterskin
        self.char1.execute_cmd("drink waterskin")

        self.assertLess(self.char1.thirst, 50)

    def test_eat_reduces_hunger(self):
        self.char1.cmdset.add(AliveCmdSet, permanent=True)
        self.char1.location = self.room1
        self.char1.hunger = 50
        self.assertEqual(self.char1.hunger, 50)

        # Eat the apple
        self.char1.execute_cmd("eat apple")

        self.assertLess(self.char1.hunger, 50)

    def test_rest_and_stand_affect_state_and_metabolism(self):
        # toggle on
        self.char1.cmdset.add(AliveCmdSet, permanent=True)
        self.char1.location = self.room1
        self.char1.is_resting = False
        self.char1.execute_cmd("rest")
        self.assertTrue(self.char1.is_resting)

        # metabolism tick should reduce tiredness while resting
        self.char1.tiredness = 20
        self.char1.start_metabolism_script()
        script = self.char1.scripts.get("metabolism_script")[0]
        script.at_repeat()
        self.assertLess(self.char1.tiredness, 20)

        # 'rest' again should not stop resting
        self.char1.execute_cmd("rest")
        self.assertTrue(self.char1.is_resting)

        # 'stand' should stop resting
        self.char1.execute_cmd("stand")
        self.assertFalse(self.char1.is_resting)
