from examples.app import app
from puepy.core import t, Page, Component, Prop


@t.component()
class Greeting(Component):
    props = [
        Prop(name="name", description="name", type=str, default_value="Monty"),  # Most explicit
        "favorite_movie",  # Also valid for simple strings,
        dict(name="favorite_show", default_value="Monty Python's Flying Circus"),  # Dicts also work
    ]

    def populate(self):
        t.p(
            f"Hello, my name is {self.name} and my favorite show is {self.favorite_show}. My favorite movie"
            f" is {self.favorite_movie}"
        )


@app.page("/props")
class PropsExample(Page):
    def initial(self):
        return dict(name="Monty", favorite_movie="Life of Brian", favorite_show="Monty Python's Flying Circus")

    def populate(self):
        with t.example(title="Props") as e:
            with e.slot():
                with t.div(classes="prose"):
                    t.p("Props provide a way of passing values down to child elements.")
                    t.h3("Example Rendering")
                    t.greeting(
                        name=self.state["name"],
                        favorite_movie=self.state["favorite_movie"],
                        favorite_show=self.state["favorite_show"],
                    )

    def page_title(self):
        return f"{self.application.base_title} | Props"
