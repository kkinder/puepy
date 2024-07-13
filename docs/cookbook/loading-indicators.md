# Showing Loading Indicators

PyScript, on which PuePy is built, provides two runtime options. When combined with PuePy, the total transfer size to
render a PuePy page as reported by Chromium's dev tools for each runtime are:

| Runtime     | Transfer Size |
|-------------|---------------|
| MicroPython | 353 KB        |
| Pyodide     | 5.9 MB        |

MicroPython's runtime, even on a slower connection, is well within the bounds of normal web frameworks. Pyodide,
however, will be perceived as initially quite slow to load on slower connections. Pyodide may be workable for internal
line-of-business software where users have fast connections or in cases where it's accepted that an application may
take some time to initially load, but will be cached during further use.

## Showing an indicator before PuePy loads

Before you mount your PuePy page into its target element, the target element's HTML is rendered in the browser. A
very simple way to show that PuePy hasn't loaded is to include an indicator in the target element, which will be
replaced upon execution by PuePy:

```html
<div id="app">Loading...</div>
```
 
The [Full App Template](A-Full-App-Template.md) example from the tutorial makes use of a
[Shoelace](https://shoelace.style) web component to show a visual loading indicator as a spinning wheel:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example</title>
    <link rel="stylesheet" href="app.css">

    <link rel="stylesheet" href="https://pyscript.net/releases/2024.6.2/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.6.2/core.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.1/cdn/themes/light.css"/>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.1/cdn/shoelace.js"></script>
</head>
<body>
<!-- Show the application with a loading indicator that will be replaced later -->
<div id="app">
    <div style="text-align: center; height: 100vh; display: flex; justify-content: center; align-items: center;">
        <sl-spinner style="font-size: 50px; --track-width: 10px;"></sl-spinner>
    </div>
</div>
<script type="mpy" src="./main.py" config="./pyscript-app.json"></script>
</body>
</html>
```

This will render as a loading indicator, animated, visible only until PuePy mounts the real application code:

![Loading indicator screenshot](../images/loading-indicator.png)


