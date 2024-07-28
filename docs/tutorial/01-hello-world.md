# Hello, World!

Let's start with the simplest possible: Hello, World!

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/01_hello_world/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest"/>

=== "hello_world.py"

    ``` py linenums="1"
    --8<-- "puepy/examples/tutorial/01_hello_world/hello_world.py"
    ```

=== "index.html"

    ``` html linenums="1"
    --8<-- "puepy/examples/tutorial/01_hello_world/index.html"
    ```

=== "pyscript.json"

    ``` json linenums="1"
    {
      "name": "PuePy Tutorial",
      "debug": true,
      "files": {},
      "js_modules": {
        "main": {
          "https://cdn.jsdelivr.net/npm/morphdom@2.7.2/+esm": "morphdom"
        }
      },
      "packages": [
        "./puepy-0.3.6-py3-none-any.whl"
      ]
    }
    ```

## Including PyScript

Let's start with the HTML. To use PuePy, we include PyScript from its CDN:

``` html title="index.html"
--8<-- "puepy/examples/tutorial/01_hello_world/index.html:7:8"
```

Then, we include our PyScript config file and also execute our `hello_world.py` file:

``` html title="index.html"
--8<-- "puepy/examples/tutorial/01_hello_world/index.html:12:12"
```

## PyScript configuration

!!! info "PyScript Configuration"

    The official PyScript documentation has more information on [PyScript configuration](https://docs.pyscript.net/2024.7.1/user-guide/configuration/).

The PyScript configuration must, at minimum, tell PyScript to use PuePy (usually as a package) and include Morphdom, which is a dependency of PuePy.

## The Python Code

Let's take a look at our Python code which actually renders Hello, World.

First, we import `Application`, `Page`, and `t` from `puepy`:

``` py
--8<-- "puepy/examples/tutorial/01_hello_world/hello_world.py:1:1"
```

To use PuePy, you must always create an `Application` instance, even if the application only has one page:

``` py
--8<-- "puepy/examples/tutorial/01_hello_world/hello_world.py:3:3"
```

Next, we define a Page and use the `t` singleton to compose our DOM in the `populate()` method. Don't worry too much about the details for now; just know that this is how we define pages and components in PuePy:

``` py
--8<-- "puepy/examples/tutorial/01_hello_world/hello_world.py:6:9"
```

Finally, we tell PuePy where to *mount* the application. This is where the application will be rendered in the DOM. The `#app` element was already defined in our HTML file.

``` py
--8<-- "puepy/examples/tutorial/01_hello_world/hello_world.py:12:12"
```

And with that, the page is added to the application, and the application is mounted in the element with id `app`.

!!! note "Watching for Errors"

    Use your browser's development console to watch for any errors.