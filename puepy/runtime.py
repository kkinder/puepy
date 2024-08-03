import sys

PLATFORM_PYODIDE = "pyodide"
PLATFORM_MICROPYTHON = "micropython"
PLATFORM_CPYTHON = "cpython"


def _detect_platform():
    if sys.platform == "emscripten":
        return PLATFORM_PYODIDE
    elif sys.platform == "webassembly" and sys.implementation.name == "micropython":
        return PLATFORM_MICROPYTHON
    elif sys.implementation.name == "cpython":
        return PLATFORM_CPYTHON


platform = _detect_platform()
is_server_side = platform not in (PLATFORM_PYODIDE, PLATFORM_MICROPYTHON)

if platform == PLATFORM_PYODIDE:
    from pyodide.ffi import create_proxy
    from pyodide.ffi.wrappers import add_event_listener, remove_event_listener
elif platform == PLATFORM_MICROPYTHON:
    from pyscript.ffi import create_proxy

    from js import addEventListener, removeEventListener

    def add_event_listener(elt, event, listener):
        return elt.addEventListener(event, listener)

    def remove_event_listener(elt, event, listener):
        return elt.removeEventListener(event, create_proxy(listener))

    # add_event_listener, remove_event_listener = addEventListener, removeEventListener

if is_server_side:
    document = setTimeout = Object = CustomEvent = window = history = add_event_listener = remove_event_listener = None

    def create_proxy(obj):
        return obj

    def next_tick(fn):
        fn()

else:
    from js import document, setTimeout, Object, CustomEvent, window, history

    def next_tick(fn):
        setTimeout(create_proxy(fn), 100)
