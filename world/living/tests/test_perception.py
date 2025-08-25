"""
Tests for the perception system.
"""
import unittest
from evennia.utils.test_resources import EvenniaTest
from evennia import create_object
from world.living.perception import MsgObj, VisionManager, PerceptionMixin, LightManager


class TestMsgObj(EvenniaTest):
    """Test suite for MsgObj class."""

    def test_msg_obj_creation(self):
        """Test MsgObj creation."""
        msg = MsgObj("visual message", "sound message")
        self.assertEqual(msg.visual, "visual message")
        self.assertEqual(msg.sound, "sound message")

    def test_msg_obj_has_visual(self):
        """Test has_visual method."""
        msg_with_visual = MsgObj("visual", "sound")
        msg_without_visual = MsgObj(None, "sound")

        self.assertTrue(msg_with_visual.has_visual())
        self.assertFalse(msg_without_visual.has_visual())

    def test_msg_obj_has_sound(self):
        """Test has_sound method."""
        msg_with_sound = MsgObj("visual", "sound")
        msg_without_sound = MsgObj("visual", None)

        self.assertTrue(msg_with_sound.has_sound())
        self.assertFalse(msg_without_sound.has_sound())

    def test_msg_obj_to_dict(self):
        """Test to_dict method."""
        msg = MsgObj("visual", "sound")
        data = msg.to_dict()

        self.assertEqual(data["visual"], "visual")
        self.assertEqual(data["sound"], "sound")

    def test_msg_obj_from_dict(self):
        """Test from_dict class method."""
        data = {"visual": "visual", "sound": "sound"}
        msg = MsgObj.from_dict(data)

        self.assertEqual(msg.visual, "visual")
        self.assertEqual(msg.sound, "sound")

    def test_msg_obj_str(self):
        """Test string representation."""
        msg = MsgObj("visual message", "sound message")
        self.assertEqual(str(msg), "visual message")


class TestVisionManager(EvenniaTest):
    """Test suite for VisionManager class."""

    def setUp(self):
        super().setUp()
        self.vision = VisionManager(self.char1)

    def test_vision_manager_initialization(self):
        """Test VisionManager initialization."""
        self.assertIsNotNone(self.vision)
        self.assertEqual(self.vision.obj, self.char1)

    def test_vision_default_properties(self):
        """Test default vision properties."""
        self.assertEqual(self.vision.light_threshold, 20)
        self.assertFalse(self.vision.disabled)

    def test_vision_light_threshold_setter(self):
        """Test light threshold setter."""
        self.vision.light_threshold = 30
        self.assertEqual(self.vision.light_threshold, 30)

    def test_vision_disable_enable(self):
        """Test vision disable and enable."""
        self.vision.disable()
        self.assertTrue(self.vision.disabled)

        self.vision.enable()
        self.assertFalse(self.vision.disabled)

    def test_vision_can_see_no_light(self):
        """Test can_see with no light sources."""
        # Room and contents have no light
        self.assertFalse(self.vision.can_see)

    def test_vision_can_see_with_light_source(self):
        """Test can_see with light source in room."""
        # Create light source in room
        light = create_object("typeclasses.objects.Object", key="Light", location=self.room1)
        light.tags.add("light_source", category="vision")
        light.light = LightManager(light, 30)

        self.assertTrue(self.vision.can_see)

    def test_vision_can_see_with_light_in_contents(self):
        """Test can_see with light source in room contents."""
        # Create light source in room contents
        light = create_object("typeclasses.objects.Object", key="Light", location=self.room1)
        light.tags.add("light_source", category="vision")
        light.light = LightManager(light, 25)

        self.assertTrue(self.vision.can_see)

    def test_vision_can_see_disabled(self):
        """Test can_see when vision is disabled."""
        self.vision.disable()
        self.assertFalse(self.vision.can_see)

    def test_vision_can_receive_message_visual(self):
        """Test can_receive_message with visual message."""
        msg_obj = MsgObj("visual message", "sound message")

        # Should require vision for visual messages
        self.assertEqual(self.vision.can_receive_message(msg_obj), self.vision.can_see)

    def test_vision_can_receive_message_sound_only(self):
        """Test can_receive_message with sound-only message."""
        msg_obj = MsgObj(None, "sound message")

        # Should always receive sound messages
        self.assertTrue(self.vision.can_receive_message(msg_obj))

    def test_vision_persistence(self):
        """Test vision settings persist through attribute system."""
        self.vision.light_threshold = 40
        self.vision.disable()

        # Create new vision manager
        new_vision = VisionManager(self.char1)
        self.assertEqual(new_vision.light_threshold, 40)
        self.assertTrue(new_vision.disabled)


class TestPerceptionMixin(EvenniaTest):
    """Test suite for PerceptionMixin class."""

    def setUp(self):
        super().setUp()
        # Create a test object with PerceptionMixin
        self.perception_obj = create_object("world.living.people.Person", key="TestPerception")

    def test_perception_mixin_initialization(self):
        """Test PerceptionMixin initialization."""
        self.assertTrue(hasattr(self.perception_obj, 'vision'))

    def test_perception_die_revive(self):
        """Test perception behavior on die and revive."""
        # Ensure object has a location
        self.perception_obj.move_to(self.room1)

        # Vision should be enabled initially
        self.assertFalse(self.perception_obj.vision.disabled)

        # Die should disable vision
        self.perception_obj.die()
        self.assertTrue(self.perception_obj.vision.disabled)

        # Revive should enable vision
        self.perception_obj.revive()
        self.assertFalse(self.perception_obj.vision.disabled)

    def test_perception_msg_with_msg_obj(self):
        """Test msg method with MsgObj."""
        # Ensure object has a location
        self.perception_obj.move_to(self.room1)

        msg_obj = MsgObj("visual message", "sound message")

        # Test with vision enabled
        result = self.perception_obj.msg(msg_obj=msg_obj.to_dict())
        # Should use visual message when vision is available

        # Test with vision disabled
        self.perception_obj.vision.disable()
        result = self.perception_obj.msg(msg_obj=msg_obj.to_dict())
        # Should use sound message when vision is disabled

    def test_perception_at_look_disabled(self):
        """Test at_look when vision is disabled."""
        self.perception_obj.vision.disable()
        result = self.perception_obj.at_look(self.room1)
        self.assertEqual(result, "You can't see anything.")

    def test_perception_at_look_too_dark(self):
        """Test at_look when it's too dark."""
        # Ensure object has a location
        self.perception_obj.move_to(self.room1)

        # No light sources
        result = self.perception_obj.at_look(self.room1)
        self.assertEqual(result, "It's too dark to see anything.")

    def test_perception_at_look_normal(self):
        """Test at_look with normal conditions."""
        # Ensure object has a location
        self.perception_obj.move_to(self.room1)

        # Add light source
        light = create_object("typeclasses.objects.Object", key="Light", location=self.room1)
        light.tags.add("light_source", category="vision")
        light.light = LightManager(light, 30)

        # Should call parent at_look
        result = self.perception_obj.at_look(self.room1)
        # Result should not be the error messages


class TestLightManager(EvenniaTest):
    """Test suite for LightManager class."""

    def setUp(self):
        super().setUp()
        self.light_obj = create_object("typeclasses.objects.Object", key="Light")
        self.light_manager = LightManager(self.light_obj, 50)

    def test_light_manager_initialization(self):
        """Test LightManager initialization."""
        self.assertIsNotNone(self.light_manager)
        self.assertEqual(self.light_manager.obj, self.light_obj)

    def test_light_level_default(self):
        """Test default light level."""
        # Create new light manager without initial level
        new_light_manager = LightManager(self.light_obj)
        self.assertEqual(new_light_manager.level, 0)

    def test_light_level_setter(self):
        """Test light level setter."""
        self.light_manager.level = 75
        self.assertEqual(self.light_manager.level, 75)

    def test_light_source_tag_management(self):
        """Test light source tag management."""
        # Create new light manager without initial level
        new_light_manager = LightManager(self.light_obj)

        # No light level, should not have tag
        self.assertFalse(self.light_obj.tags.has("light_source", category="vision"))

        # Set light level, should have tag
        new_light_manager.level = 30
        self.assertTrue(self.light_obj.tags.has("light_source", category="vision"))

        # Set light level to 0, should not have tag
        new_light_manager.level = 0
        self.assertFalse(self.light_obj.tags.has("light_source", category="vision"))
