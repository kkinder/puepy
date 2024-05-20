import logging


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
                logging.exception("Error in callback for {self}: {callback}:".format(self=self, callback=callback))

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
        self._in_mutation = False
        self._notifications_pending = set()
        self._keys_mutate = None

        # # Necessary for Micropython
        # for k, v in kwargs.items():
        #     self[k] = v

    def notify(self, *keys):
        if keys:
            self._notifications_pending.update(keys)
        else:
            self._notifications_pending.update(self.keys())

        if not self._in_mutation:
            self._flush_pending()

    def _flush_pending(self):
        while self._notifications_pending:
            key = self._notifications_pending.pop()
            self.listener.notify(key)

    def __setitem__(self, key, value):
        if (key in self and value != self[key]) or key not in self:
            super().__setitem__(key, value)
            self.notify(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.notify(key)

    def mutate(self, *keys):
        if keys:
            self._notifications_pending.update(keys)
        else:
            self._notifications_pending.update(self.keys())
        self._keys_mutate = keys
        return self

    def __enter__(self):
        self._in_mutation = True

        if len(self._keys_mutate) == 0:
            return self.get(self._keys_mutate)
        elif len(self._keys_mutate) > 1:
            return [self.get(k) for k in self._keys_mutate]

    def __exit__(self, type, value, traceback):
        self._in_mutation = False
        self._flush_pending()
