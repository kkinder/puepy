# Installation

## Client-side installation

Although PuePy is [available on pypi](https://pypi.org), because PuePy is intended primarily as a client-side framework,
"installation" is best achieved by downloading the wheel file and including it in your pyscript `packages` configuration.

A simple first project (with no web server) would be:

- `index.html` (index.html file)
- `pyscript.json` (pyscript config file)
- `hello.py` (Hello World code)
- `puepy-0.3.3-py3-none-any.whl` (PuePy wheel file)

The runtime file would contain only the files needed to actually execute PuePy code; no tests or other files. Runtime
zips are available in each release's notes on GitHub.

### Downloading client runtime

```Bash
curl -O https://files.pythonhosted.org/packages/8b/c0/cda61d314f1bab881d9e5f0c15133ec1c5da37f8f93e4d78aeeb71687da2/puepy-0.3.3-py3-none-any.whl
```

### Setting up your first project

Continue to the [tutorial](tutorial/00-using-this-tutorial.md) to see how to set up your first project.