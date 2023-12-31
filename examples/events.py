import pprint
import time

from examples.app import app
from puepy.core import t, Page, Component, Prop


@t.component()
class TodoItem(Component):
    enclosing_tag = "li"
    props = ["item", "index", "is_trash"]
    default_classes = ["flex", "justify-between", "items-center"]

    def populate(self):
        t.span(self.item, classes={"text-gray-500 line-through": self.is_trash})
        t.button(
            "Confirm" if self.is_trash else "Delete",
            classes={"btn btn-xm bg-red-500 text-white py-1 px-2 rounded": True},
            on_click=self.on_remove_click,
        )

    def on_remove_click(self, event):
        self.trigger_event("remove", detail=dict(item=self.item, index=self.index, is_trash=self.is_trash))


@t.component()
class TodoList(Component):
    def initial(self):
        return dict(items=[], trash=[])

    def on_state_change(self, key, value):
        self.trigger_event("change")

    def populate(self):
        if self.state["items"] or self.state["trash"]:
            with t.ul(classes="list-disc space-y-2"):
                for i, item in enumerate(self.state["items"]):
                    t.todo_item(item=item, index=i, on_remove=self.on_item_remove)
                for i, item in enumerate(self.state["trash"]):
                    t.todo_item(item=item, index=i, is_trash=True, on_remove=self.on_item_remove)
        else:
            t.em("Todo list now empty")

    def on_item_remove(self, event):
        with self.state.mutate("items", "trash") as (items, trash):
            if event.detail.get("is_trash"):
                del trash[int(event.detail.get("index"))]
            else:
                trash.append(items.pop(int(event.detail.get("index"))))

    def add_item(self, item):
        with self.state.mutate("items"):
            self.state["items"].append(item)

    def clear_trash(self):
        self.state["trash"] = []


@app.page("/events")
class EventsExample(Page):
    """
    We intentionally put some logic here to show moving data between parent and child elements.
    """

    def initial(self):
        return dict(item_entry="")

    def populate(self):
        with t.example(title="Events") as e:
            with e.slot():
                with t.div(classes="prose"):
                    t.p(
                        "Events allow elements to send information upwards in the stack, or possibly, internally. Here"
                        " is a simple todo list that demonstrates events."
                    )

                    with t.form(on_submit=self.on_add_item):
                        t.input(bind="item_entry", classes="input input-bordered w-full", placeholder="Add Item")

                    t.hr()

                    self.todo = t.todo_list(ref="todo", on_change=self.on_todo_list_changed)

                    if self.todo.state["trash"]:
                        t.button(
                            "Clear Trash",
                            classes="btn btn-secondary",
                            on_click=lambda e: self.todo.clear_trash(),
                        )

    def on_add_item(self, event):
        event.preventDefault()
        if self.state["item_entry"].strip():
            self.todo.add_item(self.state["item_entry"].strip())
            self.state["item_entry"] = ""
        else:
            pass
        self.trigger_redraw()

    def page_title(self):
        return f"{self.application.base_title} | Events"

    def on_todo_list_changed(self, event):
        self.trigger_redraw()
