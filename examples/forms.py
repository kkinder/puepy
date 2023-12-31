import pprint
from datetime import datetime

from examples.app import app
from puepy.core import t, Page


@app.page("/forms")
class FormsExample(Page):
    def initial(self):
        return dict(first_name="", last_name="", agree_tos=False)

    def populate(self):
        with t.example(title="Forms") as e:
            with e.slot():
                with t.form(classes="flex flex-col gap-2 mt-4 mb-4", on_submit=self.on_submit):
                    t.h3("Fields", classes="text-2xl")
                    with t.div(classes="flex gap-2"):
                        t.input(placeholder="First name", bind="first_name", classes="input input-bordered w-full")
                        t.input(placeholder="Last Name", bind="last_name", classes="input input-bordered w-full")

                    with t.div():
                        with t.div(classes="form-control"):
                            with t.label(classes="label cursor-pointer"):
                                t.span("I agree to stuff", classes="label-text")
                                t.input(type="checkbox", bind="agree_tos", classes="checkbox")
                        t.button("Submit", type="submit", classes="btn btn-primary")
                    t.h3("Component State", classes="text-2xl")
                    t.pre(pprint.pformat(self.state), classes="w-full")

    def on_submit(self, event):
        event.preventDefault()
        self.state["form_submitted"] = datetime.now()
        return False

    def page_title(self):
        return f"{self.application.base_title} | Forms"
