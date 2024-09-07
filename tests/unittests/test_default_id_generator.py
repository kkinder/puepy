import itertools
import pytest
from puepy.application import DefaultIdGenerator


class TestDefaultIdGenerator:

    @pytest.fixture
    def id_generator(self):
        return DefaultIdGenerator("test")

    def test_init(self, id_generator):
        assert id_generator.prefix == "test"
        assert isinstance(id_generator.counter, itertools.count)

    def test_int_to_base36(self):
        num = 10
        assert DefaultIdGenerator._int_to_base36(num) == "a"

    def test_call(self, id_generator):
        ids = [id_generator.get_id_for_element(None) for _ in range(100)]
        assert ids[0] == "test0"
        assert ids[99] == "test2r"
