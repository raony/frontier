"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from commands.default_cmdsets import CharacterCmdSet
from typeclasses.objects import Object
from typeclasses.container import is_container
from world.living.people import Person
from world.utils import null_func


class Character(Person):
    """Represents the in-game character entity."""

    def load_cmdset(self):
        getattr(super(), "load_cmdset", null_func)()
        if not self.cmdset.has(CharacterCmdSet):
            self.cmdset.add(CharacterCmdSet, persistent=True)

    def quiet_search_item(self, key:str, **kwargs) -> Object | None:
        return self.quiet_search(key, **kwargs)

    def search_item(self, key: str, search_location=True, search_containers=True) -> Object | None:
        """Search for an item in the character's location and containers."""

        candidates = self.contents + (self.location.contents if search_location else [])
        result = self.quiet_search_item(key, candidates=candidates)
        if result:
            return result

        if search_containers:
            for obj in candidates:
                if is_container(obj):
                    result = self.recursive_search_item(key, obj)
                    if result:
                        return result
        return None

    def recursive_search_item(self, key: str, container: Object) -> Object | None:
        result = self.quiet_search_item(key, candidates=container.contents)
        if result:
            return result

        for obj in container.contents:
            if is_container(obj):
                result = self.recursive_search_item(key, obj)
                if result:
                    return result
        return None