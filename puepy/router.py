"""
PuePy's router functionality can be optionally installed by calling the install_router method of the Application class.

Example:
    ``` py
    from puepy import Application, Router

    app = Application()
    app.install_router(Router, link_mode=Router.LINK_MODE_HASH)
    ```

Once installed, the `Router` instance is available on `app.Router` and can be used throughout the application to manage
client-side routing. Routes are defined by either using the `@app.page` decorator or by calling methods manually on
the `Router` instance.

Classes:
    puepy.router.Route: Represents a route in the router.
    puepy.router.Router: Represents a router for managing client-side routing in a web application.
"""

from .core import Page
from .runtime import window, history, platform, PLATFORM_MICROPYTHON, is_server_side
from .util import mixed_to_underscores, jsobj


def _micropython_parse_query_string(query_string):
    """
    In MicroPython, urllib isn't available and we can't use the JavaScript library:
    https://github.com/pyscript/pyscript/issues/2100
    """
    if query_string and query_string[0] == "?":
        query_string = query_string[1:]

    def url_decode(s):
        # Decode URL-encoded characters without using regex, which is also pretty broken in MicroPython...
        i = 0
        length = len(s)
        decoded = []

        while i < length:
            if s[i] == "%":
                if i + 2 < length:
                    hex_value = s[i + 1 : i + 3]
                    decoded.append(chr(int(hex_value, 16)))
                    i += 3
                else:
                    decoded.append("%")
                    i += 1
            elif s[i] == "+":
                decoded.append(" ")
                i += 1
            else:
                decoded.append(s[i])
                i += 1

        return "".join(decoded)

    params = {}
    for part in query_string.split("&"):
        if "=" in part:
            key, value = part.split("=", 1)
            key = url_decode(key)
            value = url_decode(value)
            if key in params:
                params[key].append(value)
            else:
                params[key] = [value]
        else:
            key = url_decode(part)
            if key in params:
                params[key].append("")
            else:
                params[key] = ""
    return params


if platform == PLATFORM_MICROPYTHON:
    from js import encodeURIComponent

    def url_quote(s):
        return encodeURIComponent(s)

else:
    from urllib.parse import quote as url_quote

if is_server_side:
    from urllib.parse import urlparse, parse_qs

    def parse_query_string(qs):
        return parse_qs(urlparse(qs).query)

elif platform == PLATFORM_MICROPYTHON:
    parse_query_string = _micropython_parse_query_string

else:
    import js

    def parse_query_string(qs):
        usp = js.URLSearchParams.new(qs)
        return {key: list(usp.getAll(key)) for key in usp.keys()}


class Route:
    """
    Represents a route in the router. A route is defined by a path match pattern, a page class, and a name.

    Note:
        This is usually not instanciated directly. Instead, use the `Router.add_route` method to create a new route or
        use the @app.page decorator to define a route at the time you define your Pages.
    """

    def __init__(self, path_match: str, page: Page, name: str, base_path: str, router=None):
        """
        Args:
            path_match (str): The path match pattern used for routing.
            page (Page): An instance of the Page class representing the page.
            name (str): The name of the page.
            base_path (str): The base path used for routing.
            router (Router, optional): An optional parameter representing the router used for routing.
        """
        self.path_match = path_match
        self.page = page
        self.name = name
        self.base_path = base_path
        self.router = router

    def match(self, path):
        """
        Evaluates a path against the route's pattern to determine if there is a match.

        Args:
            path: The path to be matched against the pattern.

        Returns:
            Match found (tuple): A tuple containing a True boolean value and a dictionary. The dictionary contains the
            matched variables extracted from the path.

            Match not found (tuple): If no match is found, returns `(False, None)`.
        """
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
        """
        Reverse method is used to generate a URL path using the given parameters. It replaces the placeholders in the
        path template with the corresponding values.

        Args:
            **kwargs: A variable number of keyword arguments representing the values to be inserted into the path
            template.

        Returns:
            (str): The generated URL path.

        Example:
            Let's say we have a path template `/users/<username>/posts/<post_id>`. We can use the reverse method to
            generate the URL path by providing the values for "username" and "post_id" as keyword arguments:
            `route.reverse(username="john", post_id=123)` => `"/users/john/posts/123"`
        """
        kwargs = kwargs.copy()
        result = self.path_match
        for key in list(kwargs.keys()):
            if f"<{key}>" in result:
                value = kwargs.pop(key)
                result = result.replace(f"<{key}>", str(value))

        if self.router and self.router.link_mode == Router.LINK_MODE_HASH:
            result = "#" + result

        if self.base_path:
            path = f"{self.base_path}{result}"
        else:
            path = result

        if kwargs:
            path += "?" + "&".join(f"{url_quote(k)}={url_quote(v)}" for k, v in kwargs.items())
        return path

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Route: {self.name}>"


class Router:
    """Class representing a router for managing client-side routing in a web application.



    Args:
        application (object, optional): The web application object. Defaults to None.
        base_path (str, optional): The base path URL. Defaults to None.
        link_mode (str, optional): The link mode for navigating. Defaults to "hash".

    Attributes:
        LINK_MODE_DIRECT (str): Direct link mode.
        LINK_MODE_HTML5 (str): HTML5 link mode.
        LINK_MODE_HASH (str): Hash link mode.
        routes (list): List of Route instances.
        routes_by_name (dict): Dictionary mapping route names to Route instances.
        routes_by_page (dict): Dictionary mapping page classes to Route instances.
        application (object): The web application object.
        base_path (str): The base path URL.
        link_mode (str): The link mode for navigating.
    """

    LINK_MODE_DIRECT = "direct"
    LINK_MODE_HTML5 = "html5"
    LINK_MODE_HASH = "hash"

    def __init__(self, application=None, base_path=None, link_mode=LINK_MODE_HASH):
        """
        Initializes an instance of the class.

        Parameters:
            application (Application): The application used for routing.
            base_path (str): The base path for the routes.
            link_mode (str): The mode for generating links.
        """
        self.routes = []
        self.routes_by_name = {}
        self.routes_by_page = {}
        self.application = application
        self.base_path = base_path
        self.link_mode = link_mode

    def add_route_instance(self, route: Route):
        """
        Add a route instance to the current router.

        Parameters:
            route (Route): The route instance to be added.

        Raises:
            ValueError: If the route instance or route name already exists in the router.
        """
        if route in self.routes:
            raise ValueError(f"Route already added: {route}")
        if route.name in self.routes_by_name:
            raise ValueError(f"Route name already exists for another route: {route.name}")
        self.routes.append(route)
        self.routes_by_name[route.name] = route
        self.routes_by_page[route.page] = route
        route.router = self

    def add_route(self, path_match, page_class, name=None):
        """
        Adds a route to the router. This method creates a new Route instance.

        Args:
            path_match (str): The URL path pattern to match for the route.
            page_class (Page class): The class or function to be associated with the route.
            name (str, optional): The name of the route. If not provided, the name will be derived from the page class name.
        """
        # Convert path to a simple pattern without regex
        if not name:
            name = mixed_to_underscores(page_class.__name__)
        self.add_route_instance(Route(path_match=path_match, page=page_class, name=name, base_path=self.base_path))

    def reverse(self, destination, **kwargs):
        """
        Reverses a

        Args:
            destination: The destination to reverse. It can be the name of a route, the mapped page of a route, or the default page of the application.
            **kwargs: Additional keyword arguments to be passed to the reverse method of the destination route.

        Returns:
            (str): The reversed URL for the given destination.

        Raises:
            KeyError: If the destination is not found in the routes.
        """
        route: Route
        if isinstance(destination, Route):
            return destination.reverse(**kwargs)
        elif destination in self.routes_by_name:
            route = self.routes_by_name[destination]
        elif destination in self.routes_by_page:
            route = self.routes_by_page[destination]
        elif self.application and destination is self.application.default_page:
            if self.link_mode == Router.LINK_MODE_HASH:
                path = "#/"
            else:
                path = "/"
            return self.base_path or "" + path
        else:
            raise KeyError(f"{destination} not found in routes")
        return route.reverse(**kwargs)

    def match(self, path):
        """
        Args:
            path (str): The path to be matched.

        Returns:
            (tuple): A tuple containing the matching route and the matched route arguments (if any). If no route is
                found, returns (None, None).
        """
        path = path.split("#")[0]
        if "?" not in path:
            path += "?"
        path, query_string = path.split("?", 1)
        arguments = parse_query_string(query_string)

        for route in self.routes:
            matches, path_arguments = route.match(path)
            if path_arguments:
                arguments.update(path_arguments)
            if matches:
                return route, arguments
        return None, None

    def navigate_to_path(self, path, **kwargs):
        """
        Navigates to the specified path.

        Args:
            path (str or Page): The path to navigate to. If path is a subclass of Page, it will be reversed using the reverse method
            provided by the self object. If path is a string and **kwargs is not empty, it will append the query string
            to the path.

            **kwargs: Additional key-value pairs to be included in the query string. Each key-value pair will be
            URL-encoded.

        Raises:
            Exception: If the link mode is invalid.
        """
        if isinstance(path, type) and issubclass(path, Page):
            path = self.reverse(path, **kwargs)
        elif kwargs:
            path += "?" + "&".join(f"{url_quote(k)}={url_quote(v)}" for k, v in kwargs.items())

        if self.link_mode == self.LINK_MODE_DIRECT:
            window.location = path
        elif self.link_mode == self.LINK_MODE_HTML5:
            history.pushState(jsobj(), "", path)
            self.application.mount(self.application._selector_or_element, path)
        elif self.link_mode == self.LINK_MODE_HASH:
            path = path[1:] if path.startswith("#") else path
            if not is_server_side:
                history.pushState(jsobj(), "", "#" + path)
            self.application.mount(self.application._selector_or_element, path)
        else:
            raise Exception(f"Invalid link mode: {self.link_mode}")
