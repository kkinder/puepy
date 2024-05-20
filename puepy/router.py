import re

from .core import Page
from .util import mixed_to_underscores

named_group_pattern = re.compile(r"\(\?P<(\w+)>[^)]*\)")


class Route:
    def __init__(self, pattern: re.Pattern, page: Page, name: str, base_path: str):
        self.pattern = pattern
        self.page = page
        self.name = name
        self.base_path = base_path

    def match(self, path):
        if self.base_path and path.startswith(self.base_path):
            path = path[len(self.base_path) :]

        if match := self.pattern.match(path):
            return True, match.groupdict()
        else:
            return False, None

    def reverse(self, **kwargs):
        # replace each found named group with its respective replacement
        def substitution(m):
            group_name = m.group(1)
            return str(kwargs.get(group_name, m.group(0)))

        result = named_group_pattern.sub(substitution, self.pattern.pattern)[1:-1]

        if self.base_path:
            return f"{self.base_path}{result}"
        else:
            return result

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Route: {self.name}>"


class Router:
    def __init__(self, application=None, base_path=None):
        self.routes = []
        self.routes_by_name = {}
        self.routes_by_page = {}
        self.application = application
        self.base_path = base_path

    def add_route_instance(self, route: Route):
        if route in self.routes:
            raise ValueError(f"Route already added: {route}")
        if route.name in self.routes_by_name:
            raise ValueError(f"Route name already exists for another route: {route.name}")
        self.routes.append(route)
        self.routes_by_name[route.name] = route
        self.routes_by_page[route.page] = route

    def add_route(self, path, page_class, name=None):
        pattern = re.compile("^" + re.sub(r":(\w+)", r"(?P<\1>[^/]+)", path) + "$")

        if not name:
            name = mixed_to_underscores(page_class.__name__)
        self.add_route_instance(Route(pattern=pattern, page=page_class, name=name, base_path=self.base_path))

    def reverse(self, name_or_page, **kwargs):
        route: Route
        if name_or_page in self.routes_by_name:
            route = self.routes_by_name[name_or_page]
        elif name_or_page in self.routes_by_page:
            route = self.routes_by_page[name_or_page]
        elif self.application and name_or_page is self.application.default_page:
            return "/"
        else:
            raise KeyError(f"{name_or_page} not found in routes")
        return route.reverse(**kwargs)

    def match(self, path):
        path = path.split("#")[0].split("?")[0]
        for route in self.routes:
            matches, arguments = route.match(path)
            if matches:
                return route, arguments
        return None, None
