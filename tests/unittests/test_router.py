import unittest

from puepy import Application
from puepy.core import Page
from puepy.router import Router, Route, _micropython_parse_query_string


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.page = Page()
        self.route = Route("/test/<id>", self.page, "test_route", "/base")

    def test_route_initialization(self):
        self.assertEqual(self.route.path_match, "/test/<id>")
        self.assertEqual(self.route.page, self.page)
        self.assertEqual(self.route.name, "test_route")
        self.assertEqual(self.route.base_path, "/base")

    def test_route_match(self):
        match, params = self.route.match("/base/test/123")
        self.assertTrue(match)
        self.assertEqual(params, {"id": "123"})

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
        route = Route("/test/<id>", self.page, "test_route", "/base")
        self.router.add_route_instance(route)
        self.assertIn(route, self.router.routes)
        self.assertEqual(self.router.routes_by_name["test_route"], route)
        self.assertEqual(self.router.routes_by_page[self.page], route)

    def test_add_duplicate_route_instance(self):
        route = Route("/test/<id>", self.page, "test_route", "/base")
        self.router.add_route_instance(route)
        with self.assertRaises(ValueError):
            self.router.add_route_instance(route)

    def test_add_route(self):
        self.router.add_route("/test/<id>", self.page, "test_route")
        route = self.router.routes[0]
        self.assertEqual(route.name, "test_route")
        self.assertTrue(route.match("/test/123")[0])

    def test_add_route_unnamed(self):
        class UnnamedPage(Page):
            pass

        self.router.add_route("/test_named/:id", UnnamedPage)
        route = self.router.routes[0]
        self.assertEqual(route.name, "unnamed_page")

    def test_add_duplicate_route_name(self):
        self.router.add_route("/test/<id>", self.page, "test_route")
        with self.assertRaises(ValueError):
            self.router.add_route("/test/<name>", self.page, "test_route")

    def test_reverse_route(self):
        self.router.add_route("/test/<id>", self.page, "test_route")
        self.router.link_mode = Router.LINK_MODE_HASH
        self.assertEqual(self.router.reverse("test_route", id="123"), "#/test/123")
        self.router.link_mode = Router.LINK_MODE_HTML5
        self.assertEqual(self.router.reverse("test_route", id="123"), "/test/123")

        self.assertEqual(self.router.reverse(self.page, id="123"), "/test/123")
        self.assertRaises(KeyError, self.router.reverse, "foobar")

    def test_match_route(self):
        self.router.add_route("/test/<id>", self.page, "test_route")
        route, params = self.router.match("/test/123")
        self.assertIsNotNone(route)
        self.assertEqual(route.name, "test_route")
        self.assertEqual(params, {"id": "123"})

    def test_no_match_route(self):
        self.router.add_route("/test/<id>", self.page, "test_route")
        route, params = self.router.match("/other/123")
        self.assertIsNone(route)
        self.assertIsNone(params)

    def test_hash_root(self):
        application = Application()
        application.install_router(Router)

        page = Page()
        application.default_page = page

        self.assertEqual(application.router.reverse(page), "#/")
        application.router.link_mode = Router.LINK_MODE_HTML5
        self.assertEqual(application.router.reverse(page), "/")


class TestMicropythonParseQueryString(unittest.TestCase):
    def test_simple_query(self):
        query_string = "?name=John"
        expected_output = {"name": ["John"]}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)

    def test_multiple_params(self):
        query_string = "?name=John&age=30"
        expected_output = {"name": ["John"], "age": ["30"]}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)

    def test_url_encoded_chars(self):
        query_string = "?name=John%20Doe&age=30"
        expected_output = {"name": ["John Doe"], "age": ["30"]}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)

    def test_repeated_params(self):
        query_string = "?name=John&name=Jane"
        expected_output = {"name": ["John", "Jane"]}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)

    def test_no_value_param(self):
        query_string = "?name="
        expected_output = {"name": [""]}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)

    def test_no_value_multiple_params(self):
        query_string = "?name=&age="
        expected_output = {"name": [""], "age": [""]}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)

    def test_plus_as_space(self):
        query_string = "?name=John+Doe&age=30"
        expected_output = {"name": ["John Doe"], "age": ["30"]}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)

    def test_single_param_without_value(self):
        query_string = "?name"
        expected_output = {"name": ""}
        self.assertEqual(_micropython_parse_query_string(query_string), expected_output)


if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()
