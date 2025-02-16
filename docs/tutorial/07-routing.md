# Routing

For single page apps (SPAs) or even complex pages with internal navigation, PuePy's client-side routing feature renders different pages based on the URL and provides a way of linking between various routes. Use of the router is optional and if no router is installed, the application will always render the default page.

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/07_routing/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest" height="20em"/>

!!! note "URL Changes"
    In the embedded example above, the "URL" does not change because the embedded example is not a full web page. In a full web page, the URL would change to reflect the current page. Try opening the example [in a new window](https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/07_routing/index.html) to see the URL change.

Inspired by Flask's simple and elegant routing system, PuePy uses decorators on page classes to define routes and parameters. The router can be configured to use either hash-based or history-based routing. Consider this example's source code:

``` py title="routing.py" linenums="1" hl_lines="5 15 43 54 64 65 66"

from puepy import Application, Page, Component, t
from puepy.router import Router

app = Application()
app.install_router(Router, link_mode=Router.LINK_MODE_HASH)  # (1)

pets = {
    "scooby": {"name": "Scooby-Doo", "type": "dog", "character": "fearful"},
    "garfield": {"name": "Garfield", "type": "cat", "character": "lazy"},
    "snoopy": {"name": "Snoopy", "type": "dog", "character": "playful"},
}


@t.component()
class Link(Component):  # (2)
    props = ["args"]
    enclosing_tag = "a"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_event_listener("click", self.on_click)

    def set_href(self, href):
        if issubclass(href, Page):
            args = self.args or {}
            self._resolved_href = self.page.router.reverse(href, **args)
        else:
            self._resolved_href = href

        self.attrs["href"] = self._resolved_href

    def on_click(self, event):
        if (
            isinstance(self._resolved_href, str)
            and self._resolved_href[0] in "#/"
            and self.page.router.navigate_to_path(self._resolved_href)
        ):
            # A page was found; prevent navigation and navigate to page
            event.preventDefault()


@app.page("/pet/<pet_id>")  # (3)
class PetPage(Page):
    props = ["pet_id"]

    def populate(self):
        pet = pets.get(self.pet_id)
        t.h1("Pet Information")
        with t.dl():
            for k, v in pet.items():
                t.dt(k)
                t.dd(v)
        t.link("Back to Homepage", href=DefaultPage)  # (4)


@app.page()
class DefaultPage(Page):
    def populate(self):
        t.h1("PuePy Routing Demo: Pet Listing")
        with t.ul():
            for pet_id, pet_details in pets.items():
                with t.li():
                    t.link(pet_details["name"],
                           href=PetPage,
                           args={"pet_id": pet_id})  # (5)


app.mount("#app")
```

1. The router is installed with the `link_mode` set to `Router.LINK_MODE_HASH`. This sets the router to use hash-based routing.
2. The `Link` component is a custom component that creates links to other pages. It uses the router to navigate to the specified page.
3. The `PetPage` class is decorated with a route. The `pet_id` parameter is parsed from the URL.
4. The `Link` component is used to create a link back to the homepage, as passed by the `href` parameter.
5. The `Link` component is used to create links to each pet's page, passing the `pet_id` as a parameter.

## Installing the router

The router is installed with the `install_router` method on the application instance:

``` py
app.install_router(Router, link_mode=Router.LINK_MODE_HASH)
```

If you wanted to use html5 history mode (see [the Router developer guide](../guide/advanced-routing.md)), you would set `link_mode=Router.LINK_MODE_HISTORY`.

## The default page

The default page is rendered for the "root" URL or when no URL is specified. The default page is defined with no path:

``` py
@app.page()
class DefaultPage(Page):
    ...
```

??? note "More information on the router"

    For more information on the router, see the [Router Developer Guide](../guide/advanced-routing.md).
