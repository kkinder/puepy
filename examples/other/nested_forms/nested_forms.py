from puepy import Application, Page, t

app = Application()


@app.page()
class RadioButtonsPage(Page):
    def initial(self):
        return {
            "user": {
                "name": "John",
                "age": 30,
                "favorite_color": "green",
                "enabled": True,
                "computers": [
                    {"name": "Macbook", "ram": 16, "os": "macOS"},
                    {"name": "Desktop", "ram": 32, "os": "Windows"},
                ],
            }
        }

    def populate(self):
        with t.form():

            with t.div(
                style="max-width: 500px; margin: 0 auto; padding: 1rem; font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px;"
            ):
                with t.h2(style="text-align: center; color: #333;"):
                    t("User Information Form")
                with t.form():
                    # Name Field
                    t.sl_input(
                        label="Name",
                        name="name",
                        placeholder="Enter your name",
                        required="",
                        bind=["user", "name"],
                        style="width: 100%; margin-bottom: 1rem;",
                    )
                    # Age Field
                    t.sl_input(
                        label="Age",
                        name="age",
                        type="number",
                        placeholder="Enter your age",
                        bind=["user", "age"],
                        required="",
                        style="width: 100%; margin-bottom: 1rem;",
                    )
                    # Favorite Color Radio Buttons
                    with t.div(style="margin-bottom: 1rem;"):

                        t.div(
                            t.label(t.input(type="radio", value="red", bind=["user", "favorite_color"]), "Red"),
                            classes="form-row",
                        )
                        t.div(
                            t.label(t.input(type="radio", value="green", bind=["user", "favorite_color"]), "Green"),
                            classes="form-row",
                        )
                        t.div(
                            t.label(t.input(type="radio", value="blue", bind=["user", "favorite_color"]), "Blue"),
                            classes="form-row",
                        )

                    # Enabled Checkbox
                    t.label(
                        t.input("Enabled", type="checkbox", style="margin-bottom: 1rem;", bind=["user", "enabled"]),
                        "Enabled",
                    )

                    t.sl_button("Submit", type="submit", variant="primary", style="width: 100%;")

            t.div(t.label("Name", t.input(bind=["user", "name"], name="name")), classes="form-row")
            t.div(t.label("Age", t.input(bind=["user", "age"], name="age", type="number")), classes="form-row")
            t.div(
                t.label("Enabled", t.input(type="checkbox", bind=["user", "enabled"], name="enabled")),
                classes="form-row",
            )

            # t.label("Computers", t.select(
            #     bind="user.computers",
            #     name="computers",
            #     options=[
            #         t.option(computer["name"], computer["name"])
            #         for computer in self.state["user"]["computers"]
            #     ]
            # ))
        t.pre(str(self.state))


app.mount("#app")
