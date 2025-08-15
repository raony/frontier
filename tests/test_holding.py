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
        self.assertIn('main', self.char1.held_items.slots)
        self.assertIn('off', self.char1.held_items.slots)

    def test_hold_and_release(self):
        self.assertTrue(self.char1.held_items.add(self.item1_char1_inv, slots=["main"]))
        self.assertTrue(self.char1.held_items.add(self.item2_char1_inv, slots=["off"]))
        with self.assertRaises(AlreadyHoldingError):
            self.char1.held_items.add(self.item3_char1_inv, slots=["main"])
        self.assertTrue(self.char1.held_items.remove(self.item1_char1_inv))
        self.assertTrue(self.char1.held_items.add(self.item3_char1_inv, slots=["main"]))

    def test_holding_item_not_in_inventory(self):
        with self.assertRaises(NotInInventoryError):
            self.char1.held_items.add(self.item4_char1_loc, slots=["main"])

    def test_holding_item_not_holdable(self):
        with self.assertRaises(NotHoldableError):
            self.char1.held_items.add(self.not_holdable_obj, slots=["main"])

    def test_remove_when_item_dropped(self):
        self.char1.held_items.add(self.item1_char1_inv, slots=["main"])
        self.item1_char1_inv.move_to(self.char1.location)
        self.assertEqual(len(self.char1.held_items.all), 0)
        self.assertIsNone(self.item1_char1_inv.tags.get("held", category="holding"))

    def test_remove_items(self):
        self.assertFalse(self.char1.held_items.remove(self.item1_char1_inv))
        self.assertFalse(self.char1.held_items.remove(None))
        self.assertFalse(self.char1.held_items.remove(self.item4_char1_loc))
        self.assertFalse(self.char1.held_items.remove(self.not_holdable_obj))

    def test_changing_slots(self):
        self.char1.held_items.add(self.item1_char1_inv, slots=["main"])
        self.char1.held_items.add(self.item1_char1_inv, slots=["off"])
        self.assertEqual(len(self.char1.held_items.all), 1)
        self.assertEqual(len(self.item1_char1_inv.tags.get(category="holding_slot", return_list=True)), 1)

    def test_both_hands(self):
        self.char1.held_items.add(self.item1_char1_inv, slots=["main", "off"])
        self.assertEqual(len(self.item1_char1_inv.tags.get(category="holding_slot", return_list=True, return_tagobj=True)), 2)

    def test_switch_to_both_hands(self):
        self.char1.held_items.add(self.item1_char1_inv, slots=["main"])
        self.assertTrue(self.char1.held_items.add(self.item1_char1_inv, slots=["main", "off"]))
        self.assertFalse(self.char1.held_items.add(self.item1_char1_inv, slots=["main", "off"]))
        self.assertTrue(self.char1.held_items.add(self.item1_char1_inv, slots=["main"]))
