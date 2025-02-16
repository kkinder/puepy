# Counter

In this chapter, we introduce event handlers. Take a look at this demo, with plus and minus buttons that increment and decrement a counter. You may remember it from the [pupy.dev](https://puepy.dev) homepage.

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/03_counter/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest"/>

In this example, we bind two events to event handlers. Follow along with the annotations in the code below for a more detailed explanation:

``` py title="counter.py" hl_lines="15 19 22 25" linenums="1"
from puepy import Application, Page, t

app = Application()


@app.page()
class CounterPage(Page):
    def initial(self):
        return {"current_value": 0}

    def populate(self):
        with t.div(classes="button-box"):
            t.button("-", 
                     classes=["button", "decrement-button"],
                     on_click=self.on_decrement_click)  # (1)
            t.span(str(self.state["current_value"]), classes="count")
            t.button("+", 
                     classes="button increment-button",
                     on_click=self.on_increment_click)  # (2)

    def on_decrement_click(self, event):
        self.state["current_value"] -= 1  # (3)

    def on_increment_click(self, event):
        self.state["current_value"] += 1  # (4)


app.mount("#app")
```

1. The `on_click` parameter is passed to the `button` tag, which binds the `on_decrement_click` method to the button's click event.
2. The `on_click` parameter is passed to the `button` tag, which binds the `on_increment_click` method to the button's click event.
3. The `on_decrement_click` method decrements the `current_value` key in the page's state.
4. The `on_increment_click` method increments the `current_value` key in the page's state.

!!! tip
    The `event` parameter sent to event handlers is the same as it is in JavaScript. You can call `event.preventDefault()` or `event.stopPropagation()` as needed.

As before, because we are modifying the state directly, the page will re-render automatically. This is the power of PuePy's reactivity system.