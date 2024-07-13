# In-Depth Components

Defining components in PuePy is a powerful way to encapsulate data, display, and logic in a reusable way. Components become usable like tags in the `populate()` method of other components or pages, define slots, props, and events.

## Data flow features

### Slots

Slots are a mechanism to allow parent components to inject content (tags, other components, etc) into child components in specified locations. There can be one default or unamed slot, and any number of named slots. 

- Slots are defined in the `populate()` method of a component or page using `self.insert_slot`. 
- Slots are consumed in the code using the component with a context manager object and `<component>.slot()`.

See the [Components Tutorial Chapter](../tutorial/06-components.md) for more information on slots.

### Props

Props are a way to pass data to child components. Slots must be defined by a component. When writing a component, you can simply include slots as a list of strings, where each element is the name of a slot, or include instances of the `Prop` class. You can mix and match the two as well

``` py
class MyComponent(Component):
    props = [
        "title",  # (1)!
        Prop("author_name", "Name of Author", str, "Unknown") # (2)!
    ]
```

1. This is a slot which only defines a name.
2. To add extra metadata about a prop, you can also define a Prop instance.

Regardless of how you define slots in your component, a full "expanded" list of slots is available on `self.props_expanded` as a dictionary mapping prop name to `Prop` instance, with the Prop instance created automatically if only a name is specified.

!!! note "See Also"
    - [Prop Class Reference](../reference/prop.md)

### Attributes

Keyword arguments passed to a component that do not match any known prop are considered *attributes* and stored in `self.attrs`. They are then inserted into the rendered DOM as HTML elements on the rendered attribute. This means that, for instance, you can pass arbitrary HTML attributes to newly created components without defining any custom props or other logic. Eg,

```Python
from puepy import Component, Page, t


class NameInput(Component):
    enclosing_tag = "input"

class MyPage(Page):
    def populate(self):
        t.name_input(id="name_input", placeholder="Enter your name")
```

Even if the NameInput component does not define a `placeholder` prop, the `placeholder` attribute will be rendered on the input tag.

!!! question "When to use props vs attributes?"
    - Use props when you want to pass data to a component that will be used in the component's logic or rendering.
    - Use attributes when you want to pass data to a component that will be used in the rendered HTML but not in the component's logic.

### Events

Events are a way to allow child components to communicate with parent components. When writing a component, in your own code, you can emit an event by calling `self.trigger_event`. You can also optionally pass a detail dictionary to the event, which will be passed along (after Python to JavaScript conversion) to the browser's native event system in JavaScript.

For example, suppose you want to emit a custom event, `greeting`, with a `type` attribute:

```Python
class MyComponent(Component):
    def some_method(self):
        self.trigger_event("greeting", detail={"message": "Hello There"})
```

A consumer of your component can listen for this event by defining an `on_greeting` method in their component or page:

```Python
class MyPage(Page):
    def populate(self):
        t.my_component(on_greeting=self.on_greeting_sent)
    
    def on_greeting_sent(self, event):
        print("Incoming message from component", event.detail.get('message'))
```

!!! note "See Also"
    [Mozilla's guide to JavaScript events](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Building_blocks/Events)

## Customization

You have several ways of controlling how your components are rendered. First, you can define what enclosing tag your component is rendered as. The default is a `div` tag, but this can be overridden:

```py
class MyInputComponent(Component):
    enclosing_tag = "input"
```

You can also define default classes, default attributes, and the default role for your component:

```py
class MyInputComponent(Component):
    enclosing_tag = "input"
    
    default_classes = ["my-input"]
    default_attributes = {"type": "text"}
    default_role = "textbox"
```

## Parent/Child relationships

Each tag (and thus each component) in PuePy has a parent unless it is the root page. Consider the following example:

```Python
from puepy import Application, Page, Component, t

app = Application()


@t.component()
class CustomInput(Component):
    enclosing_tag = "input"

    def on_event_handle(self, event):
        print(self.parent)


class MyPage(Page):
    def populate(self):
        with t.div():
            t.custom_input()
```

In this example, the *parent* of the `CustomInput` instance *is not* the `MyPage` instance, it is the `div`,
a `puepy.Tag` instance. In many cases, you will want to interact another relevant object, not necessarily the one
immediately parental of your current instance. In those instances, from your components, you may reference:

- `self.page` (Page instance): The page ultimately responsible for rendering this component
- `self.origin` (Component or Page instance): The component that created yours in its `populate()` method 
- `self.parent` (Tag instance): The direct parent of the current instance 

Additionally, parent instances have the following available:

- `self.children` (list): Direct child nodes
- `self.refs` (dict): Instances created during this instance's most recent `populate()` method

!!! warning
    None of the attributes regarding parent/child/origin relationships should be modified by application code.  Doing so could result in unexpected behavior.

## Refs

In addition to parent/child relationships, most components and pages define an entire hierarchy of tags and components
in the `populate()` method. If you want to reference components later, or tell PuePy which component is which (in case
the ordering changes in sebsequent redraws), using a `ref=` argument when building tags:

```Python
class MyPage(Page):
    def populate(self):
        t.button("My Button", ref="my_button")
    
    def auto_click_button(self, ...):
        self.refs["my_button"].element.click()
```

For more information on why this is useful, see the [Refs Tutorial Topic](../tutorial/04-refs.md).
