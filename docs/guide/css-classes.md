# CSS Classes

Although you are in charge of your own CSS, PuePy provides some convenience mechanisms for defining CSS classes. Because `class` is a reserved word in Python, when passing classes to tags, you should use either `class_name` or `classes`. Each can be defined as a string, list, or dictionary:

```Python
@app.page()
class HelloWorldPage(Page):
    def populate(self):
        t.button("Primary Large Button", class_name="primary large")
        t.button("Primary Small Button", classes=["primary", "small"])
        t.button("Primary Medium Button", classes={
            "primary": True, 
            "medium": True, 
            "small": False, 
            "large": False})
```

Notice that when passing a dictionary, the *value* of the dictionary indicates whether the class will be included.

## Components and classes

Components can define default classes. For example in the [Components](../tutorial/06-components.md) section of the tutorial, we define a Card component:

```Python
@t.component()
class Card(Component):
    ...

    default_classes = ["card"]
    
    ...
```

The `default_classes` attribute tells PuePy to render the component with card as a default class. Code using the Card component can add to or even remove the default classes defined by the component.

To remove a class, pass it with a "/" prefix:

```Python
class MyPage(Page):
    def populate(self):
        # This will render as a div with both "card" and "card-blue" 
        # classes.
        t.card(classes="card-blue")
        
        # This will override the default and remove the "card" class
        t.card(classes="/card")        
```

