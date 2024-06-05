from ltk.jquery import jQuery

import ltk
from puepy import Application, Page, t, Component

app = Application()


@t.component()
class LtkFragment(Component):
    """
    This is an only slightly tested attempt at showing you you *might* be able to integrate LTK with PuePy.

    Use at your own risk.
    """

    component_name = "ltk"

    def render_unknown_child(self, element, child):
        element.appendChild(child.element.get(0))

    def render_children(self, element):
        return super().render_children(element)


@app.page()
class LtkPage(Page):
    PIZZA_SIZES = ["Small ($8)", "Medium ($10)", "Large ($15)"]
    PIZZA_SPECIALTIES = ["Super Cheesy ($3)", "Extra Meaty ($5)", "Veggie ($2)"]
    PIZZA_TOPPINGS = ["Extra Cheese ($1.50)", "Pepperoni ($1.50)", "Mushrooms ($1.50)"]

    def initial(self):
        return {
            "pizzas": 1,
            "size": self.PIZZA_SIZES[0],
            "specialties": self.PIZZA_SPECIALTIES[0],
            "toppings": [],
        }

    def populate(self):
        pizza_type_options = [
            ltk.Label(pt, ltk.RadioButton(self.state["size"] == pt).element) for pt in self.PIZZA_SIZES
        ]
        pizza_specialty_options = [
            ltk.Label(
                s,
                ltk.RadioButton(self.state["specialties"] == s).element,
            )
            for s in self.PIZZA_SPECIALTIES
        ]
        pizza_topping_options = [
            ltk.Label(pt, ltk.Checkbox(pt in self.state["toppings"]).element) for pt in self.PIZZA_TOPPINGS
        ]

        with t.div(style="display: flex; "):
            with t.fieldset(style="flex: 1; margin: 10px; background-color: #efefef;"):
                t.legend("PuePy Component State")
                with t.ul():
                    for k, v in self.state.items():
                        t.li(t.strong(k + ": "), str(v))
            with t.fieldset(style="flex: 1; margin: 10px;"):
                t.legend("LTK Widgets")
                with t.ltk() as l:
                    vbox = ltk.VBox(
                        ltk.Heading1("Dave's Pizza Place"),
                        ltk.VBox(
                            ltk.Label("Number of Pizzas:"), ltk.Input(self.state["pizzas"]).attr("type", "number")
                        ),
                        ltk.Break(),
                        ltk.HBox(
                            ltk.Form(
                                ltk.FieldSet(
                                    ltk.Legend("Pizza type:"),
                                    ltk.RadioGroup(*pizza_type_options),
                                ).attr("id", "pizza-type")
                            ),
                            ltk.Form(
                                ltk.FieldSet(
                                    ltk.Legend("Specialties:"),
                                    ltk.RadioGroup(*pizza_specialty_options),
                                ).attr("id", "specialties")
                            ),
                            ltk.Form(
                                ltk.FieldSet(ltk.Legend("Toppings:"), *pizza_topping_options).attr("id", "toppings")
                            ),
                        ),
                        ltk.Break(),
                        ltk.Button("Place Order", ltk.callback(self.on_order_placed)),
                    )
                    vbox.attr("name", "Pizza")

                    t(vbox)

    def on_order_placed(self, event=None):
        with self.state.mutate():
            self.state["pizzas"] = int(ltk.find("input[type=number]").val())
            self.state["size"] = ltk.find("#pizza-type input:checked").parent().text()
            self.state["specialties"] = ltk.find("#specialties input:checked").parent().text()
            self.state["toppings"] = [
                jQuery(el).parent().text() for el in ltk.find("#toppings input:checked").toArray()
            ]


app.mount("#app")
