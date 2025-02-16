# Reactivity

Reactivity is a paradigm that causes the user interface to update automatically in response to changes in the
application state. Rather than triggering updates manually as a programmer, you can be assured that the application
state will trigger redraws, with new information, as needed. Reactivity in PuePy is inspired by Vue.js.

## State
### Initial state

Components (including Pages) define initial state through the `initial()` method:

```Python
class MyComponent(Component):
    def initial(self):
        return {
            "name": "Monty ... Something?",
            "movies": ["Monty Python and the Holy Grail"]
        }
```

### Modifying state

If any method on the component changed the name, it would trigger a UI refresh:

```Python
class MyComponent(Component):
    def update_name(self):
        # This triggers a refresh
        self.state["name"] = "Monty Python"
```

#### Modifying mutable objects in-place

!!! warnign
    PuePy's reactivity works by using dictionary `__setitem__` and `__delitem__` methods. As such, it cannot detect "nested" updates or changes to mutable objects in the state. If your code will result in a state change such as a data structure being changed in-place, you must a `mutate()` context manager.

Modifying complex (mutable) data structures in place without **setting them** will not work:

```Python
class MyComponent(Component):
    def update_movies(self):
        # THIS WILL NOT CAUSE A UI REFRESH!
        self.state["movies"].append("Monty Python’s Life of Brian")
```

Instead, use a context manager to tell the state object what is being modified. This is ideal anyway.

```Python
class MyComponent(Component):
    def update_movies(self):
        # THIS WILL NOT CAUSE A UI REFRESH!
        with self.state.mutate("movies"):
            self.state["movies"].append("Monty Python’s Life of Brian")
```

`mutate(*keys)` can be called with any number of keys you intend to modify. As an added benefit, the state change will
only call listeners after the context manager exits, making it ideal also for "batching up" changes.

## Controlling UI Refresh

### Disabling Automatic Refresh

By default, any detected mutations to a component's state will trigger a UI fresh. This can be customized. To disable
automatic refresh entirely, set `redraw_on_changes` to False.

```Python
class MyComponent(Component):
    # The UI will no longer refresh on state changes
    redraw_on_changes = False
    
    def something_happened(self):
        # This can be called to manually refresh this component and its children
        self.trigger_redraw()
        
        # Or, you can redraw the whole page
        self.page.trigger_redraw()
```

### Limiting Automatic Refresh

Suppose that you want to refresh the UI on some state changes, but not others.

```Python
class MyComponent(Component):
    # When items in this this change, the UI will be redrawn
    redraw_on_changes = ["items"]
```

## Watching for changes

You can watch for changes in state yourself.

```Python
class MyComponent(Component):
    def initial():
        return {"spam": "eggs"}
    
    def on_spam_change(self, new_value):
        print("New value for spam", new_value)
```

Or, watch for any state change:

```Python
class MyComponent(Component):
    def on_state_change(self, key, value):
        print(key, "was set to", value)
```

## Binding form element values to state

For your convenience, the `bind` parameter can be used to automatically establish a two-way connection between
input elements and component state. When the value of a form element changes, the state is updated. When the state
is updated, the corresponding form tag's value reflects that change.

```Python
class MyComponent(Component):
    def initial(self):
        return {"name": ""}
    
    def populate(self):
        # bind specifies what key on self.state should be tied to this input's value
        t.input(placeholder="Type your name", bind="name")
```

## Application State

In addition to components and pages, there is also a "global" application-wide state. Note that this state is only for
a running [Application](../reference/application.md) instance and does not survive reloads nor is it shared across
multiple browser tabs or windows.

To use the application state, use `application.state` as you would local state. For example, in the
[Full App Template](../tutorial/10-full-app.md) tutorial chapter, the working example uses 
`self.application.state["authenticated_user"]` in a variety of places:

```py title="Navigation Guard"
def precheck(self):
    if not self.application.state["authenticated_user"]:
        raise exceptions.Unauthorized()
```

```py title="Setting state"
self.application.state["authenticated_user"] = self.state["username"]
```

```py title="Rendering based on application state"
def populate(self):
    ...
    
    t.h1(f"Hello, you are authenticated as {self.application.state['authenticated_user']}")
```

As with page or component state, changes to the application state trigger refreshes by default. That behavior can
be controlled with `redraw_on_app_state_changes` on components or pages:

```py
class Page1(Page):
    redraw_on_app_state_changes = True  # (1)!


class Page2(Page):
    redraw_on_app_state_changes = False  # (2)!


class Page3(Page):
    redraw_on_app_state_changes = ["authenticated_user"]  # (3)!
```

1. The default behavior, with `redraw_on_app_state_changes` set to True, all changes to application state trigger a redraw.
2. Setting `redraw_on_app_state_changes` to False prevents changes to application state from triggering a redraw.
3. Setting `redraw_on_app_state_changes` to a list of keys will trigger a redraw only when those keys change.

!!! tip
    This behavior mirrors `redraw_on_state_changes`, which is used for local state.