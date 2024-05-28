from dataclasses import dataclass

import js

from puepy import Application, Page, t, Component
from puepy.router import Router, Route
from puepy.util import jsobj

app = Application()
app.install_router(Router, link_mode=Router.LINK_MODE_HASH)


@dataclass
class SidebarItem:
    label: str
    icon: str
    route: Route


@t.component()
class AppLayout(Component):
    sidebar_items = [
        SidebarItem("Dashboard", "emoji-sunglasses", "welcome_page"),
        SidebarItem("Charts", "graph-up", "charts_page"),
        SidebarItem("Forms", "input-cursor-text", "forms_page"),
    ]

    def populate(self):
        with t.sl_drawer(label="Menu", placement="start", classes="drawer-placement-start", ref="drawer"):
            self.populate_sidebar()

        with t.div(classes="container"):
            with t.div(classes="header"):
                with t.div():
                    with t.sl_button(classes="menu-btn", on_click=self.show_drawer):
                        t.sl_icon(name="list")
                t.div("The Dapper App")
                self.populate_topright()
            with t.div(classes="sidebar", id="sidebar"):
                self.populate_sidebar()
            with t.div(classes="main"):
                self.insert_slot()
            with t.div(classes="footer"):
                t("Business Time!")

    def populate_topright(self):
        with t.div(classes="dropdown-hoist"):
            with t.sl_dropdown(hoist=""):
                t.sl_icon_button(slot="trigger", label="User Settings", name="person-gear")
                with t.sl_menu(on_sl_select=self.on_menu_select):
                    t.sl_menu_item(
                        "Profile",
                        t.sl_icon(slot="suffix", name="person-badge"),
                        value="profile",
                    )
                    t.sl_menu_item("Settings", t.sl_icon(slot="suffix", name="gear"), value="settings")
                    t.sl_divider()
                    t.sl_menu_item("Logout", t.sl_icon(slot="suffix", name="box-arrow-right"), value="logout")

    def on_menu_select(self, event):
        print("You selected", event.detail.item.value)

    def populate_sidebar(self):
        for item in self.sidebar_items:
            with t.div():
                with t.sl_button(
                    item.label,
                    variant="text",
                    classes="sidebar-button",
                    href=self.page.router.reverse(item.route),
                ):
                    if item.icon:
                        t.sl_icon(name=item.icon, slot="prefix")

    def show_drawer(self, event):
        self.refs["drawer"].element.show()


@t.component()
class Chart(Component):
    props = ["type", "data", "options"]
    enclosing_tag = "canvas"

    def post_render(self, element):
        js.Chart.new(
            element,
            jsobj(type=self.type, data=self.data, options=self.options),
        )


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


app.mount("#app")
