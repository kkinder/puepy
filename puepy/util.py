from .runtime import is_server_side, create_proxy, Object, platform, PLATFORM_PYODIDE

try:
    from pyscript.ffi import to_js
except ImportError:

    def to_js(obj):
        return obj


def mixed_to_underscores(input_string, separator="_"):
    result = []
    for index, char in enumerate(input_string):
        if char.isupper() and index > 0:
            result.append(separator)
        result.append(char.lower())
    return "".join(result)


def merge_classes(*items):
    from .core import CssClass

    classes = set()
    python_css_classes = []
    exclude_classes = set()

    for class_option in items:
        if isinstance(class_option, str):
            classes.update(class_option.split(" "))
        elif isinstance(class_option, list):
            classes.update(class_option)
        elif isinstance(class_option, dict):
            classes.update([key for key, value in class_option.items() if value])
            exclude_classes.update([key for key, value in class_option.items() if not value])
        elif class_option is None:
            pass
        elif isinstance(class_option, CssClass):
            classes.add(class_option)
        else:
            classes.update(list(class_option))

    for c in list(classes):
        if isinstance(c, CssClass):
            classes.remove(c)
            classes.add(c.class_name)
            python_css_classes.append(c)

    for c in classes:
        if c.startswith("/"):
            exclude_classes.add(c)
            exclude_classes.add(c[1:])
    classes.difference_update(exclude_classes)
    return classes, python_css_classes


def jsobj(**kwargs):
    if is_server_side:
        return kwargs
    else:
        return to_js(kwargs)


def _extract_event_handlers(kwargs):
    event_handlers = {}
    for key in list(kwargs.keys()):
        if key.startswith("on_"):
            event_handlers[key[3:]] = kwargs.pop(key)
    return event_handlers


def get_attributes(element):
    if is_server_side:
        return list(element.attributes.keys())
    else:
        return [a.name for a in element.attributes]


def patch_dom_element(source_element, target_element):
    """
    This method patches the target DOM element with attributes and children from the source DOM element. It follows
    the following steps:

    1. Removes attributes from the target element that don't exist in the source element
    2. Sets attributes from the source element to the target element
    3. Iterates over the children of both source and target elements, preserving elements where possible

    :param source_element: The source DOM element that contains the attributes and children to patch.
    :param target_element: The target DOM element that will be patched with the attributes and children from the source
    element.
    """
    # Use morphdom on the client side
    if morphdom:
        return morphdom.default(target_element, source_element)

    # Remove attributes that don't exist in source element
    for attribute in get_attributes(target_element):
        if not source_element.hasAttribute(attribute):
            target_element.removeAttribute(attribute)

    # Set attributes from source to target
    for attribute in get_attributes(source_element):
        target_element.setAttribute(attribute, source_element.getAttribute(attribute))

    if not is_server_side:
        if source_element.tagName.lower() in ("input", "radio", "option", "textarea"):
            target_element.value = source_element.value

    # Iterate over the children
    target_child_nodes = list(target_element.childNodes)
    source_child_nodes = list(source_element.childNodes)

    child_count = max(len(source_child_nodes), len(target_child_nodes))
    for i in range(child_count):
        source_child = source_child_nodes[i] if len(source_child_nodes) > i else None
        target_child = target_child_nodes[i] if len(target_child_nodes) > i else None

        if source_child and target_child:
            if source_child.nodeName == target_child.nodeName and target_child.nodeName == "#text":
                target_child.nodeValue = source_child.nodeValue
            elif source_child.nodeName == target_child.nodeName:
                patch_dom_element(source_child, target_child)
            else:
                target_element.replaceChild(source_child, target_child)

        elif source_child:
            target_element.appendChild(source_child)
        elif target_child:
            target_element.removeChild(target_child)


# Import morphdom if available
morphdom = None
if not is_server_side:
    try:
        from pyscript.js_modules import morphdom
    except ImportError:
        print(
            "Consider loading https://cdn.jsdelivr.net/npm/morphdom@2.7.4/+esm into js_modules for faster"
            " patching and more reliable DOM updates."
        )
