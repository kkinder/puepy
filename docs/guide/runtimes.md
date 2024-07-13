# Runtimes

From its upstream project, PyScript, PuePy supports two runtime environments:

- MicroPython
- Pyodide

There are some interface differences, as well as technical ones, described in the [official PyScript docs](https://docs.pyscript.net/2024.7.1/user-guide/architecture/#interpreters). Additionally, many standard library features are missing from MicroPython. MicroPython does not have access to PyPi packages, nor does MicroPython type hinting or other advanced features as thoroughly as Pyodide.

MicroPython, however, has just a ~170k runtime, making it small enough to load on "normal" websites without the performance hit of Pyodide's 11MB runtime. It is ideal for situations where webpage response time is important.

## When to use Pyodide

You may consider using Pyodide when:

- Initial load time is less important
- You need to use PyPi packages
- You need to use advanced Python features
- You need to use the full Python standard library
- You need to use type hinting
- You need to use Python 3.9 or later

## When to use MicroPython

You may consider using MicroPython when:

- Initial load time is important
- Your PuePy code will use only simple Python features to add reactivity and interactivity to websites

## How to switch runtimes

To choose a runtime, specify either `type="mpy"` or `type="py"` in your `<script>` tag when loading PuePy. For example:

### Loading Pyodide

```html
<script type="mpy" src="./main.py" config="pyscript.json"></script>
```

### Loading MicroPython

```html
<script type="mpy" src="./main.py" config="pyscript.json"></script>
```

!!! Note "See Also"
    - [PyScript Architecture: Interpreters](https://docs.pyscript.net/2024.7.1/user-guide/architecture/#interpreters)
    - [Pyodide Project](https://pyodide.org)
    - [MicroPython Project](https://micropython.org)