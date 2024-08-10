# Installation

## Client-side installation

Although PuePy is [available on pypi](https://pypi.org/project/puepy/), because PuePy is intended primarily as a client-side framework,
"installation" is best achieved by downloading the wheel file and including it in your pyscript `packages` configuration.

A simple first project (with no web server) would be:

- `index.html` (index.html file)
- `pyscript.json` (pyscript config file)
- `hello.py` (Hello World code)
- `puepy-0.4.0-py3-none-any.whl` (PuePy wheel file)

The runtime file would contain only the files needed to actually execute PuePy code; no tests or other files. 
Runtime zips are available in each release's notes on [GitHub](https://github.com/kkinder/puepy/releases).

### Downloading client runtime

```Bash
curl -O https://files.pythonhosted.org/packages/78/8f/d0f79f3c64c9ddbe8fd49028438a102b134cf5b01908e91fb17a5aec868b/puepy-0.4.0-py3-none-any.whl
```

### Setting up your first project

Continue to the [tutorial](tutorial/00-using-this-tutorial.md) to see how to set up your first project.
