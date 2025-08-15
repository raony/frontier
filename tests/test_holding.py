from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from typeclasses.holding import HoldableItem, NoSlotsError, AlreadyHoldingError, NotInInventoryError, NotHoldableError
from typeclasses.objects import Object


class TestHolding(EvenniaTest):

    def setUp(self):
        super().setUp()
        self.item1_char1_inv = create_object(HoldableItem, key="item1_char1_inv", location=self.char1)
        self.item2_char1_inv = create_object(HoldableItem, key="item2_char1_inv", location=self.char1)
        self.item3_char1_inv = create_object(HoldableItem, key="item3_char1_inv", location=self.char1)
        self.item4_char1_loc = create_object(HoldableItem, key="item4_char1_loc", location=self.char1.location)
        self.not_holdable_obj = create_object(Object, key="not_holdable_obj", location=self.char1)

    def test_default_character_has_two_holding_slots(self):
        self.assertEqual(len(self.char1.held_items.slots), 2)
        self.assertEqual(self.char1.held_items.slots[0].db_key, 'main')
        self.assertEqual(self.char1.held_items.slots[1].db_key, 'off')

    def test_holding_and_release_no_slot_key(self):
        self.assertTrue(self.char1.held_items.add(self.item1_char1_inv))
        self.assertTrue(self.char1.held_items.add(self.item2_char1_inv))
        with self.assertRaises(NoSlotsError):
            self.char1.held_items.add(self.item3_char1_inv)
        self.assertTrue(self.char1.held_items.remove(self.item1_char1_inv))
        self.assertTrue(self.char1.held_items.add(self.item3_char1_inv))

    def test_specific_slot_key(self):
        self.assertEqual(self.char1.held_items.add(self.item1_char1_inv, slot_key="main"), "main hand")
        with self.assertRaises(AlreadyHoldingError):
            self.char1.held_items.add(self.item2_char1_inv, slot_key="main")

    def test_holding_item_not_in_inventory(self):
        with self.assertRaises(NotInInventoryError):
            self.char1.held_items.add(self.item4_char1_loc)

    def test_holding_item_not_holdable(self):
        with self.assertRaises(NotHoldableError):
            self.char1.held_items.add(self.not_holdable_obj)

    def test_remove_when_item_dropped(self):
        self.char1.held_items.add(self.item1_char1_inv)
        self.item1_char1_inv.move_to(self.char1.location)
        self.assertEqual(len(self.char1.held_items.all), 0)
        self.assertIsNone(self.item1_char1_inv.tags.get("held", category="holding"))