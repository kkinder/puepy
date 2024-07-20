# A Full App Template

Let's put together what we've learned so far. This example is an app with routing, a sidebar, and a handful of pages.

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/10_full_app/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest" height="20em" height="35em"/>


!!! note "URL Changes"
    In the embedded example above, the "URL" does not change because the embedded example is not a full web page. In a full web page, the URL would change to reflect the current page. Try opening the example [in a new window](https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/10_full_app/index.html) to see the URL change.

## Project layout

The larger example separates logic out into several files.

- main.py: The Python file started from our `<script>` tag
- common.py: A place to put objects common to other files
- components.py: A place to put reusable components
- pages.py: A place to put individual pages we navigate to

### Configuring PyScript for multiple files

To make additional source files available in the Python runtime environment, add them to the `files` list in the PyScript configuration file:

```json title="pyscript-app.json"
{
  "name": "PuePy Tutorial",
  "debug": true,
  "files": {
    "./common.py": "common.py",
    "./components.py": "components.py",
    "./main.py": "main.py",
    "./pages.py": "pages.py"
  },
  "js_modules": {
    "main": {
      "https://cdn.jsdelivr.net/npm/chart.js": "chart",
      "https://cdn.jsdelivr.net/npm/morphdom@2.7.2/+esm": "morphdom"
    }
  },
  "packages": [
    "../../puepy-0.3.5-py3-none-any.whl"
  ]
}
```

### Adding Chart.js

We also added a JavaScript library, chart.js, to the project.

```json
  "https://cdn.jsdelivr.net/npm/chart.js": "chart"
```

!!! tip "JavaScript Modules"
    See [JavaScript Modules](https://docs.pyscript.net/2024.6.2/user-guide/configuration/#javascript-modules) in
    PyScript's documentation for additional information on loading JavaScript libraries into your project.

We use charts.js directly from Python, in `components.py`:

```Python
@t.component()
class Chart(Component):
    props = ["type", "data", "options"]
    enclosing_tag = "canvas"

    def on_redraw(self):
        self.call_chartjs()

    def on_ready(self):
        self.call_chartjs()

    def call_chartjs(self):
        if hasattr(self, "_chart_js"):
            self._chart_js.destroy()

        self._chart_js = js.Chart.new(
            self.element,
            jsobj(type=self.type, data=self.data, options=self.options),
        )
```

We call the JavaScript library in two places. When the component is added to the DOM (on_ready) and when it's going to
be redrawn (on_redraw).

## Reusing Code 

### A common app layout

In `components.py`, we define a common application layout, then reuse it in multiple pages:

```Python
class SidebarItem:
    def __init__(self, label, icon, route):
        self.label = label
        self.icon = icon
        self.route = route


@t.component()
class AppLayout(Component):
    sidebar_items = [
        SidebarItem("Dashboard", "emoji-sunglasses", "dashboard_page"),
        SidebarItem("Charts", "graph-up", "charts_page"),
        SidebarItem("Forms", "input-cursor-text", "forms_page"),
    ]

    def precheck(self):
        if not self.application.state["authenticated_user"]:
            raise exceptions.Unauthorized()

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
        if event.detail.item.value == "logout":
            self.application.state["authenticated_user"] = ""

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
```


## Loading indicator

Since CPython takes a while to load on slower connections, we'll populate the `<div id="app>` element with a loading 
indicator, which will be replaced once the application mounts:

```html
<div id="app">
  <div style="text-align: center; height: 100vh; display: flex; justify-content: center; align-items: center;">
    <sl-spinner style="font-size: 50px; --track-width: 10px;"></sl-spinner>
  </div>
</div>
```

## Further experimentation

Don't forget to try cloning and modifying all the examples from this tutorial on [PyScript.com](https://pyscript.com/@kkinder/puepy-tutorial/latest).
