import unittest
from unittest.mock import MagicMock, patch

from puepy.reactivity import Listener, ReactiveDict


class TestListener(unittest.TestCase):
    def setUp(self):
        self.listener = Listener()

        self.reactive_dict = ReactiveDict({"a": 1, "b": 2})
        self.reactive_dict_notifications = []
        self.reactive_dict.listener.add_callback(self._callback)

    def _callback(self, *args, **kwargs):
        self.reactive_dict_notifications.append((args, kwargs))

    def test_dict_notify_insertion(self):
        self.reactive_dict["c"] = 5
        self.assertEqual(self.reactive_dict_notifications, [(("c",), {})])

    def test_dict_notify_deletion(self):
        del self.reactive_dict["a"]
        self.assertEqual(self.reactive_dict_notifications, [(("a",), {})])

    def test_dict_add_callback(self):
        callback = MagicMock()
        self.listener.add_callback(callback)
        self.assertEqual(len(self.listener.callbacks), 1)

    def test_remove_callback(self):
        callback = MagicMock()
        self.listener.add_callback(callback)
        self.listener.remove_callback(callback)
        self.assertEqual(len(self.listener.callbacks), 0)

    def test_notify(self):
        callback = MagicMock()
        self.listener.add_callback(callback)
        self.listener.notify("hello")
        callback.assert_called_with("hello")

    def test_str_no_callbacks(self):
        self.assertEqual(str(self.listener), "Listener with no callbacks")

    def test_str_one_callback(self):
        callback = MagicMock()
        self.listener.add_callback(callback)
        self.assertTrue(str(self.listener), "Listener: " + str(callback))

    def test_str_multiple_callbacks(self):
        callback1 = MagicMock()
        callback2 = MagicMock()
        self.listener.add_callback(callback1)
        self.listener.add_callback(callback2)
        self.assertTrue(str(self.listener), f"Listener with {len(self.listener.callbacks)} callbacks")

    def test_repr(self):
        callback = MagicMock()
        self.listener.add_callback(callback)
        self.assertTrue(repr(self.listener).startswith("<Listener:"))

    def test_notify_with_exception_in_callback(self):
        def callback_with_exception(*args, **kwargs):
            raise ValueError("Test exception")

        self.listener.add_callback(callback_with_exception)

        with patch("logging.error") as mock_log_error:
            self.listener.notify("hello")

            # Check that logging.error was called
            self.assertTrue(mock_log_error.called)


if __name__ == "__main__":
    unittest.main()
