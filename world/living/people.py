from evennia.objects.objects import DefaultCharacter
from typeclasses.objects import ObjectParent
from world.living.base import LivingMixin
from typeclasses.equipment import WearerMixin
from world.equipment import HolderMixin
from typeclasses.skills import SkillableMixin

class Person(LivingMixin, ObjectParent, HolderMixin, WearerMixin, SkillableMixin, DefaultCharacter):
    pass