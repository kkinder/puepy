import unittest
import itertools
from puepy.application import DefaultIdGenerator


class TestDefaultIdGenerator(unittest.TestCase):
    def setUp(self):
        self.id_generator = DefaultIdGenerator("test")

    def test_init(self):
        self.assertEqual(self.id_generator.prefix, "test")
        self.assertIsInstance(self.id_generator.counter, itertools.count)

    def test_int_to_base36(self):
        num = 10
        self.assertEqual(DefaultIdGenerator._int_to_base36(num), "a")

    def test_call(self):
        ids = [self.id_generator.get_id_for_element(None) for _ in range(100)]
        self.assertEqual(ids[0], "test0")
        self.assertEqual(ids[99], "test2r")


if __name__ == "__main__":
    unittest.main()
