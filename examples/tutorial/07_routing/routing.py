from puepy import Application, Page, Component, t
from puepy.router import Router

app = Application()
app.install_router(Router, link_mode=Router.LINK_MODE_HASH)

pets = {
    "scooby": {"name": "Scooby-Doo", "type": "dog", "character": "fearful"},
    "garfield": {"name": "Garfield", "type": "cat", "character": "lazy"},
    "snoopy": {"name": "Snoopy", "type": "dog", "character": "playful"},
}


@t.component()
class Link(Component):
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


@app.page("/pet/<pet_id>")
class PetPage(Page):
    props = ["pet_id"]

    def populate(self):
        pet = pets.get(self.pet_id)
        t.h1("Pet Information")
        with t.dl():
            for k, v in pet.items():
                t.dt(k)
                t.dd(v)
        t.link("Back to Homepage", href=DefaultPage)


@app.page()
class DefaultPage(Page):
    def populate(self):
        t.h1("PuePy Routing Demo: Pet Listing")
        with t.ul():
            for pet_id, pet_details in pets.items():
                with t.li():
                    t.link(pet_details["name"], href=PetPage, args={"pet_id": pet_id})


app.mount("#app")
