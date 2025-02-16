# Using Refs

Let's introduce our first bug. Try typing a word in the input box in the demo below.

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/04_refs_problem/index.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest" />

Notice that as you type, each time the page redraws, your input loses focus. This is because PuePy doesn't know which elements are supposed to "match" the ones from the previous refresh, and the ordering is now different. The original `<input>` is being discarded each refresh and replaced with a new one.

Now try the fixed version:

<puepy src="https://kkinder.pyscriptapps.com/puepy-tutorial/latest/tutorial/04_refs_problem/solution.html" edit="https://pyscript.com/@kkinder/puepy-tutorial/latest" />


Here's the problem code and the fixed code. Notice the addition of a `ref=` in the fixed version.

=== "Problem Code"
    ``` py
    @app.page()
    class RefsProblemPage(Page):
        def initial(self):
            return {"word": ""}
    
        def populate(self):
            t.h1("Problem: DOM elements are re-created")
            if self.state["word"]:
                for char in self.state["word"]:
                    t.span(char, classes="char-box")
            with t.div(style="margin-top: 1em"):
                t.input(bind="word", placeholder="Type a word")
    ```

=== "Fixed Code"
    ``` py
    @app.page()
    class RefsSolutionPage(Page):
        def initial(self):
            return {"word": ""}
    
        def populate(self):
            t.h1("Solution: Use ref=")
            if self.state["word"]:
                for char in self.state["word"]:
                    t.span(char, classes="char-box")
            with t.div(style="margin-top: 1em"):
                t.input(bind="word", placeholder="Type a word", ref="enter_word")
    ```


### Using refs to preserve elements between refreshes

To tell PuePy not to garbage collect an element, but to reuse it between redraws, just give it a `ref=` parameter. The ref should be unique to the component you're coding: that is, each ref should be unique among all elements created in the `populate()` method you're writing.

When PuePy finds an element with a ref, it will reuse that ref if it existed in the last refresh, modifying it with any updated parameters passed to it.

!!! tip "Using references in your code"
    The `#!py self.refs` dictionary is available to you in your page or component. You can access elements by their ref name, like `#!py self.refs["enter_word"]`.