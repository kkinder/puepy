try:
    from js import Object

    is_server_side = False
except ImportError:
    is_server_side = True


class BrowserStorage:
    class NoDefault:
        pass

    def __init__(self, target, description):
        self.target = target
        self.description = description

    def __getitem__(self, key):
        value = self.target.getItem(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.target.setItem(key, str(value))

    def __delitem__(self, key):
        if self.target.getItem(key) is None:
            raise KeyError(key)
        self.target.removeItem(key)

    def __contains__(self, key):
        return not self.target.getItem(key) is None

    def __len__(self):
        return self.target.length

    def __iter__(self):
        return iter(self.keys())

    def items(self):
        for item in Object.entries(self.target):
            # print("item", item)
            yield item[0], item[1]

    def keys(self):
        return list(Object.keys(self.target))

    def get(self, key, default=None):
        value = self.target.getItem(key)
        if value is None:
            return default
        else:
            return value

    def clear(self):
        self.target.clear()

    def copy(self):
        return dict(self.items())

    def pop(self, key, default=NoDefault):
        value = self.target.getItem(key)
        if value is None and default is self.NoDefault:
            raise KeyError(key)
        else:
            self.target.removeItem(key)
            return value

    def popitem(self):
        raise NotImplementedError("popitem not implemented")

    def reversed(self):
        raise NotImplementedError("reversed not implemented")

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def values(self):
        return list(Object.values(self.target))

    def __str__(self):
        return self.description

    def __repr__(self):
        return f"<{self}>"
