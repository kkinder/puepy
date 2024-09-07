import unittest
from unittest.mock import MagicMock

import puepy.storage as storage


class TestBrowserStorage(unittest.TestCase):
    def setUp(self):
        target = MagicMock()
        target.getItem = MagicMock(return_value=None)
        target.setItem = MagicMock()
        target.removeItem = MagicMock()
        target.length = 5
        self.bs = storage.BrowserStorage(target, "description")

        self.storage_class = MagicMock()
        storage.Object = self.storage_class

    def test_getitem(self):
        with self.assertRaises(KeyError):
            self.bs.__getitem__("key")

    def test_setitem(self):
        self.bs.__setitem__("key", "value")
        self.bs.target.setItem.assert_called_once_with("key", "value")

    def test_delitem(self):
        with self.assertRaises(KeyError):
            self.bs.__delitem__("key")

    def test_contains(self):
        self.assertFalse(self.bs.__contains__("key"))

    def test_len(self):
        self.assertEqual(self.bs.__len__(), 5)

    def test_items(self):
        self.storage_class.entries = MagicMock(return_value=[("key", "value")])
        self.assertEqual(list(self.bs.items()), [("key", "value")])

    def test_keys(self):
        self.storage_class.keys = MagicMock(return_value=["key1", "key2"])
        self.assertEqual(self.bs.keys(), ["key1", "key2"])

    def test_get(self):
        self.assertIsNone(self.bs.get("key"))
        self.assertEqual(self.bs.get("key", default="default value"), "default value")

    def test_clear(self):
        self.bs.clear()
        self.bs.target.clear.assert_called_once()

    def test_pop(self):
        with self.assertRaises(KeyError):
            self.bs.pop("key")

    def test_setdefault(self):
        self.bs.setdefault("key", default="default value")
        self.bs.target.setItem.assert_called_once_with("key", "default value")

    def test_update(self):
        update_dict = {"key": "value"}
        self.bs.update(update_dict)

    def test_values(self):
        self.storage_class.values = MagicMock(return_value=["value1", "value2"])
        self.assertEqual(self.bs.values(), ["value1", "value2"])

    def test_str(self):
        self.assertEqual(str(self.bs), "description")

    def test_repr(self):
        self.assertEqual(repr(self.bs), "<{}>".format(str(self.bs)))


if __name__ == "__main__":
    unittest.main()
