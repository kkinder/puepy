from examples.app import app
from examples.calc import CalcExample
from examples.forms import FormsExample
from examples.props import PropsExample
from examples.events import EventsExample
from puepy.core import t, Page


@app.page()
class Index(Page):
    redraw_on_changes = False

    def populate(self):
        t.header_bar()

        with t.standard_container(classes="prose prose-slate"):
            t.p("Here are a few examples of how you can build pages with PuePy")
            with t.ul():
                with t.li():
                    t.link("Forms", href=FormsExample)
                with t.li():
                    t.link("Calculator", href=CalcExample)
                with t.li():
                    t.link("Props", href=PropsExample)
                with t.li():
                    t.link("Events (Todo List)", href=EventsExample)

    def page_title(self):
        return self.application.base_title


app.mount("#app")
