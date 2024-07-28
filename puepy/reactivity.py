"""
Provides the base classes for PuePy's reactivity system independent of web concerns. These classes are not intended to be used directly, but could be useful for implementing a similar system in a different context.

Classes:
    Listener: A simple class that notifies a collection of callback functions when its `notify` method is called
    ReactiveDict: A dictionary that notifies a listener when it is updated
"""
import logging
from functools import partial


class Listener:
    """
    A simple class that allows you to register callbacks and then notify them all at once.

    Attributes:
        callbacks (list of callables): A list of callback functions to be called when `notify` is called
    """

    def __init__(self):
        self.callbacks = []

    def add_callback(self, callback):
        """
        Adds a callback function to the listener.

        Args:
            callback (callable): The callback function to be added
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        """
        Removes a callback function from the listener.

        Args:
            callback (callable): The callback to be removed
        """
        self.callbacks.remove(callback)

    def notify(self, *args, **kwargs):
        """
        Notify method

        Executes each callback function in the callbacks list by passing in the given arguments and keyword arguments.
        If an exception occurs during the callback execution, it is logged using the logging library.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
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
    A dictionary that notifies a listener when it is updated.

    Attributes:
        listener (Listener): A listener object that is notified when the dictionary is updated
        key_listeners (dict): A dictionary of listeners that are notified when a specific key is updated
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.listener = Listener()
        self.key_listeners = {}
        self._in_mutation = False
        self._notifications_pending = set()
        self._keys_mutate = None

    def add_key_listener(self, key, callback):
        """
        Adds a key listener to the object.

        Args:
            key (str): The key for which the listener will be added.
            callback (callable): The callback function to be executed when the key event is triggered.
        """
        if key not in self.key_listeners:
            self.key_listeners[key] = Listener()
        self.key_listeners[key].add_callback(callback)

    def notify(self, *keys):
        """
        Notifies the listener and key listeners that the object has been updated.

        Args:
            *keys: A variable number of keys to be modified for key-specific listeners.
        """
        if keys:
            self._notifications_pending.update(keys)
        else:
            self._notifications_pending.update(self.keys())

        if not self._in_mutation:
            self._flush_pending()

    def mutate(self, *keys):
        """
        To be used as a context manager, this method is for either deferring all notifications until a change has been completed and/or notifying listeners when "deep" changes are made that would have gone undetected by `__setitem__`.

        Examples:
            ``` py
            with reactive_dict.mutate("my_list", "my_dict"):
                reactive_dict["my_list"].append("spam")
                reactive_dict["my_dict"]["spam"] = "eggs"
            ```

        Args:
            *keys: A variable number of keys to update the notifications pending attribute with. If no keys are provided, all keys in the object will be updated.

        Returns:
            The reactive dict itself, which stylistically could be nice to use in a `with` statement.
        """
        if keys:
            self._notifications_pending.update(keys)
        else:
            self._notifications_pending.update(self.keys())
        self._keys_mutate = keys
        return self

    def update(self, other):
        with self.mutate(*other.keys()):
            super().update(other)

    def _flush_pending(self):
        while self._notifications_pending:
            key = self._notifications_pending.pop()
            value = self.get(key, None)
            self.listener.notify(key, value)
            if key in self.key_listeners:
                self.key_listeners[key].notify(key, value)

    def __setitem__(self, key, value):
        if (key in self and value != self[key]) or key not in self:
            super().__setitem__(key, value)
            self.notify(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.notify(key)

    def __enter__(self):
        self._in_mutation = True

        if len(self._keys_mutate) == 0:
            return self.get(self._keys_mutate)
        elif len(self._keys_mutate) > 1:
            return [self.get(k) for k in self._keys_mutate]

    def __exit__(self, type, value, traceback):
        self._in_mutation = False
        self._flush_pending()


class Stateful:
    """
    A class that provides a reactive state management system for components. A
    """

    def add_context(self, name: str, value: ReactiveDict):
        """
        Adds contxt from a reactive dict to be reacted on by the component.
        """
        value.listener.add_callback(partial(self._on_state_change, name))

    def initial(self):
        """
        To be overridden in subclasses, the `initial()` method defines the initial state of the stateful object.

        Returns:
            (dict): Initial component state
        """
        return {}

    def on_state_change(self, context, key, value):
        """
        To be overridden in subclasses, this method is called whenever the state of the component changes.

        Args:
            context: What context the state change occured in
            key: The key modified
            value: The new value
        """
        pass

    def _on_state_change(self, context, key, value):
        self.on_state_change(context, key, value)

        if hasattr(self, f"on_{key}_change"):
            getattr(self, f"on_{key}_change")(value)
