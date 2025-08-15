from evennia import create_object
from evennia.utils.test_resources import EvenniaTest
from typeclasses.characters import Character


class TestLight(EvenniaTest):
    def test_room_darkness_and_torch_light(self):
        # Make an indoor room with no sunlight
        room = create_object("typeclasses.rooms.Room", key="cave")
        # Override any default light to zero on room
        room.db.light_level = 0

        # Place character in the room
        self.char1.location = room

        # At start there is no light source present
        # Gate: at_look should report darkness
        out = self.char1.at_look(room)
        self.assertIn("too dark", out.lower())

        # Drop a torch in the room and light it: should raise light
        torch = create_object("typeclasses.items.Torch", key="torch", location=room)
        # Off by default
        self.assertFalse(getattr(torch.db, "is_on", False))
        # Command to light it won't work unless we carry it; just turn on directly for this test
        torch.turn_on(caller=self.char1)
        # Now ambient light should be above threshold 20
        ambient = room.get_light_level(looker=self.char1)
        self.assertGreaterEqual(ambient, int(self.char1.light_threshold))
        # Looking should now work and not be dark
        out2 = self.char1.at_look(room)
        self.assertNotIn("too dark", out2.lower())

    def test_torch_consumes_fuel_when_on(self):
        torch = create_object("typeclasses.items.Torch", key="torch", location=self.char1)
        # Default full fuel
        full = float(torch.db.fuel)
        torch.turn_on(caller=self.char1)
        # Simulate some ticks
        for _ in range(3):
            torch._consume_tick()
        self.assertLess(float(torch.db.fuel), full)
        # Exhaust fuel
        torch.db.consume_rate = 1000.0
        torch._consume_tick()
        self.assertEqual(torch.db.fuel, 0)
        self.assertFalse(torch.db.is_on)

    def test_darkvision_command(self):
        # Give character builder permissions
        self.char1.permissions.add("Builder")
        # Add darkvision command
        from commands.default_cmdsets import CharacterCmdSet
        self.char1.cmdset.add(CharacterCmdSet, persistent=True)

        # Initial threshold should be 20
        self.assertEqual(self.char1.light_threshold, 20)

        # Enable darkvision
        self.char1.execute_cmd("darkvision")
        self.assertEqual(self.char1.light_threshold, 0)

        # Disable darkvision
        self.char1.execute_cmd("darkvision")
        self.assertEqual(self.char1.light_threshold, 20)
