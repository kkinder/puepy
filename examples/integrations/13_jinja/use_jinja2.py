from puepy import Application, Page, t, Component, Prop
from puepy.runtime import add_event_listener

import jinja2

app = Application()


@t.component()
class Jinja2Fragment(Component):
    props = [
        Prop("template", type=str, default_value=""),
        Prop("context", type=dict, default_value=None),
        Prop(
            "event_hooks",
            description="A list of tuples: (query_selector, event, handler)",
            type=list,
            default_value=None,
        ),
    ]
    component_name = "jinja2"

    def _render_onto(self, element, attrs):
        template = jinja2.Template(source=self.template)
        output = template.render(self.context or {})
        element.innerHTML = output

        if self.event_hooks:
            for query_selector, event, handler in self.event_hooks:
                for element in element.querySelectorAll(event):
                    add_event_listener(element, event, handler)


EXAMPLE_TEMPLATE = """
<h1>Hello, {{ name }}</h1>
<input type="text" value="{{ name }}" class="my-input">
"""


@app.page()
class LtkPage(Page):
    def initial(self):
        return {"name": "Monty"}

    def populate(self):
        t.jinja2(
            template=EXAMPLE_TEMPLATE, context=self.state, event_hooks=[("input.my-input", "input", self.on_text_input)]
        )

    def on_text_input(self, event):
        self.state["name"] = event.target.value


app.mount("#app")
