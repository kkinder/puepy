from puepy import Application, Page, t

app = Application()


@app.page()
class CounterPage(Page):
    def initial(self):
        return {"current_value": 0}

    def populate(self):
        with t.div(classes="button-box"):
            t.button("-", classes=["button", "decrement-button"], on_click=self.on_decrement_click)
            t.span(str(self.state["current_value"]), classes="count")
            t.button("+", classes="button increment-button", on_click=self.on_increment_click)

    def on_decrement_click(self, event):
        self.state["current_value"] -= 1

    def on_increment_click(self, event):
        self.state["current_value"] += 1


app.mount("#app")
