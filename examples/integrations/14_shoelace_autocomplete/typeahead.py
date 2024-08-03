from puepy import Component, Page, Application, t
from puepy.runtime import next_tick

app = Application()


@t.component()
class TypeAhead(Component):
    props = ["choices", "value", "placeholder"]

    def initial(self):
        return dict(
            input_value=self.value or "",
        )

    def populate(self):
        with t.sl_popup(ref="popup", placement="bottom", on_focusout=self.on_focusout, sync="width"):
            t.sl_input(
                slot="anchor",
                bind="input_value",
                placeholder=self.placeholder or "",
                on_sl_focus=self.on_focus,
                ref="input",
                autocomplete="off",
                clearable=True,
            )
            with t.sl_menu(on_sl_select=self.on_menu_select):
                for choice in self.get_available_choices():
                    t.sl_menu_item(choice, value=choice)

    def on_focusout(self, event):
        if not self.refs["popup"].element.contains(event.relatedTarget):
            self.close_popup()

    def on_focus(self, event):
        self.open_popup()

    def on_clear(self, event):
        self.state["input_value"] = ""
        self.send_bind_event()

    def on_menu_select(self, event):
        self.state["input_value"] = event.detail.item.value
        self.send_bind_event()
        next_tick(self.close_popup)

    def close_popup(self):
        self.refs["popup"].element.active = False

    def open_popup(self):
        self.refs["popup"].element.active = True

    def send_bind_event(self):
        if self.bind:
            self.origin.state[self.bind] = self.state["input_value"]

    def get_available_choices(self):
        input_value = self.state["input_value"]
        if input_value:
            return [item for item in self.choices if input_value in item]
        else:
            return self.choices


@app.page()
class TypeAheadPage(Page):
    def initial(self):
        return {"cheese": None}

    def populate(self):
        t.h1("Typeahead/autocomplete demo")
        t.type_ahead(
            ref="select_cheese",
            bind="cheese",
            placeholder="What is your favorite type of cheese?",
            choices=[
                "cheddar cheese",
                "gouda",
                "brie",
                "swiss",
                "gorgonzola",
                "feta",
                "mozzarella",
            ],
        )
        t.p(f"You selected: {self.state['cheese'] or 'nothing yet'}")


app.mount("#app")
