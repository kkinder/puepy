from puepy.core import Component, Page, t


class StandardContainer(Component):
    default_classes = ["w-full", "max-w-6xl", "container", "mx-auto"]


class HeaderBar(Component):
    default_classes = ["navbar", "bg-base-300"]

    def populate(self):
        with t.standard_container():
            t.span(self.page.page_title(), classes="text-xl")


class Example(Component):
    props = ["title"]

    def populate(self):
        from examples.main import Index

        t.header_bar()

        with t.div(classes="bg-base-200"):
            with t.standard_container():
                with t.div(classes="text-sm breadcrumbs"):
                    with t.ul():
                        with t.li():
                            t.link("Examples", href=Index)
                        t.li(self.title)

        with t.standard_container():
            self.insert_slot()


class Link(Component):
    enclosing_tag = "a"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_event_handler("click", self.on_click)

    def set_href(self, href):
        if issubclass(href, Page):
            self._resolved_href = self.page.router.reverse(href)
        else:
            self._resolved_href = href

        self.attrs["href"] = self._resolved_href

    def on_click(self, event):
        if (
            isinstance(self._resolved_href, str)
            and self._resolved_href.startswith("/")
            and self.page.application.navigate_to_path(self._resolved_href)
        ):
            # A page was found; prevent navigation and navigate to page
            event.preventDefault()


components = [Link, Example, HeaderBar, StandardContainer]
