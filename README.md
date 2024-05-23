# PuePy -- PyScript Frontend Framework

PuePy is an attempt to create a frontend framework using [PyScript](https://pyscript.net). PuePy is partially inspired by Vue. It runs entirely in your browser, though server-side rendering is likely feasible.  PuePy aims to support two runtime environments: PyScript Pyodide or PyScript Micropython. The Micropython option foregoes some features found in the CPython, but offers a far, far smaller runtime, making it a better option for websites. Line-of-business or scientific webapp developers may prefer the CPython version, which is heavier but more functional.

Without further ado, here's a taste:

```python
from puepy import Page, Application, t

app = Application()


@app.page()
class Hello(Page):
    def initial(self):
        return dict(name="")

    def populate(self):
        with t.div(classes=["container", "mx-auto", "p-4"]):
            t.h1("Welcome to PyScript", classes=["text-xl", "pb-4"])
            if self.state["name"]:
                t.p(f"Why hello there, {self.state['name']}")
            else:
                t.p("Why don't you tell me your name?")
            t.input(placeholder="Enter your name", bind="name")
            t.button("Continue", classes="btn btn-lg", on_click=self.on_button_click)

    def on_button_click(self, event):
        print("Button clicked")  # This logs to console


app.mount("#app")
```

A few things to note:

- The `.state` dictionary, which is populated by `initial()`, is reactive. As it changes, populate is called as necessary and the page is redrawn.
- Events are simply and Python, but use JavaScript events under the hood (including custom events)
- You layout your page with context managers.

## Components, Props, Slots

You can define reusable components with PuePy, which also use slots (similar to Vue, Web Components, etc). Here's a simple Card component:

```python
from puepy import Component, Prop, t

# This registers the component
@t.component()
class Card(Component):
    default_role = "card"
    props = ["help_text", Prop("show_buttons", "whether to show buttons", bool, False)]

    def populate(self):
        with t.div(classes="card-header"):
            self.insert_slot("card-header")
        with t.div(classes="card-body"):
            self.insert_slot()
            if self.show_buttons:
                with t.div(classes="card-footer"):
                    t.button("Button 1")
                    t.button("Button 2")
```

Using the component is simple:

```python
@app.page("/my-page")
class MyPage(Page):
    def populate(self):
        with t.card(show_buttons=True) as card:
            with card.slot("card-header"):
                t("Show header here")
            with card.slot():
                t("This is the card body")
```

## Where to go from here...

A few things to note:

- PuePy is not fully documented yet
- I haven't figured out exactly what is permanent and what isn't
- You can examine, in git, the `/examples` directory and view them with `python3 ./serve_examples.py`

