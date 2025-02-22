from .exceptions import ElementNotInDom, PropsError, PageError
from .reactivity import ReactiveDict, Stateful
from .runtime import (
    add_event_listener,
    remove_event_listener,
    create_proxy,
    document,
    is_server_side,
    setTimeout,
    CustomEvent,
)
from .util import (
    mixed_to_underscores,
    merge_classes,
    _extract_event_handlers,
    patch_dom_element,
)


class CssClass:
    def __init__(self, *rules, **kw_rules):
        self.rules = list(rules)

        for k, v in kw_rules.items():
            k = k.replace("_", "-")
            self.rules.append(f"{k}: {v}")

        self.class_name = f"-ps-{id(self)}"

    def __str__(self):
        return self.class_name

    def render_css(self):
        return f".{self.class_name} {{ {';'.join(self.rules)} }}"


class Prop:
    """
    Class representing a prop for a component.

    Attributes:
        name (str): The name of the property.
        description (str): The description of the property (optional).
        type (type): The data type of the property (default: str).
        default_value: The default value of the property (optional).
    """

    def __init__(self, name, description=None, type=str, default_value=None):
        self.name = name
        self.description = description
        self.type = type
        self.default_value = default_value


def _element_input_type(element):
    try:
        if element.tagName.lower() == "input" and element.getAttribute("type"):
            return element.getAttribute("type").lower()
    except:
        return None


class Tag:
    """
    The most basic building block of a PuePy app. A Tag is a single HTML element. This is also the base class of
    `Component`, which is then the base class of `Page`.

    Attributes:
        default_classes (list): Default classes for the tag.
        default_attrs (dict): Default attributes for the tag.
        default_role (str): Default role for the tag.
        page (Page): The page the tag is on.
        router (Router or None): The router the application is using, if any.
        parent (Tag): The parent tag, component, or page.
        application (Application): The application instance.
        element: The rendered element on the DOM. Raises ElementNotInDom if not found.
        children (list): The children of the tag.
        refs (dict): The refs of the tag.
        tag_name (str): The name of the tag.
        ref (str): The reference of the tag.
    """

    stack = []
    population_stack = []
    origin_stack = [[]]
    component_stack = []
    default_classes = []
    default_attrs = {}
    default_role = None

    document = document

    # noinspection t
    def __init__(
        self,
        tag_name,
        ref,
        page: "Page" = None,
        parent=None,
        parent_component=None,
        origin=None,
        children=None,
        **kwargs,
    ):
        # Kept so we can garbage collect them later
        self._added_event_listeners = []

        # Ones manually added, which we persist when reconfigured
        self._manually_added_event_listeners = {}

        # The rendered element
        self._rendered_element = None

        # Child nodes and origin refs
        self.children = []
        self.refs = {}

        self.tag_name = tag_name
        self.ref = ref

        # Attrs that webcomponents create that we need to preserve
        self._retained_attrs = {}

        # Add any children passed to constructor
        if children:
            self.add(*children)

        # Configure self._page
        if isinstance(page, Page):
            self._page = page
        elif isinstance(self, Page):
            self._page = self
        elif page:
            raise Exception(f"Unknown page type {type(page)}")
        else:
            raise Exception("No page passed")

        if "id" in kwargs:
            self._element_id = kwargs["id"]
        elif self._page and self._page.application:
            self._element_id = self._page.application.element_id_generator.get_id_for_element(self)
        else:
            self._element_id = f"ppauto-{id(self)}"

        if isinstance(parent, Tag):
            self.parent = parent
            parent.add(self)
        elif parent:
            raise Exception(f"Unknown parent type {type(parent)}: {repr(parent)}")
        else:
            self.parent = None

        if isinstance(parent_component, Component):
            self.parent_component = parent_component
        elif parent_component:
            raise Exception(f"Unknown parent_component type {type(parent_component)}: {repr(parent_component)}")
        else:
            self.parent_component = None

        self.origin = origin
        self._children_generated = False

        self._configure(kwargs)

    def __del__(self):
        if not is_server_side:
            while self._added_event_listeners:
                remove_event_listener(*self._added_event_listeners.pop())

    @property
    def application(self):
        return self._page._application

    def _configure(self, kwargs):
        self._kwarg_event_listeners = _extract_event_handlers(kwargs)
        self._handle_bind(kwargs)
        self._handle_attrs(kwargs)

    def _handle_bind(self, kwargs):
        if "bind" in kwargs:
            self.bind = kwargs.pop("bind")
            input_type = kwargs.get("type")
            tag_name = self.tag_name.lower()

            if "value" in kwargs and not (tag_name == "input" and input_type == "radio"):
                raise Exception("Cannot specify both 'bind' and 'value'")

        else:
            self.bind = None

    def _handle_attrs(self, kwargs):
        self.attrs = self._retained_attrs.copy()
        for k, v in kwargs.items():
            if hasattr(self, f"set_{k}"):
                getattr(self, f"set_{k}")(v)
            else:
                self.attrs[k] = v

    def populate(self):
        """To be overwritten by subclasses, this method will define the composition of the element"""
        pass

    def precheck(self):
        """
        Before doing too much work, decide whether rendering this tag should raise an error or not. This may be useful,
        especially on a Page, to check if the user is authorized to view the page, for example:

        Examples:
            ``` py
            def precheck(self):
                if not self.application.state["authenticated_user"]:
                    raise exceptions.Unauthorized()
            ```
        """
        pass

    def generate_children(self):
        """
        Runs populate, but first adds self to self.population_stack, and removes it after populate runs.

        That way, as populate is executed, self.population_stack can be used to figure out what the innermost populate()
        method is being run and thus, where to send bind= parameters.
        """
        self.origin_stack.append([])
        self._refs_pending_removal = self.refs.copy()
        self.refs = {}
        self.population_stack.append(self)
        try:
            self.precheck()
            self.populate()
        finally:
            self.population_stack.pop()
            self.origin_stack.pop()

    def render(self):
        attrs = self.get_default_attrs()
        attrs.update(self.attrs)

        element = self._create_element(attrs)

        self._render_onto(element, attrs)
        self.post_render(element)
        return element

    def _create_element(self, attrs):
        if "xmlns" in attrs:
            element = self.document.createElementNS(attrs.get("xmlns"), self.tag_name)
        else:
            element = self.document.createElement(self.tag_name)

        element.setAttribute("id", self.element_id)
        if is_server_side:
            element.setIdAttribute("id")

        self.configure_element(element)

        return element

    def configure_element(self, element):
        pass

    def post_render(self, element):
        pass

    @property
    def element_id(self):
        return self._element_id

    @property
    def element(self):
        el = self.document.getElementById(self.element_id)
        if el:
            return el
        else:
            raise ElementNotInDom(self.element_id)

    # noinspection t
    def _render_onto(self, element, attrs):
        self._rendered_element = element

        # Handle classes
        classes = self.get_render_classes(attrs)

        if classes:
            # element.className = " ".join(classes)
            element.setAttribute("class", " ".join(classes))

        # Add attributes
        for key, value in attrs.items():
            if key not in ("class_name", "classes", "class"):
                if hasattr(self, f"handle_{key}_attr"):
                    getattr(self, f"handle_{key}_attr")(element, value)
                else:
                    if key.endswith("_"):
                        attr = key[:-1]
                    else:
                        attr = key
                    attr = attr.replace("_", "-")

                    if isinstance(value, bool) or value is None:
                        if value:
                            element.setAttribute(attr, attr)
                    elif isinstance(value, (str, int, float)):
                        element.setAttribute(attr, value)
                    else:
                        element.setAttribute(attr, str(value))

        if "role" not in attrs and self.default_role:
            element.setAttribute("role", self.default_role)

        # Add event handlers
        self._add_listeners(element, self._kwarg_event_listeners)
        self._add_listeners(element, self._manually_added_event_listeners)

        # Add bind
        if self.bind and self.origin:
            input_type = _element_input_type(element)

            if type(self.bind) in [list, tuple]:
                value = self.origin.state
                for key in self.bind:
                    value = value[key]
            else:
                value = self.origin.state[self.bind]

            if input_type == "checkbox":
                if is_server_side and value:
                    element.setAttribute("checked", value)
                else:
                    element.checked = bool(value)
                    element.setAttribute("checked", value)
                event_type = "change"
            elif input_type == "radio":
                is_checked = value == element.value
                if is_server_side and is_checked:
                    element.setAttribute("checked", is_checked)
                else:
                    element.checked = is_checked
                    element.setAttribute("checked", is_checked)
                event_type = "change"
            else:
                if is_server_side:
                    element.setAttribute("value", value)
                else:
                    element.value = value
                    element.setAttribute("value", value)
                event_type = "input"
            self.add_event_listener(element, event_type, self.on_bind_input)
        elif self.bind:
            raise Exception("Cannot specify bind a valid parent component")

        self.render_children(element)

    def _add_listeners(self, element, listeners):
        for key, value in listeners.items():
            key = key.replace("_", "-")
            if isinstance(value, (list, tuple)):
                for handler in value:
                    self.add_event_listener(element, key, handler)
            else:
                self.add_event_listener(element, key, value)

    def render_children(self, element):
        for child in self.children:
            if isinstance(child, Slot):
                if child.children:  # If slots don't have any children, don't bother.
                    element.appendChild(child.render())
            elif isinstance(child, Tag):
                element.appendChild(child.render())
            elif isinstance(child, html):
                element.insertAdjacentHTML("beforeend", str(child))
            elif isinstance(child, str):
                element.appendChild(self.document.createTextNode(child))
            elif child is None:
                pass
            elif getattr(child, "nodeType", None) is not None:
                # DOM element
                element.appendChild(child)
            else:
                self.render_unknown_child(element, child)

    def render_unknown_child(self, element, child):
        """
        Called when the child is not a Tag, Slot, or html. By default, it raises an error.
        """
        raise Exception(f"Unknown child type {type(child)} onto {self}")

    def get_render_classes(self, attrs):
        class_names, python_css_classes = merge_classes(
            set(self.get_default_classes()),
            attrs.pop("class_name", []),
            attrs.pop("classes", []),
            attrs.pop("class", []),
        )
        self.page.python_css_classes.update(python_css_classes)
        return class_names

    def get_default_classes(self):
        """
        Returns a shallow copy of the default_classes list.

        This could be overridden by subclasses to provide a different default_classes list.

        Returns:
            (list): A shallow copy of the default_classes list.
        """
        return self.default_classes.copy()

    def get_default_attrs(self):
        return self.default_attrs.copy()

    def add_event_listener(self, element, event, listener):
        """
        Just an internal wrapper around add_event_listener (JS function) that keeps track of what we added, so
        we can garbage collect it later.

        Should probably not be used outside this class.
        """
        self._added_event_listeners.append((element, event, listener))
        if not is_server_side:
            add_event_listener(element, event, listener)

    def mount(self, selector_or_element):
        self.update_title()
        if not self._children_generated:
            with self:
                self.generate_children()

        if isinstance(selector_or_element, str):
            element = self.document.querySelector(selector_or_element)
        else:
            element = selector_or_element

        if not element:
            raise RuntimeError(f"Element {selector_or_element} not found")

        element.innerHTML = ""
        element.appendChild(self.render())
        self.recursive_call("on_ready")
        self.add_python_css_classes()

    def add_python_css_classes(self):
        """
        This is only done at the page level.
        """
        pass

    def recursive_call(self, method, *args, **kwargs):
        """
        Recursively call a specified method on all child Tag objects.

        Args:
            method (str): The name of the method to be called on each Tag object.
            *args: Optional arguments to be passed to the method.
            **kwargs: Optional keyword arguments to be passed to the method.
        """
        for child in self.children:
            if isinstance(child, Tag):
                child.recursive_call(method, *args, **kwargs)
        getattr(self, method)(*args, **kwargs)

    def on_ready(self):
        pass

    def _retain_implicit_attrs(self):
        """
        Retain attributes set elsewhere
        """
        try:
            for attr in self.element.attributes:
                if attr.name not in self.attrs and attr.name != "id":
                    self._retained_attrs[attr.name] = attr.value
        except ElementNotInDom:
            pass

    def on_redraw(self):
        pass

    def on_bind_input(self, event):
        input_type = _element_input_type(event.target)
        if input_type == "checkbox":
            self.set_bind_value(self.bind, event.target.checked)
        elif input_type == "radio":
            if event.target.checked:
                self.set_bind_value(self.bind, event.target.value)
        elif input_type == "number":
            value = event.target.value
            try:
                if "." in str(value):
                    value = float(value)
                else:
                    value = int(value)
            except (ValueError, TypeError):
                pass
            self.set_bind_value(self.bind, value)
        else:
            self.set_bind_value(self.bind, event.target.value)

    def set_bind_value(self, bind, value):
        if type(bind) in (list, tuple):
            nested_dict = self.origin.state
            for key in bind[:-1]:
                nested_dict = nested_dict[key]
            with self.origin.state.mutate(bind[0]):
                nested_dict[bind[-1]] = value
        else:
            self.origin.state[self.bind] = value

    @property
    def page(self):
        if self._page:
            return self._page
        elif isinstance(self, Page):
            return self

    @property
    def router(self):
        if self.application:
            return self.application.router

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        existing_parent = getattr(self, "_parent", None)
        if new_parent == existing_parent:
            if new_parent and self not in new_parent.children:
                existing_parent.children.append(self)
            return

        if existing_parent and self in existing_parent.children:
            existing_parent.children.remove(self)
        if new_parent and self not in new_parent.children:
            new_parent.children.append(self)

        self._parent = new_parent

    def add(self, *children):
        for child in children:
            if isinstance(child, Tag):
                child.parent = self
            else:
                self.children.append(child)

    def redraw(self):
        if self in self.page.redraw_list:
            self.page.redraw_list.remove(self)

        try:
            element = self.element
        except ElementNotInDom:
            return

        if is_server_side:
            old_active_element_id = None
        else:
            old_active_element_id = self.document.activeElement.id if self.document.activeElement else None

            self.recursive_call("_retain_implicit_attrs")

        self.children = []

        attrs = self.get_default_attrs()
        attrs.update(self.attrs)

        self.update_title()
        with self:
            self.generate_children()

        staging_element = self._create_element(attrs)

        self._render_onto(staging_element, attrs)

        patch_dom_element(staging_element, element)

        if old_active_element_id is not None:
            el = self.document.getElementById(old_active_element_id)
            if el:
                el.focus()

        self.recursive_call("on_redraw")

    def trigger_event(self, event, detail=None, **kwargs):
        """
                Triggers an event to be consumed by code using this class.

                Args:
                    event (str): The name of the event to trigger. If the event name contains underscores, a warning message is printed suggesting to use dashes instead.
                    detail (dict, optional): Additional data to be sent with the event. This should be a dictionary where the keys and values will be converted to JavaScript objects.
                    **kwargs: Additional keyword arguments. These arguments are not used in the implementation of the method and are ignored.
        ß"""
        if "_" in event:
            print("Triggering event with underscores. Did you mean dashes?: ", event)

        # noinspection PyUnresolvedReferences
        from pyscript.ffi import to_js

        # noinspection PyUnresolvedReferences
        from js import Object, Map

        if detail:
            event_object = to_js({"detail": Map.new(Object.entries(to_js(detail)))})
        else:
            event_object = to_js({})

        self.element.dispatchEvent(CustomEvent.new(event, event_object))

    def update_title(self):
        """
        To be overridden by subclasses (usually pages), this method should update the Window title as needed.

        Called on mounting or redraw.
        """
        pass

    def __enter__(self):
        self.stack.append(self)
        self.origin_stack[0].append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stack.pop()
        self.origin_stack[0].pop()
        return False

    def __str__(self):
        return self.tag_name

    def __repr__(self):
        return f"<{self} ({id(self)})>"


class Slot(Tag):
    def __init__(self, ref, slot_name="default", tag_name="span", **kwargs):
        self.slot_name = slot_name
        super().__init__(tag_name=tag_name, ref=ref, **kwargs)

    def __str__(self):
        return f"Slot: {self.slot_name}"


class Component(Tag, Stateful):
    """
    Components are a way of defining reusable and composable elements in PuePy. They are a subclass of Tag, but provide
    additional features such as state management and props. By defining your own components and registering them, you
    can create a library of reusable elements for your application.

    Attributes:
        enclosing_tag (str): The tag name that will enclose the component. To be defined as a class attribute on subclasses.
        component_name (str): The name of the component. If left blank, class name is used. To be defined as a class attribute on subclasses.
        redraw_on_state_changes (bool): Whether the component should redraw when its state changes. To be defined as a class attribute on subclasses.
        redraw_on_app_state_changes (bool): Whether the component should redraw when the application state changes. To be defined as a class attribute on subclasses.
        props (list): A list of props for the component. To be defined as a class attribute on subclasses.
    """

    enclosing_tag = "div"
    component_name = None
    redraw_on_state_changes = True
    redraw_on_app_state_changes = True

    props = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, tag_name=self.enclosing_tag, **kwargs)
        self.state = ReactiveDict(self.initial())
        self.add_context("state", self.state)

        self.slots = {}

    def _handle_attrs(self, kwargs):
        self._handle_props(kwargs)

        super()._handle_attrs(kwargs)

    def _handle_props(self, kwargs):
        if not hasattr(self, "props_expanded"):
            self._expanded_props()

        self.props_values = {}
        for name, prop in self.props_expanded.items():
            value = kwargs.pop(prop.name, prop.default_value)
            setattr(self, name, value)
            self.props_values[name] = value

    @classmethod
    def _expanded_props(cls):
        # This would be ideal for metaprogramming, but we do it this way to be compatible with Micropython. :/
        props_expanded = {}
        for prop in cls.props:
            if isinstance(prop, Prop):
                props_expanded[prop.name] = prop
            elif isinstance(prop, dict):
                props_expanded[prop["name"]] = Prop(**prop)
            elif isinstance(prop, str):
                props_expanded[prop] = Prop(name=prop)
            else:
                raise PropsError(f"Unknown prop type {type(prop)}")
        cls.props_expanded = props_expanded

    def initial(self):
        """
        To be overridden in subclasses, the `initial()` method defines the initial state of the component.

        Returns:
            (dict): Initial component state
        """
        return {}

    def _on_state_change(self, context, key, value):
        super()._on_state_change(context, key, value)

        if context == "state":
            redraw_rule = self.redraw_on_state_changes
        elif context == "app":
            redraw_rule = self.redraw_on_app_state_changes
        else:
            return

        if redraw_rule is True:
            self.page.redraw_tag(self)
        elif redraw_rule is False:
            pass
        elif isinstance(redraw_rule, (list, set)):
            if key in redraw_rule:
                self.page.redraw_tag(self)
        else:
            raise Exception(f"Unknown value for redraw rule: {redraw_rule} (context: {context})")

    def insert_slot(self, name="default", **kwargs):
        """
        In defining your own component, when you want to create a slot in your `populate` method, you can use this method.

        Args:
            name (str): The name of the slot. If not passed, the default slot is inserted.
            **kwargs: Additional keyword arguments to be passed to Slot initialization.

        Returns:
            Slot: The inserted slot object.
        """
        if name in self.slots:
            self.slots[name].parent = Tag.stack[-1]  # The children will be cleared during redraw, so re-establish
        else:
            self.slots[name] = Slot(ref=f"slot={name}", slot_name=name, page=self.page, parent=Tag.stack[-1], **kwargs)
        slot = self.slots[name]
        if self.origin:
            slot.origin = self.origin
            if slot.ref:
                self.origin.refs[slot.ref] = slot
        return slot

    def slot(self, name="default"):
        """
        To be used in the `populate` method of code making use of this component, this method returns the slot object
        with the given name. It should be used inside of a context manager.

        Args:
            name (str): The name of the slot to clear and return.

        Returns:
            Slot: The cleared slot object.
        """
        #
        # We put this here, so it clears the children only when the slot-filler is doing its filling.
        # Otherwise, the previous children are kept. Lucky them.
        self.slots[name].children = []
        return self.slots[name]

    def __enter__(self):
        self.stack.append(self)
        self.origin_stack[0].append(self)
        self.component_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stack.pop()
        self.origin_stack[0].pop()
        self.component_stack.pop()
        return False

    def __str__(self):
        return f"{self.component_name or self.__class__.__name__} ({self.ref} {id(self)})"

    def __repr__(self):
        return f"<{self}>"


class Page(Component):
    def __init__(self, matched_route=None, application=None, **kwargs):
        ref = mixed_to_underscores(self.__class__.__name__)
        self.matched_route = matched_route
        self._application = application

        self.python_css_classes = set()

        self._redraw_timeout_set = False
        self.redraw_list = set()

        super().__init__(ref=ref, **kwargs)
        if self.application:
            self.add_context("app", self.application.state)

    def update_title(self):
        title = self.page_title()
        if title is not None:
            self.document.title = title

    def page_title(self):
        pass

    def redraw_tag(self, tag):
        assert isinstance(tag, Tag)
        self.redraw_list.add(tag)

        if not self._redraw_timeout_set:
            if is_server_side:
                self._do_redraw()
            else:
                setTimeout(create_proxy(self._do_redraw), 1)
                self._redraw_timeout_set = True

    def _do_redraw(self):
        try:
            redrawn_already = set()
            try:
                while self.redraw_list:
                    tag = self.redraw_list.pop()
                    if tag in redrawn_already:
                        raise Exception(
                            "A redraw event is causing a circular redraw event loop. Yo dawg, are you causing "
                            "a redraw from your redraw?"
                        )

                    tag.redraw()
                    redrawn_already.add(tag)
            finally:
                self._redraw_timeout_set = False
        except PageError as e:
            self.application.handle_page_error(e)
        except Exception as e:
            self.application.handle_error(e)

    def add_python_css_classes(self):
        """
        Iterates over Python css classes defined by elements and puts them in the head of the document.
        """
        css_class: CssClass
        css_rules = []
        for css_class in self.python_css_classes:
            css_rules.append(css_class.render_css())

        if css_rules:
            el = self.document.getElementById("puepy-runtime-css")
            if el:
                created = False
            else:
                el = self.document.createElement("style")
                el.type = "text/css"
                created = True
            el.innerHTML = ""
            el.appendChild(self.document.createTextNode("\n".join(css_rules)))
            if created:
                self.document.head.appendChild(el)


class Builder:
    def __init__(self):
        self.components = {}

    # noinspection t
    def generate_tag(self, tag_name, *children, **kwargs):
        tag_name = tag_name.lower().strip()
        if kwargs.get("tag"):
            tag_name = kwargs.pop("tag")
        elif "_" in tag_name:
            tag_name = tag_name.replace("_", "-")

        if tag_name == "insert_slot":
            print(f"Called t.insert_slot. Did you mean self.insert_slot?")
        elif tag_name == "slot":
            print(f"Called t.slot. Did you mean <component>.slot?")

        parent = Tag.stack[-1] if Tag.stack else None
        parent_component = Tag.component_stack[-1] if Tag.component_stack else None
        root_tag = Tag.stack[0] if Tag.stack else None
        origin = Tag.population_stack[-1] if Tag.population_stack else None

        # The root tag might not always be the page, but if it isn't, it should have a reference to the
        # actual page.
        if isinstance(root_tag, Page):
            page = root_tag
        elif root_tag:
            page = root_tag.page
        else:
            raise Exception("t.generate_tag called without a context")

        # Determine ref value
        ref_part = "__" + (f"{parent.ref}.{tag_name}_{len(parent.children) + 1}").lstrip("_")

        ref = kwargs.pop("ref", ref_part)

        if ref and origin and ref in origin._refs_pending_removal:
            element: Tag = origin._refs_pending_removal.pop(ref)

            assert element.origin == origin
            element._configure(kwargs)
            element.children = []
            if children:
                element.add(*children)
            element.parent = parent
        elif tag_name in self.components:
            element = self.components[tag_name](
                ref=ref,
                page=page,
                parent=parent,
                parent_component=parent_component,
                origin=origin,
                children=children,
                **kwargs,
            )
        else:
            element = Tag(
                tag_name,
                ref=ref,
                page=page,
                parent=parent,
                parent_component=parent_component,
                origin=origin,
                children=children,
                **kwargs,
            )
        origin.refs[ref] = element
        with element:
            element.generate_children()
        return element

    def add_library(self, library):
        for component in library.components:
            self.add_component(component)

    def component(self):
        def inner(cls):
            self.add_component(cls)
            return cls

        return inner

    def add_component(self, component: Component):
        if component.component_name:
            component_name = component.component_name.replace("_", "-")
        else:
            component_name = mixed_to_underscores(component.__name__, "-")
        self.components[component_name.lower()] = component

    def __call__(self, *texts):
        parent = Tag.stack[-1] if Tag.stack else None
        if not parent:
            raise Exception("Cannot call t() to generate text without a parent")
        parent.add(*texts)

    def __getattr__(self, name):
        def _tag(*children, **kwargs):
            return self.generate_tag(name, *children, **kwargs)

        return _tag


t = Builder()


class html(str):
    pass
