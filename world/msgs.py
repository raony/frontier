class MsgObj(object):
    def __init__(self, msg):
        self.msg = msg

    def to_dict(self):
        return {
            "msg": self.msg,
            "type": "visual" if self.is_visual() else "sound"
        }

    def is_visual(self):
        return False

    def __str__(self):
        return self.msg

    @classmethod
    def from_dict(cls, data):
        if data["type"] == "visual":
            return VisualMsg(data["msg"], data["sound"])
        elif data["type"] == "sound":
            return SoundMsg(data["msg"])
        else:
            raise ValueError(f"Invalid message type: {data['type']}")

class VisualMsg(MsgObj):
    def __init__(self, msg, sound=None):
        super().__init__(msg)
        self.sound = sound

    def is_visual(self):
        return True

    def to_dict(self):
        return {**super().to_dict(), "sound": self.sound}

class SoundMsg(MsgObj):
    pass