from puepy import Application, Page, t

app = Application()


@app.page()
class RefsSolutionPage(Page):
    def initial(self):
        return {"word": ""}

    def populate(self):
        t.h1("Solution: Use ref=")
        if self.state["word"]:
            for char in self.state["word"]:
                t.span(char, classes="char-box")
        with t.div(style="margin-top: 1em"):
            t.input(bind="word", placeholder="Type a word", ref="enter_word")
        t.hr()
        t.p(
            'Solution: by setting ref="enter_word" on the input box, we tell PuePy to identify that component by its ref.'
        )
        t.a("See Problem", href="./index.html")


app.mount("#app")
