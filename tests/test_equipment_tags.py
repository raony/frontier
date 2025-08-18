"""Test equipment tag system alongside existing attribute-based system."""

from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from typeclasses.items import HeadItem, BodyItem
from typeclasses.objects import Object
from typeclasses.equipment import AlreadyEquippedError, NotEquippableError


class TestEquipmentTags(EvenniaTest):
    """Test the tag-based equipment system alongside the existing system."""

    def setUp(self):
        super().setUp()
        # Create test items
        self.head_item = create_object(HeadItem, key="test_helmet", location=self.char1)
        self.body_item = create_object(BodyItem, key="test_armor", location=self.char1)
        self.another_head_item = create_object(HeadItem, key="another_helmet", location=self.char1)
        self.regular_item = create_object(Object, key="regular_item", location=self.char1)

    def test_character_has_equipment_slots(self):
        """Test that character has equipment slot tags."""
        slots = self.char1.tags.get(category="equipment_slot", return_list=True)
        self.assertEqual(len(slots), 6)
        self.assertIn("head", slots)
        self.assertIn("body", slots)
        self.assertIn("legs", slots)
        self.assertIn("waist", slots)
        self.assertIn("hands", slots)
        self.assertIn("feet", slots)

    def test_equipment_items_have_wearable_tags(self):
        """Test that equipment items have wearable tags."""
        self.assertTrue(self.head_item.tags.has("equipable", category="equipment"))
        self.assertTrue(self.body_item.tags.has("equipable", category="equipment"))
        self.assertFalse(self.regular_item.tags.has("equipable", category="equipment"))

    def test_equipment_items_have_slot_tags(self):
        """Test that equipment items have appropriate slot tags."""
        self.assertTrue(self.head_item.tags.has("head", category="default_wearing_slot"))
        self.assertTrue(self.body_item.tags.has("body", category="default_wearing_slot"))

    def test_equip(self):
        """Test that equipment items can be equipped."""
        self.assertTrue(self.char1.equipment.add(self.head_item))
        self.assertTrue(self.head_item.tags.has("equipped", category="equipment"))
        self.assertTrue(self.head_item.tags.has("head", category="equipment_slot"))
        self.assertEqual(self.head_item.get_display_name(), "test_helmet (head)")
        self.assertTrue(self.char1.equipment.add(self.body_item))
        self.assertTrue(self.body_item.tags.has("equipped", category="equipment"))
        self.assertTrue(self.body_item.tags.has("body", category="equipment_slot"))
        self.assertEqual(self.body_item.get_display_name(), "test_armor (body)")

        with self.assertRaises(AlreadyEquippedError):
            self.char1.equipment.add(self.another_head_item)

        with self.assertRaises(NotEquippableError):
            self.char1.equipment.add(self.regular_item)

        self.assertTrue(self.char1.equipment.remove(self.head_item))
        self.assertFalse(self.head_item.tags.has("equipped", category="equipment"))
        self.assertFalse(self.head_item.tags.has("head", category="equipment_slot"))
        self.assertEqual(self.head_item.get_display_name(), "test_helmet")

        self.assertTrue(self.char1.equipment.add(self.another_head_item))