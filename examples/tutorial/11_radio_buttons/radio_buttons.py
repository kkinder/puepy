from puepy import Application, Page, t

app = Application()

@app.page()
class RadioButtonsPage(Page):
    def initial(self):
        return {"selected_option": "Option 2"}

    def populate(self):
        t.h1("Choose an Option")

        options = ["Option 1", "Option 2", "Option 3"]

        with t.div():
            for idx, option in enumerate(options):
                option_id = f"option{idx+1}"
                t.input(
                    type="radio",
                    name="options",
                    value=option,
                    id=option_id,
                    bind="selected_option"
                )
                t.label(option, for_=option_id)
                t.br()

        t.h2(f"You selected: {self.state['selected_option']}")

app.mount("#app")
