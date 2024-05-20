from .runtime import is_server_side, add_event_listener, window, history, platform, PLATFORM_PYODIDE


from .core import ReactiveDict, jsobj, Page
from puepy.storage import BrowserStorage


class Application:
    def __init__(self):
        self.ephemeral = ReactiveDict()
        if is_server_side:
            self.session_storage = None
            self.local_storage = None
        else:
            from js import localStorage, sessionStorage

            self.session_storage = BrowserStorage(sessionStorage, "session_storage")
            self.local_storage = BrowserStorage(localStorage, "local_storage")
        self.router = None
        self.selector_or_element = None
        self.default_page = None
        if platform == PLATFORM_PYODIDE:
            add_event_listener(window, "popstate", self.on_popstate)

        self.enable_history_mode = True

    def install_router(self, router_class, **kwargs):
        self.router = router_class(application=self, **kwargs)

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

    def navigate_to_path(self, path):
        if self.enable_history_mode:
            history.pushState(jsobj(), "", path)
            return self.mount(self.selector_or_element, path)
        else:
            window.location = path

    def on_popstate(self, event):
        self.mount(self.selector_or_element, window.location.pathname)

    def mount(self, selector_or_element, path=None, **kwargs):
        path = path or window.location.pathname

        self.selector_or_element = selector_or_element

        if self.router:
            route, arguments = self.router.match(path)
            if arguments:
                kwargs.update(arguments)

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

        page: Page = page_class(router=self.router, matched_route=route, application=self, **kwargs)
        page.mount(selector_or_element)
        return page
