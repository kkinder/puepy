from puepy import Application, Page, Component, t, CssClass

app = Application()

#
# These are Python-defined css classes. You can use them instead of strings when specifying CSS classes:
# Arguments can be either strings or keyword arguments
warning = CssClass(color="darkorange")
error = CssClass("color: red")
success = CssClass("color: darkgreen")


# Using the @t.component decorator registers the component for use elsewhere
@t.component()
class Card(Component):
    props = ["type", "button_text"]

    #
    # For CSS specific to a component, put it here. The generated class name is unique per CssClass instance,
    # so this can work to "scope" CSS.
    card = CssClass(
        margin="1em",
        padding="1em",
        background_color="#efefef",
        border="solid 2px #333",
    )

    default_classes = [card]

    type_styles = {
        "success": success,
        "warning": warning,
        "error": error,
    }

    def populate(self):
        with t.h2(classes=[self.type_styles[self.type]]):
            self.insert_slot("card-header")
        with t.p():
            self.insert_slot()  # If you don't pass a name, it defaults to the main slot
        t.button(self.button_text, on_click=self.on_button_click)

    def on_button_click(self, event):
        self.trigger_event("my-custom-event", detail={"type": self.type})


@app.page()
class ComponentPage(Page):
    def initial(self):
        return {"message": ""}

    def populate(self):
        t.h1("Components are useful")
        t.message()

        with t.card(type="success", button_text="Okay Then", on_my_custom_event=self.handle_custom_event) as card:
            with card.slot("card-header"):
                t("Success!")
            with card.slot():
                t("Your operation worked")

        with t.card(type="warning", button_text="Got It", on_my_custom_event=self.handle_custom_event) as card:
            with card.slot("card-header"):
                t("Warning!")
            with card.slot():
                t("Your operation may not work")

        with t.card(type="error", button_text="Understood", on_my_custom_event=self.handle_custom_event) as card:
            with card.slot("card-header"):
                t("Failure!")
            with card.slot():
                t("Your operation failed")

        if self.state["message"]:
            t.p(self.state["message"], id="result")

    def handle_custom_event(self, event):
        self.state["message"] = f"Custom event from card with type {event.detail.get('type')}"


app.mount("#app")
