# PyScript Config

PyScript's configuration is fully [documented](https://docs.pyscript.net/2025.2.2/user-guide/configuration/) in the PyScript documentation. Configuration for PuePy simply requires adding the PuePy runtime files (see [Quick Start - Installation](../getting-started/quick-start.md)) and Morphdom:

```JSON
{
  "name": "PuePy Tutorial",
  "debug": true,
  "packages": [
    "./puepy-{{project_version}}-py3-none-any.whl"
  ],
  "js_modules": {
    "main": {
      "https://cdn.jsdelivr.net/npm/morphdom@2.7.4/+esm": "morphdom"
    }
  }
}
```