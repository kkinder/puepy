from .errors import ElementNotInDom, PropsError
from .reactivity import ReactiveDict
from .util import (
    mixed_to_underscores,
    merge_classes,
    jsobj,
    _extract_event_handlers,
    patch_dom_element,
)

from .runtime import (
    add_event_listener,
    remove_event_listener,
    create_proxy,
    document,
    is_server_side,
    setTimeout,
    CustomEvent,
)


class Prop:
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
    A class that allows you to push and pop a context
    """

    stack = []
    population_stack = []
    component_stack = []
    default_classes = []
    default_attrs = {}
    default_role = None

    document = document

    def __init__(self, tag_name, ref, page: "Page" = None, parent=None, parent_component=None, children=None, **kwargs):
        self.added_event_listeners = []
        self._rendered_element = None

        self.children = []
        self.children_by_ref = {}
        if children:
            self.add(*children)

        self.tag_name = tag_name
        self.ref = ref

        if isinstance(page, Page):
            self._page = page
        elif isinstance(self, Page):
            self._page = self
        elif page:
            raise Exception(f"Unknown page type {type(page)}")
        else:
            raise Exception("No page passed")

        if isinstance(parent, Tag):
            parent.add(self)
        elif parent:
            raise Exception(f"Unknown parent type {type(parent)}: {repr(parent)}")
        else:
            self._parent = None

        if isinstance(parent_component, Component):
            self.parent_component = parent_component
        elif parent_component:
            raise Exception(f"Unknown parent_component type {type(parent_component)}: {repr(parent_component)}")
        else:
            self.parent_component = None

        self._children_generated = False
        self.destroyed = False

        self._handle_kwargs(kwargs)

    def _handle_kwargs(self, kwargs):
        self.event_handlers = _extract_event_handlers(kwargs)
        self._handle_bind(kwargs)
        self._handle_attrs(kwargs)

    def _handle_bind(self, kwargs):
        self.bind_component = self.population_stack[-1] if self.population_stack else None
        if "bind" in kwargs:
            self.bind = kwargs.pop("bind")
            if "value" in kwargs:
                raise Exception("Cannot specify both 'bind' and 'value'")
            if "on_input" in self.event_handlers:
                raise Exception("Cannot specify both 'bind' and 'on_input'")
        else:
            self.bind = None

    def _handle_attrs(self, kwargs):
        self.attrs = {}
        for k, v in kwargs.items():
            if hasattr(self, f"set_{k}"):
                getattr(self, f"set_{k}")(v)
            else:
                self.attrs[k] = v

    def populate(self):
        pass

    def generate_children(self):
        """
        Runs populate, but first adds self to self.population_stack, and removes it after populate runs.

        That way, as populate is executed, self.population_stack can be used to figure out what the innermost populate()
        method is being run and thus, where to send bind= parameters.
        """
        self.population_stack.append(self)
        try:
            self.populate()
        finally:
            self.population_stack.pop()

    def render(self):
        if "xmlns" in self.attrs:
            element = self.document.createElementNS(self.attrs.get("xmlns"), self.tag_name)
        else:
            element = self.document.createElement(self.tag_name)

        element.setAttribute("id", self.element_id)
        if is_server_side:
            element.setIdAttribute("id")

        self._render_onto(element)
        return element

    @property
    def element_id(self):
        return self.attrs.get("id", f"e-{id(self)}")

    @property
    def element(self):
        el = self.document.getElementById(self.element_id)
        if el:
            return el
        else:
            raise ElementNotInDom(self.element_id)

    def _render_onto(self, element):
        self._rendered_element = element
        attrs = self.default_attrs.copy()
        attrs.update(self.attrs)

        # Handle classes
        classes = self.get_render_classes(attrs)

        if classes:
            # element.className = " ".join(classes)
            element.setAttribute("class", " ".join(classes))

        # Add attributes
        for key, value in self.attrs.items():
            if key not in ("class_name", "classes", "class"):
                if hasattr(self, f"handle_{key}_attr"):
                    getattr(self, f"handle_{key}_attr")(element, value)
                else:
                    if key.endswith("_"):
                        attr = key[:-1]
                    else:
                        attr = key
                    element.setAttribute(attr.replace("_", "-"), value)

        if "role" not in self.attrs and self.default_role:
            element.setAttribute("role", self.default_role)

        # Add event handlers
        for key, value in self.event_handlers.items():
            if isinstance(value, (list, tuple)):
                for handler in value:
                    self._add_event_listener(element, key, handler)
            else:
                self._add_event_listener(element, key, value)

        # Add bind

        if self.bind and self.bind_component:
            if _element_input_type(element) == "checkbox":
                if is_server_side and self.bind_component.state[self.bind]:
                    element.setAttribute("checked", self.bind_component.state[self.bind])
                else:
                    element.checked = bool(self.bind_component.state[self.bind])
            else:
                if is_server_side:
                    element.setAttribute("value", self.bind_component.state[self.bind])
                else:
                    element.value = self.bind_component.state[self.bind]

            self._add_event_listener(element, "input", self.on_bind_input)

        elif self.bind:
            raise Exception("Cannot specify bind a valid parent component")

        self.render_children(element)

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
            else:
                raise Exception(f"Unknown child type {type(child)} onto {self}")

    def get_render_classes(self, attrs):
        return merge_classes(
            set(self.get_default_classes()),
            attrs.pop("class_name", []),
            attrs.pop("classes", []),
            attrs.pop("class", []),
        )

    def get_default_classes(self):
        return self.default_classes

    def _add_event_listener(self, element, event, listener):
        """
        Just an internal wrapper around add_event_listener (JS function) that keeps track of what we added, so
        we can garbage collect it later.

        Should probably not be used outside this class.
        """
        self.added_event_listeners.append((element, event, listener))
        if not is_server_side:
            add_event_listener(element, event, listener)

    def add_event_handler(self, event, handler):
        if event not in self.event_handlers:
            self.event_handlers[event] = handler
        else:
            existing_handler = self.event_handlers[event]
            if isinstance(existing_handler, (list, tuple)):
                self.event_handlers[event] = [existing_handler] + list(handler)
            else:
                self.event_handlers[event] = [existing_handler, handler]
        if self._rendered_element:
            self._add_event_listener(self._rendered_element, event, handler)

    def mount(self, selector_or_element):
        self.update_title()
        if not self._children_generated:
            with self:
                self.generate_children()

        if isinstance(selector_or_element, str):
            element = self.document.querySelector(selector_or_element)
        else:
            element = selector_or_element

        element.innerHTML = ""
        element.appendChild(self.render())
        self.recursive_call("ready")

    def recursive_call(self, method, *args, **kwargs):
        for child in self.children:
            if isinstance(child, Tag):
                child.recursive_call(method, *args, **kwargs)
        getattr(self, method)(*args, **kwargs)

    def ready(self):
        pass

    def on_redraw(self):
        pass

    def on_bind_input(self, event):
        if _element_input_type(event.target) == "checkbox":
            self.bind_component.state[self.bind] = event.target.checked
        else:
            self.bind_component.state[self.bind] = event.target.value

    @property
    def page(self):
        if self._page:
            return self._page
        elif isinstance(self, Page):
            return self

    @property
    def parent(self):
        return self._parent

    def add(self, *children):
        for child in children:
            if isinstance(child, Tag):
                self.children_by_ref[child.ref] = child
                child._parent = self

            self.children.append(child)

    def print_tree(self, n=0):
        if n == 0:
            print("Tree")
        print("." * n, self)
        for child in self.children:
            if isinstance(child, Tag):
                child.print_tree(n + 1)
            else:
                print("." * (n + 1), child)
        if n == 0:
            print("End Tree")

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

        self.children = []

        self.update_title()
        with self:
            self.generate_children()

        if "xmls" in self.attrs:
            staging_element = self.document.createElementNS(self.attrs["xmlns"], self.tag_name)
        else:
            staging_element = self.document.createElement(self.tag_name)
        staging_element.setAttribute("id", self.element_id)
        if is_server_side:
            staging_element.setIdAttribute("id")

        self._render_onto(staging_element)
        # staging_html = staging_element.toxml() if is_server_side else staging_element.outerHTML

        patch_dom_element(staging_element, element)
        # patched_html = element.toxml() if is_server_side else element.outerHTML
        #
        # if staging_html != patched_html:
        #     print("Failed to attempt patching HTML")
        #     print("FROM: ", staging_html)
        #     print("TO:   ", patched_html)
        #     logging.error("Redraw patch not successful", exc_info=True)

        if old_active_element_id is not None:
            el = self.document.getElementById(old_active_element_id)
            if el:
                el.focus()

        self.recursive_call("on_redraw")

    def destroy_orphans(self):
        to_remove = []
        for ref, child in self.children_by_ref.items():
            if child not in self.children:
                to_remove.append((ref, child))
            child.destroy_orphans()
        for ref, child in to_remove:
            del self.children_by_ref[ref]
            if isinstance(child, Tag):
                child.destroy()

    def destroy(self):
        self.destroyed = True
        if self in self.parent.children:
            self.parent.children.remove(self)
        if self.ref in self.parent.children_by_ref:
            del self.parent.children_by_ref[self.ref]

        while self.children:
            child = self.children.pop()
            if isinstance(child, Tag):
                child.destroy()

        if not is_server_side:
            while self.added_event_listeners:
                remove_event_listener(*self.added_event_listeners.pop())

    def trigger_redraw(self):
        self.page.redraw_tag(self)

    def trigger_event(self, event, detail=None, **kwargs):
        from pyscript.ffi import to_js
        from js import Object, Map

        if detail:
            event_object = to_js({"detail": Map.new(Object.entries(to_js(detail)))})
        else:
            event_object = to_js({})

        self.element.dispatchEvent(CustomEvent.new(event, event_object))

    def update_title(self):
        pass

    def __enter__(self):
        self.stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stack.pop()
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


class Component(Tag):
    enclosing_tag = "div"
    component_name = None
    redraw_on_changes = True
    props = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, tag_name=self.enclosing_tag, **kwargs)
        self.state = ReactiveDict(self.initial())
        self.state.listener.add_callback(self._on_state_change)

        self.slots = {}

    def _handle_attrs(self, kwargs):
        self._handle_props(kwargs)

        super()._handle_attrs(kwargs)

    def _handle_props(self, kwargs):
        self.props_expanded = {}
        for prop in self.props:
            if isinstance(prop, Prop):
                self.props_expanded[prop.name] = prop
            elif isinstance(prop, dict):
                self.props_expanded[prop["name"]] = Prop(**prop)
            elif isinstance(prop, str):
                self.props_expanded[prop] = Prop(name=prop)
            else:
                raise PropsError(f"Unknown prop type {type(prop)}")

        for prop in self.props_expanded.keys():
            if prop in kwargs:
                setattr(self, prop, kwargs.pop(prop))
            else:
                setattr(self, prop, None)

    def initial(self):
        return {}

    def _on_state_change(self, key):
        value = self.state[key]

        self.on_state_change(key, value)

        if hasattr(self, f"on_{key}_change"):
            getattr(self, f"on_{key}_change")(value)

        if self.redraw_on_changes is True:
            self.trigger_redraw()
        elif isinstance(self.redraw_on_changes, list):
            if key in self.redraw_on_changes:
                self.trigger_redraw()

    def on_state_change(self, key, value):
        pass

    def insert_slot(self, name="default", **kwargs):
        if name in self.slots:
            assert self.slots[name].page == self.page
            assert self.slots[name].parent == Tag.stack[-1]
            if self.slots[name] not in Tag.stack[-1].children:
                Tag.stack[-1].children.append(self.slots[name])
            Tag.stack[-1].children_by_ref[self.slots[name].ref] = self.slots[name]

            # Moved this to slot()
            # self.slots[name].children = []
        else:
            self.slots[name] = Slot(ref=f"slot={name}", slot_name=name, page=self.page, parent=Tag.stack[-1], **kwargs)
        return self.slots[name]

    def slot(self, name="default"):
        #
        # We put this here, so it clears the children only when the slot-filler is doing its filling.
        # Otherwise, the previous children are kept. Lucky them.
        self.slots[name].children = []
        return self.slots[name]

    def __enter__(self):
        self.stack.append(self)
        self.component_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stack.pop()
        self.component_stack.pop()
        return False

    def __str__(self):
        return f"{self.component_name or self.__class__.__name__} ({self.ref} {id(self)})"

    def __repr__(self):
        return f"<{self}>"


class Page(Component):
    def __init__(self, router=None, matched_route=None, application=None, **kwargs):
        ref = mixed_to_underscores(self.__class__.__name__)
        self.router = router
        self.matched_route = matched_route
        self.application = application

        self._redraw_timeout_set = False
        self.redraw_list = set()

        super().__init__(ref=ref, **kwargs)

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
                tag.destroy_orphans()
        finally:
            self._redraw_timeout_set = False


class Builder:
    def __init__(self):
        self.components = {}

    def generate_tag(self, tag_name, *children, **kwargs):
        tag_name = tag_name.lower().strip()
        parent = Tag.stack[-1] if Tag.stack else None
        parent_component = Tag.component_stack[-1] if Tag.component_stack else None
        root_tag = Tag.stack[0] if Tag.stack else None

        # The root tag might not always be the page, but if it isn't, it should have a reference to the
        # actual page.
        if isinstance(root_tag, Page):
            page = root_tag
        elif root_tag:
            page = root_tag.page
        else:
            raise Exception("t.generate_tag called without a context")

        # Determine ref value
        ref = kwargs.pop("ref", f"_{tag_name}-{len(parent.children) + 1}")

        if ref in parent.children_by_ref:
            element = parent.children_by_ref[ref]
            element._handle_kwargs(kwargs)
            element.children = []
            if children:
                element.add(*children)
            if element not in parent.children:
                parent.children.append(element)
        elif tag_name in self.components:
            element = self.components[tag_name](
                ref=ref,
                page=page,
                parent=parent,
                parent_component=parent_component,
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
                children=children,
                **kwargs,
            )
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
            component_name = component.component_name
        else:
            component_name = mixed_to_underscores(component.__name__)
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
