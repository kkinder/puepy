from .core import Page
from .runtime import (
    window,
    history,
    platform,
    PLATFORM_MICROPYTHON,
)
from .util import mixed_to_underscores, jsobj


if platform == PLATFORM_MICROPYTHON:
    from js import encodeURIComponent

    def url_quote(s):
        return encodeURIComponent(s)

else:
    from urllib.parse import quote as url_quote


class Route:
    def __init__(self, path_match, page: Page, name: str, base_path: str, router=None):
        self.path_match = path_match
        self.page = page
        self.name = name
        self.base_path = base_path
        self.router = router

    def match(self, path):
        if self.base_path and path.startswith(self.base_path):
            path = path[len(self.base_path) :]

        # Simple pattern matching without regex
        parts = path.strip("/").split("/")
        pattern_parts = self.path_match.strip("/").split("/")
        if len(parts) != len(pattern_parts):
            return False, None

        kwargs = {}
        for part, pattern_part in zip(parts, pattern_parts):
            if pattern_part.startswith("<") and pattern_part.endswith(">"):
                group_name = pattern_part[1:-1]
                kwargs[group_name] = part
            elif part != pattern_part:
                return False, None

        return True, kwargs

    def reverse(self, **kwargs):
        result = self.path_match
        for key, value in kwargs.items():
            result = result.replace(f"<{key}>", str(value))

        if self.router and self.router.link_mode == Router.LINK_MODE_HASH:
            result = "#" + result

        if self.base_path:
            return f"{self.base_path}{result}"
        else:
            return result

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Route: {self.name}>"


class Router:
    LINK_MODE_DIRECT = "direct"
    LINK_MODE_HTML5 = "html5"
    LINK_MODE_HASH = "hash"

    def __init__(self, application=None, base_path=None, link_mode=LINK_MODE_HASH):
        self.routes = []
        self.routes_by_name = {}
        self.routes_by_page = {}
        self.application = application
        self.base_path = base_path
        self.link_mode = link_mode

    def add_route_instance(self, route: Route):
        if route in self.routes:
            raise ValueError(f"Route already added: {route}")
        if route.name in self.routes_by_name:
            raise ValueError(f"Route name already exists for another route: {route.name}")
        self.routes.append(route)
        self.routes_by_name[route.name] = route
        self.routes_by_page[route.page] = route
        route.router = self

    def add_route(self, path_match, page_class, name=None):
        # Convert path to a simple pattern without regex
        if not name:
            name = mixed_to_underscores(page_class.__name__)
        self.add_route_instance(Route(path_match=path_match, page=page_class, name=name, base_path=self.base_path))

    def reverse(self, destination, **kwargs):
        route: Route
        if isinstance(destination, Route):
            return destination.reverse(**kwargs)
        elif destination in self.routes_by_name:
            route = self.routes_by_name[destination]
        elif destination in self.routes_by_page:
            route = self.routes_by_page[destination]
        elif self.application and destination is self.application.default_page:
            return "/"
        else:
            raise KeyError(f"{destination} not found in routes")
        return route.reverse(**kwargs)

    def match(self, path):
        path = path.split("#")[0].split("?")[0]
        for route in self.routes:
            matches, arguments = route.match(path)
            if matches:
                return route, arguments
        return None, None

    def navigate_to_path(self, path, **kwargs):
        if isinstance(path, Page):
            path = self.reverse(path, **kwargs)
        else:
            path = path + "?" + "&".join(f"{url_quote(k)}={url_quote(v)}" for k, v in kwargs.items())

        if self.link_mode == self.LINK_MODE_DIRECT:
            window.location = path
        elif self.link_mode == self.LINK_MODE_HTML5:
            history.pushState(jsobj(), "", path)
            return self.application.mount(self.application._selector_or_element, path)
        elif self.link_mode == self.LINK_MODE_HASH:
            path = path[1:] if path.startswith("#") else path
            history.pushState(jsobj(), "", "#" + path)
            return self.application.mount(self.application._selector_or_element, path)
        else:
            raise Exception(f"Invalid link mode: {self.link_mode}")
