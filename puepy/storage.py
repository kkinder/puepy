"""
Browser Storage Module

This module provides a `BrowserStorage` class that interfaces with browser storage
objects such as `localStorage` and `sessionStorage`. It mimics dictionary-like
behavior for interacting with storage items.


Classes:
    BrowserStorage: A class that provides dictionary-like access to browser storage objects.
"""

try:
    from js import Object

    is_server_side = False
except ImportError:
    is_server_side = True


class BrowserStorage:
    """
    Provides dictionary-like interface to browser storage objects.

    Attributes:
        target: The browser storage object (e.g., localStorage, sessionStorage).
        description (str): Description of the storage instance.

    """

    class NoDefault:
        """Placeholder class for default values when no default is provided."""

        pass

    def __init__(self, target, description):
        """
        Initializes the BrowserStorage instance.

        Args:
            target: The browser storage object.
            description (str): Description of the storage instance.
        """
        self.target = target
        self.description = description

    def __getitem__(self, key):
        """
        Retrieves the value for a given key from the storage.

        Args:
            key (str): The key for the item to retrieve.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key does not exist in the storage.
        """
        value = self.target.getItem(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        """
        Sets the value for a given key in the storage.

        Args:
            key (str): The key for the item to set.
            value: The value to associate with the key.
        """
        self.target.setItem(key, str(value))

    def __delitem__(self, key):
        """
        Deletes the item for a given key from the storage.

        Args:
            key (str): The key for the item to delete.

        Raises:
            KeyError: If the key does not exist in the storage.
        """
        if self.target.getItem(key) is None:
            raise KeyError(key)
        self.target.removeItem(key)

    def __contains__(self, key):
        """
        Checks if a key exists in the storage.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return not self.target.getItem(key) is None

    def __len__(self):
        """
        Returns the number of items in the storage.

        Returns:
            int: The number of items in the storage.
        """
        return self.target.length

    def __iter__(self):
        """
        Returns an iterator over the keys in the storage.

        Returns:
            iterator: An iterator over the keys.
        """
        return iter(self.keys())

    def items(self):
        """
        Returns an iterator over the (key, value) pairs in the storage.

        Yields:
            tuple: (key, value) pairs in the storage.
        """
        for item in Object.entries(self.target):
            yield item[0], item[1]

    def keys(self):
        """
        Returns a list of keys in the storage.

        Returns:
            list: A list of keys.
        """
        return list(Object.keys(self.target))

    def get(self, key, default=None):
        """
        Retrieves the value for a given key, returning a default value if the key does not exist.

        Args:
            key (str): The key for the item to retrieve.
            default: The default value to return if the key does not exist.

        Returns:
            The value associated with the key, or the default value.
        """
        value = self.target.getItem(key)
        if value is None:
            return default
        else:
            return value

    def clear(self):
        """
        Clears all items from the storage.
        """
        self.target.clear()

    def copy(self):
        """
        Returns a copy of the storage as a dictionary.

        Returns:
            dict: A dictionary containing all items in the storage.
        """
        return dict(self.items())

    def pop(self, key, default=NoDefault):
        """
        Removes the item with the given key from the storage and returns its value.

        Args:
            key (str): The key for the item to remove.
            default: The default value to return if the key does not exist.

        Returns:
            The value associated with the key, or the default value.

        Raises:
            KeyError: If the key does not exist and no default value is provided.
        """
        value = self.target.getItem(key)
        if value is None and default is self.NoDefault:
            raise KeyError(key)
        else:
            self.target.removeItem(key)
            return value

    def popitem(self):
        """
        Not implemented. Raises NotImplementedError.

        Raises:
            NotImplementedError: Always raised as the method is not implemented.
        """
        raise NotImplementedError("popitem not implemented")

    def reversed(self):
        """
        Not implemented. Raises NotImplementedError.

        Raises:
            NotImplementedError: Always raised as the method is not implemented.
        """
        raise NotImplementedError("reversed not implemented")

    def setdefault(self, key, default=None):
        """
        Sets the value for the key if it does not already exist in the storage.

        Args:
            key (str): The key for the item.
            default: The value to set if the key does not exist.

        Returns:
            The value associated with the key, or the default value.
        """
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def update(self, other):
        """
        Updates the storage with items from another dictionary or iterable of key-value pairs.

        Args:
            other: A dictionary or iterable of key-value pairs to update the storage with.
        """
        for k, v in other.items():
            self[k] = v

    def values(self):
        """
        Returns a list of values in the storage.

        Returns:
            list: A list of values.
        """
        return list(Object.values(self.target))

    def __str__(self):
        return self.description

    def __repr__(self):
        return f"<{self}>"
