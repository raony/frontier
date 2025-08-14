from evennia.utils.test_resources import EvenniaTest


class TestHoldAndLight(EvenniaTest):
    def setUp(self):
        super().setUp()
        # Ensure alive cmdset so inventory output includes held items
        from commands.default_cmdsets import AliveCmdSet

        self.char1.cmdset.add(AliveCmdSet, persistent=True)

    def test_hold_and_release(self):
        # Create a simple holdable via typeclass
        torch = self.create_object("typeclasses.items.Torch", key="torch", location=self.char1)
        # Initially not held
        assert getattr(self.char1.db, "holding", None) in (None, [])
        # Hold the torch
        self.char1.execute_cmd("hold torch")
        held = self.char1.get_holding()
        assert len(held) == 1
        # Release the torch
        self.char1.execute_cmd("release torch")
        assert self.char1.get_holding() == []

    def test_room_darkness_and_torch_light(self):
        # Make an indoor room with no sunlight
        room = self.create_object("typeclasses.rooms.Room", key="cave")
        # Override any default light to zero on room
        room.db.light_level = 0

        # Place character in the room
        self.char1.location = room

        # At start there is no light source present
        # Gate: at_look should report darkness
        out = self.char1.at_look(room)
        assert "too dark" in out.lower()

        # Drop a torch in the room and light it: should raise light
        torch = self.create_object("typeclasses.items.Torch", key="torch", location=room)
        # Off by default
        assert not getattr(torch.db, "is_on", False)
        # Command to light it won't work unless we carry it; just turn on directly for this test
        torch.turn_on(caller=self.char1)
        # Now ambient light should be above threshold 20
        ambient = room.get_light_level(looker=self.char1)
        assert ambient >= int(self.char1.light_threshold)
        # Looking should now work and not be dark
        out2 = self.char1.at_look(room)
        assert "too dark" not in out2.lower()

    def test_torch_consumes_fuel_when_on(self):
        torch = self.create_object("typeclasses.items.Torch", key="torch", location=self.char1)
        # Default full fuel
        full = float(torch.db.fuel)
        torch.turn_on(caller=self.char1)
        # Simulate some ticks
        for _ in range(3):
            torch._consume_tick()
        assert float(torch.db.fuel) < full
        # Exhaust fuel
        torch.db.consume_rate = 1000.0
        torch._consume_tick()
        assert torch.db.fuel == 0
        assert not torch.db.is_on
