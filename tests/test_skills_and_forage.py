from evennia.utils.test_resources import EvenniaTest


class TestSkillsAndForage(EvenniaTest):
    def setUp(self):
        super().setUp()
        # Ensure we start in a clean room
        self.room1.location = None
        self.char1.move_to(self.room1, quiet=True)

    def test_skills_default_is_untrained(self):
        assert self.char1.get_skill_level_label("foraging") == "untrained"

    def test_set_and_show_skills(self):
        # Grant journeyman and list skills
        self.char1.execute_cmd("@createskill foraging=Foraging")
        self.char1.execute_cmd("@setskill me = foraging : journeyman")
        # The command should render a table; here we just ensure it runs
        self.char1.execute_cmd("skills")
        assert self.char1.get_skill_level_label("foraging") == "journeyman"

    def test_createresource_and_basic_forage(self):
        # Create a foraging resource in the room
        self.char1.execute_cmd("@createresource berry-bush/foraging = 1,1")
        # Attempt foraging as untrained — may fail, but should not error
        self.char1.execute_cmd("forage")
        # Give skill and try again; with limited abundance, this should consume it if success
        self.char1.execute_cmd("@createskill foraging=Foraging")
        self.char1.execute_cmd("@setskill me = foraging : master")
        self.char1.execute_cmd("forage")
