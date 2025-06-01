
# Custom minimal Events base class to replace 'events' dependency
class Events:
    def __init__(self):
        self._listeners = {}
        if hasattr(self, "__events__"):
            for event in self.__events__:
                self._listeners[event] = []

    def __getattr__(self, name):
        # Allow event access as attributes
        if hasattr(self, "__events__") and name in self.__events__:
            return self._EventSlot(self, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    class _EventSlot:
        def __init__(self, parent, event_name):
            self._parent = parent
            self._event_name = event_name

        def __iadd__(self, listener):
            self._parent._listeners[self._event_name].append(listener)
            return self

        def __isub__(self, listener):
            self._parent._listeners[self._event_name].remove(listener)
            return self

        def __call__(self, *args, **kwargs):
            for listener in list(self._parent._listeners[self._event_name]):
                listener(*args, **kwargs)


class TranslationEvents(Events):
    __events__ = ( "preprocessed", "batch_translated", "scene_translated" )

