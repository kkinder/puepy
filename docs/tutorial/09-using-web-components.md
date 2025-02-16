# Using Web Components

[Web Components](https://developer.mozilla.org/en-US/docs/Web/API/Web_components) are a collection of technologies, supported by all modern browsers, that let developers reuse custom components in a framework-agnostic way. Although PuePy is an esoteric framework, and no major component libraries exist for it (as they do with React or Vue), you can use Web Component widgets easily in PuePy and make use of common components available on the Internet.

## Using Shoelace

[Shoelace](http://shoelace.style) is a popular and professionally developed suite of web components for building high quality user experiences. In this example, we'll see how to use Shoelace Web Components inside a project of ours. Here is a working example:

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/09_webcomponents/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest" height="20em"/>

### Adding remote assets

First, we'll need to load Shoelace from its CDN in our HTML file:

```html title="index.html"
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.1/cdn/themes/light.css"/>
<script type="module"
      src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.1/cdn/shoelace-autoloader.js"></script>
```

### Using Web Components in Python

Because WebComponents are initialized just like other HTML tags, they can be used directly in Python:

```Python
@app.page()
class DefaultPage(Page):
    def populate(self):
        with t.sl_dialog(label="Dialog", classes="dialog-overview", tag="sl-dialog", ref="dialog"):  # (1)!
            t("Web Components are just delightful.")
            t.sl_button("Close", slot="footer", variant="primary", on_click=self.on_close_click)  # (2)!
        t.sl_button("Open Dialog", tag="sl-button", on_click=self.on_open_click)

    def on_open_click(self, event):
        self.refs["dialog"].element.show()

    def on_close_click(self, event):
        self.refs["dialog"].element.hide()
```
1. The `sl_dialog` tag is a custom tag that creates a `sl-dialog` Web Component. It was defined by the Shoelace library we loaded via CDN.
2. The `sl_button` tag is another custom tag that creates a `sl-button` Web Component.

### Access methods and properties of web components

Web Components are meant to be access directly, like this in JavaScript:

```html
<sl-dialog id="foo"></sl-dialog>

<script>
    document.querySelector("#foo").show()
</script>
```

The actual DOM elements are accessible in PuePy, but require using the `.element` attribute of the higher level Python
instance of your tag:

```Python
self.refs["dialog"].element.show()
```
