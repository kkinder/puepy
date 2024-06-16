from puepy import Page, t, Prop
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
class DashboardPage(Page):
    compose_app_state = ["authenticated_user"]

    def populate(self):
        with t.app_layout() as layout:
            with layout.slot():
                t.h1(f"Hello, you are authenticated as {self.application.state['authenticated_user']}")
                t.p("This is an example of how you might choose to layout an app. This example includes")
                t.ul(
                    t.li("Pages spread across multiple files"),
                    t.li("Use of a JavaScript library (charts.js)"),
                    t.li("The use of Shoelace WebComponents"),
                    t.li("An example form validation"),
                )


@app.page(route=None)
class NotFoundPage(Page):
    def populate(self):
        with t.app_layout() as layout:
            with layout.slot():
                t.h1("Page Not Found")


@app.page("/login")
class LoginPage(Page):
    props = ["return_to"]

    def initial(self):
        return {"username": "", "password": ""}

    def populate(self):
        t.style(
            """
            body, html {
              height: 100%;
              margin: 0;
              display: flex;
              align-items: center;
              justify-content: center;
              font-family: Arial, sans-serif;
            }
        
            .login-container {
              width: 300px;
              padding: 20px;
              border-radius: 10px;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
              background-color: #fff;
            }
        
            .login-container h2 {
              margin-bottom: 20px;
              text-align: center;
            }
        
            sl-input, sl-button {
              margin-bottom: 15px;
              width: 100%;
            }
            """
        )

        with t.div(classes="login-container"):
            t.h2("Login")
            with t.form(on_submit=self.on_submit, ref="form"):
                with t.sl_input(label="Username", required=True, bind="username"):
                    t.sl_icon(name="person-fill", slot="prefix")
                with t.sl_input(label="Password", type="password", required=True, bind="password"):
                    t.sl_icon(name="lock-fill", slot="prefix")
                t.sl_button("Login", type="submit")
                t.p("Use any username or password")

                t.p(f"You will be returned to {self.return_to}")

    def on_submit(self, event):
        event.preventDefault()
        if self.refs["form"].element.checkValidity():
            self.application.state["authenticated_user"] = self.state["username"]

            if self.return_to:
                self.router.navigate_to_path(self.return_to)
            else:
                self.router.navigate_to_path("/")


# app.unauthorized_page = LoginPage
