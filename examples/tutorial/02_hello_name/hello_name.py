from puepy import Application, Page, t

app = Application()


@app.page()
class HelloNamePage(Page):
    def initial(self):
        return {"name": ""}

    def populate(self):
        if self.state["name"]:
            t.h1(f"Hello, {self.state['name']}!")
        else:
            t.h1(f"Why don't you tell me your name?")

        with t.div(style="margin: 1em"):
            t.input(bind="name", placeholder="name", autocomplete="off")


app.mount("#app")
