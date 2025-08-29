from evennia.utils.utils import lazy_property
from world.utils import null_func


class MsgObj(object):
    def __init__(self, visual=None, sound=None):
        self.visual = visual
        self.sound = sound

    def to_dict(self):
        return {
            "visual": self.visual,
            "sound": self.sound,
        }

    def has_visual(self):
        return self.visual is not None

    def has_sound(self):
        return self.sound is not None

    def __str__(self):
        return self.visual

    @classmethod
    def from_dict(cls, data):
        return cls(data["visual"], data["sound"])


class VisionManager:
    def __init__(self, obj):
        self.obj = obj
        self._load()

    def _load(self):
        self._light_threshold = self.obj.attributes.get("db_light_threshold", default=20, category="vision")
        self._disabled = self.obj.attributes.get("db_vision_disabled", default=False, category="vision")

    def _save(self):
        self.obj.attributes.add("db_light_threshold", self._light_threshold, category="vision")
        self.obj.attributes.add("db_vision_disabled", self._disabled, category="vision")
        self._load()

    @property
    def light_threshold(self):
        return self._light_threshold

    @light_threshold.setter
    def light_threshold(self, value):
        self._light_threshold = value
        self._save()

    @property
    def disabled(self):
        return self._disabled

    @property
    def can_see(self):
        if self.disabled:
            return False
        light_level = self._get_light_level(self.obj.location)
        if light_level >= self.light_threshold:
            return True
        for obj in self.obj.location.contents:
            light_level = max(light_level, self._get_light_level(obj))
        return light_level >= self.light_threshold

    def _get_light_level(self, obj):
        if obj.tags.has("light_source", category="vision"):
            return obj.light.level
        return 0

    def can_receive_message(self, msg_obj: MsgObj):
        if msg_obj.has_visual():
            return self.can_see
        return True

    def disable(self):
        self._disabled = True
        self._save()

    def enable(self):
        self._disabled = False
        self._save()

class PerceptionMixin:
    @lazy_property
    def vision(self):
        return VisionManager(self)

    def die(self):
        getattr(super(), "die", null_func)()
        self.vision.disable()

    def revive(self):
        getattr(super(), "revive", null_func)()
        self.vision.enable()

    def msg(self, text=None, from_obj=None, **kwargs):
        raw_msg_obj = kwargs.pop("msg_obj", None)
        if raw_msg_obj:
            msg_obj = MsgObj.from_dict(raw_msg_obj)
            if not self.vision.can_receive_message(msg_obj):
                text = msg_obj.sound
        return super().msg(text, from_obj, **kwargs)

    def at_look(self, target, **kwargs):
        if self.vision.disabled:
            return "You can't see anything."
        if not self.vision.can_see:
            return "It's too dark to see anything."

        return super().at_look(target, **kwargs)


class LightManager:
    def __init__(self, obj, level=0):
        self.obj = obj
        self.level = level

    def _load(self):
        self._light_level = self.obj.attributes.get("light_level", default=0, category="vision")

    def _save(self):
        self.obj.attributes.add("light_level", self._light_level, category="vision")
        if self._light_level > 0:
            self.obj.tags.add("light_source", category="vision")
        else:
            self.obj.tags.remove("light_source", category="vision")
        self._load()

    @property
    def level(self):
        return self._light_level

    @level.setter
    def level(self, value):
        self._light_level = value
        self._save()