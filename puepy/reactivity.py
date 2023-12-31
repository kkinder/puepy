import logging
from contextlib import contextmanager


class Listener:
    """
    A simple class that allows you to register callbacks and then notify them
    """

    def __init__(self):
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)

    def notify(self, *args, **kwargs):
        for callback in self.callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in callback for {self}: {callback}:", e)

    def __str__(self):
        if len(self.callbacks) == 1:
            return f"Listener: {self.callbacks[0]}"
        elif len(self.callbacks) > 1:
            return f"Listener with {len(self.callbacks)} callbacks"
        else:
            return "Listener with no callbacks"

    def __repr__(self):
        return f"<{self}>"


class ReactiveDict(dict):
    """
    A dictionary that notifies a listener when it is updated
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.listener = Listener()

        # # Necessary for Micropython
        # for k, v in kwargs.items():
        #     self[k] = v

    def __setitem__(self, key, value):
        if (key in self and value != self[key]) or key not in self:
            super().__setitem__(key, value)
            self.listener.notify(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.listener.notify(key)

    @contextmanager
    def mutate(self, *keys):
        if len(keys) == 0:
            yield self.get(keys[0])
        elif len(keys) > 1:
            yield [self.get(k) for k in keys]
        else:
            yield
        if keys:
            for key in keys:
                self.listener.notify(key)
            else:
                for k in self.keys():
                    self.listener.notify(k)
