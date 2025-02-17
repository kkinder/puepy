import itertools
import random
import sys
import time

from puepy.storage import BrowserStorage

from . import exceptions
from .core import Page, t, Prop
from .reactivity import ReactiveDict, Stateful
from .runtime import (
    is_server_side,
    add_event_listener,
    window,
)


class GenericErrorPage(Page):
    props = ["error"]

    def populate(self):
        t.h1(f"Error: {self.error}")


class TracebackErrorPage(Page):
    props = ["error"]

    def format_exception(self):
        try:
            import traceback
        except ImportError:
            import io

            buf = io.StringIO()
            sys.print_exception(self.error, buf)
            return buf.getvalue()

        return "\n".join(traceback.format_exception(type(self.error), self.error, self.error.__traceback__))

    def populate(self):
        t.h1(f"Error: {self.error}")
        t.pre(str(self.format_exception()))


class DefaultIdGenerator:
    """
    A class representing a default ID generator.

    The DefaultIdGenerator class generates serial IDs with an optional prefix using a counter and base36 encoding.

    Attributes:
        counter (itertools.count): A counter object to keep track of the next ID value.
        prefix (str): An optional prefix to prepend to the generated IDs.
    """

    def __init__(self, prefix=None):
        """
        Args:
            prefix (Optional[str]): The prefix to be used for generating unique IDs. Default is "pp-", 5 random numbers and letters, then "-" (eg, "pp-df456-").
        """
        self.counter = itertools.count()
        if prefix:
            self.prefix = prefix
        else:
            self.prefix = "pp-" + "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(5)) + "-"

    @staticmethod
    def _int_to_base36(num):
        base_chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        base = len(base_chars)
        encoded = ""
        while num:
            num, rem = divmod(num, base)
            encoded = base_chars[rem] + encoded
        return encoded or base_chars[0]

    def get_id_for_element(self, element):
        """
        Returns the unique ID for the given element.

        Args:
            element: The element for which the ID is to be retrieved.

        Returns:
            The unique ID for the given element.
        """
        return self.prefix + self._int_to_base36(next(self.counter))


class Application(Stateful):
    """
    The main application class for PuePy. It manages the state, storage, router, and pages for the application.

    Attributes:
        state (ReactiveDict): The state object for the application.
        session_storage (BrowserStorage): The session storage object for the application.
        local_storage (BrowserStorage): The local storage object for the application.
        router (Router): The router object for the application, if any
        default_page (Page): The default page to mount if no route is matched.
        active_page (Page): The currently active page.
        not_found_page (Page): The page to mount when a 404 error occurs.
        forbidden_page (Page): The page to mount when a 403 error occurs.
        unauthorized_page (Page): The page to mount when a 401 error occurs.
        error_page (Page): The page to mount when an error occurs.
    """

    def __init__(self, element_id_generator=None):
        self.state = ReactiveDict(self.initial())
        self.add_context("state", self.state)

        if is_server_side:
            self.session_storage = None
            self.local_storage = None
        else:
            from js import localStorage, sessionStorage

            self.session_storage = BrowserStorage(sessionStorage, "session_storage")
            self.local_storage = BrowserStorage(localStorage, "local_storage")
        self.router = None
        self._selector_or_element = None
        self.default_page = None
        self.active_page = None

        self.not_found_page = GenericErrorPage
        self.forbidden_page = GenericErrorPage
        self.unauthorized_page = GenericErrorPage
        self.error_page = TracebackErrorPage

        self.element_id_generator = element_id_generator or DefaultIdGenerator()

    def install_router(self, router_class, **kwargs):
        """
        Install a router in the application.

        Args:
            router_class (class): A class that implements the router logic for the application. At this time, only
                `puepy.router.Router` is available.
            **kwargs: Additional keyword arguments that can be passed to the router_class constructor.
        """
        self.router = router_class(application=self, **kwargs)
        if not is_server_side:
            add_event_listener(window, "popstate", self._on_popstate)

    def page(self, route=None, name=None):
        """
        A decorator for `Page` classes which adds the page to the application with a specified route and name.

        Intended to be called as a decorator.

        Args:
            route (str): The route for the page. Default is None.
            name (str): The name of the page. If left None, page class is used as the name.

        Examples:
            ``` py
            app = Application()
            @app.page("/my-page")
            class MyPage(Page):
                ...
            ```
        """
        if route:
            if not self.router:
                raise Exception("Router not installed")

            def decorator(func):
                self.router.add_route(route, func, name=name)
                return func

            return decorator
        else:

            def decorator(func):
                self.default_page = func
                return func

            return decorator

    def _on_popstate(self, event):
        if self.router.link_mode == self.router.LINK_MODE_HASH:
            self.mount(self._selector_or_element, window.location.hash.split("#", 1)[-1])
        elif self.router.link_mode in (self.router.LINK_MODE_DIRECT, self.router.LINK_MODE_HTML5):
            self.mount(self._selector_or_element, window.location.pathname)

    def remount(self, path=None, page_kwargs=None):
        """
        Remounts the selected element or selector with the specified path and page_kwargs.

        Args:
            path (str): The new path to be used for remounting the element or selector. Default is None.
            page_kwargs (dict): Additional page kwargs to be passed when remounting. Default is None.

        """
        self.mount(self._selector_or_element, path=path, page_kwargs=page_kwargs)

    def mount(self, selector_or_element, path=None, page_kwargs=None):
        """
        Mounts a page onto the specified selector or element with optional path and page_kwargs.

        Args:
            selector_or_element: The selector or element on which to mount the page.
            path: Optional path to match against the router. Defaults to None.
            page_kwargs: Optional keyword arguments to pass to the mounted page. Defaults to None.

        Returns:
            (Page): The mounted page instance
        """
        if page_kwargs is None:
            page_kwargs = {}

        self._selector_or_element = selector_or_element

        if self.router:
            path = path or self.current_path
            route, arguments = self.router.match(path)
            if arguments:
                page_kwargs.update(arguments)

            if route:
                page_class = route.page
            elif path in ("", "/") and self.default_page:
                page_class = self.default_page
            elif self.not_found_page:
                page_class = self.not_found_page
            else:
                return None
        elif self.default_page:
            route = None
            page_class = self.default_page
        else:
            return None

        self.active_page = None
        try:
            self.mount_page(
                selector_or_element=selector_or_element,
                page_class=page_class,
                route=route,
                page_kwargs=page_kwargs,
                handle_exceptions=True,
            )
        except Exception as e:
            self.handle_error(e)
        return self.active_page

    @property
    def current_path(self):
        """
        Returns the current path based on the router's link mode.

        Returns:
            str: The current path.
        """
        if self.router.link_mode == self.router.LINK_MODE_HASH:
            return window.location.hash.split("#", 1)[-1]
        elif self.router.link_mode in (self.router.LINK_MODE_DIRECT, self.router.LINK_MODE_HTML5):
            return window.location.pathname
        else:
            return ""

    def mount_page(self, selector_or_element, page_class, route, page_kwargs, handle_exceptions=True):
        """
        Mounts a page on the specified selector or element with the given parameters.

        Args:
            selector_or_element (str or Element): The selector string or element to mount the page on.
            page_class (class): The page class to mount.
            route (str): The route for the page.
            page_kwargs (dict): Additional keyword arguments to pass to the page class.
            handle_exceptions (bool, optional): Determines whether to handle exceptions thrown during mounting.
                Defaults to True.
        """
        page_class._expanded_props()

        # For security, we only pass props to the page that are defined in the page's props
        #
        # We also handle the list or not-list props for multiple or single values
        # (eg, ?foo=1&foo=2 -> ["1", "2"] if needed)
        #
        prop_args = {}
        prop: Prop
        for prop in page_class.props_expanded.values():
            if prop.name in page_kwargs:
                value = page_kwargs.pop(prop.name)
                if prop.type is list:
                    prop_args[prop.name] = value if isinstance(value, list) else [value]
                else:
                    prop_args[prop.name] = value if not isinstance(value, list) else value[0]

        self.active_page: Page = page_class(matched_route=route, application=self, extra_args=page_kwargs, **prop_args)
        try:
            self.active_page.mount(selector_or_element)
        except exceptions.PageError as e:
            if handle_exceptions:
                self.handle_page_error(e)
            else:
                raise

    def handle_page_error(self, exc):
        """
        Handles page error based on the given exception by inspecting the exception type and passing it along to one
        of:

        - `handle_not_found`
        - `handle_forbidden`
        - `handle_unauthorized`
        - `handle_redirect`
        - `handle_error`

        Args:
            exc (Exception): The exception object representing the page error.
        """
        if isinstance(exc, exceptions.NotFound):
            self.handle_not_found(exc)
        elif isinstance(exc, exceptions.Forbidden):
            self.handle_forbidden(exc)
        elif isinstance(exc, exceptions.Unauthorized):
            self.handle_unauthorized(exc)
        elif isinstance(exc, exceptions.Redirect):
            self.handle_redirect(exc)
        else:
            self.handle_error(exc)

    def handle_not_found(self, exception):
        """
        Handles the exception for not found page. By default, it mounts the self.not_found_page class and passes it
        the exception as an argument.

        Args:
            exception (Exception): The exception that occurred.
        """
        self.mount_page(
            self._selector_or_element, self.not_found_page, None, {"error": exception}, handle_exceptions=False
        )

    def handle_forbidden(self, exception):
        """
        Handles the exception for forbidden page. By default, it mounts the self.forbidden_page class and passes it
        the exception as an argument.

        Args:
            exception (Exception): The exception that occurred.
        """
        self.mount_page(
            self._selector_or_element,
            self.forbidden_page,
            None,
            {"error": exception},
            handle_exceptions=False,
        )

    def handle_unauthorized(self, exception):
        """
        Handles the exception for unauthorized page. By default, it mounts the self.unauthorized_page class and passes it
        the exception as an argument.

        Args:
            exception (Exception): The exception that occurred.
        """
        self.mount_page(
            self._selector_or_element, self.unauthorized_page, None, {"error": exception}, handle_exceptions=False
        )

    def handle_error(self, exception):
        """
        Handles the exception for application or unknown errors. By default, it mounts the self.error_page class and
        passes it the exception as an argument.

        Args:
            exception (Exception): The exception that occurred.
        """
        self.mount_page(self._selector_or_element, self.error_page, None, {"error": exception}, handle_exceptions=False)
        if is_server_side:
            raise

    def handle_redirect(self, exception):
        """
        Handles a redirect exception by navigating to the given path.

        Args:
            exception (RedirectException): The redirect exception containing the path to navigate to.
        """
        self.router.navigate_to_path(exception.path)
