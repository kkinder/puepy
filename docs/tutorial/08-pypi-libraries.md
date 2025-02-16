# Using PyPi Libraries

Let's make use of a PyPi library in our project. In this example, we'll use BeautifulSoup to parse an HTML document and actually generate a PuePy component that would render the same content.

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/08_libraries/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest" height="40em"/>

!!! note "Small embedded example"
    This example may be more useful in a full browser window. [Open in new window](https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/08_libraries/index.html)

## Using Full CPython/Pyodide

To make use of a library like BeautifulSoup, we will configure PuePy to use the full CPython/Pyoide runtime, rather than the more minimal MicroPython runtime. This is done by specifying the runtime in the `<script>` tag in index.html:

```html
<script type="py" src="./libraries.py" config="./pyscript-bs.json"></script>
```

## Requiring packages from pypi

In `pyscript-bs.json`, we also must specify that we need BeautifulSoup4. This is done by adding it to the `packages` section of the config file:

```json title="pyscript-bs.json" hl_lines="6"
{
  "name": "PuePy Tutorial",
  "debug": true,
  "packages": [
    "./puepy-0.5.0-py3-none-any.whl",
    "beautifulsoup4"
  ],
  "js_modules": {
    "main": {
      "https://cdn.jsdelivr.net/npm/morphdom@2.7.2/+esm": "morphdom"
    }
  }
}
```

The `type` attribute in the PyScript `<script>` tag can have two values:

- `mpy`: Use the MicroPython runtime
- `py`: Use the CPython/Pyodide runtime

!!! note "See Also"

    See also the [runtimes developer guide](../guide/runtimes.md) for more information on runtimes.

Once the dependencies are specified in the config file, we can import the library in our source file:

``` python
from bs4 import BeautifulSoup, Comment
```

??? example "Full Example Source"
    ``` py title="libraries.py" 
    --8<-- "examples/tutorial/08_libraries/libraries.py"
    ```

!!! Note "PyScript documentation on packages"
    For more information, including packages available to 
    MicroPython, [refer to the PyScript docs](https://docs.pyscript.net/2025.2.2/user-guide/configuration/#packages).