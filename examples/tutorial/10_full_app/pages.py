from puepy import Page, t
from common import app


@app.page("/charts")
class ChartsPage(Page):
    def populate(self):
        with t.app_layout() as layout:
            with layout.slot():
                t.chart(
                    type="line",
                    data={
                        "labels": ["January", "February", "March", "April", "May", "June"],
                        "datasets": [
                            {
                                "label": "Tacos Per Capita",
                                "data": [54, 21, 3, 38, 26, 85],
                                "fill": False,
                            }
                        ],
                    },
                    options={"responsive": True, "scales": {"y": {"beginAtZero": True}}},
                    style="width: 100%; height: 100%;",
                )


@app.page("/forms")
class FormsPage(Page):
    def populate(self):
        with t.sl_dialog(ref="dialog"):
            t.p("You submitted the form")

        with t.app_layout() as layout:
            with layout.slot():
                t.h1("Form Validation")
                t.p("You can use browser-based form validation for a lot of things now. Try email and only letters")

                with t.form(on_submit=self.on_submit, ref="form"):
                    with t.sl_input(label="Name", required=True):
                        t.sl_icon(name="person-fill", slot="prefix")
                    t.br()
                    with t.sl_input(label="Email", type="email", required=True):
                        t.sl_icon(name="envelope-fill", slot="prefix")
                    t.br()
                    t.sl_input(label="Only Letters", required=True, pattern="[A-Za-z]+")
                    t.br()
                    t.sl_button("Submit", type="submit")

                t.sl_divider()

    def on_submit(self, event):
        event.preventDefault()
        if self.refs["form"].element.checkValidity():
            self.refs["dialog"].element.show()


@app.page("/")
class WelcomePage(Page):
    def populate(self):
        with t.app_layout() as layout:
            with layout.slot():
                t.h1("Building a big app", style="margin-top: 0;")
                t.p("This is an example of how you might choose to layout an app. This example includes")
                t.ul(
                    t.li("Pages spread across multiple files"),
                    t.li("Use of a JavaScript library (charts.js)"),
                    t.li("The use of Shoelace WebComponents"),
                    t.li("An example form validation"),
                )


@app.page(route=None, name="404 Page")
class NotFoundPage(Page):
    def populate(self):
        with t.app_layout() as layout:
            with layout.slot():
                t.h1("Page Not Found")
