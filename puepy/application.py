from puepy.storage import BrowserStorage
from .core import Page
from .runtime import (
    is_server_side,
    add_event_listener,
    window,
    platform,
    PLATFORM_PYODIDE,
)


class Application:
    def __init__(self):
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

    def install_router(self, router_class, **kwargs):
        self.router = router_class(application=self, **kwargs)
        if platform == PLATFORM_PYODIDE:
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

    def mount(self, selector_or_element, path=None, page_kwargs=None):
        if page_kwargs is None:
            page_kwargs = {}

        self._selector_or_element = selector_or_element

        if self.router:
            if self.router.link_mode == self.router.LINK_MODE_HASH:
                path = path or window.location.hash.split("#", 1)[-1]
            elif self.router.link_mode in (self.router.LINK_MODE_DIRECT, self.router.LINK_MODE_HTML5):
                path = path or window.location.pathname
            else:
                path = ""
            route, arguments = self.router.match(path)
            if arguments:
                page_kwargs.update(arguments)

            if route:
                page_class = route.page
            elif self.default_page:
                page_class = self.default_page
            else:
                return None
        elif self.default_page:
            route = None
            page_class = self.default_page
        else:
            return None

        page: Page = page_class(matched_route=route, application=self, **page_kwargs)
        page.mount(selector_or_element)
        return page
