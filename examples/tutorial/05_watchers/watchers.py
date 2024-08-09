from puepy import Application, Page, t

app = Application()


@app.page()
class WatcherPage(Page):
    def initial(self):
        self.winner = 4

        return {"number": "", "message": ""}

    def populate(self):
        t.h1("Can you guess a number between 1 and 10?")

        with t.div(style="margin: 1em"):
            t.input(bind="number", placeholder="Enter a guess", autocomplete="off", type="number", maxlength=1, min=1, max=10)

        if self.state["message"]:
            t.p(self.state["message"])

    def on_number_change(self, event):
        try:
            if int(self.state["number"]) == self.winner:
                self.state["message"] = "You guessed the number!"
            else:
                self.state["message"] = "Keep trying..."
        except (ValueError, TypeError):
            self.state["message"] = ""


app.mount("#app")
