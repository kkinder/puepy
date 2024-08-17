# PuePy - PyScript Frontend Framework

➡️ [Project Website](https://puepy.dev)
📝 [Project Documentation](https://docs.puepy.dev/)

PuePy is a lightweight web framework that uses WebAssembly via [PyScript](https://pyscript.net) to put Python right in your browser with all the modern conveniences of a web framework, but none of the headaches of Webpack, NPM or even JavaScript.

- Reactive data binding with component-based architecture
- Single Page App (SPA) router included
- No build layer: direct execution like other Python projects
- Choice of full [Pyodide](https://pyodide.org/en/stable/) or [Micropython](https://micropython.org/)

## 🐒 Try a demo app

See [ExpenseLemur.com](https://expenselemur.com) and the [Expense Lemur Github Repo](https://github.com/kkinder/expenselemur) for a demonstration of what PuePy is capable of.

## 🧑‍💻 See some code

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
                t.p(f"Hello there, {self.state['name']}")
            else:
                t.p("Why don't you tell me your name?")
            t.input(placeholder="Enter your name", bind="name")
            t.button("Continue", classes="btn btn-lg", on_click=self.on_button_click)

    def on_button_click(self, event):
        print("Button clicked")  # This logs to console


app.mount("#app")
```

## Learn

- **Project Website**: [puepy.dev](https://puepy.dev/)
- **Documentation**: [docs.puepy.dev](https://docs.puepy.dev/)

## License

PuePy is licensed under the Apache 2 license, for your coding convenience.
