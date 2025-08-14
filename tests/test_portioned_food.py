from evennia.utils.test_resources import EvenniaTest
from commands.default_cmdsets import AliveCmdSet
from evennia.utils.create import create_object


class TestPortionedFood(EvenniaTest):
    def test_roasted_chicken_portions_and_hunger(self):
        from typeclasses.food import RoastedChicken

        chicken = create_object(RoastedChicken, key="roasted chicken", location=self.room1)
        self.char1.location = self.room1
        self.char1.cmdset.add(AliveCmdSet, persistent=True)

        # initial portions
        self.assertEqual(chicken.db.parts_total, 6)
        self.assertEqual(chicken.db.parts_left, 6)

        # set hunger and eat once
        self.char1.hunger = 10
        self.char1.execute_cmd("eat roasted chicken")

        # hunger reduced by calories_per_part (clamped 1..7, here 3)
        self.assertEqual(self.char1.hunger, 7)
        self.assertEqual(chicken.db.parts_left, 5)

        # eat remaining portions
        for _ in range(5):
            self.char1.execute_cmd("eat roasted chicken")

        # chicken should be deleted after last portion
        self.assertIsNone(chicken.pk)
