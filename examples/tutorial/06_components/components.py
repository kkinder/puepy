from puepy import Application, Page, Component, t

app = Application()


# Using the @t.component decorator registers the component for use elsewhere
@t.component()
class Card(Component):
    props = ["type"]
    default_classes = ["card"]

    def populate(self):
        with t.h2(classes=[self.type]):
            self.insert_slot("card-header")
        with t.p():
            self.insert_slot()  # If you don't pass a name, it defaults to the main slot
        t.button("Understood", on_click=self.on_button_click)

    def on_button_click(self, event):
        self.trigger_event("my-custom-event", detail={"type": self.type})


@app.page()
class ComponentPage(Page):
    def initial(self):
        return {"message": ""}

    def populate(self):
        t.h1("Components are useful")

        with t.card(type="success", on_my_custom_event=self.handle_custom_event) as card:
            with card.slot("card-header"):
                t("Success!")
            with card.slot():
                t("Your operation worked")

        with t.card(type="warning", on_my_custom_event=self.handle_custom_event) as card:
            with card.slot("card-header"):
                t("Warning!")
            with card.slot():
                t("Your operation may not work")

        with t.card(type="error", on_my_custom_event=self.handle_custom_event) as card:
            with card.slot("card-header"):
                t("Failure!")
            with card.slot():
                t("Your operation failed")

        if self.state["message"]:
            t.p(self.state["message"])

    def handle_custom_event(self, event):
        self.state["message"] = f"Custom event from card with type {event.detail.get("type")}"


app.mount("#app")
