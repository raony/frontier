"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import Object, ObjectParent
from .equipment import WearerMixin
from .living import LivingMixin
from .holding import HolderMixin
from .skills import SkillableMixin
from .container import is_container
from world.msgs import SoundMsg, MsgObj


class Character(LivingMixin, HolderMixin, WearerMixin, SkillableMixin, ObjectParent, DefaultCharacter):
    """Represents the in-game character entity.

    Three persistent Attributes are introduced on all characters:
    ``hunger``, ``thirst`` and ``tiredness``. They are integers tracking
    how hungry, thirsty or tired a character is. Newly created characters
    start at ``0`` for all values.
    """

    is_pc = True

    def get_tag_objs(self, *args, **kwargs):
        return self.tags.get(*args, **kwargs, return_tagobj=True)

    def at_msg_receive(self, text=None, from_obj=None, **kwargs):
        msg_obj = MsgObj.from_dict(kwargs.pop("msg_obj", None))

        if msg_obj and msg_obj.is_visual():
            if self.is_dead():
                return False

            if self.is_too_dark():
                self.msg(msg_obj.sound, from_obj=from_obj, **kwargs, msg_obj= SoundMsg(msg_obj.sound).to_dict())
                return False

        return super().at_msg_receive(text, from_obj, **kwargs)

    def is_too_dark(self):
        return self.location.get_light_level(looker=self) < self.light_threshold

    # --- Perception / Look -------------------------------------------------
    def at_look(self, target, **kwargs):
        """Gate visibility based on ambient light vs character threshold."""
        # Check if we can see details in current light
        if self.is_too_dark():
            return "It's too dark to see anything."
        return super().at_look(target, **kwargs)

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