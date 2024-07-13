# Components

Components are a way to encapsulate a piece of UI that can be reused throughout your application. In this example, we'll create a `Card` component and use it multiple times on a page, each time using slots to fill in content.

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/06_components/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest" height="50em"/>

=== "Component Definition"

    ``` py linenums="1" hl_lines="1 2 3 4 8 10 15"
    @t.component()  # (1)
    class Card(Component):  # (2)
        props = ["type"]  # (3)
        default_classes = ["card"]  # (4)
    
        def populate(self):
            with t.h2(classes=[self.type]):
                self.insert_slot("card-header")  # (5)
            with t.p():
                self.insert_slot()  # (6)
            t.button("Understood", on_click=self.on_button_click)
    
        def on_button_click(self, event):
            self.trigger_event("my-custom-event", 
                               detail={"type": self.type})  # (7) 
    ```

    1. The `@t.component()` decorator registers the class as a component for use elsewhere.
    2. All components should subclass the `puepy.Component` class.
    3. The `props` attribute is a list of properties that can be passed to the component.
    4. `default_classes` is a list of CSS classes that will be applied to the component by default.
    5. The `insert_slot` method is used to insert content into a named slot. In this case, we are inserting content into the `card-header` slot.
    6. Unnamed, or default slots, can be filled by calling `insert_slot` without a name.
    7. `trigger_event` is used to trigger a custom event. Notice the detail dictionary. This pattern matches the JavaScript `CustomEvent` API.

=== "Component Usage"

    ```py linenums="1" hl_lines="9 10 12 14 31"
    @app.page()
    class ComponentPage(Page):
        def initial(self):
            return {"message": ""}
    
        def populate(self):
            t.h1("Components are useful")
    
            with t.card(type="success",  # (1)
                        on_my_custom_event=self.handle_custom_event) as card:  # (2)
                with card.slot("card-header"):
                    t("Success!")  # (3)
                with card.slot():
                    t("Your operation worked")  # (4)
    
            with t.card(type="warning", on_my_custom_event=self.handle_custom_event) as card:
                with card.slot("card-header"):
                    t("Warning!")
                with card.slot():
                    t("Your operation may not work")
    
            with t.card(type="error", on_my_custom_event=self.handle_custom_event) as card:
                with card.slot("card-header"):
                    t("Failure!")
                with card.slot():
                    t("Your operation failed")
    
            if self.state["message"]:
                t.p(self.state["message"])
    
        def handle_custom_event(self, event):  # (5)
            self.state["message"] = f"Custom event from card with type {event.detail.get('type')}"
    ```

    1. The `card` component is used with the `type` prop set to `"success"`.
    2. The `my-custom-event` event is bound to the `self.handle_custom_event` method.
    3. The content for the `card-header` slot, as defined in the `Card` component, is populated with "Success!".
    3. The default slot is populated with "Your operation worked". Default slots are not named.
    5. The `handle_custom_event` method is called when the `my-custom-event` event is triggered.

## Slots

Slots are a way to pass content into a component. A component can define one or more slots, and the calling code can fill in the slots with content. In the example above, the `Card` component defines two slots: `card-header` and the default slot. The calling code fills in the slots by calling `card.slot("card-header")` and `card.slot()`.

=== "Defining Slots in a component"
    
    ``` py
    with t.h2():
        self.insert_slot("card-header")
    with t.p():
        self.insert_slot()  # (1)
    ```

    1.  If you don't pass a name, it defaults to the main slot

=== "Filling Slots in the calling code"
        
    ``` py
    with t.card() as card:
        with card.slot("card-header"):
            t("Success!")
        with card.slot():
            t("Your operation worked")
    ```

!!! warning "Consuming Slots"
    When consuming components with slots, to populate a slot, you *do not call* `t.slot`. You
    call `.slot` directly on the component instance provided by the context manager:

    ``` py hl_lines="2"
    with t.card() as card:
        with card.slot("card-header"):  # (1)
            t("Success!")
    ```

    1. Notice `card.slot` is called, not `t.slot` or `self.slot`.

??? note "More information on components"

    For more information on components in PuePy, see the [Component Developer Guide](../guide/in-depth-components.md).
