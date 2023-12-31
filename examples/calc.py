import pprint

import math
from examples.app import app
from puepy.core import t, Page

eval_funcs = {}
for func in dir(math):
    if not func.startswith("_"):
        eval_funcs[func] = getattr(math, func)


@app.page("/calc")
class CalcExample(Page):
    def initial(self):
        return dict(formula="", result="", error="")

    def populate(self):
        with t.example(title="Calculator") as e:
            with e.slot():
                with t.form(classes="flex flex-col gap-2 mt-4 mb-4", on_submit=self.on_submit):
                    t.input(
                        placeholder="Try 5+1 or sin(.5)",
                        bind="formula",
                        classes="input input-bordered w-full",
                    )
                    if self.state["error"]:
                        t.div(self.state["error"], classes="bg-red-100 text-red")
                    else:
                        t.pre(self.state["result"])

    def on_formula_change(self, value):
        value = value.strip()
        if not value:
            self.state["result"] = ""
            self.state["error"] = ""
            return

        self.state["error"] = ""
        try:
            self.state["result"] = str(eval(str(value), eval_funcs, {}))
        except Exception as e:
            self.state["error"] = str(e)
            self.state["result"] = ""

    def on_submit(self, event):
        pass

    def page_title(self):
        return f"{self.application.base_title} | Calculator"
