# Hello, Name

In this chapter, we introduce state and variables by creating a simple form that asks for a name and greets the user.

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/02_hello_name/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest"/>

The html and pyscript configuration are the same as in the previous [Hello, World](01-hello-world.md) chapter, so we
will only study the Python code. Expand the annotations in the code below for a more detail explanation of the changes:

``` py title="hello_name.py" hl_lines="8 9 12 18"
from puepy import Application, Page, t

app = Application()


@app.page()
class HelloNamePage(Page):
    def initial(self):
        return {"name": ""}  # (1)

    def populate(self):
        if self.state["name"]:  # (2)
            t.h1(f"Hello, {self.state['name']}!")
        else:
            t.h1(f"Why don't you tell me your name?")

        with t.div(style="margin: 1em"):
            t.input(bind="name", placeholder="name", autocomplete="off")  # (3)


app.mount("#app")
```

1. The `initial()` method defines the page's initial **working state**. In this case, it returns a dictionary with a
   single key, `name`, which is initially an empty string.
2. We check the value of `self.state["name"]` and renders different content based on that value.
3. We define an `input` element with a `bind="name"` parameter. This binds the input element to the `name` key in the
   page's state. When the input value changes, the state is updated, and the page is re-rendered.

## Reactivity

A page or component's initial state is defined by the `initial()` method. If implemented, it should return a dictionary,
which is then stored as a special reactive dictionary, `self.state`. As the state is modified, the component redraws,
updating the DOM as needed.

!!! danger "Modifying `.state` values in-place will not work"

    For complex objects like lists and dictionaries, you cannot modify them in-place and expect the component to re-render.

    ``` py
    # THESE WILL NOT WORK:
    self.state["my_list"].append("spam")
    self.state["my_dict"]["spam"] = "eggs"
    ```

    This is because PuePy's ReactiveDict cannot detect "deep" changes to state automatically. If you are modifying objects
    in-place, use `with self.state.mutate()` as a context manager:

    ``` py
    # This will work
    with self.state.mutate("my_list", "my_dict"):
        self.state["my_list"].append("spam")
        self.state["my_dict"]["spam"] = "eggs"
    ```

??? note "More information on reactivity"

    For more information on reactivity in PuePy, see the [Reactivity Developer Guide](../guide/reactivity.md).
