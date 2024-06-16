import sys

from puepy.storage import BrowserStorage
from .core import Page, t, Prop
from .reactivity import ReactiveDict, Stateful
from .runtime import (
    is_server_side,
    add_event_listener,
    window,
    platform,
    PLATFORM_PYODIDE,
)
from . import exceptions


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


class Application(Stateful):
    def __init__(self):
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

    def install_router(self, router_class, **kwargs):
        self.router = router_class(application=self, **kwargs)
        if not is_server_side:
            add_event_listener(window, "popstate", self._on_popstate)

    def page(self, route=None, name=None):
        """
        Intended to be called as a secorator.

        app = Application()
        @app.page("/my-page")
        class MyPage(Page):
            ....
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
        self.mount(self._selector_or_element, path=path, page_kwargs=page_kwargs)

    def mount(self, selector_or_element, path=None, page_kwargs=None):
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
        if self.router.link_mode == self.router.LINK_MODE_HASH:
            return window.location.hash.split("#", 1)[-1]
        elif self.router.link_mode in (self.router.LINK_MODE_DIRECT, self.router.LINK_MODE_HTML5):
            return window.location.pathname
        else:
            return ""

    def mount_page(self, selector_or_element, page_class, route, page_kwargs, handle_exceptions=True):
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
        self.mount_page(
            self._selector_or_element, self.not_found_page, None, {"error": exception}, handle_exceptions=False
        )

    def handle_forbidden(self, exception):
        self.mount_page(
            self._selector_or_element, self.forbidden_page, None, {"error": exception}, handle_exceptions=False
        )

    def handle_unauthorized(self, exception):
        self.mount_page(
            self._selector_or_element, self.unauthorized_page, None, {"error": exception}, handle_exceptions=False
        )

    def handle_error(self, exception):
        self.mount_page(self._selector_or_element, self.error_page, None, {"error": exception}, handle_exceptions=False)
        if is_server_side:
            raise

    def handle_redirect(self, exception):
        self.router.navigate_to_path(exception.path)
        # self.mount(self._selector_or_element, exception.path)
