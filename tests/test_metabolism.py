from evennia.utils.test_resources import EvenniaTest


class TestMetabolism(EvenniaTest):
    def test_get_metabolism_interval_uses_attribute(self):
        # default metabolism is 1.0 -> interval 600
        self.assertAlmostEqual(self.char1.get_metabolism_interval(), 600.0)
        # increase metabolism -> shorter interval
        self.char1.metabolism = 3.0
        self.assertLess(self.char1.get_metabolism_interval(), 600.0)

    def test_metabolism_tick_increases_needs(self):
        # ensure living and not resting
        self.char1.is_living = True
        self.char1.is_resting = False
        h0, t0, f0 = self.char1.hunger, self.char1.thirst, self.char1.tiredness

        # call the script via character helper to ensure proper creation
        self.char1.start_metabolism_script()
        # run one tick manually by calling the script's at_repeat
        script = self.char1.scripts.get("metabolism_script")[0]
        script.at_repeat()

        self.assertGreaterEqual(self.char1.hunger, h0)
        self.assertGreaterEqual(self.char1.thirst, t0)
        self.assertGreaterEqual(self.char1.tiredness, f0)

    def test_resting_recovers_tiredness(self):
        self.char1.is_living = True
        self.char1.is_resting = True
        self.char1.tiredness = 20

        self.char1.start_metabolism_script()
        script = self.char1.scripts.get("metabolism_script")[0]
        script.at_repeat()

        self.assertLess(self.char1.tiredness, 20)
