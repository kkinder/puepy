import unittest
import re

from puepy.core import Page
from puepy.router import Router, Route


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.page = Page()
        self.route = Route(re.compile(r"^/test/(?P<id>\d+)$"), self.page, "test_route", "/base")

    def test_route_initialization(self):
        self.assertEqual(self.route.pattern.pattern, r"^/test/(?P<id>\d+)$")
        self.assertEqual(self.route.page, self.page)
        self.assertEqual(self.route.name, "test_route")
        self.assertEqual(self.route.base_path, "/base")

    def test_route_match(self):
        match, params = self.route.match("/base/test/123")
        self.assertTrue(match)
        self.assertEqual(params, {"id": "123"})

        match, params = self.route.match("/base/test/abc")
        self.assertFalse(match)
        self.assertIsNone(params)

    def test_route_reverse(self):
        url = self.route.reverse(id="123")
        self.assertEqual(url, "/base/test/123")

    def test_route_str_repr(self):
        self.assertEqual(str(self.route), "test_route")
        self.assertEqual(repr(self.route), "<Route: test_route>")


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router()
        self.page = Page()

    def test_add_route_instance(self):
        route = Route(re.compile(r"^/test/(?P<id>\d+)$"), self.page, "test_route", "/base")
        self.router.add_route_instance(route)
        self.assertIn(route, self.router.routes)
        self.assertEqual(self.router.routes_by_name["test_route"], route)
        self.assertEqual(self.router.routes_by_page[self.page], route)

    def test_add_duplicate_route_instance(self):
        route = Route(re.compile(r"^/test/(?P<id>\d+)$"), self.page, "test_route", "/base")
        self.router.add_route_instance(route)
        with self.assertRaises(ValueError):
            self.router.add_route_instance(route)

    def test_add_route(self):
        self.router.add_route("/test/:id", self.page, "test_route")
        route = self.router.routes[0]
        self.assertEqual(route.name, "test_route")
        self.assertTrue(route.pattern.match("/test/123"))

    def test_add_route_unnamed(self):
        class UnnamedPage(Page):
            pass

        self.router.add_route("/test_unmaed/:id", UnnamedPage)
        route = self.router.routes[0]
        self.assertEqual(route.name, "unnamed_page")

    def test_add_duplicate_route_name(self):
        self.router.add_route("/test/:id", self.page, "test_route")
        with self.assertRaises(ValueError):
            self.router.add_route("/test/:name", self.page, "test_route")

    def test_reverse_route(self):
        self.router.add_route("/test/:id", self.page, "test_route")
        self.assertEqual(self.router.reverse("test_route", id="123"), "/test/123")
        self.assertEqual(self.router.reverse(self.page, id="123"), "/test/123")
        self.assertRaises(KeyError, self.router.reverse, "foobar")

    def test_match_route(self):
        self.router.add_route("/test/:id", self.page, "test_route")
        route, params = self.router.match("/test/123")
        self.assertIsNotNone(route)
        self.assertEqual(route.name, "test_route")
        self.assertEqual(params, {"id": "123"})

    def test_no_match_route(self):
        self.router.add_route("/test/:id", self.page, "test_route")
        route, params = self.router.match("/other/123")
        self.assertIsNone(route)
        self.assertIsNone(params)


if __name__ == "__main__":
    unittest.main()
