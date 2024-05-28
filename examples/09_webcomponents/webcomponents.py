from puepy import Application, Page, t

app = Application()


@app.page()
class DefaultPage(Page):
    def populate(self):
        with t.sl_dialog(label="Dialog", classes="dialog-overview", tag="sl-dialog", ref="dialog"):
            t("Web Components are just delightful.")
            t.sl_button("Close", slot="footer", variant="primary", on_click=self.on_close_click)
        t.sl_button("Open Dialog", tag="sl-button", on_click=self.on_open_click)

    def on_open_click(self, event):
        self.refs["dialog"].element.show()

    def on_close_click(self, event):
        self.refs["dialog"].element.hide()


app.mount("#app")
