import evennia
from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.characters import Character


class TestCharacterAtInit(EvenniaTest):
    def test_at_init_with_no_db(self):
        char = create_object(Character, key="InitChar")
        char._state.db = None
        # should not raise when the database state is missing
        char.at_init()

