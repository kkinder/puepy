# FAQ

## Philosophical Questions

### Why not just use Javascript?

If you prefer JavaScript to Python, using it would be the obvious answer. JavaScript has mature tooling available,
there are many excellent frameworks to choose from, and the JavaScript runtimes available in most browsers are
blazingly fast.

Some developers prefer Python, however. For them, PuePy might be a good choice.

### Is WebAssembly ready?

WebAssembly is supported in all major modern browsers, including Safari. Its standard has coalesced and for using
existing JavaScript libraries or components, PyScript provides a robust bridge. WebAssembly is as ready as it needs
to be and is certainly less prone to backwards incompatible changes than many JavaScript projects that production
sites rely on.

## PuePy Design Choices

### Can you use PuePy with a templating language instead of building components inline?

The idea behind PuePy is, at least in part, to have the convenience of building all your software, including its UI,
out in Python's syntax. You may actually find that Python is more succinct, not less, than a similar template might be.
Consider:

```html
<h1>{{ name }}'s grocery shopping list</h1>
<ul>
    {% for item in items %}
        <li>{{ item }}</li>
    {% endfor %}
</ul>
<button on_click="buy()">Buy Items</button>
```

vs:

```Python
with t.h1():
    t(f"{name}'s grocery shopping list")
with t.ul():
    for item in items:
       t.li(item)
t.button("Buy Items", on_click=self.buy)
```

If you have a whole HTML file ready to go, try out the HTML to
Python [converter](https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/08_libraries/index.html) built in
the [PypII libraries](tutorial/08-pypi-libraries.md) tutorial chapter, which uses BeautifulSoup.

### Can I use SVGs?

Yes, as long as you specify xmlns:

```Python
with t.svg(xmlns="http://www.w3.org/2000/svg"):
    ...
```

### How can I use HTML directly?

If you want to directly insert HTML into a component's rendering, you can use the `html()` string:

```Python
from puepy.core import html


class MyPage(Page):
    def populate(self):
        t(html("<strong>Hello!</strong>"))
```