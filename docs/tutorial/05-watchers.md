# Watchers

We've introduced reactivity, but what happens when you want to monitor specific variables for changes? In PuePy, you can use `on_<variable>_change` methods in your components to watch for changes in specific variables. In the example below, try guessing the number 4:

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/05_watchers/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest"/>


``` py title="watchers.py" hl_lines="17"
@app.page()
class WatcherPage(Page):
    def initial(self):
        self.winner = 4

        return {"number": "", "message": ""}

    def populate(self):
        t.h1("Can you guess a number between 1 and 10?")

        with t.div(style="margin: 1em"):
            t.input(bind="number", placeholder="Enter a guess", autocomplete="off", type="number", maxlength=1)

        if self.state["message"]:
            t.p(self.state["message"])

    def on_number_change(self, event):  # (1)
        try:
            if int(self.state["number"]) == self.winner:
                self.state["message"] = "You guessed the number!"
            else:
                self.state["message"] = "Keep trying..."
        except (ValueError, TypeError):
            self.state["message"] = ""
```

1. The function name, `on_number_change` is automatically registered based on the pattern of `on_<variable>_change`. The event parameter is passed up from the original JavaScript event that triggered the change.

The watcher method itself changes the `#!py self.state["message"]` variable based on the value of `#!py self.state["number"]`. If the number is equal to the `#!py self.winner` constant, the message is updated to "You guessed the number!" Otherwise, the message is set to "Keep trying...". The state is once again changed and the page is re-rendered.
