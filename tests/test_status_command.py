from evennia.utils.test_resources import EvenniaTest
from commands.default_cmdsets import AliveCmdSet


class TestStatusCommand(EvenniaTest):
    def test_label_helpers_map_levels(self):
        # Hunger thresholds: 0->sated, 7->hungry, 30->starving, 60->starving to death
        self.char1.hunger = 0
        assert self.char1.get_hunger_label() == "sated"
        self.char1.hunger = 7
        assert self.char1.get_hunger_label() == "hungry"
        self.char1.hunger = 35
        assert self.char1.get_hunger_label() == "starving"
        self.char1.hunger = 65
        assert self.char1.get_hunger_label() == "starving to death"

        # Thirst thresholds: 0->quenched, 7->thirsty, 30->parched, 60->dying of thirst
        self.char1.thirst = 0
        assert self.char1.get_thirst_label() == "quenched"
        self.char1.thirst = 7
        assert self.char1.get_thirst_label() == "thirsty"
        self.char1.thirst = 35
        assert self.char1.get_thirst_label() == "parched"
        self.char1.thirst = 65
        assert self.char1.get_thirst_label() == "dying of thirst"

        # Tiredness thresholds: 0->rested, 7->tired, 30->exhausted, 60->about to collapse
        self.char1.tiredness = 0
        assert self.char1.get_tiredness_label() == "rested"
        self.char1.tiredness = 7
        assert self.char1.get_tiredness_label() == "tired"
        self.char1.tiredness = 35
        assert self.char1.get_tiredness_label() == "exhausted"
        self.char1.tiredness = 65
        assert self.char1.get_tiredness_label() == "about to collapse"

    def test_status_command_available(self):
        # Smoke test: ensure command set is present and command runs
        self.char1.cmdset.add(AliveCmdSet, permanent=True)
        self.char1.execute_cmd("status")
