from puepy import Application, Page, t

app = Application()


@app.page()
class RefsProblemPage(Page):
    def initial(self):
        return {"word": ""}

    def populate(self):
        t.h1("Problem: DOM elements are re-created")
        if self.state["word"]:
            for char in self.state["word"]:
                t.span(char, classes="char-box")
        with t.div(style="margin-top: 1em"):
            t.input(bind="word", placeholder="Type a word")


app.mount("#app")
