from evennia.utils.test_resources import EvenniaTest


class TestHexRoomLinkage(EvenniaTest):
    def test_set_hex_and_weather(self):
        room = self.room1
        # Link to a valid cube coordinate
        tile = room.set_hex_by_coords(0, 1, -1)
        assert tile.q == 0 and tile.r == 1 and tile.s == -1
        assert room.get_hex_coords() == (0, 1, -1)

        # Default terrain is 'plain' -> weather 'clear'
        assert room.get_hex_weather() == "clear"

        # Change terrain to something else and verify weather mapping
        tile.terrain = "forest"
        tile.save()
        assert room.get_hex_weather() == "overcast"

    def test_invalid_coords_raise(self):
        room = self.room1
        try:
            # Invalid because q + r + s != 0
            room.set_hex_by_coords(1, 0, 0)
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for invalid cube coords")
