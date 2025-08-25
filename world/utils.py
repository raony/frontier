def null_func(*args, **kwargs):
    pass

class DisplayNameWrapper:
    def __init__(self, obj, **kwargs):
        self.obj = obj
        self.kwargs = kwargs

    def get_display_name(self, looker):
        return self.obj.get_display_name(looker, **self.kwargs)